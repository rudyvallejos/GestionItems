'''
Created on 02/05/2011

@author: Rudy Vallejos
'''
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Unicode, Integer


from gestionitem.model import DeclarativeBase, metadata, DBSession

__all__ = ['Proyecto']

class EstadoProyecto(DeclarativeBase):
    __tablename__ = 'estado_proyecto'

    #column definitions
    descripcion = Column(Unicode(100), unique=True, nullable=False)
    id = Column(Integer, autoincrement=True, primary_key=True)

class Proyecto(DeclarativeBase):
    __tablename__ = 'proyecto'
    
    
    id = Column(Integer, autoincrement=True, primary_key=True)

    descripcion = Column(Unicode(100), unique=True, nullable=False)

    estado = Column(Integer, ForeignKey('estado_proyecto.id'), nullable=False)
    
