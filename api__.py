from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from slugify import slugify
from database import conectar
from esquemas import *
from models import *
from sqlalchemy import and_, func, select
#utilidades
from utilidades import *
from datetime import datetime
import os
import hashlib
#jwt
from jose import JWTError, jwt
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





##generos
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


##peliculas
# @api.get("/peliculas", tags=['peliculas'],response_model=List[PeliculaEsquema], status_code=status.HTTP_200_OK)
# async def peliculas(username: str = Depends(verificar_token)):
#     return conectar.execute(peliculas_model.select().order_by(peliculas_model.c.id.desc())).fetchall()







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



###################
###############

  
    



@api.get("/perfiles", tags=['perfiles'],response_model=List[PerfilEsquema], status_code=status.HTTP_200_OK)
async def perfiles():
    return conectar.execute(perfil_model.select().order_by(perfil_model.c.id.desc())).fetchall()


@api.post("/perfiles", tags=['perfiles'],response_model=ResponseEsquema, status_code=status.HTTP_201_CREATED)
async def perfiles_post(model:PerfilEsquema):
    try:
        conectar.execute(perfil_model.insert().values({
            "nombre": model.nombre
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
    
    






############################### recomendaciones
