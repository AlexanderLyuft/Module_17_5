from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db  # Функция подключения к БД
from app.models import Task, User  # Импорт моделей Task и User
from app.schemas import CreateTask  # Импорт Pydantic модели (у вас её должны быть)
from sqlalchemy import insert, select, update, delete  # Импорт функций работы с БД

router = APIRouter(prefix="/task", tags=["task"])

@router.get("/")
async def all_tasks(db: Session = Depends(get_db)):
    tasks = db.execute(select(Task)).scalars().all()  # Получение всех задач
    return tasks

@router.get("/{task_id}")
async def task_by_id(task_id: int, db: Session = Depends(get_db)):
    task = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()  # Поиск задачи по ID
    if task is None:
        raise HTTPException(status_code=404, detail="Task was not found")
    return task

@router.post("/create")
async def create_task(create_task: CreateTask, user_id: int, db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    # Создаём новую запись задачи
    new_task = Task(**create_task.dict(), user_id=user_id)  # Добавляем user_id к задаче
    db.execute(insert(Task).values(new_task))  # Вставка в базу данных
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}

@router.put("/update/{task_id}")
async def update_task(task_id: int, update_task: CreateTask, db: Session = Depends(get_db)):
    task = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()  # Поиск задачи по ID
    if task is None:
        raise HTTPException(status_code=404, detail="Task was not found")

    db.execute(update(Task).where(Task.id == task_id).values(**update_task.dict()))  # Обновление задачи
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'Task update is successful!'}

@router.delete("/delete/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()  # Поиск задачи по ID
    if task is None:
        raise HTTPException(status_code=404, detail="Task was not found")

    db.execute(delete(Task).where(Task.id == task_id))  # Удаление задачи
    db.commit()
    return {'status_code': status.HTTP_200_OK, 'transaction': 'Task deletion is successful!'}







