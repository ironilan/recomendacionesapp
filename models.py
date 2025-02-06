from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Text, Float, DateTime
from database import meta, motor


categorias_model = Table("categorias", 
                         meta, 
                         Column('id', Integer, primary_key=True),  
                         Column('nombre', String(100), nullable=False), 
                         Column('slug', String(100), nullable=False)
                         )

generos_model = Table("generos", 
                         meta, 
                         Column('id', Integer, primary_key=True),  
                         Column('nombre', String(100), nullable=False),
                         Column('estado', Integer, default=1)
                         )



peliculas_model = Table("peliculas", 
                         meta, 
                         Column('id', Integer, primary_key=True),  
                         Column('nombre', String(100), nullable=False), 
                         Column('slug', String(100), nullable=False),
                         Column('imagen', Text(), nullable=False),
                         Column('descripcion', Text(), nullable=False),
                         Column('precio', Float, default=1),
                         Column('estado', Integer, default=1)
                         )

generos_peliculas_model = Table('generos_peliculas',
                            meta,
                            Column('id', Integer, primary_key=True),  
                            Column('genero_id', Integer, ForeignKey('generos.id')),
                            Column('pelicula_id', Integer, ForeignKey('peliculas.id')),
                            Column('estado', Integer, default=1),
                              )

rating_model = Table('rating',
                            meta,
                            Column('id', Integer, primary_key=True),  
                            Column('usuario_id', Integer, ForeignKey('usuarios.id')),
                            Column('pelicula_id', Integer, ForeignKey('peliculas.id')),
                            Column('rating', Integer, default=1),
                            Column('timestamp', Integer, default=1),
                            Column('estado', Integer, default=1),
                              )

calificaciones_model = Table('calificaciones',
                            meta,
                            Column('id', Integer, primary_key=True),  
                            Column('id_pelicula', Integer, ForeignKey('usuarios.id')),
                            Column('id_usuario', Integer, ForeignKey('peliculas.id')),
                            Column('calificacion', Integer, default=1),
                            Column('timestamp', Integer, default=1),
                              )

tags_model = Table('tags',
                            meta,
                            Column('id', Integer, primary_key=True),  
                            Column('usuario_id', Integer, ForeignKey('usuarios.id')),
                            Column('pelicula_id', Integer, ForeignKey('peliculas.id')),
                            Column('tag', Text(), nullable=False),
                            Column('timestamp', Integer, default=1),
                            Column('estado', Integer, default=1),
                              )

peliculas_fotos_model = Table('peliculas_fotos',
                            meta,
                            Column('id', Integer, primary_key=True),  
                            Column('nombre', String(100), nullable=False), 
                            Column('peliculas_id', Integer, ForeignKey('peliculas.id')),
                              )

perfil_model = Table('perfil',
                            meta,
                            Column('id', Integer, primary_key=True),  
                            Column('nombre', String(100), nullable=False)
                              )


usuarios_model = Table('usuarios',
                            meta,
                            Column('id', Integer, primary_key=True),  
                            Column('nombre', String(100), nullable=False), 
                            Column('correo', String(100), nullable=False), 
                            Column('password', String(160), nullable=False), 
                            Column('fecha', DateTime()), 
                            Column('perfil_id', Integer, ForeignKey('perfil.id')),
                              )


usuarios_peliculas_model = Table('usuarios_peliculas',
                            meta,
                            Column('id', Integer, primary_key=True),  
                            Column('usuario_id', Integer, ForeignKey('usuarios.id')),
                            Column('pelicula_id', Integer, ForeignKey('peliculas.id')),
                            Column('fecha', DateTime()),
                            Column('estado', Integer, default=1),
                              )

meta.create_all(motor)