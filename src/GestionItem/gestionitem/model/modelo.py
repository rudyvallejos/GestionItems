'''
Created on 30/04/2011

@author: Rudy Vallejos
'''
from sqlalchemy import Column
from sqlalchemy.types import Unicode, Integer
from gestionitem.model import DeclarativeBase
from sqlalchemy.orm import relation


    
class EstadoProyecto(DeclarativeBase):
    __tablename__ = 'estado_proyecto'

    #column definitions
    descripcion = Column(Unicode(100), unique=True, nullable=False)
    id = Column(Integer, autoincrement=True, primary_key=True)


class Proyecto(DeclarativeBase):
    __tablename__ = 'proyecto'

    #column definitions
    descripcion = Column(Unicode(100), unique=True, nullable=False)
    estado = relation('EstadoProyecto', backref='proyectos')

    id = Column(Integer, autoincrement=True, primary_key=True)

    #relation definitions
