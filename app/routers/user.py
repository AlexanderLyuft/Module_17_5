from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db  # Функция подключения к БД
from typing import Annotated
from app.models import User, Task  # Импорт моделей User и Task
from app.schemas import CreateUser, UpdateUser  # Импорт Pydantic моделей
from sqlalchemy import insert, select, update, delete  # Импорт функций работы с БД
from slugify import slugify  # Импорт функции создания slug

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.execute(select(User)).scalars().all()  # Получение всех пользователей
    return users

@router.get("/{user_id}")
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()  # Поиск пользователя по ID
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")
    return user

@router.get("/{user_id}/tasks")
async def tasks_by_user_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    tasks = db.execute(select(Task).where(Task.user_id == user_id)).scalars().all()  # Получение всех задач по user_id
    if tasks is None:
        raise HTTPException(status_code=404, detail="Tasks were not found for this user")
    return tasks

@router.post("/create")
async def create_user(create_user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    slug = slugify(create_user.username)  # Генерация slug
    new_user = User(**create_user.dict(), slug=slug)  # Создание новой записи пользователя
    db.execute(insert(User).values(new_user))  # Вставка в базу данных
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}

@router.put("/update/{user_id}")
async def update_user(user_id: int, update_user: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()  # Поиск пользователя по ID
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    db.execute(update(User).where(User.id == user_id).values(**update_user.dict()))  # Обновление пользователя
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}

@router.delete("/delete/{user_id}")
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()  # Поиск пользователя по ID
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    # Удаление всех задач, связанных с пользователем
    db.execute(delete(Task).where(Task.user_id == user_id))
    db.commit()  # Сначала удаляем задачи

    db.execute(delete(User).where(User.id == user_id))  # Удаление пользователя
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'User deletion is successful!'}




