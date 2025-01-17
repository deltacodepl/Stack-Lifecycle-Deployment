from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.activityLogs.infrastructure import repositories as crud_activity
from src.aws.domain.entities import aws as schemas_aws
from src.aws.infrastructure import repositories as crud_aws
from src.shared.security import deps
from src.users.domain.entities import users as schemas_users
from src.users.infrastructure import repositories as crud_users


async def create_new_aws_profile(
    aws: schemas_aws.AwsAsumeProfile,
    current_user: schemas_users.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    # Check if the user has privileges
    if not crud_users.is_master(db, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if "string" in [aws.squad, aws.environment]:
        raise HTTPException(
            status_code=409,
            detail="The squad or environment field must have a value that is not a string.",
        )
    db_aws_account = crud_aws.get_squad_aws_profile(
        db=db, squad=aws.squad, environment=aws.environment
    )
    if db_aws_account:
        raise HTTPException(status_code=409, detail="Account already exists")
    try:
        result = crud_aws.create_aws_profile(db=db, aws=aws)
        crud_activity.create_activity_log(
            db=db,
            username=current_user.username,
            squad=current_user.squad,
            action=f"Create AWS account {aws.squad} {aws.environment}",
        )
        return {"result": f"Create AWS account {aws.squad} {aws.environment}"}
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))
