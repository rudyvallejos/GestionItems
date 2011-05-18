from gestionitem.lib.base import BaseController
from tg import redirect
from sqlalchemy import or_ 
from tg import expose, flash, require, url, request, redirect
from gestionitem.model import DBSession, metadata, Recurso, TipoItemUsuario, Proyecto,Tipo,TipoItemUsuarioAtributos


class TipoItemControler(BaseController):
      
    @expose('gestionitem.templates.tipoItem.tipoItemUsuario')
    def tipoItemUsuario(self,id,expresion,**named):
        if expresion=="lista":
            muestraBoton="false"    
            proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
            tiposItemUs=DBSession.query(TipoItemUsuario).order_by( TipoItemUsuario.id )
        else :
            muestraBoton="true"  
            if expresion.isdigit():
                proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
                tiposItemUs=DBSession.query(TipoItemUsuario).filter_by(id=expresion)     
            else:    
                proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
                tiposItemUs=DBSession.query(TipoItemUsuario).filter((TipoItemUsuario.descripcion.like('%'+expresion+'%'))).order_by( TipoItemUsuario.id )
                
        from webhelpers import paginate
        count = tiposItemUs.count()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            tiposItemUs, page, item_count=count,
            items_per_page=3,
        )
        tiposItemUs = currentPage.items

        return dict(muestraBoton=muestraBoton,page='tipoItemUsuario',
                    tiposItemUs=tiposItemUs, proyecto=proyecto,
                    subtitulo='ABM-TipoItemUsuario',currentPage = currentPage)
    @expose(template="gestionitem.templates.tipoItem.tipoItem_editar")
    def tipoItem_editar(self,id,idProy):
        proyecto = DBSession.query(Proyecto).filter_by(id=idProy).one()
        tipoItem=DBSession.query(TipoItemUsuario).filter_by(id=id).one()
        return dict(page='Editar Atributo',
                    id=id,proyecto=proyecto,tipoItem=tipoItem,subtitulo='TipoItem-Editar')
    @expose()
    def actualizar_tipoItem( self,id,idProy,nombre, submit ):
        """Create a new movie record"""
        tipoItem = DBSession.query(TipoItemUsuario).filter_by(id=id).one()
        tipoItem.descripcion=nombre,
        DBSession.flush()
        redirect( '/tipoItems/tipoItemUsuario/'+ idProy+'/lista')
 
    @expose('gestionitem.templates.tipoItem.agregar_tipoItem')
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
        redirect( './tipoItemUsuario/'+idProy+'/lista' )    
        flash( '''Tipo Item Agregado! %s''')
    @expose()
    def eliminar_tipoItem(self,idProy,id):
        DBSession.delete(DBSession.query(TipoItemUsuario).filter_by(id=id).one())
        redirect( '/tipoItems/tipoItemUsuario/'+ idProy+'/lista') 

    
       
    @expose('gestionitem.templates.tipoItem.atributosDef')
    def atributosDef(self,id,**named):
        tipoItem = DBSession.query(TipoItemUsuario).filter_by(id=id).one()
        atributos=DBSession.query(TipoItemUsuarioAtributos).filter_by(tipo_item_id=id).order_by( TipoItemUsuarioAtributos.id )    
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
        
    @expose('gestionitem.templates.tipoItem.agregar_Atributo')
    def agregar_Atributo(self,id):
        tipoItem=DBSession.query(TipoItemUsuario).filter_by(id=id).one()
        tipos=DBSession.query(Tipo).order_by(Tipo.id)
        atributo=TipoItemUsuarioAtributos
        atributo.descripcion=''
        return dict(page='Nuevo Atributo',
                    atributo=atributo, 
                    tipoItem=tipoItem,tipos=tipos,subtitulo='Agregar-Atributos')
    @expose()
    def saveItemAtri( self, id,descripcion, tipoId,submit ):
        """Create a new movie record"""
        new = TipoItemUsuarioAtributos(
            tipo_item_id=id,
            nombre_atributo = descripcion,
            tipo_id = tipoId
        )
        DBSession.add( new )
        redirect( './atributosDef/'+id )    
        flash( '''Atributo Agregado! %s''')
    @expose(template="gestionitem.templates.tipoItem.atributo_editar")
    def atributo_editar(self,id,idAtributo):
        atributo = DBSession.query(TipoItemUsuarioAtributos).filter_by(id=idAtributo).one()
        tipoItem=DBSession.query(TipoItemUsuario).filter_by(id=id).one()
        tipo=DBSession.query(Tipo).filter_by(id=atributo.tipo_id).order_by(Tipo.id)
        tipos=DBSession.query(Tipo).order_by(Tipo.id)
        return dict(page='Editar Atributo',
                    id=id,tipo=tipo,idTipo=atributo.tipo_id,tipos=tipos,tipoItem=tipoItem,atributo=atributo,subtitulo='Atributo-Editar')
    @expose()
    def actualizar_atributo( self,tipo_item_id, id, nombre,idTipo, submit ):
        """Create a new movie record"""
        atributo = DBSession.query(TipoItemUsuarioAtributos).filter_by(id=id).one()
        atributo.nombre_atributo=nombre,
        atributo.tipo_item_id=tipo_item_id,
        atributo.tipo_id=idTipo,
        DBSession.flush()
        redirect( './atributosDef/'+ tipo_item_id)
    @expose()
    def eliminar_atributo(self,tipo_item_id,id):
        DBSession.delete(DBSession.query(TipoItemUsuarioAtributos).filter_by(id=id).one())
        redirect( '/tipoItems/atributosDef/'+ tipo_item_id) 

    
