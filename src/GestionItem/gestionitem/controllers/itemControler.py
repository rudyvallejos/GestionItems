from gestionitem.lib.base import BaseController
from tg import redirect
from sqlalchemy import or_, and_
from tg import expose, flash, require, url, request, redirect
from gestionitem.model.proyecto import ItemUsuario,Proyecto,RelacionItem,Fase,LineaBase
from gestionitem.model.tipoItemUsuario import TipoItemUsuario,TipoItemUsuarioAtributos,TipoItemUsuarioAtributosValor
from gestionitem.model import DBSession 
from tw.forms import TextField,CalendarDatePicker
from sqlalchemy import schema as sa_schema
from sqlalchemy import sql, schema, exc, util
from sqlalchemy.engine import base, default, reflection
from sqlalchemy.sql import compiler, expression, util as sql_util
from sqlalchemy.sql import operators as sql_operators
from sqlalchemy import types as sqltypes
from webhelpers import paginate
from sets import Set
from tw.api import WidgetsList
#Libreria para graficar
import pygraphviz as pgv



 
class ItemControler(BaseController):

    @expose(template="gestionitem.templates.item.faseList")
    def faseList(self,id, **named):
        fases = DBSession.query(Fase).filter_by(proyecto_id=id).order_by(Fase.id).all()
        proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        mensajes=[]
        for i, fase in enumerate(fases):
            lbs = DBSession.query(LineaBase).filter_by(fase_id=fase.id).order_by(LineaBase.id).all()
            existe_sol=0
            for lb in lbs:
                if (lb.apertura=="1"):
                    existe_sol=1
            if existe_sol:
                mensajes.append("Solicitud de Apertura de LB")
            else:
                mensajes.append("")
        return dict(page='Lista de Fases',user=user,mensajes=mensajes,
                    id=id,fases=fases,proyecto=proyecto,subtitulo='Lista de Fases')
          
    @expose('gestionitem.templates.item.itemList')
    def itemList(self,id,**named):
        

        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        expresion=named.get('expresion','lista')
        existeLB=0
        if expresion=="lista":
            muestraBoton="false"
            items = DBSession.query(ItemUsuario).filter_by(fase_id=id).order_by(ItemUsuario.id).all()
            for item_aux in items:
                item_aux.relaciones=DBSession.query(RelacionItem).filter_by(antecesor_item_id=item_aux.id).order_by(RelacionItem.id)
                if item_aux.estado.id==3:
                    existeLB=1;
            fase = DBSession.query(Fase).filter_by(id=id).one()    
            proyecto = DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
            tiposItemUs=DBSession.query(TipoItemUsuario).order_by( TipoItemUsuario.id )
        else :
            muestraBoton="true"
            fase = DBSession.query(Fase).filter_by(id=id).one()      
            proyecto = DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
            items = DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==id).filter(or_(ItemUsuario.descripcion.like('%'+expresion+'%'),(ItemUsuario.cod_item.like('%'+expresion+'%')))).order_by(ItemUsuario.id).all()
            for item_aux in items:
                if item_aux.estado.id==3:
                    existeLB=1;
            fase = DBSession.query(Fase).filter_by(id=id).one()    
            proyecto = DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
            tiposItemUs=DBSession.query(TipoItemUsuario).order_by( TipoItemUsuario.id )    
        from webhelpers import paginate
        #count = items.count()
        count = items.__len__()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            items, page, item_count=count, 
            items_per_page=5,
        )
        items = currentPage.items

        return dict(muestraBoton=muestraBoton,page='Lista de Items',user=user,existeLB=existeLB,
                    tiposItemUs=tiposItemUs, fase=fase,items=items, proyecto=proyecto,
                    subtitulo='Lista de Items',currentPage = currentPage)
    @expose(template="gestionitem.templates.tipoItem.tipoItem_editar")
    def tipoItem_editar(self,id,idProy):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        proyecto = DBSession.query(Proyecto).filter_by(id=idProy).one()
        tipoItem=DBSession.query(TipoItemUsuario).filter_by(id=id).one()
        return dict(page='Editar Atributo',user=user,
                    id=id,proyecto=proyecto,tipoItem=tipoItem,subtitulo='TipoItem-Editar')
    @expose()
    def actualizar_tipoItem( self,id,idProy,nombre, submit ):
        """Create a new movie record"""
        tipoItem = DBSession.query(TipoItemUsuario).filter_by(id=id).one()
        tipoItem.descripcion=nombre,
        DBSession.flush()
        redirect( '/tipoItems/tipoItemUsuario/'+ idProy+'/lista')
 
    @expose('gestionitem.templates.item.agregar_item')
    def agregar_item(self,idFase,tipo):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        compleLista=[2,3,4,5,6,7,8,9]
        item=ItemUsuario()
        todosItems=DBSession.query(ItemUsuario).filter_by(fase_id=idFase)
        codigos=[]
        for i, itemUser in enumerate(todosItems):
           codigos.append(itemUser.cod_item)
           codigos.append(",")
            
        fase=DBSession.query(Fase).filter_by(id=idFase).one()
        if tipo!="0":
            tipos=DBSession.query(TipoItemUsuario).filter_by(id=tipo).one()
            atributos=DBSession.query(TipoItemUsuarioAtributos).filter_by(tipo_item_id=tipos.id).order_by(TipoItemUsuarioAtributos.id)
            lista=range(100)
            #Obtiene la lista de todos los codigos actuales para aumentar en 1 
            listaNumCod=DBSession.query(ItemUsuario).filter_by(tipo_item_id=tipos.id).filter(ItemUsuario.fase_id==idFase).order_by(ItemUsuario.numero_cod)
            if (listaNumCod.count()>0):
                list=listaNumCod[-1]
                numCod=list.numero_cod + 1
            else: 
                numCod=1
            #Fin Obtine lista en numCod se guarda el numero_cod actual    
            item.cod_item=fase.codigo_fase+"-"+tipos.codigo+"-"+str(numCod)
            item.numero_cod=numCod
            for i, atributo in enumerate(atributos):
                atributo.valor.valor=""
                lista[i]=""
               
        else:
            #Obtiene la lista de todos los codigos actuales para aumentar en 1 
            listaNumCod=DBSession.query(ItemUsuario).filter(ItemUsuario.tipo_item_generico==1).filter(ItemUsuario.fase_id==idFase).order_by(ItemUsuario.numero_cod)
            if (listaNumCod.count()>0):
                list=listaNumCod[-1]
                numCod=list.numero_cod + 1
            else: 
                numCod=1
            tipos=0
            atributos=""
            lista=[]    
            #Fin Obtine lista en numCod se guarda el numero_cod actual    
            item.cod_item=fase.codigo_fase+"-DF"+"-"+str(numCod)
            item.numero_cod=numCod
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        tipoItems=DBSession.query(TipoItemUsuario).filter_by(fase_id=idFase).order_by(TipoItemUsuario.id).all()
        defecto=TipoItemUsuario
        #defecto.id=0
        #defecto.descripcion='default'
        #tipoItems.add=defecto
        
        item.descripcion=""
        #recursos=DBSession.query(Recurso)
        return dict(page='Nuevo Item',todosItems=todosItems,codigos=codigos, atributos=atributos,
                    fase=fase,tipos=tipos, tipoItems=tipoItems, compleLista=compleLista,  
                    proyecto=proyecto,lista=lista,user=user, 
                    item=item,subtitulo='ABM-Item')
    @expose()
    def updateItemConTipo( self,idFase,idProy,idItem,TipoItem ,numCod,codItem,complejidad,descripcion, lista,idAtributos, submit):                
        try:
            for i, valor in enumerate(lista):
                atributo = DBSession.query(TipoItemUsuarioAtributosValor).filter_by(item_usuario_id=idItem).filter_by(atributo_id=idAtributos[i]).one()
                atributo.valor=valor
                DBSession.flush()
        except:        
            atributo = DBSession.query(TipoItemUsuarioAtributosValor).filter_by(atributo_id=idAtributos).filter_by(item_usuario_id=idItem).one()
            atributo.valor=lista
            DBSession.flush() 
        item = DBSession.query(ItemUsuario).filter_by(id=idItem).one()
        item.prioridad=complejidad
        item.descripcion=descripcion
        if (item.estado_id!=1):
            item.estado_id=2
        DBSession.flush()
        fase = DBSession.query(Fase).filter_by(id=idFase).one()          
        if (submit=="Modificar Relaciones"):        
            redirect( '/item/updateRelacion/'+idFase+'/'+idItem )
            flash( '''Item Modificado! %s''')
        else:
            if(submit=="Modificar Item"):
                redirect( '/item/itemList/'+idFase)    
    @expose()
    def updateItemSinTipo( self,idFase,idProy,idItem,TipoItem , numCod,codItem,complejidad,descripcion, submit):                
        item = DBSession.query(ItemUsuario).filter_by(id=idItem).one()
        item.prioridad=complejidad
        item.descripcion=descripcion
        if (item.estado_id!=1):
            item.estado_id=2
        DBSession.flush()
        fase = DBSession.query(Fase).filter_by(id=idFase).one()          
        if (submit=="Modificar Relaciones"):        
            redirect( '/item/updateRelacion/'+idFase+'/'+idItem )
            flash( '''Item Modificado! %s''')
        else:
            if(submit=="Modificar Item"):
                redirect( '/item/itemList/'+idFase) 
    @expose()
    def saveItemLB( self,idFase,idProy,idItem,tipoItem ,numCod,codItem,complejidad,descripcion,  **named):
        #Obtiene el id del Item a modificar
        itemAnterior=DBSession.query(ItemUsuario).filter_by(id=idItem).one()
        itemAnterior.estado_id=6
        DBSession.flush()
        lista=named.get('lista','')
        submit=named.get('submit','')
        idAtributos=named.get('idAtributos','')
        #Obtiene los items relacionados
        relaciones = DBSession.query(RelacionItem).filter(or_(RelacionItem.sucesor_item_id == itemAnterior.id, RelacionItem.antecesor_item_id == itemAnterior.id)).order_by(RelacionItem.id).all()
        relaciones_antecesores=[]
        relaciones_sucesores=[]
        for i, relacionActual in enumerate(relaciones):
            relaciones_antecesores.append(relacionActual.antecesor_item_id)
            relaciones_sucesores.append(relacionActual.sucesor_item_id)
        itemsRelacionados = DBSession.query(ItemUsuario).filter(or_(ItemUsuario.id.in_(relaciones_antecesores),ItemUsuario.id.in_(relaciones_sucesores))).all()
        for i, itemActual in enumerate(itemsRelacionados):
            
            if (itemActual.estado_id==3):
                itemActual.estado_id=4
                DBSession.flush()
                lineaBase=DBSession.query(LineaBase).filter_by(id=itemActual.linea_base_id)
                lineaBase.estado_id=4
                DBSession.flush()
        version=itemAnterior.version
        version=version+1        
        listaIds=DBSession.query(ItemUsuario).order_by(ItemUsuario.id)
        if (listaIds.count()>0):
            list=listaIds[-1]
            id=list.id + 1
        else: 
            id=1                            
        if (tipoItem!=""):
            new = ItemUsuario()
            new.id=id                              
            new.tipo_item_id = tipoItem
            new.fase_id = idFase
            new.numero_cod = numCod
            new.cod_item=codItem
            new.prioridad=complejidad
            new.descripcion=descripcion
            new.version=version
            new.estado_id=1
            
            DBSession.add( new )
            DBSession.flush()
            cont=0
            for i, valor in enumerate(idAtributos):
                cont=1+cont
            if (cont!=2):
                for i, valor in enumerate(lista):
                    new2 = TipoItemUsuarioAtributosValor(
                    item_usuario_id = id,
                    atributo_id = idAtributos[i],
                    valor=valor
                    )
                    DBSession.add( new2 )
            elif (cont==2):
                new2 = TipoItemUsuarioAtributosValor(
                    item_usuario_id = id,
                    atributo_id = idAtributos,
                    valor=lista
                    )
                DBSession.add( new2 )
        elif(tipoItem==""):
            new = ItemUsuario()
            new.id=id,                              
            new.fase_id = idFase,
            new.cod_item= codItem,
            new.numero_cod = numCod,
            new.prioridad=complejidad,
            new.descripcion=descripcion,
            new.estado_id=1,
            new.version=version,
            new.tipo_item_generico = 1
            DBSession.add( new )
            DBSession.flush()
        fase = DBSession.query(Fase).filter_by(id=idFase).one() 
        relacionesItemAnterior = DBSession.query(RelacionItem).filter(( RelacionItem.antecesor_item_id == itemAnterior.id)).order_by(RelacionItem.id).all()
        itemselect=[]
        tipo=[]
        for i, relacionActual in enumerate(relacionesItemAnterior):
            relacionActual.estado_id=2
            itemselect.append(relacionActual.sucesor_item_id)
            tipo.append(relacionActual.tipo)
            DBSession.flush()
        itemNuevaVersion=DBSession.query(ItemUsuario).filter_by(id=id).one()
        for i, itemRelacion in enumerate(itemselect):
            new = RelacionItem(
                               antecesor_item_id=id,
                               sucesor_item_id = itemRelacion,
                               tipo=tipo[i]
                               )
            DBSession.add( new )
            DBSession.flush()
        itemNuevaVersion.estado_id=2
        DBSession.flush()
        
        
        if (submit!="Relacionar"):        
            redirect( '/item/itemList/'+idFase )
            flash( '''Tipo Item Agregado! %s''')
        else:
            if(submit=="Relacionar" and fase.numero_fase==1):
                redirect( '/item/relacionar_item/'+str(id)+'/'+ idFase+'/1')    
            else:
                if (submit=="Relacionar" and fase.numero_fase!="1"):
                    redirect( '/item/relacionar_item/'+str(id)+'/'+ idFase+'/2') 
    @expose()
    def saveItem( self,idFase,idProy, numCod,codItem,complejidad,descripcion,tipoItem, lista,idAtributos, submit,):
        listaIds=DBSession.query(ItemUsuario).order_by(ItemUsuario.id)
        fase=DBSession.query(Fase).filter_by(id=idFase).one()
        if (listaIds.count()>0):
            list=listaIds[-1]
            id=list.id + 1
        else: 
            id=1                            
        if (tipoItem!="0"):
            new = ItemUsuario()
            new.id=id,                              
            new.tipo_item_id = tipoItem,
            new.fase_id = idFase,
            new.numero_cod = numCod,
            new.cod_item=codItem,
            new.prioridad=complejidad,
            new.descripcion=descripcion,
            new.estado_id=1
            new.version=1
            if (fase.numero_fase==1):
                new.estado_id=2
            DBSession.add( new )
            DBSession.flush()
            try:
                for i, valor in enumerate(lista):
                    new2 = TipoItemUsuarioAtributosValor(
                    item_usuario_id = id,
                    atributo_id = idAtributos[i],
                    valor=valor
                    )
                    DBSession.add( new2 )
            except :
                new2 = TipoItemUsuarioAtributosValor(
                item_usuario_id = id,
                atributo_id = idAtributos,
                valor=lista
                )
                DBSession.add( new2 )
        elif(tipoItem=="0"):
            new = ItemUsuario()
            new.id=id,                              
            new.fase_id = idFase,
            new.cod_item=codItem,
            new.numero_cod = numCod,
            new.prioridad=complejidad,
            new.descripcion=descripcion,
            new.estado_id=1
            new.version=1
            new.tipo_item_generico = 1
            if (fase.numero_fase==1):
                new.estado_id=2 
            DBSession.add( new )
            DBSession.flush()
        fase = DBSession.query(Fase).filter_by(id=idFase).one()          
        if (submit!="Relacionar"):        
            redirect( '/item/itemList/'+idFase )
            flash( '''Tipo Item Agregado! %s''')
        else:
            if(submit=="Relacionar" and fase.numero_fase==1):
                redirect( '/item/relacionar_item/'+str(id)+'/'+ idFase+'/1')    
            else:
                if (submit=="Relacionar" and fase.numero_fase!="1"):
                    redirect( '/item/relacionar_item/'+str(id)+'/'+ idFase+'/2') 
    @expose('gestionitem.templates.item.editar_item')
    def editar_item(self,id,idItem):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user'] 
        fase=DBSession.query(Fase).filter_by(id=id).one()
        compleLista=[1,2,3,4,5,6,7,8,9]
        item=DBSession.query(ItemUsuario).filter_by(id=idItem).one()
        if (item.estado.id==5):
            redirect( '/item/avisoEditarItem/'+ str(item.id))    
        compleLista.remove(item.prioridad)
        idTipo=item.tipo_item_id
        if(idTipo!=None):
            tipo=DBSession.query(TipoItemUsuario).filter(TipoItemUsuario.id==idTipo).one()
        else:
            tipo=TipoItemUsuario() 
            tipo.id=0
            tipo.descripcion="Item tipo general"
        atributos=DBSession.query(TipoItemUsuarioAtributos).filter_by(tipo_item_id=item.tipo_item_id).order_by(TipoItemUsuarioAtributos.id)  
        atrIds=[]
        for i, atr in enumerate(atributos):
            atrIds.append(atr.id)
        atributosValor=DBSession.query(TipoItemUsuarioAtributosValor).filter(TipoItemUsuarioAtributosValor.item_usuario_id==item.id).filter(TipoItemUsuarioAtributosValor.atributo_id.in_(atrIds)).order_by(TipoItemUsuarioAtributosValor.atributo_id)  
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        return dict(page='Editar Item', atributos=atributos,tipo=tipo,
                    fase=fase, compleLista=compleLista, user=user, 
                    proyecto=proyecto, atributosValor=atributosValor,
                    item=item,subtitulo='ABM-Item')
    @expose('gestionitem.templates.item.editar_itemLB')
    def editar_itemLB(self,id,idItem, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user'] 
        fase=DBSession.query(Fase).filter_by(id=id).one()
        compleLista=[1,2,3,4,5,6,7,8,9]
        item=DBSession.query(ItemUsuario).filter_by(id=idItem).one()  
        compleLista.remove(item.prioridad)
        idTipo=item.tipo_item_id
        if(idTipo!=None):
            tipo=DBSession.query(TipoItemUsuario).filter(TipoItemUsuario.id==idTipo).one()
        else:
            tipo=TipoItemUsuario() 
            tipo.id=0
            tipo.descripcion="Item tipo general"
        atributos=DBSession.query(TipoItemUsuarioAtributos).filter_by(tipo_item_id=item.tipo_item_id).order_by(TipoItemUsuarioAtributos.id)  
        atrIds=[]
        for i, atr in enumerate(atributos):
            atrIds.append(atr.id)
        atributosValor=DBSession.query(TipoItemUsuarioAtributosValor).filter(TipoItemUsuarioAtributosValor.item_usuario_id==item.id).filter(TipoItemUsuarioAtributosValor.atributo_id.in_(atrIds)).order_by(TipoItemUsuarioAtributosValor.atributo_id)  
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        return dict(page='Editar Item', atributos=atributos,tipo=tipo,
                    fase=fase, compleLista=compleLista,user=user,  
                    proyecto=proyecto, atributosValor=atributosValor,
                    item=item,subtitulo='ABM-Item')    
    @expose('gestionitem.templates.item.avisoEditarItem')
    def avisoEditarItem(self,id,**named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        itemUsuario=DBSession.query(ItemUsuario).filter_by(id=id).one()
        fase=DBSession.query(Fase).filter_by(id=itemUsuario.fase_id).one()
        ItemsCalculados=[]
        calculoImpacto, ItemsCalculados=self.calcularImpacto(itemUsuario.id, ItemsCalculados,0)
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        itemsCalculados=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(ItemsCalculados)).order_by(ItemUsuario.fase_id).order_by(ItemUsuario.id)
        from webhelpers import paginate
        count = itemsCalculados.count()
        page =int( named.get( 'page', '1'))
        currentPage = paginate.Page(
            itemsCalculados, page, item_count=count, 
            items_per_page=5,
        )
        itemsCalculados = currentPage.items
        item=itemUsuario
        return dict(page='Aviso Editar Item',user=user,
                    fase=fase,itemsCalculados=itemsCalculados,currentPage=currentPage,
                    proyecto=proyecto, calculoImpacto=calculoImpacto,
                    item=item,subtitulo='Aviso')

    @expose()
    def eliminar_item(self,idFase,id):
        antecesor=DBSession.query(RelacionItem).filter(RelacionItem.antecesor_item_id==id)
        for i, ant in enumerate(antecesor):
            DBSession.delete(ant)
        sucesor=DBSession.query(RelacionItem).filter(RelacionItem.sucesor_item_id==id)    
        for i, suc in enumerate(sucesor):
            DBSession.delete(suc)
        atributosValor=DBSession.query(TipoItemUsuarioAtributosValor).filter(TipoItemUsuarioAtributosValor.item_usuario_id==id)
        for i, atrVal in enumerate(atributosValor):
            DBSession.delete(atrVal)
        DBSession.delete(DBSession.query(ItemUsuario).filter_by(id=id).one())
        
        redirect( '/item/itemList/'+idFase) 
    @expose()
    def actualizarRelacion( self, id, tipo, filtros, itemselect,submit ):
        antecesor=DBSession.query(RelacionItem).filter(RelacionItem.antecesor_item_id==id)
        for i, ant in enumerate(antecesor):
            DBSession.delete(ant)
        DBSession.flush()
        item=DBSession.query(ItemUsuario).filter_by(id=id).one()
        for i, itemRelacion in enumerate(itemselect):
            new = RelacionItem(
                               antecesor_item_id=id,
                               sucesor_item_id = itemRelacion,
                               tipo=tipo
                               )
            DBSession.add( new )
            DBSession.flush()
        item.estado_id=2
        DBSession.flush()
        if(submit=="Relacionar"):
                redirect( '/item/itemList/'+str(item.fase_id) )    
        else:
            if (submit!="Relacionar"):
                    redirect( '/item/relacionar_item/'+str(id)+'/'+ str(item.fase_id)+'/1')    
        flash( '''Atributo Agregado! %s''')
   
    
    @expose()
    def saveRelacion( self, id, tipo, filtros, itemselect,submit ):
        item=DBSession.query(ItemUsuario).filter_by(id=id).one()
        for i, itemRelacion in enumerate(itemselect):
            new = RelacionItem(
                               antecesor_item_id=id,
                               sucesor_item_id = itemRelacion,
                               tipo=tipo
                               )
            DBSession.add( new )
            DBSession.flush()
        item.estado_id=2
        DBSession.flush()
        if(submit=="Relacionar"):
                redirect( '/item/itemList/'+str(item.fase_id))    
        else:
            if (submit!="Relacionar"):
                    redirect( '/item/relacionar_item/'+str(id)+'/'+ str(item.fase_id)+'/1')    
        flash( '''Atributo Agregado! %s''')
    def controlCiclos(self, idAntecesor, itemCiclos):
        relacionSucesores = DBSession.query(RelacionItem).filter_by(sucesor_item_id=idAntecesor).order_by(RelacionItem.id).all()
        if (len(relacionSucesores)!=0):
            for iRel in relacionSucesores:
                #OBS: NO se si hace falta
                itemCiclos.append(iRel.antecesor_item_id)
                itemCiclos= self.controlCiclos(iRel.antecesor_item_id, itemCiclos)
        else:
            itemCiclos.append(idAntecesor) 
        return itemCiclos
    @expose('gestionitem.templates.item.editar_relacion')
    def editar_relacion(self,id,idFase,tipo_r, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        fases_selec=""
        itemSeleccionado=DBSession.query(ItemUsuario).filter_by(id=-1)
        itemSelec=named.get( 'itemselect','0')
        if (itemSelec!=0 ):
            itemSeleccionado=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(itemSelec)).order_by(ItemUsuario.id)
        itemUsuario=DBSession.query(ItemUsuario).filter_by(id=id).one()
        fase=DBSession.query(Fase).filter_by(id=itemUsuario.fase_id).one()
        submit=named.get( 'submit')            
        if (tipo_r=="1"):
            #Necesario para el control de ciclos
            relacionSucesores = DBSession.query(RelacionItem).filter_by(sucesor_item_id=id).order_by(RelacionItem.id).all()
            #PRUEBA
            itemsSucesores=[0]
            itemCiclos = itemsSucesores
            for iRel in relacionSucesores:
                itemCiclos.append(iRel.antecesor_item_id)
                itemCiclos = self.controlCiclos(iRel.antecesor_item_id, itemCiclos)
            #FIN-PRUEBA
            ##itemsSucesores=[0]
            ##for iRel in relacionSucesores:
            ##    i=DBSession.query(ItemUsuario).filter_by(id=iRel.antecesor_item_id).one()
            ##    itemsSucesores.append(i.id)
         
                
            #Fin-Control de ciclos
            muestraBoton="false"
            tipo=1
            tipoRelacion="Padre/hijo(*)"
            observacion="Una relacion Padre/Hijo indica una relacion entre  2 items pertenecienes a la misma fase"
            #Relacionar solamente con items con LB
            items=DBSession.query(ItemUsuario).filter_by(fase_id=idFase).filter(ItemUsuario.id!=id).filter(~ItemUsuario.id.in_(itemCiclos)).filter_by(estado_id=3)
            fasesRelacion=DBSession.query(Fase).filter_by(id=idFase).one()
            itemSelec=named.get( 'itemselect','0')
            if(submit=="Buscar"): 
                expresion=named.get( 'filtros')
                expre_cad=expresion
                if (itemSelec!='1'):
                    itemSeleccionado=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(itemSelec)).filter_by(estado_id=3).order_by(ItemUsuario.id)
                items=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==idFase).filter(or_(ItemUsuario.descripcion.like('%'+str(expre_cad)+'%'),(ItemUsuario.cod_item.like('%'+str(expre_cad)+'%')))).order_by(ItemUsuario.id)
        else:
            if (tipo_r=="2"):
                muestraBoton="false"
                tipo=2
                tipoRelacion="Antecesor/Sucesor(*)"
                observacion="Una relacion Antecesor/Sucesor indica una relacion entre un item de la fase actual(Antecesor) con un item perteneciente a la fase inmediatamente anterior(Sucesor)"
                faseActual=DBSession.query(Fase).filter_by(id=idFase).one()
                faseAnterior=DBSession.query(Fase).filter_by(numero_fase=faseActual.numero_fase-1).one()
                fasesRelacion=faseAnterior
                items=DBSession.query(ItemUsuario).filter_by(fase_id=faseAnterior.id).filter(ItemUsuario.id!=id).filter_by(estado_id=3)
                itemSelec=named.get( 'itemselect','0')
                if(submit=="Buscar"): 
                    expresion=named.get( 'filtros')
                    expre_cad=expresion
                    if (itemSelec!='1'):
                        itemSeleccionado=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(itemSelec)).order_by(ItemUsuario.id)
                    items=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==faseAnterior.id).filter(or_(ItemUsuario.descripcion.like('%'+str(expre_cad)+'%'),(ItemUsuario.cod_item.like('%'+str(expre_cad)+'%')))).filter_by(estado_id=3).order_by(ItemUsuario.id)                   
        lista=range(100)
        lista=""   
        fases=DBSession.query(Fase).filter(Fase.numero_fase<=fase.numero_fase).order_by(Fase.id)
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        tipoItems=DBSession.query(TipoItemUsuario).filter_by(fase_id=fase.id).order_by(TipoItemUsuario.id)
        defecto=TipoItemUsuario        
        item=itemUsuario
        from webhelpers import paginate
        count = items.count()
        page =int( named.get( 'page', '1'))
        currentPage = paginate.Page(
            items, page, item_count=count, 
            items_per_page=3,
        )
        expresion=str(named.get( 'expresion'))
        expre_cad=expresion
        filtro=""
        return dict(page='Nuevo Item',user=user,itemSeleccionado=itemSeleccionado,named=named,filtro=filtro,itemSelec=itemSelec,parametro=submit, muestraBoton=muestraBoton,tipo=tipo,observacion=observacion,fasesRelacion=fasesRelacion,tipoRelacion=tipoRelacion,items=items,
                    fase=fase,fases=fases, tipoItems=tipoItems,fases_selec=fases_selec,  
                    proyecto=proyecto,lista=lista,currentPage = currentPage, 
                    item=item,subtitulo='ABM-Item')
             
         
    @expose()
    def updateRelacion( self,idFase,idItem,**named):                
        fase = DBSession.query(Fase).filter_by(id=idFase).one()
        submit=named.get( 'submit')            
        if(fase.numero_fase==1 or submit=="Relacionar Padre/Hijo"):
            item_sucesores = DBSession.query(ItemUsuario.id).filter_by(fase_id=idFase).all()
            itemselecccionado = DBSession.query(RelacionItem).filter_by(antecesor_item_id=idItem).filter(RelacionItem.sucesor_item_id.in_(item_sucesores)).all()      
            itemselect=""
            for item in itemselecccionado:
                itemselect=itemselect+"itemselect="+str(item.sucesor_item_id)+"&"
            redirect( '/item/editar_relacion/'+str(idItem)+'/'+ str(fase.id)+'/1?'+str(itemselect))        
        else: 
            itemselecccionado = DBSession.query(RelacionItem).filter_by(antecesor_item_id=idItem).all()      
            itemselect=""
            for item in itemselecccionado:
                itemselect=itemselect+"itemselect="+str(item.sucesor_item_id)+"&"
            redirect( '/item/editar_relacion/'+str(idItem)+'/'+ str(fase.id)+'/2?'+str(itemselect))        
    @expose('gestionitem.templates.item.aprobarItem')
    def aprobarItems(self,idFase, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user'] 
        itemSeleccionado=DBSession.query(ItemUsuario).filter_by(estado_id=8).filter(ItemUsuario.fase_id==idFase).all()
        fase=DBSession.query(Fase).filter_by(id=idFase).one()
        items=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==fase.id).filter(ItemUsuario.estado_id==2).order_by(ItemUsuario.id).all()
        itemSelec=named.get( 'itemselect','0')
        filtro=named.get( 'filtros','')
        if (itemSelec!="0" ):
            listaFiltros=[]
            for fil in itemSelec:
                car=str(fil)
                listaFiltros.append(int(car))
            itemSeleccionado=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(listaFiltros)).order_by(ItemUsuario.id)
        if (filtro!=""):
            items=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==idFase).filter(or_(ItemUsuario.descripcion.like('%'+str(filtro)+'%'),(ItemUsuario.cod_item.like('%'+str(filtro)+'%')))).order_by(ItemUsuario.id).all()
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        #from webhelpers import paginate
        count = items.__len__()
        page =int( named.get( 'page', '1'))
        currentPage = paginate.Page(
            items, page, item_count=count, 
            items_per_page=3,
        )
        expresion=str(named.get( 'expresion'))
        expre_cad=expresion
        filtro=""
        muestraBoton="false"
        return dict(page='Aprobar-Item',user=user,muestraBoton=muestraBoton,itemSeleccionado=itemSeleccionado,named=named,filtro=filtro,itemSelec=itemSelec,items=items,
                    fase=fase,  
                    proyecto=proyecto,currentPage = currentPage,subtitulo='Aprobar-Item')
    
    
    @expose()  
    def saveAprobacion( self, idFase, **named):
        itemsAprobados=DBSession.query(ItemUsuario).filter(ItemUsuario.estado_id==8).filter(ItemUsuario.fase_id==idFase).all()
        for i, itemAprob in enumerate(itemsAprobados):
            itemAprob.estado_id=2  
            DBSession.flush()
       
        itemselect_car = named.get('itemselect','')
        if (itemselect_car!=""):
            try:
                itemselect=int(itemselect_car)
                ListaSeleccionada=[itemselect]
                for i,itemSelecAprobado in enumerate(ListaSeleccionada):
                    item=DBSession.query(ItemUsuario).filter_by(id=itemSelecAprobado).one()
                    item.estado_id=8
                    DBSession.flush()
            except :
                itemselect=itemselect_car
                for itemSelecAprobado in itemselect_car:
                    item=DBSession.query(ItemUsuario).filter_by(id=itemSelecAprobado).one()
                    item.estado_id=8
                    DBSession.flush()
            
        redirect( '/item/itemList/'+idFase )    
        flash( '''Item Aprobado! %s''')
    
    
    @expose('gestionitem.templates.item.verSolicitudAperturaLB')
    def verSolicitudAperturaLB(self,idFase, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user'] 
        #CONSULTA ALA BD
        lbSolicitadas=DBSession.query(LineaBase).filter_by(apertura="1").filter(LineaBase.fase_id==idFase).all()
        itemsLBSol=[]
        for idLB in lbSolicitadas:
            items=DBSession.query(ItemUsuario).filter(ItemUsuario.linea_base_id==idLB.id).all()
            codigosItemsSol=""
            for item in items:
                codigosItemsSol=codigosItemsSol+"|"+item.cod_item+" "
            itemsLBSol.append(codigosItemsSol)

        fase=DBSession.query(Fase).filter_by(id=idFase).one()
                # SI EXISTE FILTROS DE BUSQUEDAS
        itemSelec=named.get( 'itemselect','0')
        filtro=named.get( 'filtros','')
        if (filtro!=""):
            if filtro.isdigit():
                lbSolicitadas=DBSession.query(LineaBase).filter(LineaBase.fase_id==idFase).filter_by(id=filtro).order_by(LineaBase.id).all()
            else:
                lbSolicitadas=DBSession.query(LineaBase).filter(LineaBase.fase_id==idFase).filter(LineaBase.comentario.like('%'+str(filtro)+'%')).order_by(LineaBase.id).all()
            lbIds=[]
            itemsLB=[]
            for idLB in lbSolicitadas:
                lbIds.append(idLB.id)
                items=DBSession.query(ItemUsuario).filter(ItemUsuario.linea_base_id==idLB.id).all()
                codigosItems=""
                for item in items:
                    codigosItems=codigosItems+"|"+item.cod_item+" "
                itemsLB.append(codigosItems)
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        #from webhelpers import paginate
        count = items.__len__()
        page =int( named.get( 'page', '1'))
        currentPage = paginate.Page(
            items, page, item_count=count, 
            items_per_page=3,
        )
        expresion=str(named.get( 'expresion'))
        expre_cad=expresion
        filtro=""
        muestraBoton="false"
        return dict(page='Solicitudes de Apertura',user=user,itemsLBSol=itemsLBSol,muestraBoton=muestraBoton,lbSolicitadas=lbSolicitadas,named=named,filtro=filtro,itemSelec=itemSelec,items=items,
                    fase=fase,  
                    proyecto=proyecto,currentPage = currentPage,subtitulo='Solicitudes de Apertura')
    
    @expose()  
    def accionSolicitud( self, idFase, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        lbs=DBSession.query(LineaBase).filter_by(fase_id=idFase).filter_by(apertura="1").all()
        for lb in lbs:
            accion=named.get(str(lb.id),'')
            if (accion!="") and (accion=="Rechazado"):
                lb.apertura=""
                lb.comentario=""
                lb.usuario_sol=""
                DBSession.flush()
            elif (accion!="") and (accion=="Aceptado"):
                lb.apertura=""
                lb.comentario=""
                lb.usuario_sol=""
                lb.estado_id=2
                DBSession.flush()
                ###Cambia Estado del Item
                items=DBSession.query(ItemUsuario).filter_by(linea_base_id=lb.id).all()
                for item in items:
                    item.estado_id=5
                    DBSession.flush
        fase=DBSession.query(Fase).filter_by(id=idFase).one()
                  
        redirect( '/item/faseList/'+str(fase.proyecto_id) )    
        flash( '''Item Aprobado! %s''')
    
    @expose('gestionitem.templates.item.solicitudAperturaLB')
    def solicitudAperturaLB(self,idFase, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user'] 
        #CONSULTA ALA BD
        lbSolicitadas=DBSession.query(LineaBase).filter_by(apertura="1").filter(LineaBase.fase_id==idFase).all()
        itemsLBSol=[]
        for idLB in lbSolicitadas:
            items=DBSession.query(ItemUsuario).filter(ItemUsuario.linea_base_id==idLB.id).all()
            codigosItemsSol=""
            for item in items:
                codigosItemsSol=codigosItemsSol+"|"+item.cod_item+" "
            itemsLBSol.append(codigosItemsSol)

        fase=DBSession.query(Fase).filter_by(id=idFase).one()
        lineasBases=DBSession.query(LineaBase).filter(LineaBase.fase_id==fase.id).order_by(LineaBase.id).all()
        lbIds=[]
        itemsLB=[]
        for idLB in lineasBases:
            lbIds.append(idLB.id)
            items=DBSession.query(ItemUsuario).filter(ItemUsuario.linea_base_id==idLB.id).all()
            codigosItems=""
            for item in items:
                codigosItems=codigosItems+"|"+item.cod_item+" "
            itemsLB.append(codigosItems)
        # SI EXISTE FILTROS DE BUSQUEDAS
        itemSelec=named.get( 'itemselect','0')
        filtro=named.get( 'filtros','')
        if (itemSelec!="0"):
            listaFiltros=[]
            for fil in itemSelec:
                car=str(fil)
                listaFiltros.append(int(car))
            lbSolicitadas=DBSession.query(LineaBase).filter(LineaBase.id.in_(listaFiltros)).filter(LineaBase.fase_id==fase.id).order_by(LineaBase.id).all()
            itemsLBSol=[]
            for idLB in lbSolicitadas:
                items=DBSession.query(ItemUsuario).filter(ItemUsuario.linea_base_id==idLB.id).all()
                codigosItemsSol=""
                for item in items:
                    codigosItemsSol=codigosItemsSol+"|"+item.cod_item+" "
                itemsLBSol.append(codigosItemsSol)

        if (filtro!=""):
            if filtro.isdigit():
                lineasBases=DBSession.query(LineaBase).filter(LineaBase.fase_id==idFase).filter_by(id=filtro).order_by(LineaBase.id).all()
            else:
                lineasBases=DBSession.query(LineaBase).filter(LineaBase.fase_id==idFase).filter(LineaBase.comentario.like('%'+str(filtro)+'%')).order_by(LineaBase.id).all()
            lbIds=[]
            itemsLB=[]
            for idLB in lineasBases:
                lbIds.append(idLB.id)
                items=DBSession.query(ItemUsuario).filter(ItemUsuario.linea_base_id==idLB.id).all()
                codigosItems=""
                for item in items:
                    codigosItems=codigosItems+"|"+item.cod_item+" "
                itemsLB.append(codigosItems)
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        #from webhelpers import paginate
        count = items.__len__()
        page =int( named.get( 'page', '1'))
        currentPage = paginate.Page(
            items, page, item_count=count, 
            items_per_page=3,
        )
        expresion=str(named.get( 'expresion'))
        expre_cad=expresion
        filtro=""
        muestraBoton="false"
        return dict(page='Aprobar-Item',user=user,lineasBases=lineasBases,itemsLB=itemsLB,itemsLBSol=itemsLBSol,muestraBoton=muestraBoton,lbSolicitadas=lbSolicitadas,named=named,filtro=filtro,itemSelec=itemSelec,items=items,
                    fase=fase,  
                    proyecto=proyecto,currentPage = currentPage,subtitulo='Aprobar-Item')
    
    @expose()  
    def saveSolicitud( self, idFase, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        lbs=DBSession.query(LineaBase).filter_by(fase_id=idFase).all()
        for lb in lbs:
            lb.apertura=""
            lb.comentario=""
            lb.usuario_sol=""
            DBSession.flush()
        itemselect_car = named.get('itemselect','')
        if (itemselect_car!=""):
            itemselect=itemselect_car
            listaFiltros=[]
            for fil in itemselect:
                car=str(fil)
                listaFiltros.append(int(car))
            for baseSol in listaFiltros:
                lb=DBSession.query(LineaBase).filter_by(id=baseSol).one()
                param=str(baseSol)
                comentario=named.get(param,'')
                if comentario!="":
                    lb.comentario=comentario 
                    ###IMPORTANTE CAMBIAR LUEGO POR EL ESTADO CORRECTO
                lb.apertura="1"
                lb.usuario_sol=user.user_name
                DBSession.flush()
                    ###ESTO NO SE HACE, CAMBIEAR LUEGO
                items=DBSession.query(ItemUsuario).filter_by(linea_base_id=lb.id).all()
                for item in items:
                    # item.estado_id=5
                    DBSession.flush
                    
        redirect( '/item/itemList/'+idFase )    
        flash( '''Item Aprobado! %s''')
 
    
    
    
    @expose('gestionitem.templates.item.relacionar_item')
    def relacionar_item(self,id,idFase,tipo_r, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        fases_selec=""
        itemSeleccionado=DBSession.query(ItemUsuario).filter_by(id=-1)
        itemSelec=named.get( 'itemselect','0')
        if (itemSelec!=0 ):
            itemSeleccionado=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(itemSelec)).order_by(ItemUsuario.id)
        itemUsuario=DBSession.query(ItemUsuario).filter_by(id=id).one()
        fase=DBSession.query(Fase).filter_by(id=itemUsuario.fase_id).one()
        submit=named.get( 'submit')            
        if (tipo_r=="1"):
            muestraBoton="false"
            tipo=1
            tipoRelacion="Padre/hijo(*)"
            observacion="Una relacion Padre/Hijo indica una relacion entre  2 items pertenecienes a la misma fase"
            items=DBSession.query(ItemUsuario).filter_by(fase_id=idFase).filter(ItemUsuario.estado_id==3).filter(ItemUsuario.id!=id).filter_by(estado_id=3)
            fasesRelacion=DBSession.query(Fase).filter_by(id=idFase).one()
            itemSelec=named.get( 'itemselect','0')
            if(submit=="Buscar"): 
                expresion=named.get( 'filtros')
                expre_cad=expresion
                if (itemSelec!='0'):
                    itemSeleccionado=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(itemSelec)).order_by(ItemUsuario.id)
                items=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==idFase).filter(or_(ItemUsuario.descripcion.like('%'+str(expre_cad)+'%'),(ItemUsuario.cod_item.like('%'+str(expre_cad)+'%')))).filter_by(estado_id=3).order_by(ItemUsuario.id)
        else:
            if (tipo_r=="2"):
                muestraBoton="false"
                tipo=2
                tipoRelacion="Antecesor/Sucesor(*)"
                observacion="Una relacion Antecesor/Sucesor indica una relacion entre un item de la fase actual(Antecesor) con un item perteneciente a la fase inmediatamente anterior(Sucesor)"
                faseActual=DBSession.query(Fase).filter_by(id=idFase).one()
                faseAnterior=DBSession.query(Fase).filter_by(numero_fase=faseActual.numero_fase-1).one()
                fasesRelacion=faseAnterior
                items=DBSession.query(ItemUsuario).filter_by(fase_id=faseAnterior.id).filter(ItemUsuario.estado_id==3).filter(ItemUsuario.id!=id).filter_by(estado_id=3)
                itemSelec=named.get( 'itemselect','0')
                if(submit=="Buscar"): 
                    expresion=named.get( 'filtros')
                    expre_cad=expresion
                    if (itemSelec!='0'):
                        itemSeleccionado=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(itemSelec)).order_by(ItemUsuario.id)
                    items=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==faseAnterior.id).filter(or_(ItemUsuario.descripcion.like('%'+str(expre_cad)+'%'),(ItemUsuario.cod_item.like('%'+str(expre_cad)+'%')))).filter_by(estado_id=3).order_by(ItemUsuario.id)                   
        lista=range(100)
        lista=""   
        fases=DBSession.query(Fase).filter(Fase.numero_fase<=fase.numero_fase).order_by(Fase.id)
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        tipoItems=DBSession.query(TipoItemUsuario).filter_by(fase_id=fase.id).order_by(TipoItemUsuario.id)
        defecto=TipoItemUsuario        
        item=itemUsuario
        from webhelpers import paginate
        count = items.count()
        page =int( named.get( 'page', '1'))
        currentPage = paginate.Page(
            items, page, item_count=count, 
            items_per_page=3,
        )
        expresion=str(named.get( 'expresion'))
        expre_cad=expresion
        filtro=""
        return dict(page='Nuevo Item',user=user,itemSeleccionado=itemSeleccionado,named=named,filtro=filtro,itemSelec=itemSelec,parametro=submit, muestraBoton=muestraBoton,tipo=tipo,observacion=observacion,fasesRelacion=fasesRelacion,tipoRelacion=tipoRelacion,items=items,
                    fase=fase,fases=fases, tipoItems=tipoItems,fases_selec=fases_selec,  
                    proyecto=proyecto,lista=lista,currentPage = currentPage, 
                    item=item,subtitulo='ABM-Item')
        
    @expose('gestionitem.templates.item.itemInfo')
    def itemInfo(self,id,**named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        itemUsuario=DBSession.query(ItemUsuario).filter_by(id=id).one()
        fase=DBSession.query(Fase).filter_by(id=itemUsuario.fase_id).one()
        relaciones=DBSession.query(RelacionItem).filter_by(antecesor_item_id=id).order_by(RelacionItem.id)
        relacionesSucesores=DBSession.query(RelacionItem).filter_by(sucesor_item_id=id).order_by(RelacionItem.id)
        idrelaciones=[0]
        idrelacionesSucesor=[0]
        idFaseRelacion=[0]
        contRelaciones=0
        contRelacionesSucesores=0
        ##GRAFICA RELACIONES####
        A=pgv.AGraph(directed=True)
       
        
     
        for i, relacion in enumerate(relaciones):
            contRelaciones=contRelaciones+1
            idrelaciones.append(relacion.sucesor_item_id)
            
        for i, relacionSucesor in enumerate(relacionesSucesores):
            contRelacionesSucesores=contRelacionesSucesores+1
            idrelacionesSucesor.append(relacionSucesor.antecesor_item_id)
        
        itemsRelacionados=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(idrelaciones)).order_by(ItemUsuario.fase_id)
        
        itemsAntecesoresRelacionados=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(idrelacionesSucesor)).order_by(ItemUsuario.fase_id)
        
        for i, item in enumerate(itemsRelacionados):
            A.add_edge(itemUsuario.cod_item,item.cod_item)    
            idFaseRelacion.append(item.fase_id)
        for i, item in enumerate(itemsAntecesoresRelacionados):
            A.add_edge(item.cod_item,itemUsuario.cod_item)    
    
        print A.string()
        A.write('/home/pyworkspace/GestionItems/src/GestionItem/gestionitem/public/images/relaciones.png')
        A.write('/home/pyworkspace/GestionItems/src/GestionItem/gestionitem/public/images/relaciones.png')
        B=pgv.AGraph('/home/pyworkspace/GestionItems/src/GestionItem/gestionitem/public/images/relaciones.png')
        B.layout() # layout with default (neato)
        B.draw('/home/pyworkspace/GestionItems/src/GestionItem/gestionitem/public/images/relaciones.png') # draw png
        
        fasesRelacionados=DBSession.query(Fase).filter(Fase.id.in_(idFaseRelacion)).order_by(Fase.id)
        lista=range(100)
        lista=""   
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        item=itemUsuario
        return dict(page='Nuevo Item',user=user,
                    fase=fase,contRelaciones=contRelaciones,itemsAntecesoresRelacionados=itemsAntecesoresRelacionados,contRelacionesSucesores=contRelacionesSucesores,itemsRelacionados=itemsRelacionados,fasesRelacionados=fasesRelacionados,
                    proyecto=proyecto,lista=lista, 
                    item=item,subtitulo='Informacion-Item')

    
    def calcularImpacto(self, idItemActual, ItemsCalculados, CalcImpacto):
        itemActual = DBSession.query(ItemUsuario).filter_by(id=idItemActual).one()
        ItemsCalculados.append(itemActual.id)
        #itemsRelacionados = DBSession.query(RelacionItem).filter(or_(RelacionItem.sucesor_item_id == itemActual.id, RelacionItem.antecesor_item_id == itemActual.id)).filter(and_(~RelacionItem.antecesor_item_id.in_(ItemsCalculados), ~RelacionItem.antecesor_item_id.in_(ItemsCalculados))).order_by(RelacionItem.id).all()
        itemsRelacionados = DBSession.query(RelacionItem).filter(or_(RelacionItem.sucesor_item_id == itemActual.id, RelacionItem.antecesor_item_id == itemActual.id)).order_by(RelacionItem.id).all()

        if (len(itemsRelacionados)!=0):
            for iRel in itemsRelacionados:
                if (iRel.sucesor_item_id not in ItemsCalculados):
                    CalcImpacto, ItemsCalculados= self.calcularImpacto(iRel.sucesor_item_id, ItemsCalculados,CalcImpacto)
                if (iRel.antecesor_item_id not in ItemsCalculados):
                    CalcImpacto, ItemsCalculados= self.calcularImpacto(iRel.antecesor_item_id, ItemsCalculados,CalcImpacto)
        
        CalcImpacto=itemActual.prioridad+CalcImpacto
        return CalcImpacto, ItemsCalculados
   
    @expose('gestionitem.templates.item.calculoImpacto')
    def calculoImpacto(self,id,**named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        itemUsuario=DBSession.query(ItemUsuario).filter_by(id=id).one()
        fase=DBSession.query(Fase).filter_by(id=itemUsuario.fase_id).one()
        ItemsCalculados=[]
        calculoImpacto, ItemsCalculados=self.calcularImpacto(itemUsuario.id, ItemsCalculados,0)
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        itemsCalculados=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(ItemsCalculados)).order_by(ItemUsuario.fase_id).order_by(ItemUsuario.id)
        from webhelpers import paginate
        count = itemsCalculados.count()
        page =int( named.get( 'page', '1'))
        currentPage = paginate.Page(
            itemsCalculados, page, item_count=count, 
            items_per_page=5,
        )
        itemsCalculados = currentPage.items
        item=itemUsuario
        return dict(page='Nuevo Item',user=user,
                    fase=fase,itemsCalculados=itemsCalculados,currentPage=currentPage,
                    proyecto=proyecto, calculoImpacto=calculoImpacto,
                    item=item,subtitulo='ABM-Item')
    
              
   