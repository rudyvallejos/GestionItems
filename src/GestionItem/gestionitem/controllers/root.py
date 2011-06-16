# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from gestionitem.lib.base import BaseController
from gestionitem.controllers.secure import SecureController
from gestionitem.controllers.error import ErrorController
from sqlalchemy.orm import sessionmaker
from gestionitem.model.auth import Rol, User, Permission


from gestionitem.controllers.proyectoController import ProyectoController
from gestionitem.controllers.tipoItemControler import TipoItemControler

from gestionitem.controllers.itemControler import ItemControler

from repoze.what.predicates import in_group
from gestionitem.model import DBSession  
from gestionitem.controllers.lbcontroller import LineaBaseController

from gestionitem.controllers.tgadminconfig import TGAdminConfig  

from gestionitem.model.proyecto import Proyecto,Fase
from tgext.admin.controller import AdminController

  






__all__ = ['RootController']

    
class RootController(BaseController):
    """
    The root controller for the GestionItem application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """

    item = ItemControler()
    
    proyecto = ProyectoController()
    
    
    
    tipoItems = TipoItemControler()
    
    secc = SecureController()
    
    lb= LineaBaseController()
  


   
    admin = AdminController([User, Rol, Permission], DBSession, config_type = TGAdminConfig)
    admin.allow_only=in_group('Administrador')

    error = ErrorController()
    dict(subtitulo='')
    
    @expose('gestionitem.templates.index')
    def index(self):
        identity = request.environ.get('repoze.who.identity')
       
        """Handle the front-page."""
        return dict(page='Indice',subtitulo='Indice')

    @expose('gestionitem.templates.prueba.demo')
    def demo(self):
        """Handle the front-page."""
        return dict(page='Indice',subtitulo='Indice')

    @expose(template='gestionitem.templates.proyectoList')
    def proyectoList(self, **named):
        proyectos=DBSession.query(Proyecto).order_by( Proyecto.id )
        from webhelpers import paginate
        count = proyectos.count()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            proyectos, page, item_count=count,
            items_per_page=3,
        )
        proyectos = currentPage.items
        return dict(page='proyecto',
                    proyectos=proyectos, 
                    subtitulo='Proyectos',currentPage = currentPage)
    @expose(template="gestionitem.templates.proyectoDef")
    def proyectoDef(self,id):
        proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
        return dict(page='Definir Proyecto',
                    id=id,proyecto=proyecto,subtitulo='Definicion de Proyectos')
    @expose(template="gestionitem.templates.faseList")
    def faseList(self,id):
        fases = DBSession.query(Fase).order_by(Fase.id)
        proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
        return dict(page='Lista de Fases',
                    id=id,fases=fases,proyecto=proyecto,subtitulo='Lista de Fases')
    
    @expose(template="gestionitem.templates.faseDef")
    def faseDef(self,id):
        fases = DBSession.query(Fase).order_by(Fase.id)
        proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
        return dict(page='Lista de Fases',
                    id=id,fases=fases,proyecto=proyecto,subtitulo='Lista de Fases')
    
   
  


    @expose(template='gestionitem.templates.permiso')
    def permiso(self, **named):
        permisos=DBSession.query(Permission).order_by( Permission.description )
        from webhelpers import paginate
        count = permisos.count()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            permisos, page, item_count=count,
            items_per_page=5,
        )
        permisos = currentPage.items

        return dict(page='permiso',
                    permisos=permisos, 
                    subtitulo='ABM-Permisos',currentPage = currentPage)
        
    @expose('gestionitem.templates.agregar_permiso')
    def agregar_permiso(self):
        permiso = Permission
        permiso.permission_name = ''
        permiso.description =''
        permisos=DBSession.query(Permission)
        return dict(page = 'Nuevo Permiso',
                    permisos = permisos, 
                    permiso = permiso, subtitulo = 'ABM-Permiso')
    @expose()
    def save_permiso( self, id, name,descripcion, submit ):
        """Crea un nuevo permiso"""
        new = Permission(
            permission_name = name,
            description = descripcion,
        )
        DBSession.add( new )
        redirect( './permiso' )    
        flash( '''Permiso Agregado! %s''')
        
    @expose()
    def eliminar_permiso(self,id):
        #recurso = DBSession.query(Recurso).filter_by(id=id).delete()
        #permiso=DBSession.query(Permission).filter_by(id=id).one()
        DBSession.delete(DBSession.query(Permission).filter_by(permission_id=id).one())
        redirect( '../permiso' ) 
        
    @expose(template="gestionitem.templates.permiso_editar")
    def permiso_editar(self,id):
        permiso = DBSession.query(Permission).filter_by(permission_id=id).one()
        return dict(page='Editar Permiso',
                    id=id,permiso=permiso,subtitulo='ABM-Permiso')
        
    @expose()
    def actualizar_permiso( self, id, name,descripcion, submit ):
        """Create a new movie record"""
       
        permiso = DBSession.query(Permission).filter_by(permission_id=id).one()
       
        permiso.permission_name = name
        permiso.description = descripcion
        
        DBSession.flush()
       
        redirect( './permiso' )
    
      
    
    
    
    
    
    
    
    @expose('gestionitem.templates.about')
    def about(self):
        """Handle the 'about' page."""
        #aux=Recurso()
 
        return dict(page='about',aux= 'hola' ,subtitulo='About')

    @expose('gestionitem.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(environment=request.environ,subtitulo='')

    @expose('gestionitem.templates.data')
    @expose('json')
    def data(self, **kw):
        """This method showcases how you can use the same controller for a data page and a display page"""
        return dict(params=kw)

    @expose('gestionitem.templates.authentication')
    def auth(self):
        """Display some information about auth* on this application."""
        return dict(page='auth',subtitulo='Autenticacion')

    @expose('gestionitem.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff',subtitulo='')

    @expose('gestionitem.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('gestionitem.templates.login')
    def login(self, came_from=url('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Error de acceso'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from,subtitulo='Loguin')

    @expose()
    def post_login(self, came_from='/'):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect('/login', came_from=came_from, __logins=login_counter)
        userid = request.identity['repoze.who.userid']
        flash(_('Bienvenido, %s!') % userid)
        redirect(came_from)

    
    @expose()
    def post_logout(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('Hasta pronto!'))
        redirect('/index')

    