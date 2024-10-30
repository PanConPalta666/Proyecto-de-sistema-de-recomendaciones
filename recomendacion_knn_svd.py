import requests
import random
import math
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.sparse.linalg import svds

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

# IDs de películas simuladas para el ejemplo
peliculas_ids = [299536, 597, 603, 550, 578, 680, 157336, 155, 24428, 240]

# Simulación de usuarios y valoraciones
num_usuarios = 15
num_peliculas = len(peliculas_ids)

# Generamos un diccionario de valoraciones aleatorias para algunos usuarios (historial)
usuarios_con_historial = {}
usuarios_sin_historial = {}
peliculas_descripciones = {}

# Crear valoraciones para usuarios con historial y cargar descripciones de películas
for usuario_id in range(1, num_usuarios + 1):
    if random.choice([True, False]):  # Aleatoriamente asignamos usuarios con o sin historial
        valoraciones = {pelicula_id: random.randint(1, 5) for pelicula_id in random.sample(peliculas_ids, k=random.randint(1, num_peliculas))}
        usuarios_con_historial[f'usuario{usuario_id}'] = valoraciones
        
        # Obtener detalles de películas y guardar descripción
        for pelicula_id in valoraciones:
            if pelicula_id not in peliculas_descripciones:
                detalles = obtener_detalle_pelicula(pelicula_id)
                if detalles:
                    peliculas_descripciones[pelicula_id] = detalles.get('overview', "")
    else:
        usuarios_sin_historial[f'usuario{usuario_id}'] = {}

print("Usuarios con historial:", usuarios_con_historial)
print("Usuarios sin historial:", usuarios_sin_historial)

# Construir matriz de valoraciones
usuario_ids = list(usuarios_con_historial.keys())
pelicula_indices = {pelicula_id: idx for idx, pelicula_id in enumerate(peliculas_ids)}
valoraciones_matriz = np.zeros((len(usuario_ids), len(peliculas_ids)))

for i, usuario_id in enumerate(usuario_ids):
    valoraciones = usuarios_con_historial[usuario_id]
    for pelicula_id, rating in valoraciones.items():
        if pelicula_id in pelicula_indices:
            valoraciones_matriz[i, pelicula_indices[pelicula_id]] = rating

# Cálculo de SVD para obtener características latentes
U, sigma, Vt = svds(valoraciones_matriz, k=3)
sigma = np.diag(sigma)
# Reconstruimos la matriz aproximada
valoraciones_reconstruidas = np.dot(np.dot(U, sigma), Vt)

# Recomendación para usuarios con historial usando SVD
def recomendar_por_svd(usuario_id, usuarios_con_historial, usuario_ids, valoraciones_reconstruidas, num_recomendaciones=2):
    if usuario_id not in usuario_ids:
        print("Usuario no tiene historial. Intenta con k-NN.")
        return []

    idx = usuario_ids.index(usuario_id)
    predicciones_usuario = valoraciones_reconstruidas[idx]
    
    # Ordenar películas por la predicción de valoraciones en orden descendente
    peliculas_no_vistas = [peliculas_ids[i] for i in range(len(predicciones_usuario)) if usuarios_con_historial[usuario_id].get(peliculas_ids[i]) is None]
    predicciones_no_vistas = [(peliculas_ids[i], predicciones_usuario[i]) for i in range(len(predicciones_usuario)) if peliculas_ids[i] in peliculas_no_vistas]

    # Ordenamos y retornamos las más recomendadas
    predicciones_no_vistas.sort(key=lambda x: x[1], reverse=True)
    recomendaciones = [pelicula_id for pelicula_id, _ in predicciones_no_vistas[:num_recomendaciones]]
    return recomendaciones

# Ejemplo: Recomendaciones para un usuario con historial
usuario_ejemplo = usuario_ids[0]
recomendaciones_svd = recomendar_por_svd(usuario_ejemplo, usuarios_con_historial, usuario_ids, valoraciones_reconstruidas)
print(f"Recomendaciones por SVD para {usuario_ejemplo}: {recomendaciones_svd}")

# Utilizamos k-NN para obtener recomendaciones para usuarios sin historial
knn_modelo = NearestNeighbors(metric='cosine', algorithm='auto')
knn_modelo.fit(valoraciones_matriz)

def recomendar_por_knn(usuario_sin_historial, k=3):
    # Escogemos las películas con mayor valoración promedio entre los k vecinos más cercanos
    distancias, indices = knn_modelo.kneighbors(valoraciones_matriz[:len(usuario_ids)], n_neighbors=k)
    peliculas_recomendadas = {}

    for vecino_id in indices[0]:
        for pelicula_id, rating in usuarios_con_historial[usuario_ids[vecino_id]].items():
            peliculas_recomendadas[pelicula_id] = peliculas_recomendadas.get(pelicula_id, 0) + rating

    # Ordenar y recomendar películas con mejor valoración
    recomendaciones = sorted(peliculas_recomendadas, key=peliculas_recomendadas.get, reverse=True)[:3]
    return recomendaciones

# Ejemplo: Recomendaciones para un usuario sin historial
usuario_nuevo = list(usuarios_sin_historial.keys())[0]
recomendaciones_knn = recomendar_por_knn(usuario_nuevo)
print(f"Recomendaciones por k-NN para {usuario_nuevo}: {recomendaciones_knn}")

# Función General de Recomendación
def recomendar_peliculas(usuario_id):
    if usuario_id in usuarios_con_historial:
        # Usuario con historial - usamos SVD
        return recomendar_por_svd(usuario_id, usuarios_con_historial, usuario_ids, valoraciones_reconstruidas)
    elif usuario_id in usuarios_sin_historial:
        # Usuario sin historial - usamos k-NN
        return recomendar_por_knn(usuario_id)
    else:
        return []

# Ejemplo: Recomendación para cualquier tipo de usuario
print("Recomendación para un usuario con historial:", recomendar_peliculas(usuario_ids[0]))
print("Recomendación para un usuario sin historial:", recomendar_peliculas(list(usuarios_sin_historial.keys())[0]))
