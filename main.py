import firebase_admin
from firebase_admin import credentials, firestore
from flet import *
from componentes.sideBar import SideBar
from componentes.servicios import Servicios
from componentes.pagos import Pagos

# Inicializar Firebase Admin
cred = credentials.Certificate("config/credenciales.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


# Función para autenticar usuario
def autenticar_usuario(email, password):
    users_ref = db.collection('personal')
    query = users_ref.where('email', '==', email).stream()

    for user in query:
        user_data = user.to_dict()
        if 'email' in user_data and user_data['email'] == email:
            # Simulando la verificación de contraseña
            if password == '123456':  # Aquí podrías usar un campo de contraseña en Firebase
                return user_data
            else:
                return None
    return None

# Pantalla de inicio de sesión
def pantalla_inicio_sesion(page, cambiar_pantalla):
    def login(event):
        email = email_input.value
        password = password_input.value
        
        # Verificar las credenciales en Firebase
        user_data = autenticar_usuario(email, password)
        print(user_data)
        if user_data:
            cambiar_pantalla(user_data)
        else:
            mensaje_error.value = "Usuario o contraseña incorrectos"
            mensaje_error.color = "red"
            page.update()

    # Crear los componentes de la interfaz de inicio de sesión
    email_input = TextField(label="Email", width=300)
    password_input = TextField(label="Contraseña", password=True, width=300)
    login_button = ElevatedButton(text="Iniciar Sesión", on_click=login)
    mensaje_error = Text("", size=20)

    # Contenedor de la imagen a la izquierda
    imagen = Container(
        content=Image(src="assets/inicio_sesion.jpg", fit=ImageFit.COVER, ),
    )

    # Contenedor del formulario de inicio de sesión a la derecha
    formulario = Container(
        content=Column(
            [
                Text("Iniciar Sesión", size=30, weight="bold"),
                email_input,
                password_input,
                login_button,
                mensaje_error
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        ),
        width=400,  # Ajustar ancho según sea necesario
    )

    # Añadir los elementos a la página en un Row
    page.add(
        Container(
            content=(
                Row(
                    controls=[   
                        imagen,
                        formulario
                    ],
                    spacing=0,
                )
            ),
            padding=0,
            margin=0,
            expand=True
        )
    )

# Pantalla principal con sidebar y contenedor dinámico
def pantalla_contenido(page, user_data, cambiar_a_contenido):
    # Callback para cambiar el contenido del contenedor principal
    def cambiar_pantalla(pantalla):
        if pantalla == "Servicios":
            contenedorDerecha.content = Servicios(user_data, db)  # Pasar db a Servicios
        elif pantalla == "Pagos":
            contenedorDerecha.content = Pagos()
        elif pantalla == "Cerrar sesión":
            cerrar_sesion()  # Al hacer clic en "Cerrar sesión"
        else:
            contenedorDerecha.content = Text(f"No se encontró la pantalla: {pantalla}")
        page.update()
    
    # Función para cerrar sesión
    def cerrar_sesion():
        page.clean()  # Limpiar la página
        pantalla_inicio_sesion(page, cambiar_a_contenido)  # Mostrar pantalla de inicio de sesión
        page.update()
    
    sidebar = SideBar(cambiar_pantalla, user_data)
    
    # Configurar el contenido inicial basado en el rol
    if user_data['rol'] in ['Administrador', 'Especialista en tratamientos corporales', 'Especialista en facial', 'Esteticista', 'Masajista']:
        contenido_inicial = Servicios(user_data, db)  # Pasar db a Servicios
    elif user_data['rol'] == 'Secretario/a':
        contenido_inicial = Pagos()
    else:
        contenido_inicial = Text("No tiene permisos para acceder a esta sección.")
    
    contenedorDerecha = Container(
        content=contenido_inicial, 
        expand=True, 
        bgcolor="white",
    )

    page.add(
        Row(
            spacing=0,
            controls=[Container(content=sidebar), contenedorDerecha],
            expand=True,
        )
    )
    page.update()

# Función principal que maneja la navegación
def main(page: Page):
    page.title = "Aplicación con Inicio de Sesión y Sidebar"
    page.padding = 0
    page.vertical_alignment = MainAxisAlignment.CENTER

    # Cambiar entre la pantalla de inicio de sesión y la pantalla principal
    def cambiar_a_contenido(user_data):
        page.clean()  # Limpiar la página de inicio de sesión
        pantalla_contenido(page, user_data, cambiar_a_contenido)

    # Iniciar mostrando la pantalla de inicio de sesión
    pantalla_inicio_sesion(page, cambiar_a_contenido)

app(target=main)