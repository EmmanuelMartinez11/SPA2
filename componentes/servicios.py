from flet import *

# Función para obtener los turnos basados en el rol del usuario
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
        DataColumn(Text("Cliente")),
        DataColumn(Text("Servicio")),
        DataColumn(Text("Especialidad")),
        DataColumn(Text("Fecha")),
        DataColumn(Text("Personal a cargo")),
    ]

    filas = []
    for turno in turnos:
        filas.append(
            DataRow(
                cells=[
                    DataCell(Text(turno.get('cliente', 'N/A'))),
                    DataCell(Text(turno.get('servicio', 'N/A'))),
                    DataCell(Text(turno.get('especialidad', 'N/A'))),
                    DataCell(Text(turno.get('fecha_turno', 'N/A'))),
                    DataCell(Text(turno.get('personal_a_cargo', 'N/A'))),
                ]
            )
        )
    
    return DataTable(columns=columnas, rows=filas)

# Componente Servicios
def Servicios(user_data, db):
    # Obtener los turnos basados en el rol del usuario
    turnos = obtener_turnos_por_rol(user_data, db)

    # Si no hay turnos, mostramos un mensaje
    if not turnos:
        return Column(controls=[Text("No se encontraron turnos para el rol actual.", color="black")])
    
    # Crear la tabla de turnos
    tabla_turnos = crear_tabla_turnos(turnos)
    
    return Column(
        controls=[
            Text(f"Pantalla de Servicios para {user_data['rol']}.", color="black"),
            tabla_turnos,
        ]
    )
