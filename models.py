from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Text, Float, DateTime
from database import meta, motor


categorias_model = Table("categorias", 
                         meta, 
                         Column('id', Integer, primary_key=True),  
                         Column('nombre', String(100), nullable=False), 
                         Column('slug', String(100), nullable=False)
                         )



peliculas_model = Table("peliculas", 
                         meta, 
                         Column('id', Integer, primary_key=True),  
                         Column('nombre', String(100), nullable=False), 
                         Column('slug', String(100), nullable=False),
                         Column('descripcion', Text(), nullable=False),
                         Column('precio', Float, default=1),
                         Column('categorias_id', Integer, ForeignKey('categorias.id')),
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

meta.create_all(motor)