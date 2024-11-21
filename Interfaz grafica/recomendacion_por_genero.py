# recomendacion_por_genero.py
import requests
import math
from obtener_datos_generales import obtener_peliculas


# Configuración de la API de TMDB
api_key = '6ac0804250d9d0a9be200356343abe8e'

# Función para obtener los géneros de una película por su ID
def obtener_generos_pelicula(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        detalles = response.json()
        generos = detalles.get("genres", [])
        return [genero['name'] for genero in generos]
    else:
        print(f"Error {response.status_code}: No se pudo obtener los géneros de la película con ID {movie_id}")
        return []

# Función para calcular el producto punto de dos vectores
def producto_punto(x, y):
    return sum(a * b for a, b in zip(x, y))

# Función para calcular la norma de un vector
def norma(v):
    return math.sqrt(sum(a * a for a in v))

# Calcular la similitud de coseno entre dos vectores
def similitud_coseno(x, y):
    return producto_punto(x, y) / (norma(x) * norma(y)) if norma(x) * norma(y) > 0 else 0

# Crear un vocabulario de géneros únicos en todas las películas
def construir_vocabulario_generos(peliculas_generos):
    vocabulario_generos = set()
    for generos in peliculas_generos.values():
        vocabulario_generos.update(generos)
    return list(vocabulario_generos)

# Convertir géneros de cada película en un vector binario
def vectorizar_generos(generos_pelicula, vocabulario_generos):
    return [1 if genero in generos_pelicula else 0 for genero in vocabulario_generos]

# Crear un perfil de usuario en función de los géneros y sus valoraciones
def construir_perfil_usuario_generos(valoraciones, vocabulario_generos):
    perfil_usuario = [0] * len(vocabulario_generos)
    for datos in valoraciones:
        calificacion = datos['calificacion']
        generos_pelicula = datos['generos']
        vector_generos = vectorizar_generos(generos_pelicula, vocabulario_generos)
        perfil_usuario = [p + (calificacion * g) for p, g in zip(perfil_usuario, vector_generos)]
    return perfil_usuario

# Función para recomendar películas basadas en el perfil de géneros del usuario
def recomendar_peliculas_por_genero(perfil_usuario_generos, peliculas_generos, vocabulario_generos, n_recomendaciones=5):
    similitudes = []
    for pelicula_id, generos in peliculas_generos.items():
        vector_generos = vectorizar_generos(generos, vocabulario_generos)
        similitud = similitud_coseno(perfil_usuario_generos, vector_generos)
        similitudes.append((pelicula_id, generos, similitud))
    
    # Ordenar las películas por similitud y devolver las más similares
    similitudes.sort(key=lambda x: x[2], reverse=True)
    return similitudes[:n_recomendaciones]

# Función para construir el perfil de usuario basado en sus preferencias
def construir_perfil_usuario(usuario_preferencias):
    valoraciones = {i: {"calificacion": p["calificacion"], "generos": p["genero"]} for i, p in enumerate(usuario_preferencias)}
    vocabulario_generos = construir_vocabulario_generos({i: p["genero"] for i, p in enumerate(usuario_preferencias)})
    perfil_usuario_generos = construir_perfil_usuario_generos(valoraciones, vocabulario_generos)
    return perfil_usuario_generos, vocabulario_generos

# Obtener las películas y sus géneros
peliculas = obtener_peliculas(api_key, total_movies=40)
peliculas_generos = {i: p["genero"] for i, p in enumerate(peliculas)}

# Construcción del vocabulario de géneros
vocabulario_generos = construir_vocabulario_generos(peliculas_generos)