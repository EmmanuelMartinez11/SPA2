import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

def enviar_factura_por_email(cliente_email, archivo_pdf):
    # Configuración del correo
    email_remitente = 'sentirsebienspa0@gmail.com'  # Cambia esto por tu correo
    email_contraseña = 'ijvu esza hgcg sbtg'  # Cambia esto por tu contraseña

    # Crear el mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = email_remitente
    mensaje['To'] = cliente_email
    mensaje['Subject'] = 'Tu factura de SPA SENTIRSE BIEN'

    # Agregar el cuerpo del mensaje
    cuerpo_mensaje = (
        "Estimado cliente,\n\n"
        "Adjunto encontrará su factura. ¡Gracias por su preferencia!\n\n"
        "Saludos cordiales,\n"
        "SPA SENTIRSE BIEN"
    )
    mensaje.attach(MIMEText(cuerpo_mensaje, 'plain'))

    # Adjuntar el archivo PDF
    if os.path.exists(archivo_pdf):  # Verificar si el archivo existe
        with open(archivo_pdf, 'rb') as adjunto:
            parte_adjunto = MIMEApplication(adjunto.read(), Name=os.path.basename(archivo_pdf))
        parte_adjunto['Content-Disposition'] = f'attachment; filename="{os.path.basename(archivo_pdf)}"'
        mensaje.attach(parte_adjunto)
    else:
        print(f"El archivo {archivo_pdf} no existe. No se adjuntará.")

    # Conectar y enviar el correo
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as servidor:
            servidor.starttls()  # Activar TLS
            servidor.login(email_remitente, email_contraseña)  # Iniciar sesión
            servidor.send_message(mensaje)  # Enviar el mensaje
            print(f"Factura enviada a {cliente_email}")
    except smtplib.SMTPException as e:
        print(f"Error al enviar el correo: {e}")

# Ejemplo de uso
# enviar_factura_por_email("cliente@example.com", "ruta/al/archivo.pdf")

