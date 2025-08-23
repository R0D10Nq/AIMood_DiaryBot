"""
API endpoints для работы с записями настроения
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from ..core.database import get_db
from ..crud.mood_entry import mood_entry_crud
from ..crud.user import user_crud
from ..services.mood_analyzer import mood_analyzer
from ..schemas import MoodEntry, MoodEntryCreate, MoodEntryUpdate, MoodEntryWithAnalysis

router = APIRouter()


@router.get("/", response_model=List[MoodEntryWithAnalysis])
async def get_mood_entries(
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    user_id: Optional[int] = Query(None, description="Фильтр по пользователю"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата (ISO формат)"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата (ISO формат)"),
    db: Session = Depends(get_db)
):
    """
    Получить список записей настроения
    
    - **skip**: количество записей для пропуска (пагинация)
    - **limit**: максимальное количество записей
    - **user_id**: фильтр по конкретному пользователю
    - **start_date**: начальная дата для фильтрации
    - **end_date**: конечная дата для фильтрации
    """
    if user_id:
        # Проверяем существование пользователя
        user = user_crud.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        entries = mood_entry_crud.get_user_entries(
            db, user_id, skip=skip, limit=limit, 
            start_date=start_date, end_date=end_date
        )
    else:
        # Здесь должна быть общая логика для получения всех записей
        # Пока возвращаем пустой список для неавторизованных запросов
        entries = []
    
    return entries


@router.get("/{entry_id}", response_model=MoodEntryWithAnalysis)
async def get_mood_entry(
    entry_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить запись настроения по ID
    
    - **entry_id**: уникальный идентификатор записи
    """
    entry = mood_entry_crud.get_by_id(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Запись настроения не найдена")
    return entry


@router.post("/", response_model=MoodEntryWithAnalysis)
async def create_mood_entry(
    entry_in: MoodEntryCreate,
    user_id: int = Query(..., description="ID пользователя"),
    analyze: bool = Query(True, description="Провести AI анализ"),
    db: Session = Depends(get_db)
):
    """
    Создать новую запись настроения
    
    - **entry_in**: данные для создания записи
    - **user_id**: ID пользователя
    - **analyze**: нужно ли проводить AI анализ
    """
    # Проверяем существование пользователя
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Проверяем, нет ли уже записи на эту дату
    entry_date = entry_in.entry_date.date() if hasattr(entry_in.entry_date, 'date') else entry_in.entry_date
    existing_entry = mood_entry_crud.get_by_user_and_date(db, user_id, entry_date)
    if existing_entry:
        raise HTTPException(
            status_code=400, 
            detail=f"На дату {entry_date} уже есть запись настроения"
        )
    
    # Создаем запись
    mood_entry = mood_entry_crud.create(db, entry_in, user_id)
    
    # Увеличиваем счетчик у пользователя
    user_crud.increment_mood_entries(db, user_id)
    
    # Проводим AI анализ если требуется
    if analyze:
        try:
            await mood_analyzer.analyze_and_save(db, mood_entry)
            # Обновляем запись с анализом
            mood_entry = mood_entry_crud.get_by_id(db, mood_entry.id)
        except Exception as e:
            # Логируем ошибку, но не прерываем создание записи
            pass
    
    return mood_entry


@router.put("/{entry_id}", response_model=MoodEntryWithAnalysis)
async def update_mood_entry(
    entry_id: int,
    entry_in: MoodEntryUpdate,
    reanalyze: bool = Query(False, description="Провести повторный AI анализ"),
    db: Session = Depends(get_db)
):
    """
    Обновить запись настроения
    
    - **entry_id**: ID записи для обновления
    - **entry_in**: новые данные записи
    - **reanalyze**: провести повторный AI анализ
    """
    entry = mood_entry_crud.update(db, entry_id, entry_in)
    if not entry:
        raise HTTPException(status_code=404, detail="Запись настроения не найдена")
    
    # Повторный анализ если требуется
    if reanalyze and (entry_in.mood_text or entry_in.mood_score):
        try:
            # Удаляем старый анализ
            if entry.ai_analysis:
                db.delete(entry.ai_analysis)
                db.commit()
            
            # Создаем новый анализ
            await mood_analyzer.analyze_and_save(db, entry)
            entry = mood_entry_crud.get_by_id(db, entry_id)
        except Exception as e:
            pass
    
    return entry


@router.delete("/{entry_id}")
async def delete_mood_entry(
    entry_id: int,
    db: Session = Depends(get_db)
):
    """
    Удалить запись настроения
    
    - **entry_id**: ID записи для удаления
    """
    success = mood_entry_crud.delete(db, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Запись настроения не найдена")
    return {"message": "Запись настроения успешно удалена"}


@router.get("/user/{user_id}/recent", response_model=List[MoodEntryWithAnalysis])
async def get_user_recent_entries(
    user_id: int,
    days: int = Query(7, ge=1, le=365, description="Количество дней"),
    db: Session = Depends(get_db)
):
    """
    Получить последние записи пользователя
    
    - **user_id**: ID пользователя
    - **days**: количество дней для получения записей
    """
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    entries = mood_entry_crud.get_recent_entries(db, user_id, days)
    return entries


@router.get("/user/{user_id}/stats")
async def get_user_mood_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить статистику настроения пользователя
    
    - **user_id**: ID пользователя
    """
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    stats = mood_entry_crud.get_user_stats(db, user_id)
    return stats


@router.get("/user/{user_id}/analytics")
async def get_user_mood_analytics(
    user_id: int,
    period: str = Query("month", regex="^(week|month|year)$", description="Период анализа"),
    db: Session = Depends(get_db)
):
    """
    Получить аналитику настроения пользователя
    
    - **user_id**: ID пользователя
    - **period**: период для анализа (week, month, year)
    """
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    analytics = mood_entry_crud.get_mood_analytics(db, user_id, period)
    return analytics


@router.get("/user/{user_id}/summary")
async def get_user_mood_summary(
    user_id: int,
    days: int = Query(7, ge=1, le=365, description="Период в днях"),
    db: Session = Depends(get_db)
):
    """
    Получить сводку настроения пользователя
    
    - **user_id**: ID пользователя
    - **days**: период в днях для анализа
    """
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    summary = mood_analyzer.get_mood_summary(db, user_id, days)
    return summary


@router.get("/user/{user_id}/recommendations")
async def get_user_recommendations(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить рекомендации для пользователя
    
    - **user_id**: ID пользователя
    """
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    recommendations = mood_analyzer.get_recommendations_for_user(db, user_id)
    return recommendations


@router.get("/user/{user_id}/check-today")
async def check_today_entry(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Проверить, есть ли запись на сегодня
    
    - **user_id**: ID пользователя
    """
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    today_entry = mood_entry_crud.get_by_user_and_date(db, user_id, date.today())
    
    return {
        "has_entry_today": today_entry is not None,
        "entry": today_entry.to_dict() if today_entry else None
    }