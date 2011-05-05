from tgext.crud import CrudRestController
from sprox.tablebase import TableBase
from sprox.fillerbase import TableFiller, EditFormFiller
from gestionitem.model.proyecto import Proyecto, EstadoProyecto
from gestionitem.model import DBSession
from sprox.formbase import AddRecordForm, EditableForm
from tw.core import WidgetsList
from tw.forms import TableForm, SingleSelectField, TextField
from formencode.validators import NotEmpty
# This WidgetsList is just a container


class ProyectoForm(TableForm):
    # This WidgetsList is just a container
    class fields(WidgetsList):
        descripcion =  TextField(validator=NotEmpty)
        estadochoices = ((1,"action"),
                         (2,"animation"),
                         (3,"comedy"),
                         (4,"documentary"),
                         (5,"drama"),
                         (6,"sci-fi"))

#        rows= [(row['id']) for row in estadochoices]


        estado = SingleSelectField(options=estadochoices)
proyecto_add_form_tw = ProyectoForm("create_proyecto_form")


    
    

class ProyectoTable(TableBase):
    __model__ = Proyecto
    __omit_fields__ = ['id']
proyecto_table = ProyectoTable(DBSession)

class ProyectoTableFiller(TableFiller):
    __model__ = Proyecto
proyecto_table_filler = ProyectoTableFiller(DBSession)

class ProyectoAddForm(AddRecordForm):
    __model__ = Proyecto
    __omit_fields__ = ['id']
proyecto_add_form = ProyectoAddForm(DBSession)

class ProyectoEditForm(EditableForm):
    __model__ = Proyecto
    __omit_fields__ = ['id']
proyecto_edit_form = ProyectoEditForm(DBSession)

class ProyectoFillerForm(EditFormFiller):
    __model__ = Proyecto
    __omit_fields__ = ['id']
proyecto_edit_filler = ProyectoFillerForm(DBSession)


class ProyectoController(CrudRestController):
    model = Proyecto
    table = proyecto_table
    table_filler = proyecto_table_filler
    new_form = proyecto_add_form_tw
    edit_form = proyecto_edit_form
    edit_filler = proyecto_edit_filler
