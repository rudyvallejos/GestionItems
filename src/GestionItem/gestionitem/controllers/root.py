# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.controller import AdminController
from repoze.what import predicates
from tgext.admin import AdminController, AdminConfig


from gestionitem.lib.base import BaseController
from gestionitem.model import DBSession, metadata, Recurso, TipoItemUsuario, Proyecto,TipoItemUsuarioAtributos
from gestionitem import model 
from gestionitem.controllers.secure import SecureController
from gestionitem.controllers.error import ErrorController
from sprox.formbase import AddRecordForm
from tw.forms import TextField,CalendarDatePicker
from tg import tmpl_context
from tg import validate
from sqlalchemy.orm import sessionmaker
from gestionitem.model.auth import Group, User, Permission
#from gestionitem.controllers.rest import TipoRestController


from gestionitem.controllers.proyectoController import ProyectoController
from gestionitem.controllers.tipoItemControler import TipoItemControler
from gestionitem.controllers.myAdminConfig import MyAdminConfig
from tg import config





__all__ = ['RootController']

class AddMovie(AddRecordForm):
    __model__ = Recurso
    __omit_fields__ = [
        'id'
    ]
    #descripcion = TextField

      
    
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
    
    proyecto = ProyectoController()
    
    tipoItems = TipoItemControler()
    
    secc = SecureController()
#    tipoItemUsuario = TipoRestController()
#    admin = AdminController(model, DBSession)

   
    admin = AdminController([User, Group, Permission], DBSession, config_type=MyAdminConfig)

    error = ErrorController()
    dict(subtitulo='')
    
    @expose('gestionitem.templates.index')
    def index(self):
        """Handle the front-page."""
        return dict(page='Indice',subtitulo='Indice')
   
    @expose(template='gestionitem.templates.recurso')
    def recurso(self, **named):
        recursos=DBSession.query(Recurso).order_by( Recurso.id )
        from webhelpers import paginate
        count = recursos.count()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            recursos, page, item_count=count,
            items_per_page=3,
        )
        recursos = currentPage.items

        return dict(page='recurso',
                    recursos=recursos, 
                    subtitulo='ABM-Recurso',currentPage = currentPage)
 
    @expose('gestionitem.templates.agregar_recurso')
    def agregar_recurso(self):
        #recurso=DBSession.query(Recurso).filter_by(id=6).one()
        recurso=Recurso
        recurso.descripcion=''
        recursos=DBSession.query(Recurso)
        return dict(page='Nuevo recurso',
                    recursos=recursos, 
                    recurso=recurso,subtitulo='ABM-Recurso')
    @expose()
    def save( self, id, data, submit ):
        """Create a new movie record"""
        new = Recurso(
            descripcion = data,
        )
        DBSession.add( new )
        redirect( './recurso' )    
        flash( '''Recurso Agregado! %s''')
    @expose()
    def actualizar( self, id, data, submit ):
        """Create a new movie record"""
       
        Session = sessionmaker(bind=Recurso)
        session = Session()
        recurso = DBSession.query(Recurso).filter_by(id=id).one()
        #recurso=q.filter_by(id=id).one()

        #session = create_session(bind=Recurso, autocommit=True, autoflush=False)
        #recurso = session.query(Recurso)
        recurso.descripcion=data
        #DBSession.update( new )
        #DBSession.commit()
        #setattr(recurso, id, data)
        #recurso.data=data
        #session.merge(data)
        #DBSession.execute("update recurso set descripcion=:data where id=:id", {'data':data,'id':id})
        DBSession.flush()
        #recurso.update(recurso,synchronize_session='expire')
        redirect( './recurso' )
    
    @expose()
    def eliminar_recurso(self,id):
        #recurso = DBSession.query(Recurso).filter_by(id=id).delete()
        recurso=DBSession.query(Recurso).filter_by(id=id).one()
        DBSession.delete(DBSession.query(Recurso).filter_by(id=id).one())
        redirect( '../recurso' )        
          
    @expose(template="gestionitem.templates.recurso_editar")
    def recurso_editar(self,id):
        recurso = DBSession.query(Recurso).filter_by(id=id).one()
        return dict(page='Editar recurso',
                    id=id,recurso=recurso,subtitulo='ABM-Recurso')



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
        aux=DBSession.query(Recurso).filter_by(id=1).one()
        return dict(page='about',aux=aux,subtitulo='About')

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
        redirect(came_from)

    