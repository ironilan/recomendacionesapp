from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

from typing import List


class ResponseEsquema(BaseModel):
    mensaje: str


    
    
class GeneroEsquema(BaseModel):
    id:Optional[int] = ""
    nombre:str
    estado:Optional[int] =""
    
    class Config:
        json_schema_extra={
            "ejemplo": {                
                "nombre": "Acción"
            }
        }
        
        
class CalificacionEsquema(BaseModel):
    id:Optional[int] = ""
    id_pelicula:int
    id_usuario:int
    calificacion:int
    timestamp:Optional[int] = ""
    
    class Config:
        json_schema_extra={
            "ejemplo": {
                "id_pelicula": 144,
                "id_usuario": 1,
                "calificacion": 5
            }
        }
        
        
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
    imagen:str
    
    class Config:
        json_schema_extra={
            "ejemplo": {                
                "nombre": "pelicula 1",
                "imagen": "pelicula-1",
                "descripcion": "pelicula descripcion",
                "precio": "10.00"
            }
        }
        
        
class PeliculaUnicaEsquema(BaseModel):
    id: Optional[int] = None  # Campo opcional sin valor por defecto incorrecto
    titulo: str  # Cambiado de "nombre" a "titulo" para coincidir con el endpoint
    descripcion: str
    imagen: str
    genero: List[str]  # Lista de géneros

    class Config:
        json_schema_extra = {
            "ejemplo": {
                "id": 1,
                "titulo": "pelicula 1",
                "imagen": "pelicula-1.jpg",
                "descripcion": "pelicula descripcion",
                "genero": ["Acción", "Aventura"]  # Ejemplo corregido
            }
        }
        
        
class PaginacionResponse(BaseModel):
    data: List[PeliculaEsquema]
    page: int
    total: int
    total_page: int

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
    ##perfil_id:int
    
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
        
class UltimaPeliculaCalificadaResponse(BaseModel):
    id: int
    titulo: str
    descripcion: str
    imagen: str

class JwtEsquema(BaseModel):
    token: str
    nombre: str
    id: int

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