import firebase_admin
from firebase_admin import credentials, firestore
import flet as ft

# Inicializar Firebase Admin
cred = credentials.Certificate("config/spa-sentirse-bien-firebase-adminsdk-khrkv-c8f18ec6d5.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Función para autenticar usuario
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

# Pantalla de inicio de sesión
def pantalla_inicio_sesion(page):

    def login(event):
        email = email_input.value
        password = password_input.value
        
        # Verificar las credenciales en Firebase
        user_data = autenticar_usuario(email, password)
        
        if user_data:
            page.clean()
            mostrar_bienvenida(page, user_data['nombres'])
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Credenciales incorrectas"), open=True)
            page.update()

    # Crear los componentes de la interfaz de inicio de sesión
    email_input = ft.TextField(label="Email", width=300)
    password_input = ft.TextField(label="Contraseña", password=True, width=300)
    login_button = ft.ElevatedButton(text="Iniciar Sesión", on_click=login)

    # Añadir los elementos a la página
    page.add(
        ft.Column(
            [
                ft.Text("Iniciar Sesión", size=30, weight="bold"),
                email_input,
                password_input,
                login_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

# Pantalla de bienvenida
def mostrar_bienvenida(page, nombre):
    # Mostrar mensaje de bienvenida
    page.add(ft.Text(f"Hola {nombre}", size=30, weight="bold"))

# Inicializar la aplicación Flet
def main(page: ft.Page):
    page.title = "Sistema de Login"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    pantalla_inicio_sesion(page)

ft.app(target=main)
