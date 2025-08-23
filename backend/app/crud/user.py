"""
CRUD операции для работы с пользователями
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime

from ..models.user import User
from ..schemas import UserCreate, UserUpdate


class UserCRUD:
    """CRUD операции для модели User"""
    
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_by_telegram_id(self, db: Session, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        return db.query(User).filter(User.telegram_id == telegram_id).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Получить пользователя по username"""
        return db.query(User).filter(User.username == username).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить список всех пользователей"""
        return db.query(User).offset(skip).limit(limit).all()
    
    def get_active_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить активных пользователей"""
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    def create(self, db: Session, user_in: UserCreate) -> User:
        """Создать нового пользователя"""
        user_data = user_in.model_dump()
        user_data["created_at"] = datetime.utcnow()
        user_data["last_activity"] = datetime.utcnow()
        
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def get_or_create(self, db: Session, telegram_id: int, user_data: dict) -> tuple[User, bool]:
        """
        Получить пользователя или создать если не существует
        Возвращает (user, created) где created = True если пользователь был создан
        """
        user = self.get_by_telegram_id(db, telegram_id)
        if user:
            # Обновляем последнюю активность
            user.last_activity = datetime.utcnow()
            db.commit()
            return user, False
        
        # Создаем нового пользователя
        user_create = UserCreate(telegram_id=telegram_id, **user_data)
        new_user = self.create(db, user_create)
        return new_user, True
    
    def update(self, db: Session, user_id: int, user_in: UserUpdate) -> Optional[User]:
        """Обновить данные пользователя"""
        user = self.get_by_id(db, user_id)
        if not user:
            return None
        
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.last_activity = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    
    def update_by_telegram_id(self, db: Session, telegram_id: int, user_in: UserUpdate) -> Optional[User]:
        """Обновить данные пользователя по Telegram ID"""
        user = self.get_by_telegram_id(db, telegram_id)
        if not user:
            return None
        
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.last_activity = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    
    def increment_mood_entries(self, db: Session, user_id: int) -> Optional[User]:
        """Увеличить счетчик записей настроения"""
        user = self.get_by_id(db, user_id)
        if not user:
            return None
        
        user.mood_entries_count += 1
        user.last_activity = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    
    def deactivate(self, db: Session, user_id: int) -> Optional[User]:
        """Деактивировать пользователя"""
        user = self.get_by_id(db, user_id)
        if not user:
            return None
        
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user
    
    def activate(self, db: Session, user_id: int) -> Optional[User]:
        """Активировать пользователя"""
        user = self.get_by_id(db, user_id)
        if not user:
            return None
        
        user.is_active = True
        user.last_activity = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    
    def delete(self, db: Session, user_id: int) -> bool:
        """Удалить пользователя"""
        user = self.get_by_id(db, user_id)
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True
    
    def count(self, db: Session) -> int:
        """Подсчет общего количества пользователей"""
        return db.query(User).count()
    
    def count_active(self, db: Session) -> int:
        """Подсчет активных пользователей"""
        return db.query(User).filter(User.is_active == True).count()


# Создаем экземпляр для использования в приложении
user_crud = UserCRUD()