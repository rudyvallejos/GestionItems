from gestionitem.lib.base import BaseController
from tg import redirect 
from tg import expose, flash, require, url, request, redirect
from gestionitem.model import DBSession, metadata, Recurso, TipoItemUsuario, Proyecto,TipoItemUsuarioAtributos


class TipoItemControler(BaseController):
      
    @expose('gestionitem.templates.tipoItemUsuario')
    def tipoItemUsuario(self,id,**named):
        proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
        tiposItemUs=DBSession.query(TipoItemUsuario).order_by( TipoItemUsuario.id )
        from webhelpers import paginate
        count = tiposItemUs.count()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            tiposItemUs, page, item_count=count,
            items_per_page=3,
        )
        tiposItemUs = currentPage.items

        return dict(page='tipoItemUsuario',
                    tiposItemUs=tiposItemUs, proyecto=proyecto,
                    subtitulo='ABM-TipoItemUsuario',currentPage = currentPage)
    
    @expose('gestionitem.templates.agregar_tipoItem')
    def agregar_tipoItem(self,id):
        proyecto=DBSession.query(Proyecto).filter_by(id=id).one()
        tipoItem=TipoItemUsuario
        tipoItem.descripcion=''
        #recursos=DBSession.query(Recurso)
        return dict(page='Nuevo recurso',
                    proyecto=proyecto, 
                    tipoItem=tipoItem,subtitulo='ABM-Recurso')
    @expose()
    def saveItem( self, id,idProy, descripcion,submit ):
        """Create a new movie record"""
        new = TipoItemUsuario(
            descripcion = descripcion,
            proyecto_id = idProy
        )
        DBSession.add( new )
        redirect( './agregar_tipoItem/'+idProy )    
        flash( '''Tipo Item Agregado! %s''')
    @expose('gestionitem.templates.atributosDef')
    def atributosDef(self,id,**named):
        tipoItem = DBSession.query(TipoItemUsuario).filter_by(id=id).one()
        atributos=DBSession.query(TipoItemUsuarioAtributos).order_by( TipoItemUsuarioAtributos.id )
        from webhelpers import paginate
        count = atributos.count()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            atributos, page, item_count=count,
            items_per_page=3,
        )
        atributos = currentPage.items

        return dict(page='tipoItemUsuario',
                    atributos=atributos, tipoItem=tipoItem,
                    subtitulo='ABM-TipoItemUsuario',currentPage = currentPage)
    @expose('gestionitem.templates.agregar_Atributo')
    def agregar_Atributo(self,id):
        tipoItem=DBSession.query(TipoItemUsuario).filter_by(id=id).one()
        atributo=TipoItemUsuarioAtributos
        atributo.descripcion=''
        #recursos=DBSession.query(Recurso)
        return dict(page='Nuevo Atributo',
                    atributo=atributo, 
                    tipoItem=tipoItem,subtitulo='ABM-Recurso')

