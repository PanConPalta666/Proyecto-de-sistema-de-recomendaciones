import requests

def obtener_peliculas(api_key, total_movies=40, language="es"):
    base_url = "https://api.themoviedb.org/3"
    base_image_url = "https://image.tmdb.org/t/p/w500"  # Base URL para las imágenes de las portadas

    # Endpoint de 'discover' para obtener una lista de películas
    url_discover = f"{base_url}/discover/movie?api_key={api_key}&language={language}"

    # Endpoint para obtener la lista de géneros de películas
    url_generos = f"{base_url}/genre/movie/list?api_key={api_key}&language={language}"

    # Obtener la lista de géneros
    response_generos = requests.get(url_generos)
    if response_generos.status_code == 200:
        generos = response_generos.json().get("genres", [])
        genero_dict = {genero["id"]: genero["name"] for genero in generos}
    else:
        print(f"Error al obtener los géneros: {response_generos.status_code}")
        genero_dict = {}

    # Configurar la cantidad deseada de películas y el límite de resultados por página
    movies_per_page = 20
    total_pages = (total_movies + movies_per_page - 1) // movies_per_page  # Calcular el número de páginas necesarias

    movie_list = []

    for page in range(1, total_pages + 1):
        response = requests.get(url_discover, params={"page": page})
        if response.status_code == 200:
            # Obtener la lista de películas para la página actual
            movies = response.json().get("results", [])
            
            for movie in movies:
                if len(movie_list) >= total_movies:
                    break  # Salir del bucle si ya se han obtenido las películas deseadas
                
                movie_id = movie.get("id")
                generos_ids = movie.get("genre_ids", [])
                generos_nombres = [genero_dict.get(genero_id, "Desconocido") for genero_id in generos_ids]
                
                # Obtener detalles adicionales de la película, incluyendo la duración y la calificación promedio
                url_movie_details = f"{base_url}/movie/{movie_id}?api_key={api_key}&language={language}"
                response_details = requests.get(url_movie_details)
                if response_details.status_code == 200:
                    movie_details_data = response_details.json()
                    duracion = movie_details_data.get("runtime")
                    portada_path = movie_details_data.get("poster_path")
                    portada_url = f"{base_image_url}{portada_path}" if portada_path else "Desconocido"
                    calificacion_promedio = movie_details_data.get("vote_average")
                else:
                    duracion = "Desconocido"
                    portada_url = "Desconocido"
                    calificacion_promedio = "Desconocido"
                    
                movie_details = {
                    "nombre": movie.get("title"),
                    "genero": generos_nombres,
                    "duracion": duracion,
                    "edad_publico": movie.get("adult"),
                    "portada": portada_url,
                    "calificacion_promedio": calificacion_promedio
                }
                movie_list.append(movie_details)
            
            # Imprimir progreso
            print(f"Página {page} procesada, total de películas obtenidas: {len(movie_list)}")
            
            if len(movie_list) >= total_movies:
                break  # Salir del bucle si ya se han obtenido las películas deseadas
        
        else:
            print(f"Error en la página {page}: {response.status_code}")
            break  # Sal del bucle en caso de error para evitar hacer demasiadas solicitudes fallidas

    return movie_list
'''
# Ejemplo de uso
if __name__ == "__main__":
    api_key = "6ac0804250d9d0a9be200356343abe8e"
    peliculas = obtener_peliculas(api_key)
    print(peliculas)
   '''