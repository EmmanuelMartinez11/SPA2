import firebase_admin
from firebase_admin import credentials, firestore
import flet as ft

# Inicializar Firebase Admin
cred = credentials.Certificate("config/spa-sentirse-bien-firebase-adminsdk-khrkv-c8f18ec6d5.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
def autenticar_usuario(email, password):
    # Aquí puedes acceder a la colección 'personal' en Firestore
    users_ref = db.collection('personal')
    query = users_ref.where('email', '==', email).stream()

    for user in query:
        user_data = user.to_dict()
        if 'email' in user_data and user_data['email'] == email:
            # Simulando la verificación de contraseña (puedes hacerla más segura)
            if password == '123456':  # Aquí podrías usar un campo de contraseña en Firebase
                return user_data
            else:
                return None
    return None

def pantalla_inicio_sesion(page, cambiar_contenido):
    # Contenido de la pantalla de inicio de sesión
    email = ft.TextField(label="Correo Electrónico", width=300)
    password = ft.TextField(label="Contraseña", password=True, width=300)

    def iniciar_sesion_click(e):
        # Aquí puedes agregar la lógica para verificar las credenciales
        user_data = autenticar_usuario(email.value, password.value)  # Asegúrate de definir esta función o importarla
        if user_data:  # Si las credenciales son correctas
            cambiar_contenido(user_data)  # Cambia a la pantalla principal
        else:
            ft.Toast("Usuario o contraseña incorrectos", duration=2).show(page)  # Mostrar mensaje de error

    iniciar_sesion_button = ft.ElevatedButton("Iniciar Sesión", on_click=iniciar_sesion_click)

    # Limpiamos el contenido actual de la página y mostramos la pantalla de inicio de sesión
    page.controls.clear()
    page.add(
        ft.Column(
            [
                ft.Text("Iniciar Sesión", size=30),
                email,
                password,
                iniciar_sesion_button
            ],
            alignment="center",
            horizontal_alignment="center",
        )
    )
    page.update()
