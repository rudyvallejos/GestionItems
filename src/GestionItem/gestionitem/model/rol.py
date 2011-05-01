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

from gestionitem.model import DeclarativeBase, metadata, DBSession

class Rol(DeclarativeBase):
 
    __tablename__ = 'rol'
    id = Column("id", Integer, primary_key=True)
    descripcion = Column("descripcion", String(200))

