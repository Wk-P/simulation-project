from fastapi import APIRouter, Depends
from src.repositories.user.user import UserRepository
from src.routers.deps import get_user_repo
from src.schemas.user.register import RegisterNormalUserResponse, RegisterNormalUserRequest, RegisterStaffUserRequest, RegisterStaffUserResponse, RegisterAdminUserRequest, RegisterAdminUserResponse
from src.services.user.register import register_user, register_staff, register_admin

router = APIRouter(prefix="/register")


@router.post('/user')
def post_register_user(request: RegisterNormalUserRequest, user_repo: UserRepository = Depends(get_user_repo)) -> RegisterNormalUserResponse:
    response = register_user(request, user_repo)
    return response


@router.post('/staff')
def post_register_staff(request: RegisterStaffUserRequest, user_repo: UserRepository = Depends(get_user_repo)) -> RegisterStaffUserResponse:
    response = register_staff(request, user_repo)
    return response


@router.post('/admin')
def post_register_admin(request: RegisterAdminUserRequest, user_repo: UserRepository = Depends(get_user_repo)) -> RegisterAdminUserResponse:
    response = register_admin(request, user_repo)
    return response
