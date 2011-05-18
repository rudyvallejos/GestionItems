from gestionitem.lib.base import BaseController
from tg import redirect
from sqlalchemy import or_
from tg import expose, flash, require, url, request, redirect
from gestionitem.model import DBSession, metadata, Recurso, TipoItemUsuario, Proyecto,Tipo,TipoItemUsuarioAtributos, ItemUsuario, Fase,TipoItemUsuarioAtributosValor, RelacionItem

from sqlalchemy import schema as sa_schema
from sqlalchemy import sql, schema, exc, util
from sqlalchemy.engine import base, default, reflection
from sqlalchemy.sql import compiler, expression, util as sql_util
from sqlalchemy.sql import operators as sql_operators
from sqlalchemy import types as sqltypes



class ItemControler(BaseController):
      
    @expose('gestionitem.templates.item.itemList')
    def itemList(self,id,expresion,**named):
        if expresion=="lista":
            muestraBoton="false"
            items = DBSession.query(ItemUsuario).filter_by(fase_id=id).order_by(ItemUsuario.id)
            for item_aux in items:
                item_aux.relaciones=DBSession.query(RelacionItem).filter_by(antecesor_item_id=item_aux.id).order_by(RelacionItem.id)
            fase = DBSession.query(Fase).filter_by(id=id).one()    
            proyecto = DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
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
        count = items.count()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            items, page, item_count=count, 
            items_per_page=3,
        )
        items = currentPage.items

        return dict(muestraBoton=muestraBoton,page='Lista de Items',
                    tiposItemUs=tiposItemUs, fase=fase,items=items, proyecto=proyecto,
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
 
    @expose('gestionitem.templates.item.agregar_item')
    def agregar_item(self,id,tipo):
        compleLista=[2,3,4,5,6,7,8,9]
        fase=DBSession.query(Fase).filter_by(id=id).one()
        if tipo!="0":
            tipos=DBSession.query(TipoItemUsuario).filter_by(id=tipo).one()
            atributos=DBSession.query(TipoItemUsuarioAtributos).filter_by(tipo_item_id=tipos.id).order_by(TipoItemUsuarioAtributos.id)
            lista=range(100)
            
            for i, atributo in enumerate(atributos):
                atributo.valor.valor=""
                lista[i]=""
               
        else:
            tipos=0
            atributos=""
            lista=[]    
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        tipoItems=DBSession.query(TipoItemUsuario).filter_by(proyecto_id=proyecto.id).order_by(TipoItemUsuario.id)
        defecto=TipoItemUsuario
        #defecto.id=0
        #defecto.descripcion='default'
        #tipoItems.add=defecto
        item=ItemUsuario
        item.cod_item=""
        item.descripcion=""
        #recursos=DBSession.query(Recurso)
        return dict(page='Nuevo Item', atributos=atributos,
                    fase=fase,tipos=tipos, tipoItems=tipoItems, compleLista=compleLista,  
                    proyecto=proyecto,lista=lista, 
                    item=item,subtitulo='ABM-Item')
    @expose()
    def saveItem( self,idFase,idProy, codItem,complejidad,descripcion,tipoItem, lista,idAtributos, submit,):
        listaIds=DBSession.query(ItemUsuario).order_by(ItemUsuario.id)
        if (listaIds.count()>0):
            list=listaIds[-1]
            id=list.id + 1
        else: 
            id=1                            
        if (tipoItem!="0"):
            new = ItemUsuario(
                id=id,                              
                tipo_item_id = tipoItem,
                fase_id = idFase,
                cod_item=codItem,
                prioridad=complejidad,
                descripcion=descripcion,
                estado_id=1
            )
            DBSession.add( new )
            DBSession.flush()
            #id= DBSession.execute("select nextval('item_usuario_id_seq')")
            #id=DBSession.fire_sequence("item_usuario_id_seq")
            #idItem=DBSession.query(ItemUsuario).filter(ItemUsuario.cod_item==codItem).order_by(ItemUsuario.id)                        
            #idItem=DBSession.query(ItemUsuario).filter((ItemUsuario.cod_item.like('%'+nuevo+'%'))).order_by(ItemUsuario.id )
            
            #for  id in idItem:
             #   if (id.cod_item==codItem):
             #       identificador=id.id
            
            for i, valor in enumerate(lista):
                new2 = TipoItemUsuarioAtributosValor(
                item_usuario_id = id, 
                atributo_id = idAtributos[i],
                valor=valor
                )
                DBSession.add( new2 )
        else:
             if(tipoItem=="0"):
                new = ItemUsuario(
                    id=id,                              
                    fase_id = idFase,
                    cod_item=codItem,
                    prioridad=complejidad,
                    descripcion=descripcion,
                    estado_id=1
                )
                DBSession.add( new )
                DBSession.flush()
        if (submit!="Relacionar"):        
            redirect( '/item/itemList/'+idFase+'/lista' )
            flash( '''Tipo Item Agregado! %s''')
        else:
            if(submit=="Relacionar"):
                redirect( '/item/relacionar_item/'+str(id)+'/'+ idFase+'/lista/todos')    
            
    @expose()
    def eliminar_tipoItem(self,idProy,id):
        DBSession.delete(DBSession.query(TipoItemUsuario).filter_by(id=id).one())
        redirect( '/tipoItems/tipoItemUsuario/'+ idProy+'/lista') 

    
    @expose('gestionitem.templates.item.relacionar_item')
    def relacionar_item(self,id,idFase,fases,submit,**named):
        fases_selec=fases
        itemUsuario=DBSession.query(ItemUsuario).filter_by(id=id).one()
        fase=DBSession.query(Fase).filter_by(id=itemUsuario.fase_id).one()
        if (fases=="lista"):
            items=DBSession.query(ItemUsuario).filter_by(id=-1)
        else:
            items=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id.in_(fases)).order_by(ItemUsuario.id)
        lista=range(100)
        lista=""   
        fases=DBSession.query(Fase).order_by(Fase.id)
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        tipoItems=DBSession.query(TipoItemUsuario).filter_by(proyecto_id=proyecto.id).order_by(TipoItemUsuario.id)
        defecto=TipoItemUsuario
        item=itemUsuario
        from webhelpers import paginate
        count = items.count()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            items, page, item_count=count, 
            items_per_page=3,
        )
        items = currentPage.items      
        #recursos=DBSession.query(Recurso)
        return dict(page='Nuevo Item',items=items,fases_selec=fases_selec,
                    fase=fase,fases=fases, tipoItems=tipoItems,  
                    proyecto=proyecto,lista=lista,currentPage = currentPage, 
                    item=item,subtitulo='ABM-Item')
    @expose()
    def saveRelacion( self, id,itemselect,submit ):
        item=DBSession.query(ItemUsuario).filter_by(id=id).one()
        for i, itemRelacion in enumerate(itemselect):
            new = RelacionItem(
                               antecesor_item_id=id,
                               sucesor_item_id = itemRelacion,
                               )
            DBSession.add( new )
            DBSession.flush()
        item.estado_id=2
        DBSession.flush()
        redirect( '/item/itemList/'+str(item.fase_id)+'/lista' )    
        flash( '''Atributo Agregado! %s''') 
              
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

    
