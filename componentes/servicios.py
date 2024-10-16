from flet import *
from datetime import datetime

# Paleta de colores
COLOR_BOTONES = "#202B4B"
COLOR_TABLA_HEADER = "#ebd975"
COLOR_TABLA_ALTERNADO = "#f4fef8"
COLOR_FONDO = "#f4fef8"
COLOR_TEXTO = "#74994E"  # Color del texto (oscuro)

# Función para obtener los turnos basados en el rol
def obtener_turnos_por_rol(user_data, db):
    turnos_ref = db.collection('turnos')
    
    if user_data['rol'] == 'Administrador':
        turnos_query = turnos_ref.stream()
    elif user_data['rol'] == 'Especialista en tratamientos corporales':
        turnos_query = turnos_ref.where('servicio', '==', 'Tratamientos Corporales').stream()
    elif user_data['rol'] == 'Especialista en tratamientos faciales':
        turnos_query = turnos_ref.where('servicio', '==', 'Tratamientos Faciales').stream()
    elif user_data['rol'] == 'Esteticista':
        turnos_query = turnos_ref.where('servicio', '==', 'Belleza').stream()
    elif user_data['rol'] == 'Masajista':
        turnos_query = turnos_ref.where('servicio', '==', 'Masajes').stream()
    else:
        return []

    turnos = []
    for turno in turnos_query:
        turnos.append(turno.to_dict())
    
    return turnos

# Función para crear la tabla con los datos de los turnos
def crear_tabla_turnos(turnos):
    columnas = [
        DataColumn(Text("Cliente", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
        DataColumn(Text("Servicio", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
        DataColumn(Text("Especialidad", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
        DataColumn(Text("Fecha", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
        DataColumn(Text("Personal", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
    ]

    filas = []
    for i, turno in enumerate(turnos):
        filas.append(
            DataRow(
                cells=[
                    DataCell(Text(turno.get('cliente', 'N/A'), color=COLOR_TEXTO)),
                    DataCell(Text(turno.get('servicio', 'N/A'), color=COLOR_TEXTO)),
                    DataCell(Text(turno.get('especialidad', 'N/A'), color=COLOR_TEXTO)),
                    DataCell(Text(turno.get('fecha_turno', 'N/A'), color=COLOR_TEXTO)),
                    DataCell(Text(turno.get('personal_a_cargo', 'N/A'), color=COLOR_TEXTO)),
                ],
                color=COLOR_TABLA_ALTERNADO if i % 2 == 0 else colors.WHITE,  # Alternar colores de filas
            )
        )

    return DataTable(
        columns=columnas,
        rows=filas,
        heading_row_color=COLOR_TABLA_HEADER,  # Color de fondo para el encabezado
        border=border.all(1, "grey"),  # Borde de la tabla
        vertical_lines=border.BorderSide(1, "grey"),  # Líneas verticales
        horizontal_lines=border.BorderSide(1, "grey"),  # Líneas horizontales
    )

def Servicios(page, user_data, db):
    """
    Componente Servicios con dos dropdowns para filtrar por servicio y especialidad,
    y un campo para filtrar por nombre de cliente.
    """

    # Función para actualizar la tabla de turnos al seleccionar un servicio o especialidad del Dropdown
    def actualizar_tabla(e=None):
        # Obtener todos los turnos según el rol del usuario
        turnos = obtener_turnos_por_rol(user_data, db)

        # Filtrar por servicio si el dropdown está visible y se selecciona algo diferente de "Mostrar todas"
        if user_data['rol'] == 'Administrador':
            servicio_filtro = dropdown_servicio.value
            if servicio_filtro != "Mostrar todas":
                turnos = [turno for turno in turnos if turno.get('servicio') == servicio_filtro]

            # Filtrar por especialidad si el dropdown está visible y se selecciona algo diferente de "Mostrar todas"
            especialidad_filtro = dropdown_especialidad.value
            if especialidad_filtro != "Mostrar todas":
                turnos = [turno for turno in turnos if turno.get('especialidad') == especialidad_filtro]

        # Filtrar por cliente si se proporciona
        cliente_filtro = textfield_cliente.value.strip()
        if cliente_filtro:
            turnos = [turno for turno in turnos if cliente_filtro.lower() in turno.get('cliente', '').lower()]

        # Filtrar por fecha si se selecciona una fecha en el campo de fecha
        fecha_filtro = textfield_fecha.value.strip()

        # Validar si la fecha ingresada es válida (formato correcto: AAAA-MM-DD)
        if fecha_filtro:
            try:
                # Validar que la fecha ingresada esté en el formato correcto (DD-MM-AAAA)
                datetime.strptime(fecha_filtro, '%d-%m-%Y')
                
                # Filtrar los turnos que coincidan con la fecha (asegurando el formato correcto)
                turnos = [turno for turno in turnos if turno.get('fecha_turno', '').strftime('%d-%m-%Y') == fecha_filtro]
        
            except ValueError:
                page.dialog.show_alert("Fecha no válida. Usa el formato DD-MM-AAAA")
        # Actualizar la tabla con los turnos filtrados
        tabla_turnos.rows = crear_tabla_turnos(turnos).rows
        page.update()

    # Crear el dropdown para servicio con "Mostrar todas" como valor predeterminado
    dropdown_servicio = Dropdown(
        label="Selecciona un servicio",
        width=300,
        options=[
            dropdown.Option("Mostrar todas"),
            dropdown.Option("Tratamientos Corporales"),
            dropdown.Option("Tratamientos Faciales"),
            dropdown.Option("Belleza"),
            dropdown.Option("Masajes"),
        ],
        value="Mostrar todas",  # Establecer "Mostrar todas" como valor predeterminado
        on_change=actualizar_tabla  # Llamar a la función cuando se cambie el valor
    )

    # Crear el dropdown para especialidad con "Mostrar todas" como valor predeterminado
    dropdown_especialidad = Dropdown(
        label="Selecciona una especialidad",
        width=300,
        options=[
            dropdown.Option("Mostrar todas"),
            dropdown.Option("Descontracturantes"),
            dropdown.Option("Masajes con piedras calientes"),
            dropdown.Option("Circulatorios"),
            dropdown.Option("Lifting de pestaña"),
            dropdown.Option("Depilación facial"),
            dropdown.Option("Belleza de manos y pies"),
            dropdown.Option("Punta de Diamante"),
            dropdown.Option("Crio frecuencia facial"),
            dropdown.Option("VelaSlim"),
            dropdown.Option("DermoHealth"),
            dropdown.Option("Criofrecuencia"),
            dropdown.Option("Ultracavitación"),
        ],
        value="Mostrar todas",  # Establecer "Mostrar todas" como valor predeterminado
        on_change=actualizar_tabla  # Llamar a la función cuando se cambie el valor
    )

    # Campo de texto para buscar por nombre de cliente
    textfield_cliente = TextField(
        label="Buscar por cliente",
        on_change=actualizar_tabla,  # Llamar a la función cuando se cambie el valor
        color=COLOR_TEXTO  # Color del texto en el campo de búsqueda
    )
    
    # Campo de texto para ingresar fecha manualmente (con validación)
    textfield_fecha = TextField(
        label="Selecciona una fecha (DD-MM-AAAA):",
        on_change=actualizar_tabla,  # Llamar a la función cuando se seleccione una fecha
        color=COLOR_TEXTO  # Color del texto en el campo de búsqueda
    )

    # Obtener los turnos iniciales basados en el rol del usuario
    turnos = obtener_turnos_por_rol(user_data, db)

    # Crear la tabla de turnos
    tabla_turnos = crear_tabla_turnos(turnos)

    # Layout de la página: solo mostrar filtros para Administrador
    controls = [
        Row([textfield_cliente, textfield_fecha]),  # Agregar el campo de texto y el selector de fecha
        tabla_turnos,  # Mostrar la tabla de turnos
    ]

    # Si el usuario es Administrador, añadir los filtros de servicio y especialidad
    if user_data['rol'] == 'Administrador':
        controls.insert(0, Row(controls=[dropdown_servicio, dropdown_especialidad]))

    # Layout de la página
    return Container(
        content=Column(controls=controls),  # Añadir los controles aquí
        bgcolor=COLOR_FONDO,
        padding=10,
    )
