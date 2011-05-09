'''
Created on 02/05/2011

@author: Rudy Vallejos
'''
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from datetime import datetime
from sqlalchemy.orm import relation

from gestionitem.model import DeclarativeBase


__all__ = ['Proyecto']

class EstadoProyecto(DeclarativeBase):
    __tablename__ = 'estado_proyecto'

    #column definitions
    descripcion = Column(Unicode(100), unique=True, nullable=False)
    id = Column(Integer, autoincrement=True, primary_key=True)

class Proyecto(DeclarativeBase):
    __tablename__ = 'proyecto'
    
    
    id = Column(Integer, autoincrement=True, primary_key=True)

    descripcion = Column(Unicode(100), unique=True, nullable = False)

    estado = Column(Integer, ForeignKey('estado_proyecto.id'), nullable = False)
    
    estadoObj = relation('EstadoProyecto',foreign_keys = estado )
    
    fecha_creacion = Column(DateTime, default = datetime.now)
    
    id_lider = Column(Integer, ForeignKey('tg_user.user_id'), nullable = False)
    
    lider = relation('User',foreign_keys = id_lider )

