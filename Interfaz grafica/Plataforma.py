import tkinter as tk
from tkinter import messagebox
from obtener_datos_generales import obtener_peliculas
from PIL import Image, ImageTk  # Necesitarás instalar Pillow para manejar imágenes
import requests
from io import BytesIO
from recomendacion_por_genero import construir_perfil_usuario_generos, recomendar_peliculas_por_genero, peliculas_generos, vocabulario_generos

# Estructura de datos para almacenar los usuarios
usuarios = {
    "usuario1": {
        "id": 1,
        "nombre": "usuario1",
        "contrasena": "1234",
        "preferencias": [
            {"nombre": "Venom: El último baile", "genero": ["Ciencia ficción", "Acción", "Aventura"], "calificacion": 4},
            {"nombre": "Transformers One", "genero": ["Animación", "Ciencia ficción", "Aventura", "Familia"], "calificacion": 3},
            {"nombre": "Deadpool y Lobezno", "genero": ["Acción", "Comedia", "Ciencia ficción"], "calificacion": 5}
        ]
    },
    "usuario2": {
        "id": 2,
        "nombre": "usuario2",
        "contrasena": "1234",
        "preferencias": [
            {"nombre": "Terrifier 3", "genero": ["Terror", "Suspense", "Misterio"], "calificacion": 2},
            {"nombre": "La sustancia", "genero": ["Drama", "Terror", "Ciencia ficción"], "calificacion": 4},
            {"nombre": "Alien: Romulus", "genero": ["Ciencia ficción", "Terror"], "calificacion": 5}
        ]
    },
    "usuario3": {
        "id": 3,
        "nombre": "usuario3",
        "contrasena": "1234",
        "preferencias": [
            {"nombre": "Gladiator II", "genero": ["Acción", "Aventura", "Drama"], "calificacion": 1},
            {"nombre": "Red One", "genero": ["Acción", "Comedia", "Fantasía"], "calificacion": 3},
            {"nombre": "Arcadian", "genero": ["Acción", "Terror", "Suspense", "Ciencia ficción"], "calificacion": 4}
        ]
    }
}

api_key = "6ac0804250d9d0a9be200356343abe8e"
peliculas = obtener_peliculas(api_key, total_movies=40)

# Variable global para almacenar el nombre del usuario que ha iniciado sesión
usuario_actual = None

# Función para obtener los géneros de un usuario específico
def obtener_valoraciones_usuario(usuarios, nombre_usuario):
    if nombre_usuario in usuarios:
        valoraciones = []
        for pelicula in usuarios[nombre_usuario]["preferencias"]:
            valoraciones.append({
                "calificacion": pelicula["calificacion"],
                "generos": pelicula["genero"]
            })
        return valoraciones
    else:
        return f"El usuario '{nombre_usuario}' no existe."

# Función para verificar las credenciales de ingreso
def verificar_ingreso():
    global usuario_actual
    usuario = entry_usuario.get()
    contrasena = entry_contrasena.get()

    if usuario in usuarios and usuarios[usuario]["contrasena"] == contrasena:
        usuario_actual = usuario  # Guardar el nombre del usuario que ha iniciado sesión
        messagebox.showinfo("Ingreso exitoso", "¡Bienvenido!")
        ventana.destroy()
        abrir_pagina_principal()
    else:
        messagebox.showerror("Error de ingreso", "Usuario o contraseña incorrectos")

# Función para abrir la página principal
def abrir_pagina_principal():
    PaginaPrincipal = tk.Tk()
    PaginaPrincipal.title("Visualizador de Películas")
    PaginaPrincipal.geometry("1080x720")  # Tamaño de la ventana

    # Configurar el grid para que sea responsivo
    PaginaPrincipal.columnconfigure(0, weight=1)
    PaginaPrincipal.rowconfigure(0, weight=1)
    PaginaPrincipal.rowconfigure(1, weight=1)
    PaginaPrincipal.rowconfigure(2, weight=1)

    # Título de la sección
    titulo = tk.Label(PaginaPrincipal, text="Películas", font=("Arial", 24))
    titulo.grid(row=0, column=0, pady=10, sticky="n")

    # Crear un canvas para el scrollbar
    canvas = tk.Canvas(PaginaPrincipal, bg="white")
    canvas.grid(row=1, column=0, sticky="nsew")

    # Crear un scrollbar vertical
    scrollbar_vertical = tk.Scrollbar(PaginaPrincipal, orient="vertical", command=canvas.yview)
    scrollbar_vertical.grid(row=1, column=1, sticky="ns")

    # Crear un scrollbar horizontal
    scrollbar_horizontal = tk.Scrollbar(PaginaPrincipal, orient="horizontal", command=canvas.xview)
    scrollbar_horizontal.grid(row=2, column=0, sticky="ew")

    # Configurar el canvas para usar los scrollbars
    canvas.configure(yscrollcommand=scrollbar_vertical.set, xscrollcommand=scrollbar_horizontal.set)

    # Crear un frame dentro del canvas para el contenido general
    frame_contenedor = tk.Frame(canvas, bg="white")
    canvas.create_window((0, 0), window=frame_contenedor, anchor="nw")

    # Función para actualizar la región desplazable del canvas
    def actualizar_scrollregion(event=None):
        canvas.config(scrollregion=canvas.bbox("all"))

    # Conectar el evento <Configure> al frame interno
    frame_contenedor.bind("<Configure>", actualizar_scrollregion)

    # Frame para las primeras películas
    frame_peliculas = tk.Frame(frame_contenedor, bg="white")
    frame_peliculas.grid(row=0, column=0, pady=20, padx=10, sticky="nsew")

    # Mostrar las primeras películas
    for i, pelicula in enumerate(peliculas[:20]):  # Mostrar las primeras 20 películas
        # Cargar la imagen de la portada desde la URL
        response = requests.get(pelicula['portada'])
        imagen = Image.open(BytesIO(response.content))
        imagen = imagen.resize((100, 150), Image.Resampling.LANCZOS)
        imagen_tk = ImageTk.PhotoImage(imagen)

        # Crear un label para la imagen
        label_imagen = tk.Label(frame_peliculas, image=imagen_tk, bg="white")
        label_imagen.image = imagen_tk
        label_imagen.grid(row=0, column=i, padx=10, pady=10, sticky="n")

        # Crear un label para el nombre de la película
        label_nombre = tk.Label(frame_peliculas, text=pelicula['nombre'], bg="white")
        label_nombre.grid(row=1, column=i, padx=10, pady=10, sticky="n")

    # Frame para películas recomendadas
    frame_recomendadas = tk.Frame(frame_contenedor, bg="white")
    frame_recomendadas.grid(row=1, column=0, pady=20, padx=10, sticky="nsew")

    # Configurar el grid del frame para asegurar un buen diseño
    frame_recomendadas.columnconfigure(0, weight=1)

    # Título para el segundo frame
    titulo_recomendadas = tk.Label(frame_recomendadas, text="Recomendadas", font=("Arial", 18), bg="white")
    titulo_recomendadas.grid(row=0, column=0, pady=10, sticky="n", columnspan=5)  # Ocupa toda la fila con columnspan

    # Construir el perfil del usuario y recomendar películas
    valoraciones_usuario = obtener_valoraciones_usuario(usuarios, usuario_actual)
    perfil_usuario_generos = construir_perfil_usuario_generos(valoraciones_usuario, vocabulario_generos)
    recomendaciones = recomendar_peliculas_por_genero(perfil_usuario_generos, peliculas_generos, vocabulario_generos, n_recomendaciones=20)

    # Mostrar películas recomendadas basadas en cálculos
    for i, (pelicula_id, generos, similitud) in enumerate(recomendaciones):
        pelicula = peliculas[pelicula_id]
        # Cargar la imagen de la portada desde la URL
        response = requests.get(pelicula['portada'])
        imagen = Image.open(BytesIO(response.content))
        imagen = imagen.resize((100, 150), Image.Resampling.LANCZOS)
        imagen_tk = ImageTk.PhotoImage(imagen)

        # Crear un label para la imagen
        label_imagen = tk.Label(frame_recomendadas, image=imagen_tk, bg="white")
        label_imagen.image = imagen_tk
        label_imagen.grid(row=i // 5 * 2, column=i % 5, padx=10, pady=10, sticky="n")  # Igual disposición que el frame_peliculas

        # Crear un label para el nombre de la película
        label_nombre = tk.Label(frame_recomendadas, text=pelicula['nombre'], bg="white")
        label_nombre.grid(row=i // 5 * 2 + 1, column=i % 5, padx=10, pady=10, sticky="n")  # Igual disposición que el frame_peliculas

    # Actualizar el scrollregion después de añadir todos los elementos
    frame_contenedor.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    PaginaPrincipal.mainloop()

# Crear la ventana de inicio de sesión
ventana = tk.Tk()
ventana.title("Inicio de Sesión")
ventana.geometry("300x200")

# Etiqueta y campo de entrada para el nombre de usuario
label_usuario = tk.Label(ventana, text="Usuario:")
label_usuario.pack(pady=5)
entry_usuario = tk.Entry(ventana)
entry_usuario.pack(pady=5)

# Etiqueta y campo de entrada para la contraseña
label_contrasena = tk.Label(ventana, text="Contraseña:")
label_contrasena.pack(pady=5)
entry_contrasena = tk.Entry(ventana, show="*")
entry_contrasena.pack(pady=5)

# Botón para iniciar sesión
boton_ingresar = tk.Button(ventana, text="Ingresar", command=verificar_ingreso)
boton_ingresar.pack(pady=20)

# Iniciar el bucle principal de Tkinter
ventana.mainloop()