from io import BytesIO
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import pdfkit
from sqlalchemy import select
from app.models.request_bodies import TaskTitle, TaskPriority
from app.models.task import Task
from app.dependencies.database import get_db
from sqlalchemy.orm import Session
from app.utils.utils import generate_html_table
from app.dependencies.jwt_management import get_current_user_email

router = APIRouter()

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

"""
It is a common practice to use:
@router.route("/", methods=["GET", "POST"])

But I like to keep each method with its function 

"""



@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_tasks(token:str = Depends(oauth_scheme) ,db: Session = Depends(get_db)):
    print(token)
    try:
        user_email = get_current_user_email(token)
    except Exception as e:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    stmt = (
        select(Task)
        .where(Task.owner_email == user_email)
        .order_by(Task.priority.asc(), Task.date_created.asc())
    )

    query = db.execute(stmt).all()
    result = [row[0] for row in query]
    result_list = []
    for row in result:
        task_dict = {
            "id": row.id,
            "title": row.title,
            "owner_email": row.owner_email,
            "priority": row.priority,
            "created": f"{row.date_created}"
        }
        result_list.append(task_dict)

        response = {"data": result_list, "success": True}
        return response


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_new_task(req_body: TaskTitle, token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):
    try:
        user_email = get_current_user_email(token)
    except Exception as e:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    new_task = Task(title=req_body.title, owner_email=user_email)

    db.add(new_task)
    try:
        db.commit()
        db.refresh(new_task)

        if new_task.id is not None:
            response = {"message": "Task created successfully",
                        "data": new_task,
                        "success": True}
            return response
    except Exception as e:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.patch("/{task_id}", status_code=status.HTTP_200_OK)
async def set_priority(task_id: int, req_body: TaskPriority, token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):
    try:
        user_email = get_current_user_email(token)
    except Exception as e:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        with db.begin():
            query = db.query(Task).filter(Task.id == task_id)
            task = query.first()

            if task is None:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
            elif task.owner_email == user_email:

                tasks_to_be_updated = db.query(Task) \
                    .filter(Task.priority.isnot(None), Task.priority >= req_body.priority, task.owner_email == user_email)

                tasks_to_be_updated.update({"priority": Task.priority + 1})

                task.update({"priority": req_body.priority})
                db.commit()
                response = {"message": "Task updated successfully", "success": True}
                return response
            else:
                db.rollback()
                return HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    except Exception as e:
        print(e)
        db.rollback()
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.put("/{task_id}", status_code=status.HTTP_200_OK)
async def update_task(task_id: int, req_body: TaskTitle, token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):

    try:
        user_email = get_current_user_email(token)
    except Exception as e:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        query = db.query(Task).filter(Task.id == task_id)
        task = query.first()
        if task is None:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        elif task.owner_email == user_email:
            query.update({"title": req_body.title})
            db.commit()
            response = {"message": "Task updated successfully", "success": True}
            return response
        else:
            return HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        db.rollback()
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(task_id: int, token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):

    try:
        user_email = get_current_user_email(token)
    except Exception as e:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        query = db.query(Task).filter(Task.id == task_id)
        task = query.first()
        if task is None:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        elif task.owner_email == user_email:
            query.delete()
            db.commit()
            response = {"message": "Task deleted successfully", "success": True}
            return response
        else:
            return HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        db.rollback()
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/print")
async def print_tasks_list(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):

    try:
        user_email = get_current_user_email(token)
    except Exception as e:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    stmt = (
        select(Task)
        .where(Task.owner_email == user_email)
    )

    query = db.execute(stmt).all()
    result = [row[0] for row in query]
    result_list = []
    for i in range(0, len(result)):
        task_dict = {
            "#": i + 1,
            "Title": result[i].title,
            "Done?": " "
        }
        result_list.append(task_dict)

        html_content = generate_html_table(result_list)

        pdf_content = pdfkit.from_string(html_content, False)

        pdf_buffer = BytesIO(pdf_content)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=output.pdf"},
        )
