"""
Gmail SMTP 邮件服务
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings


class SMTPEmailService:
    """Gmail SMTP 邮件服务类"""
    
    def __init__(self):
        # 从统一配置对象读取
        self.host = settings.SMTP_HOST or "smtp.gmail.com"
        self.port = settings.SMTP_PORT or 587
        self.username = settings.SMTP_USER or ""
        self.password = settings.SMTP_PASSWORD or ""
        self.use_tls = settings.SMTP_USE_TLS
        self.from_email = settings.FROM_EMAIL.strip()
        self.from_name = settings.FROM_NAME.strip()
        
        print(f"🔧 Gmail SMTP 邮件服务初始化:")
        print(f"   - Host: {self.host}")
        print(f"   - Port: {self.port}")
        print(f"   - Username: {self.username}")
        print(f"   - Password: {'已配置' if self.password else '❌ 未配置'}")
        print(f"   - Use TLS: {self.use_tls}")
        print(f"   - From Email: {self.from_email}")
        print(f"   - From Name: {self.from_name}")
        
        if not self.username:
            print("⚠️  警告: SMTP_USER 未设置，邮件功能将无法使用")
        if not self.password:
            print("⚠️  警告: SMTP_PASSWORD 未设置，邮件功能将无法使用")
    
    async def send_verification_code(self, to_email: str, code: str) -> bool:
        """
        发送验证码邮件
        
        Args:
            to_email: 收件人邮箱
            code: 6位验证码
            
        Returns:
            bool: 是否发送成功
        """
        try:
            # HTML 邮件内容（与 Resend 服务保持一致）
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background-color: #0f172a;
                        color: #e2e8f0;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                        border: 1px solid #334155;
                        border-radius: 8px;
                        padding: 40px;
                    }}
                    .logo {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .logo-box {{
                        display: inline-block;
                        width: 60px;
                        height: 60px;
                        background: linear-gradient(135deg, #00D9FF 0%, #0099cc 100%);
                        border-radius: 8px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 32px;
                        font-weight: bold;
                        color: #0f172a;
                    }}
                    .title {{
                        font-size: 24px;
                        font-weight: bold;
                        margin-bottom: 10px;
                        text-align: center;
                    }}
                    .subtitle {{
                        color: #94a3b8;
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .code-box {{
                        background: #1e293b;
                        border: 2px solid #00D9FF;
                        border-radius: 8px;
                        padding: 30px;
                        text-align: center;
                        margin: 30px 0;
                    }}
                    .code {{
                        font-size: 48px;
                        font-weight: bold;
                        letter-spacing: 10px;
                        color: #00D9FF;
                        font-family: 'Courier New', monospace;
                    }}
                    .note {{
                        color: #94a3b8;
                        font-size: 14px;
                        text-align: center;
                        margin-top: 20px;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 40px;
                        padding-top: 20px;
                        border-top: 1px solid #334155;
                        color: #64748b;
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="logo">
                        <div class="logo-box">F</div>
                        <h1 style="margin: 10px 0; font-size: 28px;">Formy｜形我</h1>
                    </div>
                    
                    <div class="title">验证码登录</div>
                    <div class="subtitle">您的登录验证码如下</div>
                    
                    <div class="code-box">
                        <div class="code">{code}</div>
                    </div>
                    
                    <div class="note">
                        ⏱️ 此验证码 <strong>10 分钟</strong> 内有效<br>
                        🔒 请勿将验证码告知他人<br>
                        ⚠️ 如非本人操作，请忽略此邮件
                    </div>
                    
                    <div class="footer">
                        © 2025 Formy｜形我. All rights reserved.<br>
                        AI 视觉创作工具 - 专为服装行业打造
                    </div>
                </div>
            </body>
            </html>
            """
            
            # 纯文本版本（备用）
            text_content = f"""
Formy｜形我 - 验证码登录

您的登录验证码是: {code}

⏱️ 此验证码 10 分钟内有效
🔒 请勿将验证码告知他人
⚠️ 如非本人操作，请忽略此邮件

© 2025 Formy｜形我. All rights reserved.
            """.strip()
            
            # 创建邮件消息
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = f"【Formy】您的验证码是 {code}"
            
            # 添加文本和 HTML 内容
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(text_part)
            msg.attach(html_part)
            
            print(f"📤 准备通过 Gmail SMTP 发送邮件:")
            print(f"   - Host: {self.host}")
            print(f"   - Port: {self.port}")
            print(f"   - From: {self.from_email}")
            print(f"   - To: {to_email}")
            print(f"   - Subject: {msg['Subject']}")
            
            # 连接 SMTP 服务器并发送
            try:
                # 使用同步 SMTP（因为 smtplib 是同步的）
                # 在实际应用中，可以使用 asyncio.to_thread 或线程池来避免阻塞
                import asyncio
                
                def send_sync():
                    """同步发送邮件（在线程中执行）"""
                    server = None
                    try:
                        # 创建 SMTP 连接
                        server = smtplib.SMTP(self.host, self.port)
                        server.set_debuglevel(0)  # 0 = 不显示调试信息，1 = 显示
                        
                        # 启用 TLS
                        if self.use_tls:
                            server.starttls()
                            print(f"   ✅ TLS 已启用")
                        
                        # 登录
                        print(f"   🔐 正在登录 SMTP 服务器...")
                        server.login(self.username, self.password)
                        print(f"   ✅ 登录成功")
                        
                        # 发送邮件
                        print(f"   📧 正在发送邮件...")
                        server.send_message(msg)
                        print(f"   ✅ 邮件发送成功")
                        
                        return True
                    except smtplib.SMTPAuthenticationError as e:
                        print(f"   ❌ SMTP 认证失败: {e}")
                        print(f"   ⚠️  请检查用户名和密码是否正确")
                        return False
                    except smtplib.SMTPException as e:
                        print(f"   ❌ SMTP 错误: {e}")
                        return False
                    except Exception as e:
                        print(f"   ❌ 发送邮件异常: {type(e).__name__}: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        return False
                    finally:
                        if server:
                            try:
                                server.quit()
                            except:
                                pass
                
                # 在线程池中执行同步操作
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, send_sync)
                
                if result:
                    print(f"✅ 验证码邮件已发送到: {to_email}")
                else:
                    print(f"❌ 邮件发送失败，请查看上方详细错误信息")
                
                return result
                
            except Exception as e:
                print(f"❌ 发送邮件异常: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
                
        except Exception as e:
            print(f"❌ 构建邮件异常: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


# 全局邮件服务实例
_email_service: Optional[SMTPEmailService] = None


def get_email_service() -> SMTPEmailService:
    """获取邮件服务实例（单例）"""
    global _email_service
    if _email_service is None:
        _email_service = SMTPEmailService()
    return _email_service

