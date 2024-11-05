import os
from datetime import datetime
from flet import *
from fpdf import FPDF  # Asegúrate de que fpdf está instalado
from random import randint  # Importa randint desde random
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Paleta de colores
COLOR_BOTONES = "#CD4875"
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
        DataColumn(Text("Seleccionar", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
        DataColumn(Text("Cliente", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
        DataColumn(Text("Servicio", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
        DataColumn(Text("Estado", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
        DataColumn(Text("Precio", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
        DataColumn(Text("Fecha", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
        DataColumn(Text("Tipo de pago", weight=FontWeight.BOLD, color=COLOR_TEXTO)),
    ]

    filas = []
    for i, pago in enumerate(pagos):
        if pago.get('estado', '') == 'Pagado':  # Asegúrate de que sea "pagado"
            filas.append(
                DataRow(
                    cells=[
                        DataCell(Checkbox(value=False, on_change=lambda e, idx=i: actualizar_seleccion(idx))),
                        DataCell(Text(pago.get('cliente', 'N/A'), color=COLOR_TEXTO)),
                        DataCell(Text(pago.get('servicio', 'N/A'), color=COLOR_TEXTO)),
                        DataCell(Text(pago.get('estado', 'N/A'), color=COLOR_TEXTO)),
                        DataCell(Text(str(pago.get('precio', 'N/A')), color=COLOR_TEXTO)),  # Convertir a string
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

# Variable para mantener el estado de selección
selecciones = []

# Función para actualizar la selección
def actualizar_seleccion(indice):
    if indice in selecciones:
        selecciones.remove(indice)
    else:
        selecciones.append(indice)

def generar_factura(clientes, servicios, email):
    pdf = FPDF()

    # Obtén la ruta del directorio de la aplicación
    if getattr(sys, 'frozen', False):
        directorio_aplicacion = os.path.dirname(sys.executable)
    else:
        directorio_aplicacion = os.path.dirname(os.path.abspath(__file__))

    # Asegúrate de que la carpeta de facturas exista
    directorio_facturas = os.path.join(directorio_aplicacion, "facturas")
    os.makedirs(directorio_facturas, exist_ok=True)

    # Crear la primera página
    pdf.add_page()

    # Encabezado de la factura
    pdf.set_font("Arial", size=12, style="B")

    # Logo de la empresa
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo_spa.png")
    pdf.image(logo_path, x=(pdf.w - 33) / 2, y=8, w=33)  # Centrar el logo

    # Nombre de la empresa
    pdf.cell(100, 10, "SPA SENTIRSE BIEN", ln=False)  # Cambia el nombre de la empresa
    pdf.cell(0, 10, txt=f"Factura N° {randint(1000, 9999)}", ln=True, align="R")  # Número de factura random
    
    # Información de contacto
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, "Dirección: Calle French 123, Resistencia", ln=True)
    pdf.cell(0, 10, "Teléfono: (123) 456-7890", ln=True)
    pdf.cell(0, 10, "Email: sentirsebienspa0@gmail.com", ln=True)
    
    pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(10)  # Salto de línea

    # Solo se toma el primer cliente para evitar múltiples tablas
    cliente = clientes[0]
    
    # Datos del cliente
    pdf.set_font("Arial", size=12, style="B")
    pdf.cell(100, 10, txt=f"Cliente: {cliente.get('cliente')}", ln=True)
    pdf.ln(5)  # Salto de línea

    # Título de la tabla de servicios
    pdf.set_font("Arial", size=12, style="B")
    pdf.cell(0, 10, "Detalle de Servicios", ln=True)
    pdf.ln(5)  # Salto de línea

    # Tabla de servicios
    pdf.set_font("Arial", size=10, style="B")
    pdf.cell(50, 10, "Servicio", border=1, align='C')
    pdf.cell(50, 10, "Especialidad", border=1, align='C')
    pdf.cell(50, 10, "Tipo de Pago", border=1, align='C')
    pdf.cell(40, 10, "Precio", border=1, align='C')
    pdf.ln()

    pdf.set_font("Arial", size=10)
    for servicio in servicios:
        if servicio.get('cliente') == cliente.get('cliente'):  # Filtrar servicios por cliente
            pdf.cell(50, 10, servicio.get("servicio"), border=1)
            pdf.cell(50, 10, servicio.get("especialidad"), border=1)
            pdf.cell(50, 10, servicio.get("tipo_pago"), border=1)
            pdf.cell(40, 10, f"${servicio.get('precio')}", border=1)
            pdf.ln()

    # Total
    total = sum([s.get('precio') for s in servicios if s.get('cliente') == cliente.get('cliente')])
    pdf.cell(150, 10, "Total", border=1, align='C')
    pdf.cell(40, 10, f"${total}", border=1, align='C')
    pdf.ln(10)  # Salto de línea

    # Mensaje de agradecimiento
    pdf.set_font("Arial", style='I', size=10)
    pdf.cell(0, 10, "Gracias por elegirnos!", ln=True, align='C')
    
    # Guardar el PDF
    archivo_pdf = f"{directorio_facturas}\\factura_{cliente.get('cliente')}.pdf"
    pdf.output(archivo_pdf)
    print(f"Factura generada: {archivo_pdf}")

    # Enviar el PDF por correo electrónico
    enviar_factura_por_email(email, archivo_pdf)

    # Abrir el PDF generado
    os.startfile(archivo_pdf)  # Esto abrirá el archivo PDF en el programa predeterminado

def enviar_factura_por_email(email, archivo_pdf):
    try:
        servidor_smtp = 'smtp.gmail.com'  # Servidor SMTP
        puerto_smtp = 587  # Puerto para TLS
        
        # Configura el mensaje
        mensaje = MIMEMultipart()
        mensaje['From'] = 'sentirsebienspa0@gmail.com'  # Cambia esto por tu dirección de correo
        mensaje['To'] = email
        mensaje['Subject'] = 'Tu factura'

        # Adjuntar el archivo PDF
        with open(archivo_pdf, 'rb') as adjunto:
            parte = MIMEBase('application', 'octet-stream')
            parte.set_payload(adjunto.read())
            encoders.encode_base64(parte)
            parte.add_header('Content-Disposition', f'attachment; filename={archivo_pdf.split("/")[-1]}')
            mensaje.attach(parte)

        # Conectar y enviar
        with smtplib.SMTP(servidor_smtp, puerto_smtp) as servidor:
            servidor.starttls()  # Iniciar TLS
            servidor.login('sentirsebienspa0@gmail.com', 'ijvu esza hgcg sbtg')  # Login
            servidor.send_message(mensaje)  # Enviar mensaje
            print("Factura enviada correctamente")
    except Exception as e:
        print(f"Ocurrió un error al enviar la factura: {e}")
        
def Pagos(page, user_data, db):
    """
    Componente Pagos que muestra una tabla con la información de los pagos 
    y permite filtrar por nombre de cliente.
    """

    # Obtener los pagos iniciales
    pagos = obtener_pagos(db)

    # Crear la tabla de pagos
    tabla_pagos = crear_tabla_pagos(pagos)

    # Checkbox para filtrar por la fecha actual
    checkbox_fecha = Checkbox(label="Filtrar por fecha actual", on_change=lambda e: actualizar_tabla_por_fecha())

    # Función para actualizar la tabla por fecha actual
    def actualizar_tabla_por_fecha():
        if checkbox_fecha.value:
            fecha_actual = datetime.now()
            mes_actual = fecha_actual.month
            dia_actual = fecha_actual.day

            # Filtrar pagos por el mes y día actual
            pagos_filtrados = [pago for pago in obtener_pagos(db) if (
                pago['fecha_turno'].month == mes_actual and pago['fecha_turno'].day == dia_actual
            )]
            tabla_pagos.rows = crear_tabla_pagos(pagos_filtrados).rows
        else:
            # Si se desmarca, mostrar todos los pagos
            tabla_pagos.rows = crear_tabla_pagos(obtener_pagos(db)).rows

        page.update()

    # Función para actualizar la tabla según el filtro
    def actualizar_tabla(e=None):
        pagos_filtrados = obtener_pagos(db)

        # Filtrar por cliente si se proporciona
        cliente_filtro = textfield_cliente.value.strip()
        if cliente_filtro:
            pagos_filtrados = [
                pago for pago in pagos_filtrados 
                if cliente_filtro.lower() in pago.get('cliente', '').lower()
            ]

        # Actualizar la tabla con los pagos filtrados
        tabla_pagos.rows = crear_tabla_pagos(pagos_filtrados).rows
        page.update()
    
    # Función para generar la factura para los pagos filtrados
    def generar_factura_filtrada(e):
        clientes_seleccionados = []
        servicios_seleccionados = []

        for idx in selecciones:
            if idx < len(pagos):  # Asegurarse de que el índice esté dentro de los límites
                pago = pagos[idx]
                clientes_seleccionados.append(pago)  # Agregar el cliente
                servicios_seleccionados.append(pago)  # Aquí puedes agregar la lógica para obtener los servicios del cliente

        # Obtener el correo electrónico del campo de texto
        email = textfield_correo.value.strip()

        if clientes_seleccionados and email:
            generar_factura(clientes_seleccionados, servicios_seleccionados, email)

    # Campo de texto para buscar por nombre de cliente
    textfield_cliente = TextField(
        label="Buscar por cliente",
        on_change=actualizar_tabla,
        color=COLOR_TEXTO,
        width=200
    )

    # Campo de texto para ingresar el correo electrónico
    textfield_correo = TextField(
        label="Correo electrónico",
        color=COLOR_TEXTO,
        width=200
    )

    # Botón para generar la factura
    boton_factura = ElevatedButton(
        text="Generar Factura",
        bgcolor=COLOR_BOTONES,
        color=colors.WHITE,
        on_click=generar_factura_filtrada,
    )

    # Llamar a la actualización inicial de la tabla
    actualizar_tabla()
    # Layout de la página
    return Container(
        content=Column(controls=[
            textfield_cliente,
            textfield_correo,  # Añadido el campo de correo electrónico
            boton_factura,
            tabla_pagos,
        ]),
        bgcolor=COLOR_FONDO,
        padding=10,
    )