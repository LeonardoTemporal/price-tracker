"""
Email service using Resend
Handles sending verification codes and notifications

Author: HellSpawn
"""
import resend
import os
import random
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Configuración de Resend
resend.api_key = os.getenv("RESEND_API_KEY")
# Resend requiere usar onboarding@resend.dev para testing o un dominio verificado
FROM_EMAIL = "onboarding@resend.dev"

# Debug: Verificar configuración
if not resend.api_key:
    print("⚠️  WARNING: RESEND_API_KEY no está configurada")
else:
    print(f"✓ Resend API key configurada (longitud: {len(resend.api_key)})")
    print(f"✓ Email de origen: {FROM_EMAIL}")


def generate_verification_code() -> str:
    """Generar código de verificación de 6 dígitos"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


def send_verification_email(email: str, username: str, code: str) -> bool:
    """
    Enviar email de verificación con código de 6 dígitos
    
    Args:
        email: Email del destinatario
        username: Nombre de usuario
        code: Código de verificación de 6 dígitos
    
    Returns:
        bool: True si se envió exitosamente, False en caso contrario
    """
    if not resend.api_key:
        print("❌ Error: RESEND_API_KEY no configurada")
        return False
    
    try:
        print(f"📧 Intentando enviar email a {email}...")
        params = {
            "from": f"Pricy Price Tracker <{FROM_EMAIL}>",
            "to": [email],
            "subject": "Verifica tu cuenta en Pricy 🎯",
            "html": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .container {{
                        background: #ffffff;
                        border-radius: 10px;
                        padding: 40px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .logo {{
                        font-size: 32px;
                        font-weight: bold;
                        color: #3b82f6;
                        margin-bottom: 10px;
                    }}
                    .code-container {{
                        background: #f3f4f6;
                        border-radius: 8px;
                        padding: 30px;
                        text-align: center;
                        margin: 30px 0;
                    }}
                    .code {{
                        font-size: 42px;
                        font-weight: bold;
                        letter-spacing: 8px;
                        color: #3b82f6;
                        font-family: 'Courier New', monospace;
                    }}
                    .info {{
                        color: #6b7280;
                        font-size: 14px;
                        margin-top: 20px;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #e5e7eb;
                        color: #9ca3af;
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🎯 Pricy</div>
                        <h1 style="margin: 0; color: #1f2937; font-size: 24px;">¡Bienvenido a Pricy!</h1>
                    </div>
                    
                    <p>Hola <strong>{username}</strong>,</p>
                    
                    <p>Gracias por registrarte en <strong>Pricy Price Tracker</strong>. Para completar tu registro y comenzar a rastrear precios, por favor verifica tu correo electrónico usando el siguiente código:</p>
                    
                    <div class="code-container">
                        <div class="code">{code}</div>
                        <p class="info">Este código expira en 15 minutos</p>
                    </div>
                    
                    <p>Ingresa este código en la aplicación para activar tu cuenta y comenzar a:</p>
                    <ul>
                        <li>📊 Rastrear precios de tus productos favoritos</li>
                        <li>💰 Recibir alertas de descuentos</li>
                        <li>📈 Ver historial de precios</li>
                        <li>🎯 Establecer precios objetivo</li>
                    </ul>
                    
                    <p style="color: #6b7280; font-size: 14px;">Si no creaste esta cuenta, puedes ignorar este correo.</p>
                    
                    <div class="footer">
                        <p>Este correo fue enviado por <strong>Pricy Price Tracker</strong></p>
                        <p>Un proyecto desarrollado por HellSpawn</p>
                    </div>
                </div>
            </body>
            </html>
            """
        }
        
        email_response = resend.Emails.send(params)
        print(f"✅ Email enviado exitosamente a {email}")
        print(f"   Response: {email_response}")
        return True
    
    except Exception as e:
        print(f"❌ Error al enviar email a {email}")
        print(f"   Tipo de error: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False


def send_feedback_notification(feedback_data: dict) -> bool:
    """
    Enviar notificación de feedback recibido al administrador
    
    Args:
        feedback_data: Diccionario con datos del feedback
    
    Returns:
        bool: True si se envió exitosamente
    """
    try:
        user_info = f"Usuario: {feedback_data.get('username', 'Anónimo')}" if feedback_data.get('username') else "Usuario anónimo"
        email_info = f"Email: {feedback_data.get('email', 'No proporcionado')}"
        rating_stars = "⭐" * feedback_data.get('rating', 0) if feedback_data.get('rating') else "Sin calificación"
        
        params = {
            "from": f"Pricy Feedback <{FROM_EMAIL}>",
            "to": [FROM_EMAIL],  # Enviar a tu propio email
            "subject": f"Nuevo Feedback en Pricy - Rating: {rating_stars}",
            "html": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .container {{
                        background: #f9fafb;
                        border-radius: 8px;
                        padding: 30px;
                    }}
                    .header {{
                        background: #3b82f6;
                        color: white;
                        padding: 20px;
                        border-radius: 8px 8px 0 0;
                        margin: -30px -30px 20px -30px;
                    }}
                    .info-box {{
                        background: white;
                        padding: 15px;
                        border-radius: 6px;
                        margin: 10px 0;
                    }}
                    .message {{
                        background: white;
                        padding: 20px;
                        border-radius: 6px;
                        border-left: 4px solid #3b82f6;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2 style="margin: 0;">📬 Nuevo Feedback Recibido</h2>
                    </div>
                    
                    <div class="info-box">
                        <p><strong>{user_info}</strong></p>
                        <p><strong>{email_info}</strong></p>
                        <p><strong>Calificación:</strong> {rating_stars}</p>
                        <p><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    </div>
                    
                    <div class="message">
                        <h3 style="margin-top: 0;">Mensaje:</h3>
                        <p>{feedback_data.get('mensaje', 'Sin mensaje')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
        }
        
        email_response = resend.Emails.send(params)
        print(f"Notificación de feedback enviada: {email_response}")
        return True
    
    except Exception as e:
        print(f"Error al enviar notificación de feedback: {e}")
        return False


def send_welcome_email(email: str, username: str) -> bool:
    """
    Enviar email de bienvenida después de verificar cuenta
    
    Args:
        email: Email del destinatario
        username: Nombre de usuario
    
    Returns:
        bool: True si se envió exitosamente
    """
    try:
        params = {
            "from": f"Pricy Price Tracker <{FROM_EMAIL}>",
            "to": [email],
            "subject": "¡Tu cuenta ha sido verificada! 🎉",
            "html": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .container {{
                        background: #ffffff;
                        border-radius: 10px;
                        padding: 40px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .success {{
                        text-align: center;
                        font-size: 48px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="success">✅</div>
                    <h1 style="text-align: center; color: #3b82f6;">¡Cuenta Verificada!</h1>
                    
                    <p>Hola <strong>{username}</strong>,</p>
                    
                    <p>Tu cuenta ha sido verificada exitosamente. Ya puedes comenzar a usar todas las funciones de <strong>Pricy Price Tracker</strong>:</p>
                    
                    <ul>
                        <li>✅ Agrega tus productos favoritos</li>
                        <li>✅ Rastrea cambios de precios en tiempo real</li>
                        <li>✅ Recibe alertas cuando bajen los precios</li>
                        <li>✅ Ve el historial completo de precios</li>
                    </ul>
                    
                    <p style="text-align: center; margin: 30px 0;">
                        <strong>¡Empieza a ahorrar ahora!</strong>
                    </p>
                    
                    <p style="color: #6b7280; font-size: 14px; text-align: center;">
                        Gracias por usar Pricy 🎯
                    </p>
                </div>
            </body>
            </html>
            """
        }
        
        email_response = resend.Emails.send(params)
        print(f"Email de bienvenida enviado a {email}: {email_response}")
        return True
    
    except Exception as e:
        print(f"Error al enviar email de bienvenida a {email}: {e}")
        return False
