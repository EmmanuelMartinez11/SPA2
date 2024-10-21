from flet import *


def crearIdentificadorUsuario(toggle_sidebar, sidebar_expandido, user_data):
    # Columna con la información del usuario que se oculta cuando el sidebar está colapsado
    columna_usuario = Column(
        spacing=0,
        controls=[
            Text(
                value=f'{user_data['nombres']} {user_data['apellidos']}',  # Mostrar nombre y apellido
                size=18,
                weight='bold',
                opacity=1 if sidebar_expandido else 0,  # Mostrar si el sidebar está expandido
                animate_opacity=200
            ),
            Text(
                value=user_data["rol"],  # Mostrar el rol
                size=12,
                weight='w400',
                color="white54",
                opacity=1 if sidebar_expandido else 0,  # Mostrar si el sidebar está expandido
                animate_opacity=200
            )
        ]
    )
    
    return Container(
        padding=10,
        on_click=toggle_sidebar,  # Asignar el evento de click para colapsar/desplegar
        content=Row(
            controls=[
                Container(
                    width=42,
                    height=42,
                    bgcolor="bluegrey900",
                    alignment=alignment.center,
                    border_radius=8,
                    content=Text(
                        value=user_data["nombres"][0].upper(),  # Letra inicial del nombre
                        size=28,
                    )
                ),
                columna_usuario  # Columna que se oculta cuando el sidebar está colapsado
            ]
        )
    )


def crearBotonesDeBusqueda(nombreIcono: str, texto: str, cambiarPantalla, sidebar_expandido: bool):
    return Container(
        border_radius=10,
        padding=10,
        on_hover=lambda e: iluminarBotones(e),
        content=Row(
            controls=[
                Icon(
                    name=nombreIcono, 
                    size=22, 
                    color="white54"
                ),
                # Mostrar el texto solo si el sidebar está expandido
                Text(
                    value=texto,
                    color="white54", 
                    size=17, 
                    opacity=1 if sidebar_expandido else 0, 
                    animate_opacity=200
                )
            ],
        ),
        on_click=lambda e: cambiarPantalla(texto),  # Llama al manejador de clic con el texto del botón
        ink=True  # Efecto visual de click
    )

def iluminarBotones(e):
    icon = e.control.content.controls[0]  # Icono
    text = e.control.content.controls[1]  # Texto

    if e.data == "true":
        e.control.bgcolor = "white10"  # Fondo al iluminar
        icon.color = "white"  # Cambiar color del icono al iluminar
        text.color = "white"  # Cambiar color del texto al iluminar
    else:
        e.control.bgcolor = None  # Restaurar fondo
        icon.color = "white54"  # Restaurar color del icono
        text.color = "white54"  # Restaurar color del texto

    e.control.update()

def obtenerPreferencias(user_data):
    # Administrador
    if user_data["rol"] == "Administrador":
        return {
            icons.PAID: "Servicios",
            icons.PERSON: "Pagos",
            icons.POWER_SETTINGS_NEW: "Cerrar sesión"
        }
    # Secretario/a
    elif user_data["rol"] == "Secretario/a":
        return {
            icons.PERSON: "Pagos",
            icons.POWER_SETTINGS_NEW: "Cerrar sesión"
        }
    # Especialistas y otros roles
    elif user_data["rol"] in ["Especialista en tratamientos corporales", "Especialista en facial", "Esteticista", "Masajista"]:
        return {
            icons.PAID: "Servicios",
            icons.POWER_SETTINGS_NEW: "Cerrar sesión"
        }
    return {}

# Función principal del sidebar
def SideBar(cambiarPantalla, user_data):
    # Variable de estado para alternar entre expandido/colapsado
    sidebar_expandido = True

    # Acción de colapsar/desplegar el sidebar
    def toggle_sidebar(e):
        nonlocal sidebar_expandido
        sidebar_expandido = not sidebar_expandido
        actualizarSidebar()

    # Obtener las preferencias según el rol del usuario
    preferencias = obtenerPreferencias(user_data)

    # Crear los botones en base a las preferencias
    botones = []
    for icono, texto in preferencias.items():
        botones.append(crearBotonesDeBusqueda(icono, texto, cambiarPantalla, sidebar_expandido))

    # Contenedor del sidebar
    sidebar_container = Container(
        padding=0,
        margin=0,
        bgcolor="#CD849A",
        width=300 if sidebar_expandido else 70,  # Ajustar el ancho según el estado
        animate=animation.Animation(300, "ease"),
        alignment=alignment.center,
        content=Column(
            controls=[
                Divider(height=15, color="transparent"),
                crearIdentificadorUsuario(toggle_sidebar, sidebar_expandido, user_data),  # Usar el container como botón y pasar estado expandido
                Divider(height=15, color="transparent"),
                *botones  # Renderizar los botones generados
            ]
        )
    )

    # Función para actualizar el sidebar cuando se colapsa o despliega
    def actualizarSidebar():
        sidebar_container.width = 300 if sidebar_expandido else 70
        # Actualizar la visibilidad de los textos en los botones y en la columna de usuario
        for i, (icono, texto) in enumerate(preferencias.items()):
            botones[i].content.controls[1].opacity = 1 if sidebar_expandido else 0
            botones[i].content.controls[1].update()
        
        # Actualizar la columna de usuario
        sidebar_container.content.controls[1].content.controls[1].opacity = 1 if sidebar_expandido else 0
        sidebar_container.content.controls[1].content.controls[1].update()

        sidebar_container.update()

    # Retornar el contenedor del sidebar
    return sidebar_container