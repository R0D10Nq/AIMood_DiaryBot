"""
CRUD операции для работы с записями настроения
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func, extract
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta

from ..models.mood_entry import MoodEntry
from ..models.user import User
from ..schemas import MoodEntryCreate, MoodEntryUpdate


class MoodEntryCRUD:
    """CRUD операции для модели MoodEntry"""
    
    def get_by_id(self, db: Session, entry_id: int) -> Optional[MoodEntry]:
        """Получить запись по ID с AI анализом"""
        return db.query(MoodEntry).options(
            joinedload(MoodEntry.ai_analysis)
        ).filter(MoodEntry.id == entry_id).first()
    
    def get_by_user_and_date(self, db: Session, user_id: int, entry_date: date) -> Optional[MoodEntry]:
        """Получить запись пользователя за конкретную дату"""
        return db.query(MoodEntry).filter(
            and_(
                MoodEntry.user_id == user_id,
                func.date(MoodEntry.entry_date) == entry_date
            )
        ).first()
    
    def get_user_entries(
        self, 
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[MoodEntry]:
        """Получить записи пользователя за период"""
        query = db.query(MoodEntry).options(
            joinedload(MoodEntry.ai_analysis)
        ).filter(MoodEntry.user_id == user_id)
        
        if start_date:
            query = query.filter(MoodEntry.entry_date >= start_date)
        if end_date:
            query = query.filter(MoodEntry.entry_date <= end_date)
        
        return query.order_by(desc(MoodEntry.entry_date)).offset(skip).limit(limit).all()
    
    def get_recent_entries(self, db: Session, user_id: int, days: int = 7) -> List[MoodEntry]:
        """Получить последние записи пользователя"""
        start_date = datetime.utcnow() - timedelta(days=days)
        return self.get_user_entries(db, user_id, start_date=start_date)
    
    def get_latest_entry(self, db: Session, user_id: int) -> Optional[MoodEntry]:
        """Получить последнюю запись пользователя"""
        return db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(desc(MoodEntry.entry_date)).first()
    
    def create(self, db: Session, entry_in: MoodEntryCreate, user_id: int) -> MoodEntry:
        """Создать новую запись настроения"""
        entry_data = entry_in.model_dump()
        entry_data["user_id"] = user_id
        entry_data["created_at"] = datetime.utcnow()
        entry_data["updated_at"] = datetime.utcnow()
        
        db_entry = MoodEntry(**entry_data)
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return db_entry
    
    def update(self, db: Session, entry_id: int, entry_in: MoodEntryUpdate) -> Optional[MoodEntry]:
        """Обновить запись настроения"""
        entry = self.get_by_id(db, entry_id)
        if not entry:
            return None
        
        update_data = entry_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entry, field, value)
        
        entry.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(entry)
        return entry
    
    def delete(self, db: Session, entry_id: int) -> bool:
        """Удалить запись настроения"""
        entry = self.get_by_id(db, entry_id)
        if not entry:
            return False
        
        db.delete(entry)
        db.commit()
        return True
    
    def get_user_stats(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Получить статистику пользователя"""
        entries = db.query(MoodEntry).filter(MoodEntry.user_id == user_id).all()
        
        if not entries:
            return {
                "total_entries": 0,
                "average_mood": 0,
                "mood_trend": "no_data",
                "streak_days": 0
            }
        
        # Базовая статистика
        total_entries = len(entries)
        average_mood = sum(entry.mood_score for entry in entries) / total_entries
        
        # Тренд настроения (сравнение последних 7 дней с предыдущими 7)
        recent_entries = sorted(entries, key=lambda x: x.entry_date, reverse=True)[:7]
        previous_entries = sorted(entries, key=lambda x: x.entry_date, reverse=True)[7:14]
        
        mood_trend = "stable"
        if recent_entries and previous_entries:
            recent_avg = sum(e.mood_score for e in recent_entries) / len(recent_entries)
            previous_avg = sum(e.mood_score for e in previous_entries) / len(previous_entries)
            
            if recent_avg > previous_avg + 0.5:
                mood_trend = "improving"
            elif recent_avg < previous_avg - 0.5:
                mood_trend = "declining"
        
        # Подсчет streak (последовательных дней с записями)
        streak_days = self._calculate_streak(entries)
        
        return {
            "total_entries": total_entries,
            "average_mood": round(average_mood, 2),
            "mood_trend": mood_trend,
            "streak_days": streak_days,
            "last_entry_date": recent_entries[0].entry_date if recent_entries else None
        }
    
    def get_mood_analytics(
        self, 
        db: Session, 
        user_id: int, 
        period: str = "month"
    ) -> Dict[str, Any]:
        """Получить аналитику настроения за период"""
        # Определяем период
        end_date = datetime.utcnow()
        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        elif period == "year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)  # по умолчанию месяц
        
        entries = self.get_user_entries(db, user_id, start_date=start_date, end_date=end_date)
        
        if not entries:
            return {
                "period": period,
                "average_mood": 0,
                "mood_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "daily_averages": []
            }
        
        # Средняя оценка
        average_mood = sum(entry.mood_score for entry in entries) / len(entries)
        
        # Распределение настроения
        mood_distribution = {"positive": 0, "neutral": 0, "negative": 0}
        for entry in entries:
            if entry.mood_score >= 7:
                mood_distribution["positive"] += 1
            elif entry.mood_score >= 4:
                mood_distribution["neutral"] += 1
            else:
                mood_distribution["negative"] += 1
        
        # Ежедневные средние
        daily_averages = []
        entries_by_date = {}
        for entry in entries:
            date_key = entry.entry_date.date()
            if date_key not in entries_by_date:
                entries_by_date[date_key] = []
            entries_by_date[date_key].append(entry.mood_score)
        
        for date_key, scores in sorted(entries_by_date.items()):
            daily_averages.append({
                "date": date_key.isoformat(),
                "average_mood": round(sum(scores) / len(scores), 2),
                "entries_count": len(scores)
            })
        
        return {
            "period": period,
            "average_mood": round(average_mood, 2),
            "mood_distribution": mood_distribution,
            "daily_averages": daily_averages,
            "total_entries": len(entries)
        }
    
    def _calculate_streak(self, entries: List[MoodEntry]) -> int:
        """Подсчитать streak - количество последовательных дней с записями"""
        if not entries:
            return 0
        
        # Сортируем по дате (убывающая)
        sorted_entries = sorted(entries, key=lambda x: x.entry_date.date(), reverse=True)
        
        # Группируем по датам
        dates = []
        for entry in sorted_entries:
            entry_date = entry.entry_date.date()
            if not dates or dates[-1] != entry_date:
                dates.append(entry_date)
        
        # Подсчитываем streak
        streak = 0
        today = date.today()
        
        for i, entry_date in enumerate(dates):
            expected_date = today - timedelta(days=i)
            if entry_date == expected_date:
                streak += 1
            else:
                break
        
        return streak
    
    def count_by_user(self, db: Session, user_id: int) -> int:
        """Подсчет записей пользователя"""
        return db.query(MoodEntry).filter(MoodEntry.user_id == user_id).count()


# Создаем экземпляр для использования в приложении
mood_entry_crud = MoodEntryCRUD()