import os 
from datetime import datetime
import sys
try:
    from hashlib import sha1
except ImportError:
    sys.exit('ImportError: No module named hashlib\n'
             'If you are on python2.4 this library is not part of python. '
             'Please install it. Example: easy_install hashlib')

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime, String
from sqlalchemy.orm import relation, synonym

from gestionitem.model import DeclarativeBase,metadata , DBSession

estado_proyecto_tabla = Table('estado_proyecto', metadata,
    Column('user_id', Integer, ForeignKey('tg_user.user_id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('group_id', Integer, ForeignKey('tg_group.group_id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)


class Proyecto(DeclarativeBase):
 
    __tablename__ = 'proyecto'
    id = Column("id", Integer, primary_key=True)
    estado = Column("estado", Integer, primary_key=True)
    descripcion = Column("descripcion", String(200))
