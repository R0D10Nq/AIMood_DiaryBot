"""
API endpoints для аналитики и AI анализа
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta

from ..core.database import get_db
from ..crud.user import user_crud
from ..crud.mood_entry import mood_entry_crud
from ..services.gemini_service import gemini_service
from ..services.mood_analyzer import mood_analyzer
from ..models.ai_analysis import AIAnalysis

router = APIRouter()


@router.get("/dashboard/{user_id}")
async def get_dashboard_data(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить данные для dashboard пользователя
    
    - **user_id**: ID пользователя
    """
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Собираем все данные для dashboard
    dashboard_data = {
        "user": user.to_dict(),
        "summary": mood_analyzer.get_mood_summary(db, user_id, 7),
        "recent_entries": [
            entry.to_dict() for entry in mood_entry_crud.get_recent_entries(db, user_id, 5)
        ],
        "monthly_analytics": mood_entry_crud.get_mood_analytics(db, user_id, "month"),
        "recommendations": mood_analyzer.get_recommendations_for_user(db, user_id),
        "stats": mood_entry_crud.get_user_stats(db, user_id)
    }
    
    return dashboard_data


@router.get("/trends/{user_id}")
async def get_mood_trends(
    user_id: int,
    period: str = Query("month", regex="^(week|month|quarter|year)$"),
    db: Session = Depends(get_db)
):
    """
    Получить тренды настроения пользователя
    
    - **user_id**: ID пользователя
    - **period**: период анализа
    """
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Определяем временной период
    end_date = datetime.utcnow()
    if period == "week":
        start_date = end_date - timedelta(days=7)
        group_by = "day"
    elif period == "month":
        start_date = end_date - timedelta(days=30)
        group_by = "day"
    elif period == "quarter":
        start_date = end_date - timedelta(days=90)
        group_by = "week"
    else:  # year
        start_date = end_date - timedelta(days=365)
        group_by = "month"
    
    # Получаем записи за период
    entries = mood_entry_crud.get_user_entries(
        db, user_id, start_date=start_date, end_date=end_date
    )
    
    # Группируем данные
    trends_data = {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "mood_trend": [],
        "emotion_trends": {},
        "average_mood": 0
    }
    
    if not entries:
        return trends_data
    
    # Вычисляем средние значения по периодам
    period_data = {}
    
    for entry in entries:
        if group_by == "day":
            key = entry.entry_date.date()
        elif group_by == "week":
            key = entry.entry_date.date() - timedelta(days=entry.entry_date.weekday())
        else:  # month
            key = entry.entry_date.date().replace(day=1)
        
        if key not in period_data:
            period_data[key] = {
                "mood_scores": [],
                "emotions": {}
            }
        
        period_data[key]["mood_scores"].append(entry.mood_score)
        
        # Добавляем эмоции из AI анализа
        if entry.ai_analysis and entry.ai_analysis.emotions:
            for emotion, value in entry.ai_analysis.emotions.items():
                if emotion not in period_data[key]["emotions"]:
                    period_data[key]["emotions"][emotion] = []
                period_data[key]["emotions"][emotion].append(value)
    
    # Формируем результат
    for period_key, data in sorted(period_data.items()):
        avg_mood = sum(data["mood_scores"]) / len(data["mood_scores"])
        
        trends_data["mood_trend"].append({
            "date": period_key.isoformat(),
            "average_mood": round(avg_mood, 2),
            "entries_count": len(data["mood_scores"])
        })
        
        # Средние эмоции
        for emotion, values in data["emotions"].items():
            if emotion not in trends_data["emotion_trends"]:
                trends_data["emotion_trends"][emotion] = []
            
            avg_emotion = sum(values) / len(values)
            trends_data["emotion_trends"][emotion].append({
                "date": period_key.isoformat(),
                "value": round(avg_emotion, 2)
            })
    
    # Общая средняя оценка
    all_scores = [entry.mood_score for entry in entries]
    trends_data["average_mood"] = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0
    
    return trends_data


@router.get("/insights/{user_id}")
async def generate_insights(
    user_id: int,
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """
    Генерировать инсайты с помощью AI
    
    - **user_id**: ID пользователя
    - **days**: период для анализа в днях
    """
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Получаем записи за период
    entries = mood_entry_crud.get_recent_entries(db, user_id, days)
    
    if not entries:
        return {
            "message": "Недостаточно данных для генерации инсайтов",
            "recommendations": [
                "Начните вести дневник настроения регулярно",
                "Записывайте подробности о своем дне и эмоциях"
            ]
        }
    
    # Подготавливаем данные для AI
    entries_data = []
    for entry in entries[-10:]:  # Последние 10 записей
        entries_data.append({
            "date": entry.entry_date.strftime("%Y-%m-%d"),
            "mood_score": entry.mood_score,
            "mood_text": entry.mood_text[:200],  # Ограничиваем длину
            "emotions": entry.ai_analysis.emotions if entry.ai_analysis else {}
        })
    
    try:
        # Генерируем инсайты с помощью AI
        insights_text = await gemini_service.generate_daily_insights(entries_data)
        
        return {
            "period_days": days,
            "entries_analyzed": len(entries_data),
            "ai_insights": insights_text,
            "summary": mood_analyzer.get_mood_summary(db, user_id, days)
        }
        
    except Exception as e:
        return {
            "period_days": days,
            "entries_analyzed": len(entries_data),
            "ai_insights": "Анализ инсайтов временно недоступен",
            "summary": mood_analyzer.get_mood_summary(db, user_id, days),
            "error": str(e)
        }


@router.get("/compare-periods/{user_id}")
async def compare_periods(
    user_id: int,
    current_days: int = Query(30, ge=7, le=365),
    previous_days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """
    Сравнить настроение между двумя периодами
    
    - **user_id**: ID пользователя
    - **current_days**: количество дней для текущего периода
    - **previous_days**: количество дней для предыдущего периода
    """
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    end_date = datetime.utcnow()
    
    # Текущий период
    current_start = end_date - timedelta(days=current_days)
    current_entries = mood_entry_crud.get_user_entries(
        db, user_id, start_date=current_start, end_date=end_date
    )
    
    # Предыдущий период
    previous_start = current_start - timedelta(days=previous_days)
    previous_end = current_start
    previous_entries = mood_entry_crud.get_user_entries(
        db, user_id, start_date=previous_start, end_date=previous_end
    )
    
    def calculate_period_stats(entries):
        if not entries:
            return {
                "entries_count": 0,
                "average_mood": 0,
                "mood_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "dominant_emotions": {}
            }
        
        # Базовая статистика
        scores = [entry.mood_score for entry in entries]
        avg_mood = sum(scores) / len(scores)
        
        # Распределение настроения
        distribution = {"positive": 0, "neutral": 0, "negative": 0}
        for score in scores:
            if score >= 7:
                distribution["positive"] += 1
            elif score >= 4:
                distribution["neutral"] += 1
            else:
                distribution["negative"] += 1
        
        # Доминирующие эмоции
        emotion_sums = {}
        emotion_counts = {}
        
        for entry in entries:
            if entry.ai_analysis and entry.ai_analysis.emotions:
                for emotion, value in entry.ai_analysis.emotions.items():
                    if emotion not in emotion_sums:
                        emotion_sums[emotion] = 0
                        emotion_counts[emotion] = 0
                    emotion_sums[emotion] += value
                    emotion_counts[emotion] += 1
        
        dominant_emotions = {}
        for emotion, total in emotion_sums.items():
            dominant_emotions[emotion] = round(total / emotion_counts[emotion], 2)
        
        return {
            "entries_count": len(entries),
            "average_mood": round(avg_mood, 2),
            "mood_distribution": distribution,
            "dominant_emotions": dominant_emotions
        }
    
    current_stats = calculate_period_stats(current_entries)
    previous_stats = calculate_period_stats(previous_entries)
    
    # Вычисляем изменения
    mood_change = current_stats["average_mood"] - previous_stats["average_mood"]
    
    comparison = {
        "current_period": {
            "days": current_days,
            "start_date": current_start.date().isoformat(),
            "end_date": end_date.date().isoformat(),
            "stats": current_stats
        },
        "previous_period": {
            "days": previous_days,
            "start_date": previous_start.date().isoformat(),
            "end_date": previous_end.date().isoformat(),
            "stats": previous_stats
        },
        "comparison": {
            "mood_change": round(mood_change, 2),
            "mood_trend": "improving" if mood_change > 0.5 else "declining" if mood_change < -0.5 else "stable",
            "entries_change": current_stats["entries_count"] - previous_stats["entries_count"]
        }
    }
    
    return comparison


@router.get("/global-stats")
async def get_global_statistics(
    db: Session = Depends(get_db)
):
    """
    Получить общую статистику по всем пользователям
    """
    # Базовая статистика пользователей
    total_users = user_crud.count(db)
    active_users = user_crud.count_active(db)
    
    # Получаем всех пользователей и их статистику
    users = user_crud.get_all(db, limit=1000)
    
    total_entries = 0
    mood_scores = []
    
    for user in users:
        user_entries = mood_entry_crud.get_user_entries(db, user.id, limit=1000)
        total_entries += len(user_entries)
        mood_scores.extend([entry.mood_score for entry in user_entries])
    
    global_stats = {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users
        },
        "entries": {
            "total": total_entries,
            "average_per_user": round(total_entries / total_users, 1) if total_users > 0 else 0
        },
        "mood": {
            "global_average": round(sum(mood_scores) / len(mood_scores), 2) if mood_scores else 0,
            "total_mood_points": len(mood_scores)
        }
    }
    
    return global_stats