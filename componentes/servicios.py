from flet import *
from datetime import datetime
from collections import Counter


# Paleta de colores
COLOR_BOTONES = "#f4fef8"
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
def obtener_datos_pagos(db, servicio_filtro=None, especialidad_filtro=None, cliente_filtro=None, fecha_filtro=None):
    pagos = db.collection('turnos').stream()  # Obtener todos los pagos
    
    ingresos_totales = 0
    ingresos_por_servicio = {}
    ingresos_por_metodo = {}      # <-- Inicializar diccionario para ingresos por método de pago
    ingresos_por_especialidad = {}  # <-- Inicializar diccionario para ingresos por especialidad
    ingresos_por_cliente = {}      # <-- Inicializar diccionario para ingresos por cliente
    servicios_por_cliente = {}     # <-- Inicializar diccionario para contar servicios por cliente


    for pago in pagos:
        pago = pago.to_dict()

        # Aplicar filtros
        if servicio_filtro and pago.get('servicio') != servicio_filtro:
            continue
        if especialidad_filtro and pago.get('especialidad') != especialidad_filtro:
            continue
        if cliente_filtro and cliente_filtro.lower() not in pago.get('cliente', '').lower():
            continue
        if fecha_filtro and pago.get('fecha_turno') != fecha_filtro:
            continue

        # Calcular ingresos
        monto = float(pago.get('precio', 0))  # Convertir el precio a número
        servicio = pago.get('servicio')
        metodo_pago = pago.get('tipo_pago')  # <-- Obtener el método de pago
        especialidad = pago.get('especialidad')  # <-- Obtener la especialidad
        cliente = pago.get('cliente')          # <-- Obtener el cliente

        ingresos_totales += monto

        # Ingresos por método de pago  <-- Añadir esta sección
        if metodo_pago in ingresos_por_metodo:
            ingresos_por_metodo[metodo_pago] += monto
        else:
            ingresos_por_metodo[metodo_pago] = monto
        # Ingresos por servicio
        if servicio in ingresos_por_servicio:
            ingresos_por_servicio[servicio] += monto
        else:
            ingresos_por_servicio[servicio] = monto

        # Ingresos por especialidad  <-- Calcular ingresos por especialidad
        if especialidad in ingresos_por_especialidad:
            ingresos_por_especialidad[especialidad] += monto
        else:
            ingresos_por_especialidad[especialidad] = monto

        # Ingresos por cliente  <-- Calcular ingresos por cliente
        if cliente in ingresos_por_cliente:
            ingresos_por_cliente[cliente] += monto
        else:
            ingresos_por_cliente[cliente] = monto

        # Contar servicios por cliente  <-- Contar servicios por cliente
        if cliente in servicios_por_cliente:
            servicios_por_cliente[cliente] += 1
        else:
            servicios_por_cliente[cliente] = 1
    # Calcular nuevas estadísticas

    return {
        "ingresos_totales": ingresos_totales,
        "ingresos_por_servicio": ingresos_por_servicio,
        "ingresos_por_metodo": ingresos_por_metodo,
        "ingresos_por_especialidad": ingresos_por_especialidad,  # <-- Añadir al diccionario de resultados
        "ingresos_por_cliente": ingresos_por_cliente,        # <-- Añadir al diccionario de resultados
        "servicios_por_cliente": servicios_por_cliente,       # <-- Añadir al diccionario de resultados  
          
    }

def Servicios(page, user_data, db):
    """
    Componente Servicios con dos dropdowns para filtrar por servicio y especialidad,
    y un campo para filtrar por nombre de cliente.
    """

    # Crear un AlertDialog para mostrar mensajes de error
    dlg_error = AlertDialog(title=Text("Error"))
    page.dialog = dlg_error  # Asignar el AlertDialog a page.dialog
   
    def seleccionar_fecha(e):
        date_picker_dialog.open = True
        page.update()
    
    def actualizar_fecha(e):
        date_picker.value = e.control.value
        textfield_fecha.value = e.control.value.strftime("%d-%m-%Y")  # Formatear la fecha para el TextField
        actualizar_tabla()
        page.update()

    textfield_fecha = TextField(
        label="Selecciona una fecha (DD-MM-AAAA):",
        color=COLOR_TEXTO
    )

    # Crear el DatePicker (calendario)
    date_picker_dialog = DatePicker(
        on_change=actualizar_fecha,
    )

    # Crear el botón para abrir el calendario
    boton_calendario = IconButton(
        icon=icons.CALENDAR_MONTH,
        on_click=seleccionar_fecha,
        bgcolor=COLOR_BOTONES,
        icon_color=COLOR_TEXTO,
    )
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

        # Filtrar por fecha seleccionada en el DatePicker
        fecha_filtro = textfield_fecha.value.strip()

    # Validar si la fecha ingresada es válida (formato correcto: DD-MM-AAAA)
        if fecha_filtro:
            try:
            # Validar que la fecha ingresada esté en el formato correcto (DD-MM-AAAA)
                datetime.strptime(fecha_filtro, '%d-%m-%Y')

            # Convertir la fecha al formato AAAA-MM-DD para la comparación
                fecha_filtro_dt = datetime.strptime(fecha_filtro, '%d-%m-%Y').date()

            # Filtrar los turnos que coincidan con la fecha
                turnos = [turno for turno in turnos if turno.get('fecha_turno').date() == fecha_filtro_dt]

            except ValueError:
                page.dialog.show_alert("Fecha no válida. Usa el formato DD-MM-AAAA")
                return  # Salir de la función si la fecha no es válida

        tabla_turnos.rows.clear() 
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
        bgcolor=COLOR_BOTONES,
        color=COLOR_TEXTO,
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
        bgcolor=COLOR_BOTONES,
        color=COLOR_TEXTO,
        value="Mostrar todas",  # Establecer "Mostrar todas" como valor predeterminado
        on_change=actualizar_tabla  # Llamar a la función cuando se cambie el valor
    )

    # Campo de texto para buscar por nombre de cliente
    textfield_cliente = TextField(
        label="Buscar por cliente",
        on_change=actualizar_tabla,  # Llamar a la función cuando se cambie el valor
        color=COLOR_TEXTO  # Color del texto en el campo de búsqueda
    )
    # DatePicker para seleccionar la fecha
    date_picker = DatePicker(
        on_change=actualizar_tabla,  # Llamar a la función cuando se seleccione una fecha
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
        Row([textfield_cliente]),
        Row([textfield_fecha, boton_calendario]),   # Quitar datepicker_fecha del Row
        Text("Tabla de Turnos", size=20, color=COLOR_TEXTO),  # Título de la tabla
        tabla_turnos,  # Mostrar la tabla de turnos
    ]
    page.overlay.append(date_picker_dialog)


    # Si el usuario es Administrador, añadir los filtros de servicio y especialidad
    if user_data['rol'] == 'Administrador':
        controls.insert(0, Row(controls=[dropdown_servicio, dropdown_especialidad]))
        def on_click_mostrar_estadisticas(e):  # <-- Mover la lógica aquí
            servicio_filtro = dropdown_servicio.value if dropdown_servicio.value != "Mostrar todas" else None
            especialidad_filtro = dropdown_especialidad.value if dropdown_especialidad.value != "Mostrar todas" else None
            cliente_filtro = textfield_cliente.value.strip()
            fecha_filtro = textfield_fecha.value.strip()

            datos_pagos = obtener_datos_pagos(
                db, 
                servicio_filtro=servicio_filtro, 
                especialidad_filtro=especialidad_filtro, 
                cliente_filtro=cliente_filtro, 
                fecha_filtro=fecha_filtro
            )
            promedio_por_servicio = {servicio: ingresos / datos_pagos["servicios_por_cliente"].get(cliente, 1) 
                             for cliente, ingresos in datos_pagos["ingresos_por_cliente"].items()
                             for servicio in datos_pagos["ingresos_por_servicio"]}

            cliente_mas_gasta = max(datos_pagos["ingresos_por_cliente"], key=datos_pagos["ingresos_por_cliente"].get, default=None)

            especialidad_mas_rentable = max(datos_pagos["ingresos_por_especialidad"], key=datos_pagos["ingresos_por_especialidad"].get, default=None)

            metodo_pago_mas_usado = max(datos_pagos["ingresos_por_metodo"], key=datos_pagos["ingresos_por_metodo"].get, default=None)

    # Añadir nuevas estadísticas al diccionario datos_pagos  <-- AÑADIR AQUÍ
            datos_pagos["promedio_por_servicio"] = promedio_por_servicio
            datos_pagos["cliente_mas_gasta"] = cliente_mas_gasta
            datos_pagos["especialidad_mas_rentable"] = especialidad_mas_rentable
            datos_pagos["metodo_pago_mas_usado"] = metodo_pago_mas_usado

            # Crear la ventana modal (AlertDialog)
            dlg_modal = AlertDialog(
                title=Text("Estadísticas de Pagos", color=COLOR_TEXTO),
                content=Column(
                    controls=[
                        Text(f"Ingresos Totales: ${datos_pagos['ingresos_totales']:.2f}", size=20, color=COLOR_TEXTO),

                        # DataTable para ingresos por servicio
                        DataTable(
                            columns=[
                                DataColumn(Text("Servicio", weight=FontWeight.BOLD, color=COLOR_TEXTO )),
                                DataColumn(Text("Ingresos", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
                            ],
                            rows=[
                                DataRow(
                                    cells=[
                                        DataCell(Text(servicio, color=COLOR_TEXTO)),
                                        DataCell(Text(f"${ingresos:.2f}", color=COLOR_TEXTO)),
                                    ]
                                )
                                for servicio, ingresos in datos_pagos["ingresos_por_servicio"].items()
                            ],column_spacing=100,
                        ),

                        # DataTable para ingresos por especialidad
                        DataTable(
                            columns=[
                                DataColumn(Text("Especialidad", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
                                DataColumn(Text("Ingresos", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
                            ],
                            rows=[
                                DataRow(
                                    cells=[
                                        DataCell(Text(especialidad, color=COLOR_TEXTO)),
                                        DataCell(Text(f"${ingresos:.2f}", color=COLOR_TEXTO)),
                                    ]
                                )
                                for especialidad, ingresos in datos_pagos["ingresos_por_especialidad"].items()
                            ],column_spacing=100,
                        ),

                        # DataTable para ingresos por cliente
                        DataTable(
                            columns=[
                                DataColumn(Text("Cliente", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
                                DataColumn(Text("Ingresos", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
                                DataColumn(Text("Servicios", weight=FontWeight.BOLD, color=COLOR_TEXTO)),  # <-- Nueva columna
                            ],
                            rows=[
                                DataRow(
                                    cells=[
                                        DataCell(Text(cliente, color=COLOR_TEXTO)),
                                        DataCell(Text(f"${ingresos:.2f}", color=COLOR_TEXTO)),
                                        DataCell(Text(str(datos_pagos["servicios_por_cliente"][cliente]), color=COLOR_TEXTO)),  # <-- Mostrar cantidad de servicios
                                    ]
                                )
                                for cliente, ingresos in datos_pagos["ingresos_por_cliente"].items()
                            ],column_spacing=100,
                        ), Text(f"Promedio de ingresos por servicio: {datos_pagos['promedio_por_servicio']}", color=COLOR_TEXTO),
                        Text(f"Cliente que más gasta: {datos_pagos['cliente_mas_gasta'] or 'N/A'}", color=COLOR_TEXTO),
                        Text(f"Especialidad más rentable: {datos_pagos['especialidad_mas_rentable'] or 'N/A'}", color=COLOR_TEXTO),
                        Text(f"Método de pago más usado: {datos_pagos['metodo_pago_mas_usado'] or 'N/A'}", color=COLOR_TEXTO),                       
                    ]
                ),
                bgcolor=COLOR_BOTONES,
                actions=[
                    TextButton("Cerrar", on_click=lambda e: (setattr(dlg_modal, 'open', False), page.go('/servicios'))),
                ],
                modal=True,
            )
             # Mostrar la ventana modal
            page.overlay.append(dlg_modal) 
            dlg_modal.open = True
            page.update()
        boton_estadisticas = ElevatedButton(
            text="Ver estadísticas de pagos",
            on_click=on_click_mostrar_estadisticas,  # <-- Asignar la función al botón
            bgcolor=COLOR_BOTONES,
            color=COLOR_TEXTO,
        )
        controls.append(boton_estadisticas)     
    
    # Layout de la página
    return Container(
        content=Column(controls=controls),  # Añadir los controles aquí
        bgcolor=COLOR_FONDO,
        padding=10,
    )