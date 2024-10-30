import requests
import random
import math

# Configuración de la API de TMDB
api_key = '6ac0804250d9d0a9be200356343abe8e'
base_url = 'https://api.themoviedb.org/3'

# Función para obtener los actores principales de una película por su ID
def obtener_actores_pelicula(movie_id):
    url = f"{base_url}/movie/{movie_id}/credits?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        creditos = response.json()
        actores = [cast['name'] for cast in creditos.get("cast", [])][:5]  # Limita a los primeros 5 actores
        return actores
    else:
        print(f"Error {response.status_code}: No se pudo obtener los actores de la película con ID {movie_id}")
        return []

# IDs de películas para el ejemplo
peliculas_ids = [299536, 597, 603, 550, 578, 680, 157336, 155, 24428, 240]

# Simulación de datos de usuarios y películas con valoraciones
usuarios_peliculas = {}
peliculas_actores = {}

# Crear datos para 10 usuarios con puntuaciones y actores
num_usuarios = 10
num_peliculas_por_usuario = 10

for usuario_id in range(1, num_usuarios + 1):
    peliculas_aleatorias = random.sample(peliculas_ids, num_peliculas_por_usuario)
    valoraciones = {}
    
    for pelicula_id in peliculas_aleatorias:
        if pelicula_id not in peliculas_actores:
            peliculas_actores[pelicula_id] = obtener_actores_pelicula(pelicula_id)
        
        # Generar una valoración aleatoria entre 1 y 5
        valoraciones[pelicula_id] = {
            'calificacion': random.randint(1, 5),
            'actores': peliculas_actores[pelicula_id]
        }
    
    usuarios_peliculas[f'usuario{usuario_id}'] = valoraciones

# Función para calcular el producto punto de dos vectores
def producto_punto(x, y):
    return sum(a * b for a, b in zip(x, y))

# Función para calcular la norma de un vector
def norma(v):
    return math.sqrt(sum(a * a for a in v))

# Calcular la similitud de coseno entre dos vectores
def similitud_coseno(x, y):
    return producto_punto(x, y) / (norma(x) * norma(y)) if norma(x) * norma(y) > 0 else 0

# Crear un vocabulario de actores únicos en todas las películas
def construir_vocabulario_actores(peliculas_actores):
    vocabulario_actores = set()
    for actores in peliculas_actores.values():
        vocabulario_actores.update(actores)
    return list(vocabulario_actores)

# Convertir actores de cada película en un vector binario
def vectorizar_actores(actores_pelicula, vocabulario_actores):
    return [1 if actor in actores_pelicula else 0 for actor in vocabulario_actores]

# Crear un perfil de usuario en función de los actores y sus valoraciones
def construir_perfil_usuario_actores(valoraciones, vocabulario_actores):
    perfil_usuario = [0] * len(vocabulario_actores)
    for pelicula_id, datos in valoraciones.items():
        calificacion = datos['calificacion']
        actores_pelicula = datos['actores']
        vector_actores = vectorizar_actores(actores_pelicula, vocabulario_actores)
        perfil_usuario = [p + (calificacion * a) for p, a in zip(perfil_usuario, vector_actores)]
    return perfil_usuario

# Función para recomendar películas basadas en el perfil de actores del usuario
def recomendar_peliculas_por_actores(perfil_usuario_actores, peliculas_actores, vocabulario_actores, n_recomendaciones=5):
    similitudes = []
    for pelicula_id, actores in peliculas_actores.items():
        vector_actores = vectorizar_actores(actores, vocabulario_actores)
        similitud = similitud_coseno(perfil_usuario_actores, vector_actores)
        similitudes.append((pelicula_id, actores, similitud))
    
    # Ordenar las películas por similitud y devolver las más similares
    similitudes.sort(key=lambda x: x[2], reverse=True)
    return similitudes[:n_recomendaciones]

# Construcción del vocabulario de actores y el perfil de usuario en función de actores
vocabulario_actores = construir_vocabulario_actores(peliculas_actores)

# Ejemplo: construir el perfil de actores de un usuario y recomendar películas
usuario_id = 'usuario1'  # Ejemplo con el primer usuario
perfil_usuario_actores = construir_perfil_usuario_actores(usuarios_peliculas[usuario_id], vocabulario_actores)
recomendaciones_por_actores = recomendar_peliculas_por_actores(perfil_usuario_actores, peliculas_actores, vocabulario_actores)

# Imprimir recomendaciones con actores
print(f"Recomendaciones por actores para {usuario_id}:")
for pelicula_id, actores, similitud in recomendaciones_por_actores:
    print(f"Película ID: {pelicula_id}, Actores: {actores}, Similitud: {similitud:.2f}")
