from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from backend.utilidades.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_SERVER=settings.mail_server,
    MAIL_PORT=settings.mail_port,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=None,
    SUPPRESS_SEND=False
)

fm = FastMail(conf)

async def send_activation_email(email: str, token: str):
    confirm_link = f"http://localhost:8000/usuarios/activar?token={token}"
    html = f"""
    <html>
    <body>
        <h2>¡Bienvenido a Yavanna!</h2>
        <p>Gracias por registrarte. Para activar tu cuenta, haz clic en el siguiente botón:</p>
        <p>
            <a href='{confirm_link}' style='background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>
                Activar mi cuenta
            </a>
        </p>
        <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
        <p><a href='{confirm_link}'>{confirm_link}</a></p>
        <br>
        <p>¡Gracias por confiar en Yavanna!</p>
    </body>
    </html>
    """
    message = MessageSchema(
        subject="Activa tu cuenta en Yavanna",
        recipients=[email],
        body=html,
        subtype="html"
    )
    await fm.send_message(message)

async def send_reminder_email(email: str, nombre_cliente: str, fecha: str, hora: str, servicio: str, mascota: str, cita_id: int):
    link = f"http://localhost:8000/citas/{cita_id}"
    html = f"""
    <html>
    <body>
        <h2>¡Hola {nombre_cliente}!</h2>
        <p>Este es un recordatorio de tu cita próxima en Yavanna.</p>
        <ul>
            <li><b>Fecha:</b> {fecha}</li>
            <li><b>Hora:</b> {hora}</li>
            <li><b>Servicio:</b> {servicio}</li>
            <li><b>Mascota:</b> {mascota}</li>
        </ul>
        <p>Puedes ver los detalles de tu cita haciendo clic aquí:<br>
        <a href='{link}' style='color: #4CAF50; font-weight: bold;'>Ver mi cita</a></p>
        <br>
        <p>¡Te esperamos!</p>
    </body>
    </html>
    """
    message = MessageSchema(
        subject="Recordatorio de tu cita en Yavanna",
        recipients=[email],
        body=html,
        subtype="html"
    )
    await fm.send_message(message)
