'''
Created on 06/05/2011

@author: Rudy Vallejos
'''
from gestionitem.lib.base import BaseController
from gestionitem.model.proyecto import Proyecto , EstadoProyecto
from gestionitem.model import DBSession
from gestionitem.model.auth import User
from tg import expose, flash, tmpl_context, validate, redirect
from sprox.formbase import AddRecordForm
from tg import request



class AddProyecto(AddRecordForm):
    __model__ = Proyecto
    __omit_fields__ = ['id','estadoObj','fecha_creacion']
    

add_Proyecto_form = AddProyecto(DBSession)



class ProyectoController(BaseController):
    
    @expose()
    def index(self):
        """Handle the front-page."""
        redirect('/proyecto/lista')
        
    
    @expose(template='gestionitem.templates.proyectoTmpl.lista')
    def lista(self, **named):
        identity = request.environ.get('repoze.who.identity')

        if request.identity:
            id = identity['user']
        proyectos=DBSession.query(Proyecto).filter(Proyecto.id_lider == id.user_id)
#        nombre = request.identity['repoze.who.userid']
        
         
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
               


    @expose()
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
        
    
    @expose(template="gestionitem.templates.proyectoTmpl.editar")
    def editar(self,id):
        proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
        usuarios=DBSession.query(User).filter(User.user_id != proyecto.lider.user_id)
        return dict(page='Editar Proyecto',
                    id=id,
                    proyecto=proyecto,
                    subtitulo='ABM-Permiso',
                    usuarios = usuarios)
    
    
    @expose()    
    def actualizar( self, id, descripcion,id_user ,submit ):
        """Create a new movie record"""
        proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
        proyecto.descripcion = descripcion
        proyecto.id_lider = id_user
        
        DBSession.flush()
        
        redirect( '/proyecto' )
        
    
    @expose()
    def eliminar(self,id):
        DBSession.delete(DBSession.query(Proyecto).filter_by(id=id).one())
        redirect( '/proyecto' )    


        
    @expose(template="gestionitem.templates.proyectoDef")
    def proyectoDef(self,id):
        proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
        return dict(page='Definir Proyecto',
                    id=id,proyecto=proyecto,subtitulo='Definicion de Proyectos')
        
        
    
    
    
        
    
        



