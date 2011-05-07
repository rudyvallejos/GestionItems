from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, String

from gestionitem.model import DeclarativeBase, metadata, DBSession

#__all__ = ['TipoItemUsuario']

class Tipo(DeclarativeBase):
    __tablename__ = 'tipo'
    
    
    id = Column("id",Integer, autoincrement=True, primary_key=True)

    descripcion = Column("descripcion", String(100), unique=True, nullable=False)



class TipoItemUsuario(DeclarativeBase):
    __tablename__ = 'tipo_item_usuario'
    
    
    id = Column("id",Integer, autoincrement=True, primary_key=True)

    descripcion = Column("descripcion", String(100), unique=True, nullable=False)

    proyecto_id = Column("proyecto_id", Integer, ForeignKey('proyecto.id'), nullable=False)
    

class TipoItemUsuarioAtributos(DeclarativeBase):
    __tablename__ = 'tipo_item_usuario_atributos'
    
    
    id = Column("id",Integer, autoincrement=True, primary_key=True)

    nombre_atributo = Column("nombre_atributo", String(100), unique=True, nullable=False)

    tipo_item_id = Column("tipo_item_id", Integer, ForeignKey('tipo_item_usuario.id'), nullable=False)
    tipo_id = Column("tipo_id", Integer, ForeignKey('tipo.id'), nullable=False)