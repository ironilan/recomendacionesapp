from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Dict, Any
from database import conectar
from sqlalchemy import and_, func, select
import pandas as pd
from models import *
from esquemas import *
from utilidades import *
import hashlib
#jwt
from jose import JWTError, jwt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time


api = APIRouter()

##metodo para que el usuario se loguee
@api.post("/login", tags=['Autenticacion'],  response_model=JwtEsquema,status_code=status.HTTP_200_OK)
async def login_user(model:LoginEsquema):
    try:
        datos = conectar.execute(usuarios_model.select().where(and_(
            usuarios_model.c.correo==model.correo,
            usuarios_model.c.password==hashlib.sha512(model.password.encode('utf8')).hexdigest()
        ))).first()
        
        token = jwt.encode({'id': datos.id, 'nombre': datos.nombre, 'iat': int(time.time())}, "123456", algorithm="HS512")
        ##print(token)
        return {"token": token, "nombre": datos.nombre, "id": datos.id}
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Las credenciales no son validas")



def recomendaciones_contenido(titulo: str, peliculas: pd.DataFrame, top_n: int = 5):
    """
    Devuelve recomendaciones de películas basadas en la similitud de contenido.
    
    :param titulo: Título de la película para la cual se desean recomendaciones.
    :param peliculas: DataFrame que contiene las películas con columnas 'nombre' y 'descripcion'.
    :param top_n: Número de recomendaciones a devolver.
    :return: DataFrame con las películas recomendadas.
    """
    try:
        # Verifica si el título existe en el DataFrame
        if titulo not in peliculas["nombre"].values:
            return pd.DataFrame()  # Retorna un DataFrame vacío si el título no existe

        # Preprocesamiento de texto
        tfidf = TfidfVectorizer(stop_words="english")
        peliculas["descripcion"] = peliculas["descripcion"].fillna("")
        tfidf_matrix = tfidf.fit_transform(peliculas["descripcion"])

        # Cálculo de similitud coseno
        similitud_coseno = cosine_similarity(tfidf_matrix, tfidf_matrix)

        # Obtener el índice de la película con el título dado
        idx = peliculas[peliculas["nombre"] == titulo].index[0]

        # Obtener las películas más similares
        puntajes_similitud = list(enumerate(similitud_coseno[idx]))
        puntajes_similitud = sorted(puntajes_similitud, key=lambda x: x[1], reverse=True)
        puntajes_similitud = puntajes_similitud[1:top_n + 1]  # Excluir la película misma
        indices_recomendados = [i[0] for i in puntajes_similitud]

        return peliculas.iloc[indices_recomendados]
    except Exception as e:
        print(f"Error en recomendaciones_contenido: {e}")
        return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error



@api.get("/generos", tags=['Géneros'],response_model=List[GeneroEsquema], status_code=status.HTTP_200_OK)
async def generos():
    return conectar.execute(generos_model.select().order_by(generos_model.c.id.desc())).fetchall()


@api.post("/generos", tags=['Géneros'],response_model=ResponseEsquema, status_code=status.HTTP_201_CREATED)
async def categorias_post(model:GeneroEsquema):
    try:
        conectar.execute(generos_model.insert().values({
            "nombre": model.nombre
        }))
        conectar.commit()
        
        return {"mensaje": "se ha creado correctamente"}
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ocurrio un error")



@api.get("/peliculas", tags=['peliculas'], response_model=PaginacionResponse, status_code=status.HTTP_200_OK)
async def peliculas(page: int = 1, limit: int = 10, username: str = Depends(verificar_token)):
    # Calcular el offset (desplazamiento) basado en la página solicitada y el límite
    offset = (page - 1) * limit

    # Consultar los datos paginados directamente desde la base de datos
    query = select(peliculas_model).limit(limit).offset(offset)
    result = conectar.execute(query).fetchall()

    # Consultar el total de registros (sin paginación)
    count_query = select(func.count()).select_from(peliculas_model)
    total = conectar.execute(count_query).scalar()

    # Verificar si se encontraron resultados
    if result:
        # Mapear los resultados a una lista de diccionarios (desempaquetar los campos de las filas)
        peliculas = [PeliculaEsquema(**dict(zip([column.name for column in peliculas_model.columns], row))) for row in result]

        # Calcular el total de páginas
        total_pages = (total // limit) + (1 if total % limit > 0 else 0)

        # Crear una respuesta con los datos, la página actual y el total de elementos
        response = {
            "data": peliculas,
            "page": page,
            "total": total,
            "total_page": total_pages
        }

        return response

    # Si no hay resultados
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sin resultados")


@api.get("/peliculas/{id}", tags=['peliculas'],response_model=PeliculaEsquema, status_code=status.HTTP_200_OK)
async def peliculas_get(id:int):
    datos = conectar.execute(peliculas_model.select().where(peliculas_model.c.id==id)).first()
    if datos:
        return datos
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sin resultados")


@api.post("/peliculas", tags=['peliculas'],response_model=ResponseEsquema, status_code=status.HTTP_201_CREATED)
async def peliculas_post(model:PeliculaEsquema):
    try:
        conectar.execute(peliculas_model.insert().values({
            "nombre": model.nombre,
            "slug": slugify(model.nombre),
            "descripcion": model.descripcion,
            "imagen": model.imagen,
            "precio": model.precio,
           ## "categorias_id": model.categorias_id,
            
        }))
        conectar.commit()
        
        return {"mensaje": "se ha creado correctamente"}
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ocurrio un error")



@api.get("/users", tags=['usuarios'],response_model=List[UsuarioEsquema], status_code=status.HTTP_200_OK)
async def users():
    return conectar.execute(usuarios_model.select().order_by(usuarios_model.c.id.desc())).fetchall()


    
@api.post("/users", tags=['usuarios'],response_model=ResponseEsquema, status_code=status.HTTP_201_CREATED)
async def usuarios_post(model:UsuarioEsquema):
    try:
        conectar.execute(usuarios_model.insert().values({
            "nombre": model.nombre,
            "correo": model.correo,
            "fecha": datetime.now(),
            "password": hashlib.sha512(model.password.encode('utf8')).hexdigest(),
            "perfil_id": model.perfil_id,
        }))
        conectar.commit()
        
        return {"mensaje": "se ha creado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"ocurrio un error: {str(e)}")
    
    
def obtener_peliculas_por_genero(genero_id: int, peliculas: pd.DataFrame, generos_peliculas: pd.DataFrame, n: int = 20):
    peliculas_ids = generos_peliculas[generos_peliculas["genero_id"] == genero_id]["pelicula_id"]
    peliculas_filtradas = peliculas[peliculas["id"].isin(peliculas_ids)].sort_values(by="id", ascending=False).head(n)
    return peliculas_filtradas



@api.get("/generos/{genero_id}/peliculas", tags=['Recomendaciones'], response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def obtener_peliculas_por_categoria(genero_id: int):
    query_genero = select(generos_model.c.id, generos_model.c.nombre).where(generos_model.c.id == genero_id)
    genero_db = conectar.execute(query_genero).fetchone()

    if not genero_db:
        raise HTTPException(status_code=404, detail="Género no encontrado")
    
    genero_id_valor, genero_nombre_valor = genero_db  # Desestructuración de la tupla

    query_peliculas = select(peliculas_model.c.id, peliculas_model.c.nombre, peliculas_model.c.descripcion, peliculas_model.c.imagen)
    peliculas_db = conectar.execute(query_peliculas).fetchall()
    peliculas = pd.DataFrame(peliculas_db, columns=["id", "nombre", "descripcion", "imagen"])
    
    query_generos_peliculas = select(generos_peliculas_model.c.pelicula_id, generos_peliculas_model.c.genero_id)
    generos_peliculas_db = conectar.execute(query_generos_peliculas).fetchall()
    generos_peliculas = pd.DataFrame(generos_peliculas_db, columns=["pelicula_id", "genero_id"])
    
    peliculas_filtradas = obtener_peliculas_por_genero(genero_id, peliculas, generos_peliculas)
    ##print(peliculas_filtradas)
    
    peliculas_json = [
        {
            "id": str(row["id"]),
            "titulo": row["nombre"],
            "descripcion": row["descripcion"],
            "imagen": row["imagen"] if row["imagen"] else "https://placehold.co/150"
        }
        for _, row in peliculas_filtradas.iterrows()
    ]
    
    return {
        "categorias": {
            "id": str(genero_id_valor),
            "nombre": genero_nombre_valor,
            "peliculas": peliculas_json
        }
    }






def recomendaciones_contenido(titulo: str, peliculas: pd.DataFrame, top_n: int = 5):
    """
    Devuelve recomendaciones de películas basadas en la similitud de contenido.
    
    :param titulo: Título de la película para la cual se desean recomendaciones.
    :param peliculas: DataFrame que contiene las películas con columnas 'nombre' y 'descripcion'.
    :param top_n: Número de recomendaciones a devolver.
    :return: DataFrame con las películas recomendadas.
    """
    try:
        # Verifica si el título existe en el DataFrame
        if titulo not in peliculas["nombre"].values:
            return pd.DataFrame()  # Retorna un DataFrame vacío si el título no existe

        # Preprocesamiento de texto
        tfidf = TfidfVectorizer(stop_words="english")
        peliculas["descripcion"] = peliculas["descripcion"].fillna("")
        tfidf_matrix = tfidf.fit_transform(peliculas["descripcion"])

        # Cálculo de similitud coseno
        similitud_coseno = cosine_similarity(tfidf_matrix, tfidf_matrix)

        # Obtener el índice de la película con el título dado
        idx = peliculas[peliculas["nombre"] == titulo].index[0]

        # Obtener las películas más similares
        puntajes_similitud = list(enumerate(similitud_coseno[idx]))
        puntajes_similitud = sorted(puntajes_similitud, key=lambda x: x[1], reverse=True)
        puntajes_similitud = puntajes_similitud[1:top_n + 1]  # Excluir la película misma
        indices_recomendados = [i[0] for i in puntajes_similitud]

        return peliculas.iloc[indices_recomendados]
    except Exception as e:
        print(f"Error en recomendaciones_contenido: {e}")
        return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

#################### recomendaciones basadas en contenido ################################

@api.get("/recomendaciones/pelicula/{titulo}", tags=['Recomendaciones'], response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def obtener_recomendaciones(titulo: str, top_n: int = 5):
    """
    Endpoint para obtener recomendaciones de películas basadas en un título dado.
    
    :param titulo: Título de la película para la cual se desean recomendaciones.
    :param top_n: Número de recomendaciones a devolver (por defecto 5).
    :return: Lista de diccionarios con las películas recomendadas.
    """
    # Obtener las películas de la base de datos
    query = select(peliculas_model.c.nombre, peliculas_model.c.descripcion)  # Corrección aquí
    peliculas_db = conectar.execute(query).fetchall()

    # Convertir a DataFrame de pandas
    peliculas = pd.DataFrame(peliculas_db, columns=["nombre", "descripcion"])

    # Obtener recomendaciones
    recomendaciones = recomendaciones_contenido(titulo, peliculas, top_n)

    if recomendaciones.empty:
        raise HTTPException(status_code=404, detail="Película no encontrada o no hay recomendaciones disponibles")

    # Convertir el DataFrame de recomendaciones a una lista de diccionarios
    recomendaciones_json = recomendaciones.to_dict(orient="records")

    return recomendaciones_json



#################### Recomendaciones colaborativas ################################

def recomendaciones_colaborativas(id_usuario: int, calificaciones: pd.DataFrame, peliculas: pd.DataFrame, top_n: int = 5):
    """
    Devuelve recomendaciones de películas basadas en filtrado colaborativo.
    
    :param id_usuario: ID del usuario para el cual se desean recomendaciones.
    :param calificaciones: DataFrame con las calificaciones de usuarios.
    :param peliculas: DataFrame con información de películas.
    :param top_n: Número de recomendaciones a devolver.
    :return: DataFrame con las películas recomendadas.
    """
    try:
        # Crear la matriz usuario-película
        matriz_usuario_pelicula = calificaciones.pivot(index="id_usuario", columns="id_pelicula", values="calificacion").fillna(0)
        
        # Verificar si el usuario está en la matriz
        if id_usuario not in matriz_usuario_pelicula.index:
            return pd.DataFrame()  # Retorna un DataFrame vacío si el usuario no existe
        
        # Aplicar modelo de vecinos más cercanos
        modelo = NearestNeighbors(metric="cosine", algorithm="brute")
        modelo.fit(matriz_usuario_pelicula)
        
        # Encontrar vecinos más cercanos
        distancias, indices = modelo.kneighbors([matriz_usuario_pelicula.loc[id_usuario]], n_neighbors=top_n + 1)
        indices_recomendados = indices.flatten()[1:]  # Omitimos el primer índice (el usuario mismo)
        
        print(indices_recomendados)
        # Obtener las películas recomendadas
        peliculas_recomendadas = matriz_usuario_pelicula.columns[indices_recomendados]
        
        # Ajuste: Filtrar películas por 'id' en lugar de 'id_pelicula'
        return peliculas[peliculas["id"].isin(peliculas_recomendadas)]
    
    except Exception as e:
        print(f"Error en recomendaciones_colaborativas: {e}")
        return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

@api.get("/recomendaciones/colaborativas/{id_usuario}", tags=['Recomendaciones'], response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def obtener_recomendaciones_colaborativas(id_usuario: int, top_n: int = 5):
    """
    Endpoint para obtener recomendaciones de películas basadas en filtrado colaborativo.
    
    :param id_usuario: ID del usuario para el cual se desean recomendaciones.
    :param top_n: Número de recomendaciones a devolver (por defecto 5).
    :return: Lista de diccionarios con las películas recomendadas.
    """
    # Obtener las calificaciones de la base de datos
    query_calificaciones = select(calificaciones_model.c.id_usuario, calificaciones_model.c.id_pelicula, calificaciones_model.c.calificacion)
    calificaciones_db = conectar.execute(query_calificaciones).fetchall()

    ##print(calificaciones_db)
    calificaciones = pd.DataFrame(calificaciones_db, columns=["id_usuario", "id_pelicula", "calificacion"])
    
    # Obtener las películas de la base de datos
    query_peliculas = select(peliculas_model.c.id, peliculas_model.c.nombre, peliculas_model.c.descripcion)
    peliculas_db = conectar.execute(query_peliculas).fetchall()

    # Ajuste: Usar nombres correctos en películas
    peliculas = pd.DataFrame(peliculas_db, columns=["id", "nombre", "descripcion"])
    
    # Obtener recomendaciones
    recomendaciones = recomendaciones_colaborativas(id_usuario, calificaciones, peliculas, top_n)
    
    if recomendaciones.empty:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o no hay recomendaciones disponibles")
    
    # Convertir el DataFrame de recomendaciones a una lista de diccionarios
    recomendaciones_json = recomendaciones.to_dict(orient="records")
    
    return recomendaciones_json




#################### Recomendaciones vieron tambien ################################

def vieron_tambien(id_pelicula: int, calificaciones: pd.DataFrame, peliculas: pd.DataFrame, top_n: int = 5):
    usuarios = calificaciones[calificaciones["id_pelicula"] == id_pelicula]["id_usuario"].unique()
    peliculas_relacionadas = calificaciones[calificaciones["id_usuario"].isin(usuarios)]["id_pelicula"].value_counts().head(top_n + 1)
    peliculas_relacionadas = peliculas_relacionadas.index[peliculas_relacionadas.index != id_pelicula]
    return peliculas[peliculas["id"].isin(peliculas_relacionadas)]



@api.get("/recomendaciones/vieron_tambien/{id_pelicula}", tags=['Recomendaciones'], response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def obtener_vieron_tambien(id_pelicula: int, top_n: int = 5):
    query_calificaciones = select(calificaciones_model.c.id_usuario, calificaciones_model.c.id_pelicula, calificaciones_model.c.calificacion)
    calificaciones_db = conectar.execute(query_calificaciones).fetchall()
    calificaciones = pd.DataFrame(calificaciones_db, columns=["id_usuario", "id_pelicula", "calificacion"])
    query_peliculas = select(peliculas_model.c.id, peliculas_model.c.nombre, peliculas_model.c.descripcion)
    peliculas_db = conectar.execute(query_peliculas).fetchall()
    peliculas = pd.DataFrame(peliculas_db, columns=["id", "nombre", "descripcion"])
    recomendaciones = vieron_tambien(id_pelicula, calificaciones, peliculas, top_n)
    if recomendaciones.empty:
        raise HTTPException(status_code=404, detail="Película no encontrada o no hay recomendaciones disponibles")
    recomendaciones_json = recomendaciones.to_dict(orient="records")
    return recomendaciones_json


#################### Recomendaciones peliculas sorprendentes ################################
def peliculas_sorprendentes(calificaciones: pd.DataFrame, peliculas: pd.DataFrame, n: int = 5):
    calificaciones_promedio = calificaciones.groupby("id_pelicula")["calificacion"].mean().reset_index()
    calificaciones_promedio = calificaciones_promedio.rename(columns={"calificacion": "calificacion_promedio"})
    peliculas = peliculas.merge(calificaciones_promedio, left_on="id", right_on="id_pelicula", how="left").fillna(0)
    peliculas_filtradas = peliculas[peliculas["calificacion_promedio"] >= 4.0]
    if peliculas_filtradas.empty:
        return peliculas.iloc[0:0]
    return peliculas_filtradas.sample(min(n, len(peliculas_filtradas)))


@api.get("/recomendaciones/peliculas_sorprendentes", tags=['Recomendaciones'], response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def obtener_peliculas_sorprendentes(n: int = 5):
    query_calificaciones = select(calificaciones_model.c.id_pelicula, calificaciones_model.c.calificacion)
    calificaciones_db = conectar.execute(query_calificaciones).fetchall()
    calificaciones = pd.DataFrame(calificaciones_db, columns=["id_pelicula", "calificacion"])
    query_peliculas = select(peliculas_model.c.id, peliculas_model.c.nombre, peliculas_model.c.descripcion)
    peliculas_db = conectar.execute(query_peliculas).fetchall()
    peliculas = pd.DataFrame(peliculas_db, columns=["id", "nombre", "descripcion"])
    recomendaciones = peliculas_sorprendentes(calificaciones, peliculas, n)
    if recomendaciones.empty:
        raise HTTPException(status_code=404, detail="No hay películas sorprendentes disponibles")
    recomendaciones_json = recomendaciones.to_dict(orient="records")
    return recomendaciones_json


#################### Recomendaciones mas vistas ################################
def mas_vistas(calificaciones: pd.DataFrame, peliculas: pd.DataFrame, n: int = 10):
    num_calificaciones = calificaciones.groupby("id_pelicula").size().reset_index(name="num_calificaciones")
    peliculas = peliculas.merge(num_calificaciones, left_on="id", right_on="id_pelicula", how="left").fillna(0)
    return peliculas.sort_values(by="num_calificaciones", ascending=False).head(n)



@api.get("/recomendaciones/mas_vistas", tags=['Recomendaciones'], response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def obtener_mas_vistas(n: int = 10):
    query_calificaciones = select(calificaciones_model.c.id_pelicula, calificaciones_model.c.calificacion)
    calificaciones_db = conectar.execute(query_calificaciones).fetchall()
    calificaciones = pd.DataFrame(calificaciones_db, columns=["id_pelicula", "calificacion"])
    query_peliculas = select(peliculas_model.c.id, peliculas_model.c.nombre, peliculas_model.c.descripcion)
    peliculas_db = conectar.execute(query_peliculas).fetchall()
    peliculas = pd.DataFrame(peliculas_db, columns=["id", "nombre", "descripcion"])
    recomendaciones = mas_vistas(calificaciones, peliculas, n)
    if recomendaciones.empty:
        raise HTTPException(status_code=404, detail="No hay películas disponibles")
    recomendaciones_json = recomendaciones.to_dict(orient="records")
    return recomendaciones_json



#################### Recomendaciones lo mas recomendado ################################
def mas_recomendadas(calificaciones: pd.DataFrame, peliculas: pd.DataFrame, n: int = 10):
    calificaciones_promedio = calificaciones.groupby("id_pelicula")["calificacion"].mean().reset_index()
    calificaciones_promedio = calificaciones_promedio.rename(columns={"calificacion": "calificacion_promedio"})
    peliculas = peliculas.merge(calificaciones_promedio, left_on="id", right_on="id_pelicula", how="left").fillna(0)
    return peliculas.sort_values(by="calificacion_promedio", ascending=False).head(n)



@api.get("/recomendaciones/mas_recomendadas", tags=['Recomendaciones'], response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def obtener_mas_recomendadas(n: int = 10):
    query_calificaciones = select(calificaciones_model.c.id_pelicula, calificaciones_model.c.calificacion)
    calificaciones_db = conectar.execute(query_calificaciones).fetchall()
    calificaciones = pd.DataFrame(calificaciones_db, columns=["id_pelicula", "calificacion"])
    query_peliculas = select(peliculas_model.c.id, peliculas_model.c.nombre, peliculas_model.c.descripcion)
    peliculas_db = conectar.execute(query_peliculas).fetchall()
    peliculas = pd.DataFrame(peliculas_db, columns=["id", "nombre", "descripcion"])
    recomendaciones = mas_recomendadas(calificaciones, peliculas, n)
    if recomendaciones.empty:
        raise HTTPException(status_code=404, detail="No hay películas recomendadas disponibles")
    recomendaciones_json = recomendaciones.to_dict(orient="records")
    return recomendaciones_json