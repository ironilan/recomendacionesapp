from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class ResponseEsquema(BaseModel):
    mensaje: str


class CategoriaEsquema(BaseModel):
    id:Optional[int] = ""
    nombre:str
    slug:Optional[str] =""
    
    class Config:
        json_schema_extra={
            "ejemplo": {                
                "nombre": "categoria 1"
            }
        }

class PeliculaEsquema(BaseModel):
    id:Optional[int] = ""
    nombre:str
    slug:Optional[str] = ""
    descripcion:str
    precio:float
    categorias_id:int
    
    class Config:
        json_schema_extra={
            "ejemplo": {                
                "nombre": "pelicula 1",
                "slug": "pelicula-1",
                "descripcion": "pelicula descripcion",
                "precio": "10.00",
                "categorias_id": 1
            }
        }

class PeliculaFotoEsquema(BaseModel):
    id:Optional[int] = ""
    nombre:str
    pelicula_id:int

class PerfilEsquema(BaseModel):
    id:Optional[int] = ""
    nombre:str
    
    class Config:
        json_schema_extra={
            "ejemplo": {                
                "nombre": "Foo"
            }
        }
        
        
class UsuarioEsquema(BaseModel):
    id:Optional[int] = ""
    nombre:str
    correo:str
    password:str
    fecha:Optional[datetime] = ''
    perfil_id:int
    
    class Config:
        json_schema_extra={
            "ejemplo": {                
                "nombre": "Alex",
                "correo": "Alex@gmail.com",
                "password": "1234566",
                "fecha": "Alex",
                "perfil_id": 1
            }
        }


class LoginEsquema(BaseModel):
    correo: str
    password: str

    class Config:
        json_schema_extra={
            "ejemplo": {                
                "correo": "sssss@gmail.com",
                "password": "123456"
            }
        }