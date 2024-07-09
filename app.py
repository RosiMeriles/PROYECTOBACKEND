# app = Flask(__name__, template_folder='src/templates', static_folder='src/static')

#--------------------------------------------------------------------
# Instalar con pip install Flask
from flask import Flask, request, jsonify, render_template
from flask import request

# Instalar con pip install flask-cors
from flask_cors import CORS

# Instalar con pip install mysql-connector-python
import mysql.connector

# Si es necesario, pip install Werkzeug
from werkzeug.utils import secure_filename

# No es necesario instalar, es parte del sistema standard de Python
import os
import time
#--------------------------------------------------------------------



app = Flask(__name__)
CORS(app)  # Esto habilitará CORS para todas las rutas

#--------------------------------------------------------------------
class Catalogo:
    #----------------------------------------------------------------
    # Constructor de la clase
    def __init__(self, host, user, password, database):
        # Primero, establecemos una conexión sin especificar la base de datos
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()


        # Intentamos seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

        # Una vez que la base de datos está establecida, creamos la tabla si no existe
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS peliculas (
            codigo INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(30) NOT NULL,
            genero VARCHAR (30) NOT NULL,
            puntuacion INT(10) NOT NULL,
            fecha de estreno DATE (255),
            cantidad de veces vista INT(5))''')
        self.conn.commit()

        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)
        
    #----------------------------------------------------------------
    def agregar_pelicula(self, titulo, genero, puntuacion, date, cantidadVeces):
               
        sql = """INSERT INTO pelicula (titulo, genero, puntuacion, fecha de estreno, cantidad de veces vista)
          VALUES (%s, %s, %s, %s, %s)"""
        valores = (titulo, genero, puntuacion, date, cantidadVeces)

        self.cursor.execute(sql, valores)   
        self.conn.commit()
        return self.cursor.lastrowid

    #----------------------------------------------------------------
    def consultar_pelicula(self, codigo):
        # Consultamos una película a partir de su código
        self.cursor.execute(f"SELECT * FROM peliculas WHERE codigo = {codigo}")
        return self.cursor.fetchone() #Me da el diccionario o None si no existe

    #----------------------------------------------------------------
    def modificar_pelicula(self, codigo, nuevo_titulo, nuevo_genero, nueva_puntuacion, nueva_date, nueva_cantidadVeces):
        sql = "UPDATE peliculas SET titulo = %s, genero = %s, puntuacion = %s, date = %s, cantidadVeces = %s WHERE codigo = %s"
        valores = (nuevo_titulo, nuevo_genero, nueva_puntuacion, nueva_date, nueva_cantidadVeces, codigo)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    #----------------------------------------------------------------
    def listar_pelicula(self):
        self.cursor.execute("SELECT * FROM peliculas")
        peliculas = self.cursor.fetchall()
        return peliculas

    #----------------------------------------------------------------
    def eliminar_pelicula(self, codigo):
        # Eliminamos una película de la tabla a partir de su código
        self.cursor.execute(f"DELETE FROM peliculas WHERE codigo = {codigo}")
        self.conn.commit()
        return self.cursor.rowcount > 0

    #----------------------------------------------------------------
    def mostrar_pelicula(self, codigo):
        # Mostramos los datos de una película a partir de su código
        pelicula = self.consultar_pelicula(codigo)
        if pelicula:
            print("-" * 40)
            print(f"Código.....: {pelicula['codigo']}")
            print(f"Titulo: {pelicula['titulo']}")
            print(f"Genero...: {pelicula['genero']}")
            print(f"Puntuacion.....: {pelicula['puntuacion']}")
            print(f"Fecha de estreno.....: {pelicula['date']}")
            print(f"CantidadVeces vista..: {pelicula['cantidadVeces']}")
            print("-" * 40)
        else:
            print("Pelicula no encontrada.")


#--------------------------------------------------------------------
# Cuerpo del programa
#--------------------------------------------------------------------
# Crear una instancia de la clase Catalogo
catalogo = Catalogo(host='localhost', user='root', password='', database='miapp')
#catalogo = Catalogo(host='USUARIO.mysql.pythonanywhere-services.com', user='USUARIO', password='CLAVE', database='USUARIO$miapp')


# Carpeta para guardar las imagenes.
RUTA_DESTINO = 'static/imagenes/'

#Al subir al servidor, deberá utilizarse la siguiente ruta. USUARIO debe ser reemplazado por el nombre de usuario de Pythonanywhere
#RUTA_DESTINO = '/home/USUARIO/mysite/static/imagenes'


#--------------------------------------------------------------------
# Listar todas las películas
#--------------------------------------------------------------------
#La ruta Flask /películas con el método HTTP GET está diseñada para proporcionar los detalles de todos los productos almacenados en la base de datos.
#El método devuelve una lista con todos las películas en formato JSON.
@app.route("/peliculas", methods=["GET"])
def listar_pelicula():
    peliculas = catalogo.listar_pelicula()
    return jsonify(peliculas)


#--------------------------------------------------------------------
# Mostrar una sola película según su código
#--------------------------------------------------------------------
#La ruta Flask /productos/<int:codigo> con el método HTTP GET está diseñada para proporcionar los detalles de un producto específico basado en su código.
#El método busca en la base de datos el producto con el código especificado y devuelve un JSON con los detalles del producto si lo encuentra, o None si no lo encuentra.
@app.route("/peliculas/<int:codigo>", methods=["GET"])
def mostrar_pelicula(codigo):
    pelicula = catalogo.consultar_pelicula(codigo)
    if pelicula:
        return jsonify(pelicula), 201
    else:
        return "Pelicula no encontrada", 404


#--------------------------------------------------------------------
# Agregar una película
#--------------------------------------------------------------------
@app.route("/peliculas", methods=["POST"])
#La ruta Flask `/peliculas` con el método HTTP POST está diseñada para permitir la adición de una nueva película a la base de datos.
#La función agregar_pelicula se asocia con esta URL y es llamada cuando se hace una solicitud POST a /peliculas.
def agregar_pelicula():
    #Recojo los datos del form
    titulo = request.form['titulo']
    genero = request.form['genero']
    puntuacion = request.form['puntuacion']
    date = request.files['date']
    cantidadVeces = request.form['cantidadVeces']
    # nombre_imagen=""

    
    # Genero el nombre de la imagen
    # nombre_imagen = secure_filename(imagen.filename) #Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
    # nombre_base, extension = os.path.splitext(nombre_imagen) #Separa el nombre del archivo de su extensión.
    # nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" #Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.

    # nuevo_codigo = catalogo.agregar_producto(titulo, genero, puntuacion, date, cantidadVeces)
    # if nuevo_codigo:    
    #     imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
    #     print("Se guardo!")
    #     #Si el producto se agrega con éxito, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 201 (Creado).
    #     return jsonify({"mensaje": "Producto agregado correctamente.", "codigo": nuevo_codigo, "imagen": nombre_imagen}), 201
    # else:
    #     #Si el producto no se puede agregar, se devuelve una respuesta JSON con un mensaje de error y un código de estado HTTP 500 (Internal Server Error).
    #     return jsonify({"mensaje": "Error al agregar la pelicula."}), 500
    

#--------------------------------------------------------------------
# Modificar una película según su código
#--------------------------------------------------------------------
@app.route("/peliculas/<int:codigo>", methods=["PUT"])
#La ruta Flask /peliculas/<int:codigo> con el método HTTP PUT está diseñada para actualizar la información de una película existente en la base de datos, identificado por su código.
#La función modificar_producto se asocia con esta URL y es invocada cuando se realiza una solicitud PUT a /películas/ seguido de un número (el código de la película).
def modificar_pelicula(codigo):
    #Se recuperan los nuevos datos del formulario
    nuevo_titulo = request.form.get("titulo")
    nuevo_genero = request.form.get("genero")
    nueva_puntuacion = request.form.get("puntuacion")
    nueva_date = request.form.get("date")
    nueva_cantidadVeces = request.form.get("cantidadVeces")
    
    # Verifica si se proporcionó una nueva imagen
    # if 'imagen' in request.files:
    #     imagen = request.files['imagen']
    #     # Procesamiento de la imagen
    #     nombre_imagen = secure_filename(imagen.filename) #Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
    #     nombre_base, extension = os.path.splitext(nombre_imagen) #Separa el nombre del archivo de su extensión.
    #     nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" #Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.

    #     # Guardar la imagen en el servidor
    #     imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
        
    #     # Busco la película guardada
    #     pelicula = catalogo.consultar_pelicula(codigo)
    #     if pelicula: # Si existe la película...
    #         imagen_vieja = pelicula["imagen_url"]
    #         # Armo la ruta a la imagen
    #         ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

    #         # Y si existe la borro.
    #         if os.path.exists(ruta_imagen):
    #             os.remove(ruta_imagen)
    
    # else:
    #     # Si no se proporciona una nueva imagen, simplemente usa la imagen existente del producto
    #     pelicula = catalogo.consultar_pelicula(codigo)
    #       if producto:
    #       nombre_imagen = producto["imagen_url"]


    # Se llama al método modificar_pelicula pasando el codigo de la película y los nuevos datos.
    if catalogo.modificar_pelicula(codigo, nuevo_titulo, nuevo_genero, nueva_puntuacion, nueva_date, nueva_cantidadVeces):
        
        #Si la actualización es exitosa, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
        return jsonify({"mensaje": "Pelicula modificada"}), 200
    else:
        #Si la película no se encuentra (por ejemplo, si no hay ninguna película con el código dado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado).
        return jsonify({"mensaje": "Pelicula no encontrada"}), 404



#--------------------------------------------------------------------
# Eliminar una película según su código
#--------------------------------------------------------------------
@app.route("/peliculas/<int:codigo>", methods=["DELETE"])
#La ruta Flask /pelicula/<int:codigo> con el método HTTP DELETE está diseñada para eliminar una película específica de la base de datos, utilizando su código como identificador.
#La función eliminar_pelicula se asocia con esta URL y es llamada cuando se realiza una solicitud DELETE a /peliculas/ seguido de un número (el código del producto).
def eliminar_pelicula(codigo):
    # Busco el producto en la base de datos
    pelicula = catalogo.consultar_pelicula(codigo)
    if pelicula: # Si la película existe, verifica si hay una imagen asociada en el servidor.
        imagen_vieja = pelicula["imagen_url"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

        # Y si existe, la elimina del sistema de archivos.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

        # Luego, elimina la película del catálogo
        if catalogo.eliminar_pelicula(codigo):
            #Si la película se elimina correctamente, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
            return jsonify({"mensaje": "Pelicula eliminada"}), 200
        else:
            #Si ocurre un error durante la eliminación (por ejemplo, si la película no se puede eliminar de la base de datos por alguna razón), se devuelve un mensaje de error con un código de estado HTTP 500 (Error Interno del Servidor).
            return jsonify({"mensaje": "Error al eliminar la pelicula"}), 500
    else:
        #Si la película no se encuentra (por ejemplo, si no existe una película con el codigo proporcionado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado). 
        return jsonify({"mensaje": "Pelicula no encontrada"}), 404

#--------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)