from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, String
from sqlalchemy.orm import relationship, backref

from gestionitem.model import DeclarativeBase, metadata, DBSession

#__all__ = ['TipoItemUsuario']



class TipoItemUsuarioAtributosValor(DeclarativeBase):
    __tablename__ = 'tipo_item_usuario_valor'
    id = Column("id",Integer, autoincrement=True, primary_key=True)
    valor = Column("valor", String(100), unique=True, nullable=False)
    item_usuario_id = Column("item_usuario_id", Integer, ForeignKey('item_usuario.id'), nullable=False)
    atributo_id = Column("atributo_id", Integer, ForeignKey('tipo_item_usuario_atributos.id'), nullable=False)
    
class Tipo(DeclarativeBase):
    __tablename__ = 'tipo'
    
    
    id = Column("id",Integer, autoincrement=True, primary_key=True)

    descripcion = Column("descripcion", String(100), unique=True, nullable=False)
    #tipoItemUsuarioAtributos = relationship(TipoItemUsuarioAtributos, backref=backref('tipo', order_by=id))


class TipoItemUsuarioAtributos(DeclarativeBase):
    __tablename__ = 'tipo_item_usuario_atributos'
    id = Column("id",Integer, autoincrement=True, primary_key=True)

    nombre_atributo = Column("nombre_atributo", String(100), unique=True, nullable=False)

    tipo_item_id = Column("tipo_item_id", Integer, ForeignKey('tipo_item_usuario.id'), nullable=False)
    tipo_id = Column("tipo_id", Integer, ForeignKey('tipo.id'), nullable=False)
    tipo = relationship(Tipo, order_by=Tipo.id, backref="tipo_item_usuario_atributos")
    valor = relationship(TipoItemUsuarioAtributosValor, order_by=TipoItemUsuarioAtributosValor.id, backref="tipo_item_usuario_valor")


class TipoItemUsuario(DeclarativeBase):
    __tablename__ = 'tipo_item_usuario'
    
    
    id = Column("id",Integer, autoincrement=True, primary_key=True)

    descripcion = Column("descripcion", String(100), unique=True, nullable=False)

    proyecto_id = Column("proyecto_id", Integer, ForeignKey('proyecto.id'), nullable=False)
    
    atributos = relationship(TipoItemUsuarioAtributos, order_by=TipoItemUsuarioAtributos.id, backref="tipo_item_usuario_atributos")
    

   
