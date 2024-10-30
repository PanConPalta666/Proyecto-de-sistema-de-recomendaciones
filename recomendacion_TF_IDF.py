import requests
import random
import math

# Configuración de la API de TMDB
api_key = '6ac0804250d9d0a9be200356343abe8e'
base_url = 'https://api.themoviedb.org/3'

# Función para obtener detalles de una película por su ID
def obtener_detalle_pelicula(movie_id):
    url = f"{base_url}/movie/{movie_id}?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: No se pudo obtener la información de la película con ID {movie_id}")
        return None

# IDs de películas para el ejemplo
peliculas_ids = [299536, 597, 603, 550, 578, 680, 157336, 155, 24428, 240]

# Simulación de datos de usuarios y películas con valoraciones
usuarios_peliculas = {}
peliculas_descripciones = {}

# Crear datos para 10 usuarios
num_usuarios = 10
num_peliculas_por_usuario = 10

for usuario_id in range(1, num_usuarios + 1):
    # Selección de películas aleatorias y generación de valoraciones
    peliculas_aleatorias = random.sample(peliculas_ids, num_peliculas_por_usuario)
    valoraciones = {}
    
    for pelicula_id in peliculas_aleatorias:
        # Obtener detalles de la película y guardar su descripción
        if pelicula_id not in peliculas_descripciones:
            detalles_pelicula = obtener_detalle_pelicula(pelicula_id)
            if detalles_pelicula:
                peliculas_descripciones[pelicula_id] = detalles_pelicula['overview']
        
        # Agregar una valoración aleatoria entre 1 y 5
        valoraciones[pelicula_id] = random.randint(1, 5)
    
    usuarios_peliculas[f'usuario{usuario_id}'] = valoraciones

# --------------------------------------------
# Sección de TF-IDF (Term Frequency - Inverse Document Frequency)
# --------------------------------------------

# Función para calcular la frecuencia de palabras en una descripción
def frecuencia_palabras(texto):
    palabras = texto.lower().split()
    frecuencias = {}
    for palabra in palabras:
        frecuencias[palabra] = frecuencias.get(palabra, 0) + 1
    return frecuencias

# Función para construir el vocabulario de todas las descripciones
def construir_vocabulario(peliculas):
    vocabulario = set()
    for descripcion in peliculas.values():
        palabras = descripcion.lower().split()
        vocabulario.update(palabras)
    return list(vocabulario)

# Calcular TF (Frecuencia de Término)
def calcular_tf(descripcion, vocabulario):
    frecuencias = frecuencia_palabras(descripcion)
    tf_vector = [frecuencias.get(palabra, 0) / len(descripcion.split()) for palabra in vocabulario]
    return tf_vector

# Calcular IDF (Frecuencia Inversa de Documento)
def calcular_idf(peliculas, vocabulario):
    num_peliculas = len(peliculas)
    idf_vector = []
    for palabra in vocabulario:
        num_peliculas_con_palabra = sum(1 for descripcion in peliculas.values() if palabra in descripcion.lower().split())
        idf = math.log(num_peliculas / (1 + num_peliculas_con_palabra))
        idf_vector.append(idf)
    return idf_vector

# Calcular TF-IDF para cada película
def calcular_tfidf(peliculas, vocabulario):
    idf_vector = calcular_idf(peliculas, vocabulario)
    tfidf_matriz = {}
    for pelicula_id, descripcion in peliculas.items():
        tf_vector = calcular_tf(descripcion, vocabulario)
        tfidf_vector = [tf * idf for tf, idf in zip(tf_vector, idf_vector)]
        tfidf_matriz[pelicula_id] = tfidf_vector
    return tfidf_matriz

# --------------------------------------------
# Fin de la sección de TF-IDF
# --------------------------------------------

# --------------------------------------------
# Sección de Modelos de Similaridad de Coseno
# --------------------------------------------

# Función para calcular el producto punto de dos vectores
def producto_punto(x, y):
    return sum(a * b for a, b in zip(x, y))

# Función para calcular la norma de un vector
def norma(v):
    return math.sqrt(sum(a * a for a in v))

# Calcular la similitud de coseno entre dos vectores
def similitud_coseno(x, y):
    return producto_punto(x, y) / (norma(x) * norma(y)) if norma(x) * norma(y) > 0 else 0

# --------------------------------------------
# Sección para construir el perfil de usuario y recomendar
# --------------------------------------------

# Crear un perfil de usuario a partir de sus valoraciones
def construir_perfil_usuario(valoraciones, tfidf_matriz):
    perfil_usuario = [0] * len(next(iter(tfidf_matriz.values())))
    for pelicula_id, calificacion in valoraciones.items():
        if pelicula_id in tfidf_matriz:
            tfidf_vector = tfidf_matriz[pelicula_id]
            perfil_usuario = [p + (calificacion * tf) for p, tf in zip(perfil_usuario, tfidf_vector)]
    return perfil_usuario

# Función para obtener el nombre de la película por ID
def obtener_nombre_pelicula(movie_id):
    detalles_pelicula = obtener_detalle_pelicula(movie_id)
    if detalles_pelicula:
        return detalles_pelicula['title']
    return "Nombre desconocido"

# Función para recomendar películas basadas en el perfil de usuario (incluye nombre y similitud)
def recomendar_peliculas_usuario(perfil_usuario, tfidf_matriz, n_recomendaciones=5):
    similitudes = []
    for pelicula_id, tfidf_vector in tfidf_matriz.items():
        similitud = similitud_coseno(perfil_usuario, tfidf_vector)
        similitudes.append((pelicula_id, similitud))
    
    # Ordenar las películas por similitud y devolver las más similares
    similitudes.sort(key=lambda x: x[1], reverse=True)
    recomendaciones = []

    for pelicula_id, similitud in similitudes[:n_recomendaciones]:
        nombre_pelicula = obtener_nombre_pelicula(pelicula_id)
        recomendaciones.append((nombre_pelicula, similitud))
    
    return recomendaciones

# Construcción del vocabulario y cálculo de TF-IDF
vocabulario = construir_vocabulario(peliculas_descripciones)
tfidf_matriz = calcular_tfidf(peliculas_descripciones, vocabulario)

# Ejemplo: construcción del perfil de un usuario y recomendación de películas
usuario_id = 'usuario1'  # Ejemplo con el primer usuario
perfil_usuario = construir_perfil_usuario(usuarios_peliculas[usuario_id], tfidf_matriz)
recomendaciones_usuario = recomendar_peliculas_usuario(perfil_usuario, tfidf_matriz)

# Mostrar el nombre y la similitud de cada película recomendada
for nombre, puntuacion in recomendaciones_usuario:
    print(f"Película: {nombre}, Puntuación de similitud: {puntuacion:.2f}")
