from flet import *

# Paleta de colores
COLOR_BOTONES = "#202B4B"
COLOR_TABLA_HEADER = "#ebd975"
COLOR_TABLA_ALTERNADO = "#f4fef8"
COLOR_FONDO = "#f4fef8"
COLOR_TEXTO = "#74994E"  # Color del texto (oscuro)

# Función para obtener los pagos
def obtener_pagos(db):
    pagos_ref = db.collection('turnos')
    pagos_query = pagos_ref.stream()  # Obtiene todos los pagos

    pagos = []
    for pago in pagos_query:
        pagos.append(pago.to_dict())
    return pagos

# Función para crear la tabla con los datos de los pagos
def crear_tabla_pagos(pagos):
    columnas = [
        DataColumn(Text("Cliente", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
        DataColumn(Text("Servicio", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
        DataColumn(Text("Estado", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
        DataColumn(Text("Precio", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
        DataColumn(Text("Fecha", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
        DataColumn(Text("Tipo de pago", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
    ]

    filas = []
    for i, pago in enumerate(pagos):
        filas.append(
            DataRow(
                cells=[
                    DataCell(Text(pago.get('cliente', 'N/A'), color=COLOR_TEXTO)),
                    DataCell(Text(pago.get('servicio', 'N/A'), color=COLOR_TEXTO)),
                    DataCell(Text(pago.get('estado', 'N/A'), color=COLOR_TEXTO)),
                    DataCell(Text(pago.get('precio', 'N/A'), color=COLOR_TEXTO)),
                    DataCell(Text(pago.get('fecha_turno', 'N/A'), color=COLOR_TEXTO)),
                    DataCell(Text(pago.get('tipo_pago', 'N/A'), color=COLOR_TEXTO)),
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

def Pagos(user_data, db):
    """
    Componente Pagos que muestra una tabla con la información de los pagos.
    """

    # Obtener los pagos iniciales
    pagos = obtener_pagos(db)

    # Crear la tabla de pagos
    tabla_pagos = crear_tabla_pagos(pagos)

    # Layout de la página
    return Container(
        content=Column(controls=[
            Text("Esta es la pantalla de Pagos.", color="black"),
            tabla_pagos,  # Mostrar la tabla de pagos
        ]),
        bgcolor=COLOR_FONDO,
        padding=10,
    )
