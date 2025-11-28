"""
Роуты достижений
API для работы с достижениями пользователей
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user, rate_limit_dependency
from app.models.achievement import Achievement
from app.models.user import User
from app.schemas.achievement import AchievementCreate, AchievementRead, AchievementUpdate

router = APIRouter()


@router.get("/my", response_model=List[AchievementRead])
async def get_my_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Получить список достижений текущего пользователя"""
    achievements = db.query(Achievement).filter(Achievement.user_id == current_user.id).all()
    return achievements


@router.get("/", response_model=List[AchievementRead])
async def get_achievements(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить список всех достижений"""
    # Проверка на корректность параметров пагинации
    if skip < 0:
        skip = 0
    if limit <= 0 or limit > 100:
        limit = 100

    achievements = db.query(Achievement).offset(skip).limit(limit).all()
    return achievements


@router.get("/{achievement_id}", response_model=AchievementRead)
async def get_achievement(
    achievement_id: int, 
    db: Session = Depends(get_db), 
    rate_limit: bool = Depends(rate_limit_dependency)
):
    """Получить информацию о достижении по ID"""
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if not achievement:
        raise HTTPException(status_code=404, detail="Достижение не найдено")
    return achievement


@router.post("/", response_model=AchievementRead, status_code=status.HTTP_201_CREATED)
async def create_achievement(
    achievement: AchievementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Создать достижение для текущего пользователя"""
    db_achievement = Achievement(
        user_id=current_user.id,
        title=achievement.title,
        description=achievement.description,
        icon=achievement.icon,
    )
    db.add(db_achievement)
    db.commit()
    db.refresh(db_achievement)
    return db_achievement


@router.put("/{achievement_id}", response_model=AchievementRead)
async def update_achievement(
    achievement_id: int,
    achievement: AchievementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Обновить достижение"""
    db_achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if not db_achievement:
        raise HTTPException(status_code=404, detail="Достижение не найдено")
    
    # Проверяем, что пользователь является владельцем достижения
    if db_achievement.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому достижению")

    # Обновляем поля
    for key, value in achievement.model_dump(exclude_unset=True).items():
        setattr(db_achievement, key, value)

    db.commit()
    db.refresh(db_achievement)
    return db_achievement


@router.delete("/{achievement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_achievement(
    achievement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(rate_limit_dependency),
):
    """Удалить достижение"""
    db_achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if not db_achievement:
        raise HTTPException(status_code=404, detail="Достижение не найдено")
    
    # Проверяем, что пользователь является владельцем достижения
    if db_achievement.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому достижению")

    db.delete(db_achievement)
    db.commit()
    return None