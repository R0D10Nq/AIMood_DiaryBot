"""
API endpoints для работы с пользователями
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..crud.user import user_crud
from ..schemas import User, UserCreate, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[User])
async def get_users(
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    active_only: bool = Query(False, description="Только активные пользователи"),
    db: Session = Depends(get_db)
):
    """
    Получить список пользователей
    
    - **skip**: количество записей для пропуска (пагинация)
    - **limit**: максимальное количество записей
    - **active_only**: фильтр только активных пользователей
    """
    if active_only:
        users = user_crud.get_active_users(db, skip=skip, limit=limit)
    else:
        users = user_crud.get_all(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить пользователя по ID
    
    - **user_id**: уникальный идентификатор пользователя
    """
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.get("/telegram/{telegram_id}", response_model=User)
async def get_user_by_telegram_id(
    telegram_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить пользователя по Telegram ID
    
    - **telegram_id**: ID пользователя в Telegram
    """
    user = user_crud.get_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь с таким Telegram ID не найден")
    return user


@router.post("/", response_model=User)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Создать нового пользователя
    
    - **user_in**: данные для создания пользователя
    """
    # Проверяем, нет ли уже пользователя с таким Telegram ID
    existing_user = user_crud.get_by_telegram_id(db, user_in.telegram_id)
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="Пользователь с таким Telegram ID уже существует"
        )
    
    return user_crud.create(db, user_in)


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить данные пользователя
    
    - **user_id**: ID пользователя для обновления
    - **user_in**: новые данные пользователя
    """
    user = user_crud.update(db, user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Удалить пользователя
    
    - **user_id**: ID пользователя для удаления
    """
    success = user_crud.delete(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"message": "Пользователь успешно удален"}


@router.post("/{user_id}/activate", response_model=User)
async def activate_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Активировать пользователя
    
    - **user_id**: ID пользователя для активации
    """
    user = user_crud.activate(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.post("/{user_id}/deactivate", response_model=User)
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Деактивировать пользователя
    
    - **user_id**: ID пользователя для деактивации
    """
    user = user_crud.deactivate(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.get("/stats/summary")
async def get_users_summary(
    db: Session = Depends(get_db)
):
    """
    Получить общую статистику пользователей
    """
    total_users = user_crud.count(db)
    active_users = user_crud.count_active(db)
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users
    }