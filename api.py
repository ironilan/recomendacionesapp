from fastapi import APIRouter, status, HTTPException
from typing import List
from slugify import slugify
from database import conectar
from esquemas import *
from models import *
from datetime import datetime
import os
import hashlib


api = APIRouter()

@api.get("/categorias", tags=['Categorías'],response_model=List[CategoriaEsquema], status_code=status.HTTP_200_OK)
async def categorias():
    return conectar.execute(categorias_model.select().order_by(categorias_model.c.id.desc())).fetchall()



@api.get("/categorias/{id}", tags=['Categorías'],response_model=CategoriaEsquema, status_code=status.HTTP_200_OK)
async def categorias_get(id:int):
    datos = conectar.execute(categorias_model.select().where(categorias_model.c.id==id)).first()
    if datos:
        return datos
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sin resultados")



@api.post("/categorias", tags=['Categorías'],response_model=ResponseEsquema, status_code=status.HTTP_201_CREATED)
async def categorias_post(model:CategoriaEsquema):
    try:
        conectar.execute(categorias_model.insert().values({
            "nombre": model.nombre,
            "slug": slugify(model.nombre)
        }))
        conectar.commit()
        
        return {"mensaje": "se ha creado correctamente"}
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ocurrio un error")
    
    
    
@api.put("/categorias/{id}", tags=['Categorías'],response_model=ResponseEsquema, status_code=status.HTTP_200_OK)
async def categorias_put(id: int, model:CategoriaEsquema):
    datos = conectar.execute(categorias_model.select().where(categorias_model.c.id==id)).first()
    if datos:
        conectar.execute(categorias_model.update().values(nombre=model.nombre, slug= slugify(model.nombre)).where(categorias_model.c.id==id))
        conectar.commit()
        return {"mensaje": "se ha modificado correctamente"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sin resultados")



@api.delete("/categorias/{id}", tags=['Categorías'],response_model=ResponseEsquema, status_code=status.HTTP_200_OK)
async def categorias_delete(id: int, model:CategoriaEsquema):
    datos = conectar.execute(categorias_model.select().where(categorias_model.c.id==id)).first()
    if datos:
        
        existe = conectar.execute(peliculas_model.select().where(peliculas_model.c.categorias_id==id)).first()
        if existe:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se puede eliminar pues esta asociado en al menos una pelicula")
        else:
            conectar.execute(categorias_model.delete().where(categorias_model.c.id==id))
            conectar.commit()
        return {"mensaje": "se ha eliminado correctamente"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sin resultados")




@api.get("/peliculas", tags=['peliculas'],response_model=List[PeliculaEsquema], status_code=status.HTTP_200_OK)
async def peliculas():
    return conectar.execute(peliculas_model.select().order_by(peliculas_model.c.id.desc())).fetchall()


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
            "precio": model.precio,
            "categorias_id": model.categorias_id,
            
        }))
        conectar.commit()
        
        return {"mensaje": "se ha creado correctamente"}
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ocurrio un error")
    
    



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
async def perfiles():
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
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ocurrio un error")