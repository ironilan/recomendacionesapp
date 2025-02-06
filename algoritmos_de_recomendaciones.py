# Importar bibliotecas necesarias
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import logging
from prettytable import PrettyTable

# Configuración inicial
CONFIG = {
    "dataset_url": "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip",
    "dataset_zip": "ml-latest-small.zip",
    "movies_file": "ml-latest-small/movies.csv",
    "ratings_file": "ml-latest-small/ratings.csv",
    "tags_file": "ml-latest-small/tags.csv",
    "default_top_n": 5,
}

# Configuración del logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Descargar y preparar el dataset MovieLens
def cargar_datos(config):
    import os
    if not os.path.exists(config["dataset_zip"]):
        logging.info("Descargando el dataset...")
        !wget -q --show-progress {config["dataset_url"]}
        !unzip -q {config["dataset_zip"]}
        logging.info("Dataset descargado y extraído.")
    else:
        logging.info("Dataset ya disponible localmente.")

    peliculas = pd.read_csv(config["movies_file"])
    calificaciones = pd.read_csv(config["ratings_file"])
    tags = pd.read_csv(config["tags_file"])

    # Renombrar columnas al español
    peliculas.rename(columns={"movieId": "id_pelicula", "title": "titulo", "genres": "generos"}, inplace=True)
    calificaciones.rename(columns={
        "userId": "id_usuario",
        "movieId": "id_pelicula",
        "rating": "calificacion",
        "timestamp": "marca_tiempo"
    }, inplace=True)
    
    tags.rename(columns={
        "userId": "id_usuario",
        "movieId": "id_pelicula",
        "tag": "etiqueta",
        "timestamp": "marca_tiempo"
    }, inplace=True)

    # Agregar calificación promedio
    promedios_calificacion = calificaciones.groupby("id_pelicula")["calificacion"].mean().reset_index()
    promedios_calificacion.rename(columns={"calificacion": "calificacion_promedio"}, inplace=True)
    promedios_calificacion["calificacion_promedio"] = promedios_calificacion["calificacion_promedio"].round(2)
    peliculas = peliculas.merge(promedios_calificacion, on="id_pelicula", how="left")

    # Agregar el número de calificaciones
    num_calificaciones = calificaciones.groupby("id_pelicula").size().reset_index(name="num_calificaciones")
    peliculas = peliculas.merge(num_calificaciones, on="id_pelicula", how="left")

    # Agregar los tags
    tags_agrupados = tags.groupby("id_pelicula")["etiqueta"].apply(lambda x: ", ".join(x)).reset_index()
    peliculas = peliculas.merge(tags_agrupados, on="id_pelicula", how="left")

    # Reemplazar valores nulos en la columna etiqueta con cadena vacía
    peliculas["etiqueta"] = peliculas["etiqueta"].fillna("")

    return peliculas, calificaciones

# Función para mostrar resultados en formato de tabla
def mostrar_tabla(titulo, datos):
    print(f"\n{titulo}")
    tabla = PrettyTable()
    tabla.field_names = ["id_pelicula", "titulo", "generos", "calificacion_promedio", "num_calificaciones", "etiqueta"]
    for _, row in datos.iterrows():
        tabla.add_row(row.tolist())
    print(tabla)

# Funciones de recomendación

# Función 1: Lo más visto
def mas_vistas(calificaciones, peliculas, n=10):
    return peliculas.sort_values(by="num_calificaciones", ascending=False).head(n)

# Función 2: Lo más recomendado
def mas_recomendadas(peliculas, n=10):
    return peliculas.sort_values(by="calificacion_promedio", ascending=False).head(n)

# Función 3: Recomendaciones basadas en contenido
def recomendaciones_contenido(titulo, peliculas, top_n=5):
    try:
        tfidf = TfidfVectorizer(stop_words="english")
        peliculas["generos"] = peliculas["generos"].fillna("")
        tfidf_matrix = tfidf.fit_transform(peliculas["generos"])
        similitud_coseno = cosine_similarity(tfidf_matrix, tfidf_matrix)

        idx = peliculas[peliculas["titulo"] == titulo].index[0]
        puntajes_similitud = list(enumerate(similitud_coseno[idx]))
        puntajes_similitud = sorted(puntajes_similitud, key=lambda x: x[1], reverse=True)
        puntajes_similitud = puntajes_similitud[1:top_n + 1]
        indices_recomendados = [i[0] for i in puntajes_similitud]
        return peliculas.iloc[indices_recomendados]
    except IndexError:
        return peliculas.iloc[0:0]  # Retorna tabla vacía si no encuentra el título

# Función 4: Recomendaciones colaborativas
def recomendaciones_colaborativas(id_usuario, calificaciones, peliculas, top_n=5):
    matriz_usuario_pelicula = calificaciones.pivot(index="id_usuario", columns="id_pelicula", values="calificacion").fillna(0)
    if id_usuario not in matriz_usuario_pelicula.index:
        return peliculas.iloc[0:0]  # Retorna tabla vacía si no encuentra el usuario
    modelo = NearestNeighbors(metric="cosine", algorithm="brute")
    modelo.fit(matriz_usuario_pelicula)

    distancias, indices = modelo.kneighbors([matriz_usuario_pelicula.loc[id_usuario]], n_neighbors=top_n + 1)
    indices_recomendados = indices.flatten()[1:]
    peliculas_recomendadas = matriz_usuario_pelicula.columns[indices_recomendados]
    return peliculas[peliculas["id_pelicula"].isin(peliculas_recomendadas)]

# Función 5: Lo que vieron los que vieron este producto
def vieron_tambien(id_pelicula, calificaciones, peliculas, top_n=5):
    usuarios = calificaciones[calificaciones["id_pelicula"] == id_pelicula]["id_usuario"].unique()
    peliculas_relacionadas = calificaciones[calificaciones["id_usuario"].isin(usuarios)]["id_pelicula"].value_counts().head(top_n + 1)
    peliculas_relacionadas = peliculas_relacionadas.index[peliculas_relacionadas.index != id_pelicula]
    return peliculas[peliculas["id_pelicula"].isin(peliculas_relacionadas)]

# Función 6: Productos sorprendentes
def productos_sorprendentes(peliculas, n=5):
    peliculas_filtradas = peliculas[peliculas["calificacion_promedio"] >= 4.0]
    if peliculas_filtradas.empty:
        return peliculas.iloc[0:0]  # Retorna tabla vacía si no hay películas con alta calificación
    return peliculas_filtradas.sample(min(n, len(peliculas_filtradas)))

# Función 7: Lo que compraron los que compraron este producto
def compraron_tambien(id_pelicula, calificaciones, peliculas, top_n=5):
    usuarios = calificaciones[calificaciones["id_pelicula"] == id_pelicula]["id_usuario"].unique()
    productos_comprados = calificaciones[calificaciones["id_usuario"].isin(usuarios)]["id_pelicula"]
    productos_comprados = productos_comprados[productos_comprados != id_pelicula].value_counts().head(top_n)
    if productos_comprados.empty:
        return peliculas.iloc[0:0]  # Retorna tabla vacía si no hay datos suficientes
    return peliculas[peliculas["id_pelicula"].isin(productos_comprados.index)]

# Cargar datos y probar el sistema
peliculas, calificaciones = cargar_datos(CONFIG)

# Ejecución de las recomendaciones
mostrar_tabla("1. Lo más visto", mas_vistas(calificaciones, peliculas, CONFIG["default_top_n"]))
mostrar_tabla("2. Lo más recomendado", mas_recomendadas(peliculas, CONFIG["default_top_n"]))
mostrar_tabla("3. Basado en contenido (similar a 'Toy Story (1995)')", recomendaciones_contenido("Toy Story (1995)", peliculas, CONFIG["default_top_n"]))
mostrar_tabla("4. Basado en colaborativo (usuario ID=1)", recomendaciones_colaborativas(1, calificaciones, peliculas, CONFIG["default_top_n"]))
mostrar_tabla("5. Lo que vieron los que vieron este producto (ID=1)", vieron_tambien(1, calificaciones, peliculas, CONFIG["default_top_n"]))
mostrar_tabla("6. Productos sorprendentes", productos_sorprendentes(peliculas, CONFIG["default_top_n"]))
mostrar_tabla("7. Lo que compraron los que compraron este producto (ID=1)", compraron_tambien(1, calificaciones, peliculas, CONFIG["default_top_n"]))