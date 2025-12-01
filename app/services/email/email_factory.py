"""
邮件服务工厂 - 根据配置选择邮件服务提供商
"""
from typing import Union
from app.core.config import settings
from app.services.email.resend_service import ResendEmailService
from app.services.email.smtp_service import SMTPEmailService


def get_email_service() -> Union[ResendEmailService, SMTPEmailService]:
    """
    根据 EMAIL_PROVIDER 配置返回对应的邮件服务实例
    
    Returns:
        ResendEmailService 或 SMTPEmailService
    """
    provider = (settings.EMAIL_PROVIDER or "smtp").lower().strip()
    
    if provider == "resend":
        print(f"📧 使用 Resend 邮件服务")
        return ResendEmailService()
    elif provider == "smtp":
        print(f"📧 使用 Gmail SMTP 邮件服务")
        return SMTPEmailService()
    else:
        print(f"⚠️  未知的邮件提供商: {provider}，默认使用 SMTP")
        return SMTPEmailService()

