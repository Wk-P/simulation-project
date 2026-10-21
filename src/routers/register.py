from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.repositories.user import UserRepository
from src.schemas.user import NormalUserResponse, NormalUserRequest, StaffUserRequest, StaffUserResponse, AdminUserRequest, AdminUserResponse
from src.services.user.register import user_register_svc, staff_register_svc, admin_register_svc

router = APIRouter()


def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


@router.post('/user/register/')
def user_register(user: NormalUserRequest, repo: UserRepository = Depends(get_user_repo)) -> NormalUserResponse:
    return user_register_svc(user, repo)


@router.post('/staff/register/')
def staff_register(user: StaffUserRequest, repo: UserRepository = Depends(get_user_repo)) -> StaffUserResponse:
    return staff_register_svc(user, repo)


@router.post('/admin/register/')
def admin_register(user: AdminUserRequest, repo: UserRepository = Depends(get_user_repo)) -> AdminUserResponse:
    return admin_register_svc(user, repo)
