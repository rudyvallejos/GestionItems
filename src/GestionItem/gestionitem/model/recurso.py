import os 
from datetime import datetime
# -*- coding: utf-8 -*-
"""
Auth* related model.

This is where the models used by :mod:`repoze.who` and :mod:`repoze.what` are
defined.

It's perfectly fine to re-use this definition in the GestionItem application,
though.

"""
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
from sqlalchemy.types import Unicode, String, Integer, DateTime
from sqlalchemy.orm import relation, synonym

from gestionitem.model import DeclarativeBase, metadata, DBSession

class Recurso(DeclarativeBase):
 
    __tablename__ = 'recurso'
    id = Column("id", Integer, primary_key=True)
    descripcion = Column("descripcion", String(200))
