'''
Created on 02/05/2011

@author: Rudy Vallejos
'''
from sqlalchemy import ForeignKey, Column
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Unicode, Integer, DateTime, String
from datetime import datetime
from sqlalchemy.orm import relation

from gestionitem.model import DeclarativeBase


#__all__ = ['Proyecto']

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




class EstadoFase(DeclarativeBase):
    __tablename__ = 'estado_fase'
    
    
    id = Column("id",Integer, autoincrement=True, primary_key=True)

    descripcion = Column("descripcion", String(100), unique=True, nullable=False)
    #tipoItemUsuarioAtributos = relationship(TipoItemUsuarioAtributos, backref=backref('tipo', order_by=id))


class Fase(DeclarativeBase):
    __tablename__ = 'fase'
    id = Column("id",Integer, autoincrement=True, primary_key=True)
    numero_fase = Column("numero_fase",Integer)
    descripcion = Column("descripcion", String(100), unique=True, nullable=False)
    estado_id = Column("estado_id", Integer, ForeignKey('estado_fase.id'), nullable=False)
    proyecto_id = Column("proyecto_id", Integer, ForeignKey('proyecto.id'), nullable=False)
    estado = relationship(EstadoFase, order_by=EstadoFase.id, backref="estado_fase")
    proyecto = relationship(Proyecto, order_by=Proyecto.id, backref="proyecto") 

class EstadoItem(DeclarativeBase):
    __tablename__ = 'estado_item'
    id = Column("id",Integer, autoincrement=True, primary_key=True)

    descripcion = Column("descripcion", String(100), unique=True, nullable=False)
    #tipoItemUsuarioAtributos = relationship(TipoItemUsuarioAtributos, backref=backref('tipo', order_by=id))



class RelacionItem(DeclarativeBase):
    __tablename__ = 'relacion_item'
    
    id = Column("id",Integer, autoincrement=True, primary_key=True)
    antecesor_item_id = Column("antecesor_item_id", Integer, ForeignKey('item_usuario.id'), nullable=False)
    sucesor_item_id = Column("sucesor_item_id", Integer, ForeignKey('item_usuario.id'), nullable=False)
    #tipoItemUsuarioAtributos = relationship(TipoItemUsuarioAtributos, backref=backref('tipo', order_by=id))

class ItemUsuario(DeclarativeBase):
    __tablename__ = 'item_usuario'
    
    
    id = Column("id",Integer, autoincrement=True, primary_key=True)
    tipo_item_id = Column("tipo_item_id", Integer, ForeignKey('tipo_item_usuario.id'), nullable=False)
    fase_id = Column("fase_id", Integer, ForeignKey('fase.id'), nullable=False)
    #linea_base_id = Column("linea_base_id", Integer, ForeignKey('linea_base.id'), nullable=False)
    cod_item = Column("cod_item", String(20), unique=False, nullable=False)
    prioridad = Column("prioridad",Integer)
    descripcion = Column("descripcion", String(200), unique=False, nullable=False)
    observacion = Column("observaciones", String(100), unique=False, nullable=False)
    version = Column("version",Integer)
    estado_id = Column("estado_id", Integer, ForeignKey('estado_item.id'), nullable=False)
    fase = relationship(Fase, order_by=Fase.id, backref="fase")
    estado = relationship(EstadoItem, order_by=EstadoItem.id, backref="estado_item")
    def relaciones(self):
        return    
