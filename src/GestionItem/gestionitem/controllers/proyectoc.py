from tgext.crud import CrudRestController
from GestionItem.gestionitem.model import DBSession, proyecto
from sprox.tablebase import TableBase
from sprox.fillerbase import TableFiller
from gestionitem.lib.base import BaseController

class ProyectoTable(TableBase):
    __model__ = proyecto
    proyecto_table = ProyectoTable(DBSession)

class ProyectoTableFiller(TableFiller):
    __model__ = proyecto
    proyecto_table_filler = ProyectoTableFiller(DBSession)

class ProyectoController(CrudRestController):
    model = proyecto
    table = proyecto_table
    table_filler = proyecto_table_filler

class RootController(BaseController):
    proyecto = ProyectoController(DBSession)
