"""
认证相关路由
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional

from app.schemas.auth import (
    SendCodeRequest,
    SendCodeResponse,
    LoginRequest,
    LoginResponse,
    UserInfo,
    CurrentUserResponse
)
from app.services.auth.auth_service import get_auth_service
from app.services.email.resend_service import get_email_service


router = APIRouter()


@router.post("/auth/send-code", response_model=SendCodeResponse)
async def send_verification_code(request: SendCodeRequest):
    """
    API 1: 发送验证码
    
    发送 6 位数字验证码到指定邮箱
    验证码有效期 10 分钟
    """
    try:
        auth_service = get_auth_service()
        email_service = get_email_service()
        
        # 生成验证码
        code = auth_service.generate_code()
        
        # 保存验证码到 Redis
        if not auth_service.save_verification_code(request.email, code):
            raise HTTPException(
                status_code=500,
                detail="保存验证码失败，请稍后重试"
            )
        
        # 发送邮件
        if not await email_service.send_verification_code(request.email, code):
            raise HTTPException(
                status_code=500,
                detail="发送邮件失败，请检查邮箱地址或稍后重试"
            )
        
        return SendCodeResponse(
            success=True,
            message=f"验证码已发送到 {request.email}",
            expires_in=600  # 10 分钟
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"发送验证码失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"发送验证码失败: {str(e)}"
        )


@router.post("/auth/login", response_model=LoginResponse)
async def login_with_code(request: LoginRequest):
    """
    API 2: 验证码登录
    
    使用邮箱和验证码登录
    登录成功返回 JWT 令牌
    """
    try:
        auth_service = get_auth_service()
        
        # 验证验证码
        if not auth_service.verify_code(request.email, request.code):
            raise HTTPException(
                status_code=400,
                detail="验证码错误或已过期"
            )
        
        # 获取或创建用户
        user = auth_service.get_or_create_user(request.email)
        
        # 创建访问令牌
        access_token = auth_service.create_access_token(user)
        
        # 返回用户信息和令牌
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserInfo(
                user_id=user.user_id,
                email=user.email,
                username=user.username,
                avatar=user.avatar,
                created_at=user.created_at.isoformat(),
                last_login=user.last_login.isoformat() if user.last_login else None
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"登录失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"登录失败: {str(e)}"
        )


async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    依赖项：从 Authorization header 获取当前用户
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="未登录"
        )
    
    try:
        # 解析 Bearer token
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="无效的认证方案"
            )
        
        # 解码 JWT
        auth_service = get_auth_service()
        payload = auth_service.decode_access_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=401,
                detail="无效的令牌"
            )
        
        # 获取用户
        user_id = payload.get("sub")
        user = auth_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="用户不存在"
            )
        
        return user
        
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="无效的 Authorization header"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取当前用户失败: {e}")
        raise HTTPException(
            status_code=401,
            detail="认证失败"
        )


@router.get("/auth/me", response_model=CurrentUserResponse)
async def get_current_user_info(current_user=Depends(get_current_user)):
    """
    API 3: 获取当前用户信息
    
    需要在 Header 中提供 Authorization: Bearer <token>
    """
    return CurrentUserResponse(
        user=UserInfo(
            user_id=current_user.user_id,
            email=current_user.email,
            username=current_user.username,
            avatar=current_user.avatar,
            created_at=current_user.created_at.isoformat(),
            last_login=current_user.last_login.isoformat() if current_user.last_login else None
        )
    )

