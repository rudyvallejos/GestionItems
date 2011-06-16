from gestionitem.lib.base import BaseController
#from sqlalchemy import or_ 
from tg import expose, flash,redirect
from gestionitem.model import DBSession
from gestionitem.model.proyecto import Fase,Proyecto
from gestionitem.model.tipoItemUsuario import TipoItemUsuario,TipoItemUsuarioAtributos, Tipo


class TipoItemControler(BaseController):
      
    @expose('gestionitem.templates.tipoItem.tipoItemUsuario')
    def tipoItemUsuario(self,id,expresion,**named):
        if expresion=="lista":
            muestraBoton="false"    
            fase = DBSession.query(Fase).filter_by(id=id).one()
            proyecto = DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
            tiposItemUs=DBSession.query(TipoItemUsuario).filter_by(fase_id=fase.id).order_by( TipoItemUsuario.id )
        else :
            muestraBoton="true"  
            if expresion.isdigit():
                fase = DBSession.query(Fase).filter_by(id=id).one()
                proyecto = DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
                tiposItemUs=DBSession.query(TipoItemUsuario).filter_by(fase_id=fase.id).filter_by(id=expresion)     
            else:
                fase = DBSession.query(Fase).filter_by(id=id).one()    
                proyecto = DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
                tiposItemUs=DBSession.query(TipoItemUsuario).filter_by(fase_id=fase.id).filter((TipoItemUsuario.descripcion.like('%'+expresion+'%'))).order_by(TipoItemUsuario.id)
                
        from webhelpers import paginate
        count = tiposItemUs.count()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            tiposItemUs, page, item_count=count,
            items_per_page=3,
        )
        tiposItemUs = currentPage.items

        return dict(muestraBoton=muestraBoton,page='tipoItemUsuario',fase=fase,
                    tiposItemUs=tiposItemUs, proyecto=proyecto,
                    subtitulo='ABM-TipoItemUsuario',currentPage = currentPage)
    @expose(template="gestionitem.templates.tipoItem.tipoItem_editar")
    def tipoItem_editar(self,id,idFase):
        fase=DBSession.query(Fase).filter_by(id=idFase).one()
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        tipoItem=DBSession.query(TipoItemUsuario).filter_by(id=id).one()
        todosItems=DBSession.query(TipoItemUsuario).filter_by(fase_id=fase.id)
        codigos=[]
        for i, itemUser in enumerate(todosItems):
            codigos.append(itemUser.codigo)
            codigos.append(",")
        
        
        return dict(page='Editar Tipo de Item',codigos=codigos,
                    id=id,proyecto=proyecto,fase=fase,tipoItem=tipoItem,subtitulo='TipoItem-Editar')
    @expose()
    def actualizar_tipoItem( self,id,idProy, idFase,codItem,nombre, submit ):
        """Create a new movie record"""
        tipoItem = DBSession.query(TipoItemUsuario).filter_by(id=id).one()
        tipoItem.descripcion=nombre,
        tipoItem.codigo=codItem,
        DBSession.flush()
        redirect( '/tipoItems/tipoItemUsuario/'+ idFase+'/lista')
 
    @expose('gestionitem.templates.tipoItem.agregar_tipoItem')
    def agregar_tipoItem(self,id):
        fase=DBSession.query(Fase).filter_by(id=id).one()
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        todosItems=DBSession.query(TipoItemUsuario).filter_by(fase_id=fase.id)
        codigos=[]
        for i, itemUser in enumerate(todosItems):
            codigos.append(itemUser.codigo)
            codigos.append(",")
        
        tipoItem=TipoItemUsuario()
        tipoItem.descripcion=''
        tipoItem.codigo=''
        #fases=DBSession.query(Fase).filter_by(proyecto_id=id)
        return dict(page='Nuevo recurso',codigos=codigos,fase=fase,
                    proyecto=proyecto, 
                    tipoItem=tipoItem,subtitulo='ABM-Recurso')
    @expose()
    def saveItem( self, idProy, idFase, codItem, descripcion,submit ):
        """Create a new movie record"""
        new = TipoItemUsuario(
            descripcion = descripcion,
            fase_id = idFase,
            codigo = codItem
        )
        DBSession.add( new )
        redirect( './tipoItemUsuario/'+idFase+'/lista' )    
        flash( '''Tipo Item Agregado! %s''')
    @expose()
    def eliminar_tipoItem(self,idFase,id):
  
        tipoAtrib=DBSession.query(TipoItemUsuarioAtributos).filter(TipoItemUsuarioAtributos.tipo_item_id==id)
        for i, atri in enumerate(tipoAtrib):
            DBSession.delete(atri) 
        DBSession.delete(DBSession.query(TipoItemUsuario).filter_by(id=id).one())
        redirect( '/tipoItems/tipoItemUsuario/'+ idFase+'/lista') 

    
       
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
        atributo=TipoItemUsuarioAtributos()
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

    
