'''
Created on 06/05/2011

@author: Rudy Vallejos
'''
from gestionitem.lib.base import BaseController
from gestionitem.model.proyecto import Proyecto , EstadoProyecto
from gestionitem.model import *
from tg import expose, flash, tmpl_context, validate, redirect
from sprox.formbase import AddRecordForm
from formencode.validators import NotEmpty
from sprox.formbase import EditableForm
from sprox.fillerbase import EditFormFiller






class AddProyecto(AddRecordForm):
    __model__ = Proyecto
    __omit_fields__ = ['id','estadoObj','fecha_creacion']

add_Proyecto_form = AddProyecto(DBSession)


class ProyectoController(BaseController):
    
    @expose()
    def index(self):
        """Handle the front-page."""
        redirect('/proyecto/lista')
               

    @expose( )
    @validate(
        form = add_Proyecto_form,
        error_handler = index,
    )
    def add_proyecto( self, descripcion, lider, **named ):
        """Registra un proyecto nuevo """
        new = Proyecto(
            descripcion = descripcion,
            id_lider = lider,
            estado = 1,
        )
        DBSession.add( new )
        flash( '''Proyecto Registrado: %s'''%( descripcion, ))
        redirect( './index' )

   
    @expose(template='gestionitem.templates.proyectoTmpl.lista')
    def lista(self, **named):
        proyectos=DBSession.query(Proyecto).order_by( Proyecto.id )
        from webhelpers import paginate
        count = proyectos.count()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            proyectos, page, item_count=count,
            items_per_page=5,
        )
        proyectos = currentPage.items
        return dict(page='Lista de proyectos',
                    proyectos=proyectos, 
                    subtitulo='Proyectos',currentPage = currentPage)
        
    @expose('gestionitem.templates.proyectoTmpl.nuevo')
    def nuevo(self):
        """Handle the front-page."""
        tmpl_context.add_Proyecto_form = add_Proyecto_form

        return dict(
            page='Nuevo Proyecto',
        )

        
        
    @expose(template="gestionitem.templates.proyectoDef")
    def proyectoDef(self,id):
        proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
        return dict(page='Definir Proyecto',
                    id=id,proyecto=proyecto,subtitulo='Definicion de Proyectos')
        
        
    @expose(template="gestionitem.templates.proyectoTmpl.editar")
    def editar(self,id):
        proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
        return dict(page='Editar Proyecto',
                    id=id,proyecto=proyecto,subtitulo='ABM-Proyecto')
    





