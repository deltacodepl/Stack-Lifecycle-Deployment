import datetime

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import src.stacks.domain.entities.stacks as schemas
import src.stacks.infrastructure.models as models


def create_new_stack(
    db: Session,
    stack: schemas.StackCreate,
    user_id: int,
    task_id: str,
    var_json: str,
    var_list: str,
    squad_access: str,
):
    db_stack = models.Stack(
        stack_name=stack.stack_name,
        git_repo=stack.git_repo,
        tf_version=stack.tf_version,
        project_path=stack.project_path,
        description=stack.description,
        branch=stack.branch,
        user_id=user_id,
        created_at=datetime.datetime.now(),
        var_json=var_json,
        var_list=var_list,
        squad_access=squad_access,
        task_id=task_id,
    )
    try:
        db.add(db_stack)
        db.commit()
        db.refresh(db_stack)
        return db_stack
    except IntegrityError:
        raise HTTPException(status_code=409, detail="The stack name already exist")
    except Exception as err:
        raise err


def update_stack(
    db: Session,
    stack: schemas.StackCreate,
    stack_id: int,
    user_id: int,
    task_id: str,
    var_json: str,
    var_list: str,
    squad_access: str,
):
    db_stack = db.query(models.Stack).filter(models.Stack.id == stack_id).first()

    db_stack.user_id = user_id
    db_stack.task_id = task_id
    db_stack.var_json = var_json
    db_stack.var_list = var_list
    db_stack.updated_at = datetime.datetime.now()
    check_None = ["string", ""]
    if db_stack.stack_name not in check_None:
        db_stack.stack_name = stack.stack_name
    if db_stack.git_repo not in check_None:
        db_stack.git_repo = stack.git_repo
    if db_stack.branch not in check_None:
        db_stack.branch = stack.branch
    if db_stack.tf_version not in check_None:
        db_stack.tf_version = stack.tf_version
    if db_stack.project_path not in check_None:
        db_stack.project_path = stack.project_path
    if db_stack.description not in check_None:
        db_stack.description = stack.description
    if db_stack.squad_access not in check_None:
        db_stack.squad_access = squad_access
    try:
        db.add(db_stack)
        db.commit()
        db.refresh(db_stack)
        return db_stack
    except Exception as err:
        raise err


def get_all_stacks_by_squad(
    db: Session, squad_access: str, skip: int = 0, limit: int = 100
):
    try:
        filter_all = (
            db.query(models.Stack)
            .filter(models.Stack.squad_access.contains("*"))
            .offset(skip)
            .limit(limit)
            .all()
        )
        from sqlalchemy import func

        result = []
        for i in squad_access:
            a = f'["{i}"]'
            result.extend(
                db.query(models.Stack)
                .filter(func.json_contains(models.Stack.squad_access, a) == 1)
                .all()
            )
        merge_query = result + filter_all
        return set(merge_query)
    except Exception as err:
        raise err


def get_all_stacks(db: Session, squad_access: str, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.Stack).offset(skip).limit(limit).all()
    except Exception as err:
        raise err


def get_stack_by_id(db: Session, stack_id: int):
    try:
        return db.query(models.Stack).filter(models.Stack.id == stack_id).first()
    except Exception as err:
        raise err


def delete_stack_by_id(db: Session, stack_id: int):
    try:
        db.query(models.Stack).filter(models.Stack.id == stack_id).delete()
        db.commit()
        return {"result": "deleted", "stack_id": stack_id}
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="The stack cannot be removed, check that it is not used by any deploy",
        )
    except Exception as err:
        raise err


def get_stack_by_name(db: Session, stack_name: str):
    try:
        return (
            db.query(models.Stack).filter(models.Stack.stack_name == stack_name).first()
        )
    except Exception as err:
        raise err


def delete_stack_by_name(db: Session, stack_name: str):
    try:
        db.query(models.Stack).filter(models.Stack.stack_name == stack_name).delete()
        db.commit()
        return {"result": "deleted", "stack_name": stack_name}
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="The stack cannot be removed, check that it is not used by any deploy",
        )
    except Exception as err:
        raise err
