from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)  

class Catalogo:

    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS peliculas (
            codigo INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(30) NOT NULL,
            genero VARCHAR(30) NOT NULL,
            puntuacion INT NOT NULL,
            fecha_estreno DATE,
            cantidad_veces_vista INT)''')
        self.conn.commit()

        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

    def agregar_pelicula(self, titulo, genero, puntuacion, fecha_estreno, cantidad_veces_vista):
        sql = """INSERT INTO peliculas (titulo, genero, puntuacion, fecha_estreno, cantidad_veces_vista)
                 VALUES (%s, %s, %s, %s, %s)"""
        valores = (titulo, genero, puntuacion, fecha_estreno, cantidad_veces_vista)
        self.cursor.execute(sql, valores)        
        self.conn.commit()
        return self.cursor.lastrowid

    def consultar_pelicula(self, codigo):
        self.cursor.execute("SELECT * FROM peliculas WHERE codigo = %s", (codigo,))
        return self.cursor.fetchone()

    def modificar_peliculas(self, codigo, nuevo_titulo, nuevo_genero, nueva_puntuacion, nueva_fecha_estreno, nueva_cantidad_veces_vista):
        sql = """UPDATE peliculas SET titulo = %s, genero = %s, puntuacion = %s, fecha_estreno = %s, cantidad_veces_vista = %s 
                 WHERE codigo = %s"""
        valores = (nuevo_titulo, nuevo_genero, nueva_puntuacion, nueva_fecha_estreno, nueva_cantidad_veces_vista, codigo)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def listar_peliculas(self):
        self.cursor.execute("SELECT * FROM peliculas")
        return self.cursor.fetchall()

    def eliminar_pelicula(self, codigo):
        self.cursor.execute("DELETE FROM peliculas WHERE codigo = %s", (codigo,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def mostrar_pelicula(self, codigo):
        pelicula = self.consultar_pelicula(codigo)
        if pelicula:
            print("-" * 40)
            print(f"Código.....: {pelicula['codigo']}")
            print(f"Titulo: {pelicula['titulo']}")
            print(f"Genero...: {pelicula['genero']}")
            print(f"Puntuacion.....: {pelicula['puntuacion']}")
            print(f"Fecha de estreno.....: {pelicula['fecha_estreno']}")
            print(f"CantidadVeces vista..: {pelicula['cantidad_veces_vista']}")
            print("-" * 40)
        else:
            print("Pelicula no encontrada.")

catalogo = Catalogo(host='localhost', user='root', password='', database='miapp')

@app.route("/peliculas", methods=["GET"])
def listar_peliculas():
    peliculas = catalogo.listar_peliculas()
    return jsonify(peliculas)

@app.route("/peliculas/<int:codigo>", methods=["GET"])
def mostrar_pelicula(codigo):
    pelicula = catalogo.consultar_pelicula(codigo)
    if pelicula:
        return jsonify(pelicula), 200
    else:
        return "Pelicula no encontrada", 404

@app.route("/peliculas", methods=["POST"])
def agregar_pelicula():
    try:
        titulo = request.form['titulo']
        genero = request.form['genero']
        puntuacion = int(request.form['puntuacion'])
        fecha_estreno = request.form.get('date')  # Optional, puede ser None
        cantidad_veces_vista = int(request.form.get('cantidadVeces', 0))  # Optional, default to 0
        codigo = catalogo.agregar_pelicula(titulo, genero, puntuacion, fecha_estreno, cantidad_veces_vista)
        return jsonify({"mensaje": "Película agregada correctamente", "codigo": codigo}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"mensaje": "Error al agregar la película"}), 500

@app.route("/peliculas/<int:codigo>", methods=["PUT"])
def modificar_pelicula(codigo):
    nuevo_titulo = request.form.get("titulo")
    nuevo_genero = request.form.get("genero")
    nueva_puntuacion = request.form.get("puntuacion")
    nueva_fecha_estreno = request.form.get("date")
    nueva_cantidad_veces_vista = request.form.get("cantidadVeces")
    if catalogo.modificar_peliculas(codigo, nuevo_titulo, nuevo_genero, nueva_puntuacion, nueva_fecha_estreno, nueva_cantidad_veces_vista):
        return jsonify({"mensaje": "Película modificada"}), 200
    else:
        return jsonify({"mensaje": "Película no encontrada"}), 404

@app.route("/peliculas/<int:codigo>", methods=["DELETE"])
def eliminar_pelicula(codigo):
    if catalogo.eliminar_pelicula(codigo):
        return jsonify({"mensaje": "Película eliminada"}), 200
    else:
        return jsonify({"mensaje": "Película no encontrada"}), 404

if __name__ == "__main__":
    app.run(debug=True)
