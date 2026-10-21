from fastapi import APIRouter
from src.services.user.register import NormalUserResponse, NormalUserRequest, StaffUserRequest, StaffUserResponse, AdminUserRequest, AdminUserResponse, user_register_svc, staff_register_svc, admin_register_svc

router = APIRouter()

@router.post('/user/register/')
def user_register(user: NormalUserRequest):
    # 前处理
    resp: NormalUserResponse = user_register_svc(user)
    # 后处理
    return resp
    

@router.post('/staff/register/')
def staff_register(user: StaffUserRequest):
    # 前处理
    resp: StaffUserResponse = staff_register_svc(user)
    # 后处理
    return resp

@router.post('/admin/register/')
def admin_register(user: AdminUserRequest):
    # 前处理
    resp: AdminUserResponse = admin_register_svc(user)
    # 后处理
    return resp

