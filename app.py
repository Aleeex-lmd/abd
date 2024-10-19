from flask import Flask, render_template, request, redirect, url_for
import cx_Oracle
import re

app = Flask(__name__)

# Configura la conexión con Oracle
def get_db_connection(username, password, host, port, service_name):
    dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
    connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
    return connection

# Página de inicio de sesión
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        host = '192.168.33.236'  # Cambia esto según tu configuración
        port = '1521'
        service_name = "ORCLCDB"  # Cambia a service_name si es necesario

        try:
            connection = get_db_connection(username, password, host, port, service_name)
            return redirect(url_for('tables', username=username, password=password))
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            return f"Error de conexión: {error.message}"
    
    return render_template('login.html')

# Página que muestra las tablas accesibles para el usuario autenticado
@app.route('/tables')
def tables():
    username = request.args.get('username')
    password = request.args.get('password')
    host = '192.168.33.236'
    port = '1521'
    service_name = 'ORCLCDB'

    try:
        connection = get_db_connection(username, password, host, port, service_name)
        cursor = connection.cursor()

        # Obtener las tablas accesibles
        cursor.execute("SELECT table_name FROM all_tables WHERE owner = :owner", [username.upper()])
        tables = cursor.fetchall()
        return render_template('tables.html', tables=tables, username=username, password=password)

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return f"Error al obtener las tablas: {error.message}"

# Página que muestra los registros de una tabla específica
@app.route('/table/<table_name>')
def view_table(table_name):
    username = request.args.get('username')
    password = request.args.get('password')
    host = '192.168.33.236'  # Asegúrate de que sea la IP correcta
    port = '1521'
    service_name = 'ORCLCDB'  # Cambia a service_name si es necesario

    # Validar que el nombre de la tabla solo contenga caracteres válidos
    if not re.match(r'^[a-zA-Z0-9_]+$', table_name):
        return "Nombre de tabla inválido", 400

    try:
        connection = get_db_connection(username, password, host, port, service_name)
        cursor = connection.cursor()

        # Obtener los registros de la tabla seleccionada
        cursor.execute(f"SELECT * FROM {table_name} FETCH FIRST 10 ROWS ONLY")
        records = cursor.fetchall()

        # Obtener nombres de columnas
        column_names = [desc[0] for desc in cursor.description]

        return render_template('view_table.html', records=records, columns=column_names, table_name=table_name)
    
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Error al obtener los registros: {error.message}")
        return f"Error al obtener los registros: {error.message}"
    
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
