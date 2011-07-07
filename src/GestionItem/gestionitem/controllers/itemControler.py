from gestionitem.lib.base import BaseController
from tg import expose, flash, require, url, request, redirect, response
from sqlalchemy import or_, and_
from tg import expose, flash, require, url, request, redirect
from gestionitem.model.proyecto import ItemUsuario, ArchivosAdjuntos,UsuarioFaseRol, Proyecto,RelacionItem,Fase,LineaBase, TipoItemUsuario,TipoItemUsuarioAtributos,TipoItemUsuarioAtributosValor
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
from tg.controllers import CUSTOM_CONTENT_TYPE
from repoze.what.predicates import not_anonymous, in_group, has_permission, All
from tg.decorators import require

#Libreria para graficar
import pygraphviz as pgv



 
class ItemControler(BaseController):
    @expose()
    def concluir_proyecto( self,id, **named ):
        """Create a new movie record"""
        submit= named.get('submit','0')
        if submit=="Reabrir":
            proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
            proyecto.estado=2,
            DBSession.flush()
        else:    
            proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
            proyecto.estado=3,
            DBSession.flush()
        redirect( '/item/faseList/'+ id)
    @expose(template="gestionitem.templates.item.faseList")
    def faseList(self,id, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
        
        fasesDelUsuario=DBSession.query(UsuarioFaseRol).filter_by(user_id=user.user_id).all()
        idsFasesUsuario=[]
        for idFaseUser in fasesDelUsuario:
            idsFasesUsuario.append(idFaseUser.fase_id)
        
        esLider=0    
        if (proyecto.id_lider==user.user_id):
            esLider=1
        
        
        if (esLider==0):    
            fases = DBSession.query(Fase).filter_by(proyecto_id=id).filter(Fase.id.in_(idsFasesUsuario)).order_by(Fase.id).all()
        else:
            fases = DBSession.query(Fase).filter_by(proyecto_id=id).order_by(Fase.id).all()
        
        puedeCerrar=1
        for f in fases:
            if(f.estado_id!=4):
                puedeCerrar=0
        
            
        
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
        from webhelpers import paginate
        #count = items.count()
        count = fases.__len__()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            fases, page, item_count=count, 
            items_per_page=3,
        )
        fases = currentPage.items
        
        return dict(currentPage=currentPage,puedeCerrar=puedeCerrar,user=user,mensajes=mensajes,
                    id=id,fases=fases,proyecto=proyecto,subtitulo='Lista de Fases')
          
    @expose('gestionitem.templates.item.itemList')
    def itemList(self,id,**named):
        

        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        expresion=named.get('expresion','lista')
        fase = DBSession.query(Fase).filter_by(id=id).one()
        
        
        fasesDelUsuario=DBSession.query(UsuarioFaseRol).filter_by(fase_id=id).filter_by(user_id=user.user_id).all()
        
        esDesarrollador=0
        esAprobador=0
        
        for fg in fasesDelUsuario:
            if(fg.rol.group_name=="Desarrollador"):
                esDesarrollador=1
            if(fg.rol.group_name=="Aprobador"):
                esAprobador=1
            
        mensajes=""
        lbs = DBSession.query(LineaBase).filter_by(fase_id=fase.id).order_by(LineaBase.id).all()
        cerrarLB=0
        existe_sol=0
        for lb in lbs:
            if (lb.apertura=="1"):
                existe_sol=1
            if existe_sol:
                mensajes="Solicitud de Apertura de LB"
            if (lb.estado_id==2):
                cerrarLB=1
        
    
        existeLB=0
        if expresion=="lista":
            muestraBoton="false"
            items = DBSession.query(ItemUsuario).filter(and_(ItemUsuario.estado_id!=6, ItemUsuario.estado_id!=7)).filter_by(fase_id=id).order_by(ItemUsuario.id).all()
            for item_aux in items:
                item_aux.relaciones=DBSession.query(RelacionItem).filter_by(estado_id=1).filter_by(antecesor_item_id=item_aux.id).order_by(RelacionItem.id)
                if item_aux.estado.id==3 or item_aux.estado.id==4:
                    existeLB=1;
            fase = DBSession.query(Fase).filter_by(id=id).one()    
            proyecto = DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
            tiposItemUs=DBSession.query(TipoItemUsuario).order_by( TipoItemUsuario.id )
        else :
            muestraBoton="true"
            fase = DBSession.query(Fase).filter_by(id=id).one()      
            proyecto = DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
            items = DBSession.query(ItemUsuario).filter(and_(ItemUsuario.estado_id!=6, ItemUsuario.estado_id!=7)).filter(ItemUsuario.fase_id==id).filter(or_(ItemUsuario.descripcion.like('%'+expresion+'%'),(ItemUsuario.cod_item.like('%'+expresion+'%')))).order_by(ItemUsuario.id).all()
            for item_aux in items:
                if item_aux.estado.id==3 or item_aux.estado.id==4:
                    existeLB=1;
            fase = DBSession.query(Fase).filter_by(id=id).one()    
            proyecto = DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
            tiposItemUs=DBSession.query(TipoItemUsuario).order_by( TipoItemUsuario.id )    
        
        itemTodos = DBSession.query(ItemUsuario).filter_by(fase_id=id).order_by(ItemUsuario.id).all()
            
        esLider=0    
        if (proyecto.id_lider==user.user_id):
            esLider=1
        esAprobado=0
        esEliminado=0
        for itemAprob in itemTodos:
            if (itemAprob.estado_id==8):
                esAprobado=1
            if (itemAprob.estado_id==7):
                esEliminado=1
        from webhelpers import paginate
        #count = items.count()
        count = items.__len__()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            items, page, item_count=count, 
            items_per_page=5,
        )
        items = currentPage.items

        return dict(cerrarLB=cerrarLB,esItemEliminado=esEliminado,esItemAprobado=esAprobado,mensajes=mensajes,esLider=esLider,esDesarrollador=esDesarrollador,esAprobador=esAprobador,muestraBoton=muestraBoton,page='Lista de Items',user=user,existeLB=existeLB,
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
    @require(All(in_group('Desarrollador', msg='Debe poseer Rol "Desarrollador" para editar Items'),
                 has_permission('Agregar items', msg='Debe poseer Permiso "Agregar items" gestionar Items')))
   
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
    def updateItemConTipo( self,idFase,idProy,idItem,TipoItem ,numCod,codItem,complejidad,descripcion,file, lista,idAtributos, submit):                
        try:
            for i, valor in enumerate(lista):
                atributo = DBSession.query(TipoItemUsuarioAtributosValor).filter_by(item_usuario_id=idItem).filter_by(atributo_id=idAtributos[i]).one()
                atributo.valor=valor
                DBSession.flush()
        except:        
            atributo = DBSession.query(TipoItemUsuarioAtributosValor).filter_by(atributo_id=idAtributos).filter_by(item_usuario_id=idItem).one()
            atributo.valor=lista
            DBSession.flush() 
        try:
            filecontent = file.file.read()
            new_file = ArchivosAdjuntos(nombre=file.filename, archivo=filecontent,item_usuario_id=idItem)
            DBSession.add(new_file)
            DBSession.flush()
        except:
            filecontent=""        
            
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
    def updateItemSinTipo( self,idFase,idProy,idItem,TipoItem , numCod,codItem,complejidad,descripcion,file, submit):                
        try:
            filecontent = file.file.read()
            new_file = ArchivosAdjuntos(nombre=file.filename, archivo=filecontent,item_usuario_id=idItem)
            DBSession.add(new_file)
            DBSession.flush()
        except:
            filecontent="" 
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
    def saveItemLB( self,idFase,idProy,idItem,tipoItem ,numCod,codItem,complejidad,descripcion,file,  **named):
        #Obtiene el id del Item a modificar
        itemAnterior=DBSession.query(ItemUsuario).filter_by(id=idItem).one()
        itemAnterior.estado_id=6
        DBSession.flush()
        lb=DBSession.query(LineaBase).filter_by(id=itemAnterior.linea_base_id).one()
        lb.estado_id=5
        DBSession.flush()
        lbAnterior=itemAnterior.linea_base_id
        lista=named.get('lista','')
        submit=named.get('submit','')
        idAtributos=named.get('idAtributos','')
        #Obtiene los items relacionados
        relaciones = DBSession.query(RelacionItem).filter_by(estado_id=1).filter(or_(RelacionItem.sucesor_item_id == itemAnterior.id, RelacionItem.antecesor_item_id == itemAnterior.id)).order_by(RelacionItem.id).all()
        relaciones_antecesores=[]
        relaciones_sucesores=[]
        for i, relacionActual in enumerate(relaciones):
            relaciones_antecesores.append(relacionActual.antecesor_item_id)
            relaciones_sucesores.append(relacionActual.sucesor_item_id)
        itemsRelacionados = DBSession.query(ItemUsuario).filter(or_(ItemUsuario.id.in_(relaciones_antecesores),ItemUsuario.id.in_(relaciones_sucesores))).all()
        for i, itemActual in enumerate(itemsRelacionados):
            
            if (itemActual.estado_id==3) or (itemActual.estado_id==5):
                itemActual.estado_id=4
                DBSession.flush()
                lineaBase=DBSession.query(LineaBase).filter_by(id=itemActual.linea_base_id)
                lineaBase.estado_id=4
                DBSession.flush()
        version=itemAnterior.version
        version=version+1        
        listaIds=DBSession.query(ItemUsuario).order_by(ItemUsuario.id)
        if (listaIds.count()>0):
            listTemp=listaIds[-1]
            id=listTemp.id + 1
        else: 
            id=1
        try:
            filecontent = file.file.read()
            new_file = ArchivosAdjuntos(nombre=file.filename, archivo=filecontent,item_usuario_id=id)
            DBSession.add(new_file)
            DBSession.flush()
        except:
            filecontent=""                             
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
            new.estado_id=2
            new.linea_base_ant=lbAnterior
            DBSession.add( new )
            DBSession.flush()
            cont=0
            for i, valor in enumerate(idAtributos):
                cont=1+cont
            if type(idAtributos) == list:
                for i, valor in enumerate(lista):
                    new2 = TipoItemUsuarioAtributosValor(
                    item_usuario_id = id,
                    atributo_id = idAtributos[i],
                    valor=valor
                    )
                    DBSession.add( new2 )
            else:
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
            new.estado_id=2,
            new.linea_base_ant=lbAnterior
            new.version=version,
            new.tipo_item_generico = 1
            DBSession.add( new )
            DBSession.flush()
        
        
        
        
        fase = DBSession.query(Fase).filter_by(id=idFase).one() 
        
        archivosAnteriores=DBSession.query(ArchivosAdjuntos).filter_by(item_usuario_id=itemAnterior.id).all()
        for newFile in archivosAnteriores:
            new_file2 = ArchivosAdjuntos(nombre=newFile.nombre, archivo=newFile.archivo,item_usuario_id=id)
            DBSession.add(new_file2)
            DBSession.flush()
        ####ESTA INCOMPLETO-VER!!! FALTA LAS RELACIONES SUCESORAS
        relacionesItemAnterior = DBSession.query(RelacionItem).filter_by(estado_id=1).filter(( RelacionItem.antecesor_item_id == itemAnterior.id)).order_by(RelacionItem.id).all()
        relacionesItemAnteriorS = DBSession.query(RelacionItem).filter_by(estado_id=1).filter(( RelacionItem.sucesor_item_id == itemAnterior.id)).order_by(RelacionItem.id).all()
        
        itemselect=[]
        tipo=[]
        itemselectS=[]
        tipoS=[]
        for i, relacionActual in enumerate(relacionesItemAnterior):
            relacionActual.estado_id=2
            itemselect.append(relacionActual.sucesor_item_id)
            tipo.append(relacionActual.tipo)
            DBSession.flush()
        for i, relacionActualS in enumerate(relacionesItemAnteriorS):
            relacionActualS.estado_id=2
            itemselectS.append(relacionActualS.antecesor_item_id)
            tipoS.append(relacionActualS.tipo)
            DBSession.flush()
        itemNuevaVersion=DBSession.query(ItemUsuario).filter_by(id=id).one()
        for i, itemRelacion in enumerate(itemselect):
            new = RelacionItem(
                               antecesor_item_id=id,
                               sucesor_item_id = itemRelacion,
                               tipo=tipo[i],
                               estado_id=1
                               )
            DBSession.add( new )
            DBSession.flush()
        itemNuevaVersion.estado_id=2
        DBSession.flush()
        
        
        for i, itemRelacionS in enumerate(itemselectS):
            newS = RelacionItem(
                               antecesor_item_id= itemRelacionS,
                               sucesor_item_id = id,
                               tipo=tipoS[i],
                               estado_id=1
                               )
            DBSession.add( newS )
            DBSession.flush()
        
        
        
        
        
        if (submit!="Modificar Relaciones"):        
            redirect( '/item/itemList/'+idFase )
            flash( '''Tipo Item Agregado! %s''')
        else: 
            if (submit=="Modificar Relaciones"):        
                redirect( '/item/updateRelacion/'+idFase+'/'+str(id) )
                flash( '''Item Modificado! %s''')
    
    
    @expose()
    def updateItem( self,idFase,idProy,idItem,tipoItem ,numCod,codItem,complejidad,descripcion,file,  **named):
        #Obtiene el id del Item a modificar
        itemAnterior=DBSession.query(ItemUsuario).filter_by(id=idItem).one()
        itemAnterior.estado_id=6
        DBSession.flush()
        DBSession.flush()
        lista=named.get('lista','')
        submit=named.get('submit','')
        idAtributos=named.get('idAtributos','')
        #Obtiene los items relacionados
        relaciones = DBSession.query(RelacionItem).filter_by(estado_id=1).filter(or_(RelacionItem.sucesor_item_id == itemAnterior.id, RelacionItem.antecesor_item_id == itemAnterior.id)).order_by(RelacionItem.id).all()
        relaciones_antecesores=[]
        relaciones_sucesores=[]
        for i, relacionActual in enumerate(relaciones):
            relaciones_antecesores.append(relacionActual.antecesor_item_id)
            relaciones_sucesores.append(relacionActual.sucesor_item_id)
        itemsRelacionados = DBSession.query(ItemUsuario).filter(or_(ItemUsuario.id.in_(relaciones_antecesores),ItemUsuario.id.in_(relaciones_sucesores))).all()
        #for i, itemActual in enumerate(itemsRelacionados):
            
         #   if (itemActual.estado_id==3) or (itemActual.estado_id==5):
          #      itemActual.estado_id=4
        #     DBSession.flush()
        version=itemAnterior.version
        version=version+1        
        listaIds=DBSession.query(ItemUsuario).order_by(ItemUsuario.id)
        if (listaIds.count()>0):
            listTemp=listaIds[-1]
            id=listTemp.id + 1
        else: 
            id=1
        try:
            filecontent = file.file.read()
            new_file = ArchivosAdjuntos(nombre=file.filename, archivo=filecontent,item_usuario_id=id)
            DBSession.add(new_file)
            DBSession.flush()
        except:
            filecontent=""                             
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
            new.estado_id=2
            DBSession.add( new )
            DBSession.flush()
            cont=0
            for i, valor in enumerate(idAtributos):
                cont=1+cont
            if type(idAtributos) == list:
                for i, valor in enumerate(lista):
                    new2 = TipoItemUsuarioAtributosValor(
                    item_usuario_id = id,
                    atributo_id = idAtributos[i],
                    valor=valor
                    )
                    DBSession.add( new2 )
            else:
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
            new.estado_id=2,
            new.version=version,
            new.tipo_item_generico = 1
            DBSession.add( new )
            DBSession.flush()
        
        
        
        
        fase = DBSession.query(Fase).filter_by(id=idFase).one() 
        
        archivosAnteriores=DBSession.query(ArchivosAdjuntos).filter_by(item_usuario_id=itemAnterior.id).all()
        for newFile in archivosAnteriores:
            new_file2 = ArchivosAdjuntos(nombre=newFile.nombre, archivo=newFile.archivo,item_usuario_id=id)
            DBSession.add(new_file2)
            DBSession.flush()
        ####ESTA INCOMPLETO-VER!!! FALTA LAS RELACIONES SUCESORAS
        relacionesItemAnterior = DBSession.query(RelacionItem).filter_by(estado_id=1).filter(( RelacionItem.antecesor_item_id == itemAnterior.id)).order_by(RelacionItem.id).all()
        relacionesItemAnteriorS = DBSession.query(RelacionItem).filter_by(estado_id=1).filter(( RelacionItem.sucesor_item_id == itemAnterior.id)).order_by(RelacionItem.id).all()
        
        itemselect=[]
        tipo=[]
        itemselectS=[]
        tipoS=[]
        for i, relacionActual in enumerate(relacionesItemAnterior):
            relacionActual.estado_id=2
            itemselect.append(relacionActual.sucesor_item_id)
            tipo.append(relacionActual.tipo)
            DBSession.flush()
        for i, relacionActualS in enumerate(relacionesItemAnteriorS):
            relacionActualS.estado_id=2
            itemselectS.append(relacionActualS.antecesor_item_id)
            tipoS.append(relacionActualS.tipo)
            DBSession.flush()
        itemNuevaVersion=DBSession.query(ItemUsuario).filter_by(id=id).one()
        for i, itemRelacion in enumerate(itemselect):
            new = RelacionItem(
                               antecesor_item_id=id,
                               sucesor_item_id = itemRelacion,
                               tipo=tipo[i],
                               estado_id=1
                               )
            DBSession.add( new )
            DBSession.flush()
        itemNuevaVersion.estado_id=2
        DBSession.flush()
        
        
        for i, itemRelacionS in enumerate(itemselectS):
            newS = RelacionItem(
                               antecesor_item_id= itemRelacionS,
                               sucesor_item_id = id,
                               tipo=tipoS[i],
                               estado_id=1
                               )
            DBSession.add( newS )
            DBSession.flush()
        
        
        
        
        
        if (submit!="Modificar Relaciones"):        
            redirect( '/item/itemList/'+idFase )
            flash( '''Tipo Item Agregado! %s''')
        else: 
            if (submit=="Modificar Relaciones"):        
                redirect( '/item/updateRelacion/'+idFase+'/'+str(id) )
                flash( '''Item Modificado! %s''')
    @expose()
    def saveItem( self,idFase,idProy, numCod,codItem,complejidad,descripcion,file,tipoItem, lista,idAtributos, submit,):
        listaIds=DBSession.query(ItemUsuario).order_by(ItemUsuario.id)
        
        fase=DBSession.query(Fase).filter_by(id=idFase).one()
        fase.estado_id=2
        DBSession.flush()
        
        if (listaIds.count()>0):
            listaTemp=listaIds[-1]
            id=listaTemp.id + 1
        else: 
            id=1                            
        
        
        try:
            filecontent = file.file.read()
            new_file = ArchivosAdjuntos(nombre=file.filename, archivo=filecontent,item_usuario_id=id)
            DBSession.add(new_file)
            DBSession.flush()
        except:
            filecontent="" 
        
        
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
            if type(lista) == list:
                for i, valor in enumerate(lista):
                    new2 = TipoItemUsuarioAtributosValor(
                    item_usuario_id = id,
                    atributo_id = idAtributos[i],
                    valor=valor
                    )
                    DBSession.add( new2 )
            else:    
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
    
    
    @expose()
    def delete(self, fileid, path):
        try:
            userfile = DBSession.query(ArchivosAdjuntos).filter_by(id=fileid).one()
        except:
            return redirect(path)
        DBSession.delete(userfile)
        return redirect(path)
    
    @expose('gestionitem.templates.item.editar_item')
    @require(All(in_group('Desarrollador', msg='Debe poseer Rol "Desarrollador" para editar Items'),
                 has_permission('Editar items', msg='Debe poseer Permiso "Editar items" gestionar Items')))
    
    def editar_item(self,id,idItem):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user'] 
        fase=DBSession.query(Fase).filter_by(id=id).one()
        current_files = DBSession.query(ArchivosAdjuntos).filter_by(item_usuario_id=idItem).all()
        
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
                    item=item,subtitulo='ABM-Item',current_files=current_files)
    @expose('gestionitem.templates.item.editar_itemLB')
    @require(All(in_group('Desarrollador', msg='Debe poseer Rol "Desarrollador" para editar Items'),
                 has_permission('Editar items', msg='Debe poseer Permiso "Editar items" gestionar Items')))
   
    def editar_itemLB(self,id,idItem, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user'] 
        current_files = DBSession.query(ArchivosAdjuntos).filter_by(item_usuario_id=idItem).all()
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
                    proyecto=proyecto, atributosValor=atributosValor,current_files=current_files,
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
    @expose('gestionitem.templates.item.avisoRevertirItemLB')
    def avisoRevertirItemLB(self,id,idAnterior,**named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        itemUsuario=DBSession.query(ItemUsuario).filter_by(id=id).one()
        itemAnterior=DBSession.query(ItemUsuario).filter_by(id=idAnterior).one()
        
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
        return dict(page='Aviso Revertir Item',user=user,itemAnterior=itemAnterior,
                    fase=fase,itemsCalculados=itemsCalculados,currentPage=currentPage,
                    proyecto=proyecto, calculoImpacto=calculoImpacto,
                    item=item,subtitulo='Aviso')
    @expose('gestionitem.templates.item.avisoEliminarItem')
    def avisoEliminarItem(self,id,**named):
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
        return dict(page='Aviso Eliminar Item',user=user,
                    fase=fase,itemsCalculados=itemsCalculados,currentPage=currentPage,
                    proyecto=proyecto, calculoImpacto=calculoImpacto,
                    item=item,subtitulo='Aviso')

    @expose()
    @require(All(in_group('Desarrollador', msg='Debe poseer Rol "Desarrollador" para editar Items'),
                 has_permission('Eliminar items', msg='Debe poseer Permiso "Eliminar items" gestionar Items')))
   
    def eliminar_item(self,idFase,id):
        item=DBSession.query(ItemUsuario).filter_by(id=id).one()
        sucesor=DBSession.query(RelacionItem).filter(RelacionItem.sucesor_item_id==id).filter(RelacionItem.estado_id!=2)  
        for i, suc in enumerate(sucesor):
            itemRel=DBSession.query(ItemUsuario).filter_by(id=suc.antecesor_item_id).one()
            #Verirfica si existe item relacionado con LB o LB Abierta
            if (itemRel.estado_id==3 or itemRel.estado_id==5):    
                redirect( '/item/errorEliminarItem/'+ str(item.id))
        existeSucesor=0
        for i, suc in enumerate(sucesor):
            existeSucesor=1
        if (existeSucesor):
            redirect( '/item/errorEliminarItem/'+ str(item.id))
        
            # (Hoy jueves quite) itemRel=DBSession.query(ItemUsuario).filter_by(id=suc.antecesor_item_id).one()
            #(Hoy jueves quite) if (itemRel.estado_id==2 or itemRel.estado_id==8):
            #(Hoy jueves quite)    DBSession.delete(suc)
            #(Hoy jueves quite)   DBSession.flush()
            #(Hoy jueves quite)   if(item.fase.numero_fase>1):
            #(Hoy jueves quite)       item.estado_id=1
            #(Hoy jueves quite)       DBSession.flush()
            # else:    
            #    redirect( '/item/errorEliminarItem/'+ str(item.id))
        
        antecesor=DBSession.query(RelacionItem).filter(RelacionItem.antecesor_item_id==id)
        for i, ant in enumerate(antecesor):
            DBSession.delete(ant)
            DBSession.flush()
            #DBSession.delete(suc)
        #atributosValor=DBSession.query(TipoItemUsuarioAtributosValor).filter(TipoItemUsuarioAtributosValor.item_usuario_id==id)
        #for i, atrVal in enumerate(atributosValor):
            #DBSession.delete(atrVal)
        
        #DBSession.delete(DBSession.query(ItemUsuario).filter_by(id=id).one())
        item.estado_id=7
        DBSession.flush()
        estados=[1,2,3,4,5,8]
        itemsEnLB=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==idFase).filter(ItemUsuario.estado_id.in_(estados)).order_by(ItemUsuario.id).all()
        faseConLB=0
        for itemP in itemsEnLB:
            if itemP.estado_id!=3:
                faseConLB=1
        if faseConLB==0:
            fase=DBSession.query(Fase).filter_by(id=idFase).one()
            fase.estado_id=4
            DBSession.flush()
        
        itemConLB=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==idFase).filter_by(estado_id=3).all()
        existeItem=0 
        for i in itemConLB:
            existeItem=1
        if(existeItem==0):
            fase=DBSession.query(Fase).filter_by(id=idFase).one()
            fase.estado_id=2
            DBSession.flush()
        redirect( '/item/itemList/'+idFase)
    
    @expose()
    def eliminarItemLB(self,idFase,id, **named):
        item=DBSession.query(ItemUsuario).filter_by(id=id).one()
        sucesor=DBSession.query(RelacionItem).filter(RelacionItem.sucesor_item_id==id).filter(RelacionItem.estado_id!=2)  
        for i, suc in enumerate(sucesor):
            itemRel=DBSession.query(ItemUsuario).filter_by(id=suc.antecesor_item_id).one()
            #Verirfica si existe item relacionado con LB o LB Abierta
            if (itemRel.estado_id==3 or itemRel.estado_id==5):    
                redirect( '/item/errorEliminarItem/'+ str(item.id))
        for i, suc in enumerate(sucesor):
            itemRel=DBSession.query(ItemUsuario).filter_by(id=suc.antecesor_item_id).one()
            if (itemRel.estado_id==2 or itemRel.estado_id==8):
                DBSession.delete(suc)
                DBSession.flush()
                if(item.fase.numero_fase>1):
                    item.estado_id=1
                    DBSession.flush()
            else:    
                redirect( '/item/errorEliminarItem/'+ str(item.id))
        
        antecesor=DBSession.query(RelacionItem).filter(RelacionItem.antecesor_item_id==id)
        for i, ant in enumerate(antecesor):
            DBSession.delete(ant)
            #DBSession.delete(suc)
        #atributosValor=DBSession.query(TipoItemUsuarioAtributosValor).filter(TipoItemUsuarioAtributosValor.item_usuario_id==id)
        #for i, atrVal in enumerate(atributosValor):
            #DBSession.delete(atrVal)
        
        #DBSession.delete(DBSession.query(ItemUsuario).filter_by(id=id).one())
        item.estado_id=7
        DBSession.flush()
        lbAC=DBSession.query(LineaBase).filter_by(id=item.linea_base_id).one()
        itemsEnLB=DBSession.query(ItemUsuario).filter_by(linea_base_id=lbAC.id).filter(ItemUsuario.id!=item.id).all()
        existeItemEnLB=0
        for elemen in itemsEnLB:
            existeItemEnLB=1
        if existeItemEnLB==1:
            lbAC.estado_id=2
            DBSession.flush()
        else: 
            lbAC.estado_id=5
            DBSession.flush()
        estados=[1,2,3,4,5,8]
        itemsEnLB=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==idFase).filter(ItemUsuario.estado_id.in_(estados)).order_by(ItemUsuario.id).all()
        faseConLB=0
        for itemP in itemsEnLB:
            if itemP.estado_id!=3:
                faseConLB=1
        if faseConLB==0:
            fase=DBSession.query(Fase).filter_by(id=idFase).one()
            fase.estado_id=4
            DBSession.flush()
        
        itemConLB=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==idFase).filter_by(estado_id=3).all()
        existeItem=0 
        for i in itemConLB:
            existeItem=1
        if(existeItem==0):
            fase=DBSession.query(Fase).filter_by(id=idFase).one()
            fase.estado_id=2
            DBSession.flush()
        redirect( '/item/itemList/'+idFase)
            
    @expose('gestionitem.templates.item.errorEliminarItem')
    def errorEliminarItem(self,id,**named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        itemUsuario=DBSession.query(ItemUsuario).filter_by(id=id).one()
        fase=DBSession.query(Fase).filter_by(id=itemUsuario.fase_id).one()
        sucesores=DBSession.query(RelacionItem).filter(RelacionItem.sucesor_item_id==id).filter(RelacionItem.estado_id!=2).all()   
        sucesores_ids=[]
        for suc in sucesores:
            itemRel=DBSession.query(ItemUsuario).filter_by(id=suc.antecesor_item_id).one()
            if (itemRel.estado_id==3 or itemRel.estado_id==5):
                sucesores_ids.append(suc.antecesor_item_id)
        sucesoresSinLB=DBSession.query(RelacionItem).filter(RelacionItem.sucesor_item_id==id).filter(RelacionItem.estado_id!=2).all()   
        sucesoresSinLB_ids=[]
        for sucSinLB in sucesoresSinLB:
            itemRelSinLB=DBSession.query(ItemUsuario).filter_by(id=sucSinLB.antecesor_item_id).one()
            estados=[1,2,4,8]
            if (itemRelSinLB.estado_id in estados):
                sucesoresSinLB_ids.append(sucSinLB.antecesor_item_id)
        
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        itemsCalculados=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(sucesores_ids)).order_by(ItemUsuario.fase_id).order_by(ItemUsuario.id)
        itemsCalculadosSinLB=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(sucesoresSinLB_ids)).order_by(ItemUsuario.fase_id).order_by(ItemUsuario.id)
        from webhelpers import paginate
        count = itemsCalculados.count()
        page =int( named.get( 'page', '1'))
        currentPage = paginate.Page(
            itemsCalculados, page, item_count=count, 
            items_per_page=5,
        )
        itemsCalculados = currentPage.items
        
        count = itemsCalculadosSinLB.count()
        page =int( named.get( 'page', '1'))
        currentPage2 = paginate.Page(
            itemsCalculadosSinLB, page, item_count=count, 
            items_per_page=5,
        )
        item=itemUsuario
        return dict(page='Error Eliminar Item',user=user,
                    fase=fase,itemsCalculados=itemsCalculados,itemsCalculadosSinLB=itemsCalculadosSinLB,currentPage=currentPage,currentPage2=currentPage2,
                    proyecto=proyecto,
                    item=item,subtitulo='Error')
    @expose()
    def actualizarRelacion( self, id, tipo, filtros, **named ):
        item=DBSession.query(ItemUsuario).filter_by(id=id).one()
        if (tipo=="1"):
            itemsMifase=DBSession.query(ItemUsuario).filter_by(fase_id=item.fase_id).all()
            idsMifase=[]
            for xItem in itemsMifase:
                idsMifase.append(xItem.id)
            antecesor=DBSession.query(RelacionItem).filter_by(estado_id=1).filter(RelacionItem.antecesor_item_id==id).filter(RelacionItem.sucesor_item_id.in_(idsMifase)).all()
            for i, ant in enumerate(antecesor):
                DBSession.delete(ant)
                DBSession.flush()
        else:
            antecesor=DBSession.query(RelacionItem).filter_by(estado_id=1).filter(RelacionItem.antecesor_item_id==id)
            for i, ant in enumerate(antecesor):
                itemSuc=DBSession.query(ItemUsuario).filter_by(id=ant.sucesor_item_id).one()
                if (item.fase_id!=itemSuc.fase_id):
                    DBSession.delete(ant)
                    DBSession.flush()
        item=DBSession.query(ItemUsuario).filter_by(id=id).one()
        item.estado_id=2
        DBSession.flush()
        itemselect=named.get('itemselect','')
        if itemselect!='':
            try:
                itemselect=int(itemselect)
                itemselect=[itemselect]
                for i, itemRelacion in enumerate(itemselect):
                    new = RelacionItem(
                                       antecesor_item_id=id,
                                       sucesor_item_id = itemRelacion,
                                       tipo=tipo,
                                       estado_id=1
                                       )
                    DBSession.add( new )
                    DBSession.flush()
            except :
                for i, itemRelacion in enumerate(itemselect):
                    new = RelacionItem(
                                       antecesor_item_id=id,
                                       sucesor_item_id = itemRelacion,
                                       tipo=tipo,
                                       estado_id=1
                                       )
                    DBSession.add( new )
                    DBSession.flush()
            
        else:
            if(itemselect=='' )and(item.fase.numero_fase>1):
                    relaciones=DBSession.query(RelacionItem).filter(RelacionItem.antecesor_item_id==item.id).all()
                    if (relaciones.__len__()==0):
                        item.estado_id=1
                        DBSession.flush()
        
        
        submit=named.get('submit','')
        
        if(submit=="Relacionar"):
                redirect( '/item/itemList/'+str(item.fase_id) )    
        else:
            if (submit!="Relacionar"):
                    #redirect( '/item/relacionar_item/'+str(id)+'/'+ str(item.fase_id)+'/1')
                    redirect( '/item/updateRelacion/'+ str(item.fase_id)+'/'+str(id)+'?submit='+submit)    
        flash( '''Atributo Agregado! %s''')
   
    
    @expose()
    def saveRelacion( self, id, tipo, filtros, itemselect,submit ):
        item=DBSession.query(ItemUsuario).filter_by(id=id).one()
        try:
            itemselect=int(itemselect)
            ListaSeleccionada=[itemselect]
            for i,itemRelacion in enumerate(ListaSeleccionada):
                new = RelacionItem(
                                   antecesor_item_id=id,
                                   sucesor_item_id = itemRelacion,
                                   tipo=tipo,
                                   estado_id=1
                                   )
                DBSession.add( new )
                DBSession.flush()
        except :
            for i, itemRelacion in enumerate(itemselect):
                new = RelacionItem(
                               antecesor_item_id=id,
                               sucesor_item_id = itemRelacion,
                               tipo=tipo,
                               estado_id=1
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
        relacionSucesores = DBSession.query(RelacionItem).filter_by(estado_id=1).filter_by(sucesor_item_id=idAntecesor).order_by(RelacionItem.id).all()
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
            try:
                itemselect=int(itemSelec)
                itemSeleccionado=DBSession.query(ItemUsuario).filter(ItemUsuario.id==itemselect).order_by(ItemUsuario.id)
            except:
                itemSeleccionado=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(itemSelec)).order_by(ItemUsuario.id)
        itemUsuario=DBSession.query(ItemUsuario).filter_by(id=id).one()
        fase=DBSession.query(Fase).filter_by(id=itemUsuario.fase_id).one()
        submit=named.get( 'submit')            
        if (tipo_r=="1"):
            #Necesario para el control de ciclos
            relacionSucesores = DBSession.query(RelacionItem).filter_by(estado_id=1).filter_by(sucesor_item_id=id).order_by(RelacionItem.id).all()
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
            #Relacionar solamente con items con LB (Ahora cambie con cualquier item si es tipo_r=1!!)
            estados=[1,2,3,4,5,8]
            
            items=DBSession.query(ItemUsuario).filter_by(fase_id=idFase).filter(ItemUsuario.id!=id).filter(~ItemUsuario.id.in_(itemCiclos)).filter(ItemUsuario.estado_id.in_(estados))
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
                faseAnterior=DBSession.query(Fase).filter_by(proyecto_id=faseActual.proyecto_id).filter_by(numero_fase=faseActual.numero_fase-1).one()
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
            itemselecccionado = DBSession.query(RelacionItem).filter_by(estado_id=1).filter_by(antecesor_item_id=idItem).filter(RelacionItem.sucesor_item_id.in_(item_sucesores)).all()      
            itemselect=""
            for item in itemselecccionado:
                itemselect=itemselect+"itemselect="+str(item.sucesor_item_id)+"&"
            redirect( '/item/editar_relacion/'+str(idItem)+'/'+ str(fase.id)+'/1?'+str(itemselect))        
        else: 
            item_sucesores = DBSession.query(ItemUsuario.id).filter(ItemUsuario.fase_id!=idFase).all()
            itemselecccionado = DBSession.query(RelacionItem).filter_by(estado_id=1).filter_by(antecesor_item_id=idItem).filter(RelacionItem.sucesor_item_id.in_(item_sucesores)).all()      
            itemselect=""
            for item in itemselecccionado:
                itemselect=itemselect+"itemselect="+str(item.sucesor_item_id)+"&"
            redirect( '/item/editar_relacion/'+str(idItem)+'/'+ str(fase.id)+'/2?'+str(itemselect))        
    
    @require(All(in_group('Aprobador', msg='Debe poseer Rol "Aprobador" para aprobar Items'),
                 has_permission('Aprobar items', msg='Debe poseer Permiso "Aprobar items" aprobar Items')))
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
        path=named.get('return','0')
        
        #CONSULTA ALA BD
        lbSolicitadas=DBSession.query(LineaBase).filter_by(apertura="1").filter(LineaBase.fase_id==idFase).all()
        itemsLBSol=[]
        for idLB in lbSolicitadas:
            items=DBSession.query(ItemUsuario).filter(ItemUsuario.estado_id==3).filter(ItemUsuario.linea_base_id==idLB.id).all()
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
                items=DBSession.query(ItemUsuario).filter(ItemUsuario.estado_id==3).filter(ItemUsuario.linea_base_id==idLB.id).all()
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
        path=named.get('return','0')
        retorno="/item/itemList/"+idFase
        if path!=0:
            retorno=path
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
                fase=DBSession.query(Fase).filter_by(id=idFase).one()
                fase.estado_id=2
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
            items=DBSession.query(ItemUsuario).filter(ItemUsuario.estado_id==3).filter(ItemUsuario.linea_base_id==idLB.id).all()
            codigosItemsSol=""
            for item in items:
                codigosItemsSol=codigosItemsSol+"|"+item.cod_item+" "
            itemsLBSol.append(codigosItemsSol)

        fase=DBSession.query(Fase).filter_by(id=idFase).one()
        lineasBases=DBSession.query(LineaBase).filter(LineaBase.fase_id==fase.id).filter_by(estado_id=1).order_by(LineaBase.id).all()
        lbIds=[]
        itemsLB=[]
        for idLB in lineasBases:
            lbIds.append(idLB.id)
            items=DBSession.query(ItemUsuario).filter(ItemUsuario.estado_id==3).filter(ItemUsuario.linea_base_id==idLB.id).all()
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
                items=DBSession.query(ItemUsuario).filter(ItemUsuario.estado_id==3).filter(ItemUsuario.linea_base_id==idLB.id).all()
                codigosItemsSol=""
                for item in items:
                    codigosItemsSol=codigosItemsSol+"|"+item.cod_item+" "
                itemsLBSol.append(codigosItemsSol)

        if (filtro!=""):
            if filtro.isdigit():
                lineasBases=DBSession.query(LineaBase).filter(LineaBase.fase_id==idFase).filter_by(id=filtro).filter_by(estado_id=1).order_by(LineaBase.id).all()
            else:
                lineasBases=DBSession.query(LineaBase).filter(LineaBase.fase_id==idFase).filter(LineaBase.comentario.like('%'+str(filtro)+'%')).filter_by(estado_id=1).order_by(LineaBase.id).all()
            lbIds=[]
            itemsLB=[]
            for idLB in lineasBases:
                lbIds.append(idLB.id)
                items=DBSession.query(ItemUsuario).filter(ItemUsuario.estado_id==3).filter(ItemUsuario.linea_base_id==idLB.id).all()
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
            try:
                itemselect=int(itemselect_car)
                itemselect=[itemselect]
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
            except :
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
            estados=[1,2,3,4,5,8]
            items=DBSession.query(ItemUsuario).filter_by(fase_id=idFase).filter(ItemUsuario.estado_id.in_(estados)).filter(ItemUsuario.id!=id)
            fasesRelacion=DBSession.query(Fase).filter_by(id=idFase).one()
            itemSelec=named.get( 'itemselect','0')
            if(submit=="Buscar"): 
                expresion=named.get( 'filtros')
                expre_cad=expresion
                if (itemSelec!='0'):
                    itemSeleccionado=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(itemSelec)).order_by(ItemUsuario.id)
                items=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==idFase).filter(or_(ItemUsuario.descripcion.like('%'+str(expre_cad)+'%'),(ItemUsuario.cod_item.like('%'+str(expre_cad)+'%')))).filter(ItemUsuario.estado_id.in_(estados)).order_by(ItemUsuario.id)
        else:
            if (tipo_r=="2"):
                muestraBoton="false"
                tipo=2
                tipoRelacion="Antecesor/Sucesor(*)"
                observacion="Una relacion Antecesor/Sucesor indica una relacion entre un item de la fase actual(Antecesor) con un item perteneciente a la fase inmediatamente anterior(Sucesor)"
                faseActual=DBSession.query(Fase).filter_by(id=idFase).one()
                faseAnterior=DBSession.query(Fase).filter_by(proyecto_id=faseActual.proyecto_id).filter_by(numero_fase=faseActual.numero_fase-1).one()
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
                    item=item,subtitulo='Relacionar-Item')
        
    @expose('gestionitem.templates.item.itemInfo')
    def itemInfo(self,id,**named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        itemUsuario=DBSession.query(ItemUsuario).filter_by(id=id).one()
        current_files = DBSession.query(ArchivosAdjuntos).filter_by(item_usuario_id=id).all()
        ###OBTIENE LOS ATRIBUTOS DEL TIPO DE ITEM
        conTipo=0
        atributos=""
        tipoItem=""
        atributoValor=[]
        if (itemUsuario.tipo_item_id!=None):
            conTipo=1
            tipo=DBSession.query(TipoItemUsuario).filter_by(id=itemUsuario.tipo_item_id).one()
            tipoItem=tipo.descripcion
            atributos=DBSession.query(TipoItemUsuarioAtributos).filter_by(tipo_item_id=tipo.id).order_by(TipoItemUsuarioAtributos.id).all()
            
        
            for i, atri in enumerate(atributos):
                atributoValor.append(DBSession.query(TipoItemUsuarioAtributosValor).filter_by(item_usuario_id=itemUsuario.id).filter_by(atributo_id=atri.id).one())
        if (conTipo==0):
            tipoItem="General"
        
        ###FIN OBTIENE LOS ATRIBUTOS DEL TIPO DE ITEM
        
        fase=DBSession.query(Fase).filter_by(id=itemUsuario.fase_id).one()
        relaciones=DBSession.query(RelacionItem).filter_by(estado_id=1).filter_by(antecesor_item_id=id).filter_by(estado_id=1).order_by(RelacionItem.id)
        relacionesSucesores=DBSession.query(RelacionItem).filter_by(estado_id=1).filter_by(sucesor_item_id=id).filter_by(estado_id=1).order_by(RelacionItem.id)
        idrelaciones=[0]
        idrelacionesSucesor=[0]
        idFaseRelacion=[0]
        idFaseRelacionSucesor=[0]
        contRelaciones=0
        contRelacionesSucesores=0
        ##GRAFICA RELACIONES####
        A=pgv.AGraph(directed=True,strict=True,rankdir='LR')
       
        
        A.node_attr['fixedsize']='true'
       
        
        A.add_node(itemUsuario.cod_item,color='blue')
        
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
            idFaseRelacionSucesor.append(item.fase_id)    
        A.graph_attr['epsilon']='0.3'
        print A.string()
        A.write('/home/pyworkspace/GestionItems/src/GestionItem/gestionitem/public/images/relaciones.png')
        A.write('/home/pyworkspace/GestionItems/src/GestionItem/gestionitem/public/images/relaciones.png')
        B=pgv.AGraph('/home/pyworkspace/GestionItems/src/GestionItem/gestionitem/public/images/relaciones.png')
        B.layout() # layout with default (neato)
        B.draw('/home/pyworkspace/GestionItems/src/GestionItem/gestionitem/public/images/relaciones.png') # draw png
        fasesRelacionadosSucesoras=DBSession.query(Fase).filter(Fase.id.in_(idFaseRelacionSucesor)).order_by(Fase.id)
        
        fasesRelacionados=DBSession.query(Fase).filter(Fase.id.in_(idFaseRelacion)).order_by(Fase.id)
        lista=range(100)
        lista=""   
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        item=itemUsuario
        return dict(page='Nuevo Item',user=user,current_files=current_files,
                    fase=fase,contRelaciones=contRelaciones,itemsAntecesoresRelacionados=itemsAntecesoresRelacionados,contRelacionesSucesores=contRelacionesSucesores,itemsRelacionados=itemsRelacionados,fasesRelacionados=fasesRelacionados,
                    proyecto=proyecto,lista=lista,fasesRelacionadosSucesoras=fasesRelacionadosSucesoras,
                    conTipo=conTipo,
                    atributos=atributos,atributoValor=atributoValor,tipoItem=tipoItem, 
                    item=item,subtitulo='Informacion-Item')
    
    
    @expose(content_type=CUSTOM_CONTENT_TYPE)
    def view(self, fileid, idItem):
        try:
            userfile = DBSession.query(ArchivosAdjuntos).filter_by(id=fileid).one()
            iid= idItem
        except:
            redirect("/")
        content_types = {
            'display': {'.png': 'image/jpeg', '.jpeg':'image/jpeg', '.jpg':'image/jpeg', '.gif':'image/jpeg'},
            'download': {'.pdf':'application/pdf', '.zip':'application/zip','.rar':'application/x-rar-compressed', '.txt': 'text/plain',
                         '.py':'application/text','.c':'application/text','.java':'application/text'}
        }
        for file_type in content_types['display']:
            if userfile.nombre.endswith(file_type):
                response.headers["Content-Type"] = content_types['display'][file_type]
        for file_type in content_types['download']:
            if userfile.nombre.endswith(file_type):
                response.headers["Content-Type"] = content_types['download'][file_type]
                response.headers["Content-Disposition"] = 'attachment; filename="'+userfile.nombre+'"'
        if userfile.nombre.find(".") == -1:
            response.headers["Content-Type"] = "text/plain"
        return userfile.archivo
   
        return redirect('/desarrollar/items/index/?itemid='+str(iid))
        
    @expose('gestionitem.templates.item.verificarItem')
    def verificarItem(self,id, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        itemUsuario=DBSession.query(ItemUsuario).filter_by(id=id).one()
        
        ###OBTIENE LOS ATRIBUTOS DEL TIPO DE ITEM
        conTipo=0
        atributos=""
        tipoItem=""
        atributoValor=[]
        if (itemUsuario.tipo_item_id!=None):
            conTipo=1
            tipo=DBSession.query(TipoItemUsuario).filter_by(id=itemUsuario.tipo_item_id).one()
            tipoItem=tipo.descripcion
            atributos=DBSession.query(TipoItemUsuarioAtributos).filter_by(tipo_item_id=tipo.id).order_by(TipoItemUsuarioAtributos.id).all()
            
        
            for i, atri in enumerate(atributos):
                atributoValor.append(DBSession.query(TipoItemUsuarioAtributosValor).filter_by(item_usuario_id=itemUsuario.id).filter_by(atributo_id=atri.id).one())
        if (conTipo==0):
            tipoItem="General"
        
        ###FIN OBTIENE LOS ATRIBUTOS DEL TIPO DE ITEM
        
        
        
        
        fase=DBSession.query(Fase).filter_by(id=itemUsuario.fase_id).one()
        relaciones=DBSession.query(RelacionItem).filter_by(estado_id=1).filter_by(antecesor_item_id=id).filter_by(estado_id=1).order_by(RelacionItem.id)
        relacionesSucesores=DBSession.query(RelacionItem).filter_by(estado_id=1).filter_by(sucesor_item_id=id).filter_by(estado_id=1).order_by(RelacionItem.id)
        idrelaciones=[0]
        idrelacionesSucesor=[0]
        idFaseRelacion=[0]
        idFaseRelacionSucesor=[0]
        contRelaciones=0
        contRelacionesSucesores=0
        ##GRAFICA RELACIONES####
        A=pgv.AGraph(directed=True,strict=True,rankdir='LR')
       
        
        A.node_attr['fixedsize']='true'
       
        
        A.add_node(itemUsuario.cod_item,color='blue')
        
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
            idFaseRelacionSucesor.append(item.fase_id)    
        A.graph_attr['epsilon']='0.3'
        print A.string()
        A.write('/home/pyworkspace/GestionItems/src/GestionItem/gestionitem/public/images/relaciones.png')
        A.write('/home/pyworkspace/GestionItems/src/GestionItem/gestionitem/public/images/relaciones.png')
        B=pgv.AGraph('/home/pyworkspace/GestionItems/src/GestionItem/gestionitem/public/images/relaciones.png')
        B.layout() # layout with default (neato)
        B.draw('/home/pyworkspace/GestionItems/src/GestionItem/gestionitem/public/images/relaciones.png') # draw png
        fasesRelacionadosSucesoras=DBSession.query(Fase).filter(Fase.id.in_(idFaseRelacionSucesor)).order_by(Fase.id)
        
        fasesRelacionados=DBSession.query(Fase).filter(Fase.id.in_(idFaseRelacion)).order_by(Fase.id)
        lista=range(100)
        lista=""   
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        item=itemUsuario
        return dict(page='Nuevo Item',user=user,
                    fase=fase,contRelaciones=contRelaciones,itemsAntecesoresRelacionados=itemsAntecesoresRelacionados,contRelacionesSucesores=contRelacionesSucesores,itemsRelacionados=itemsRelacionados,fasesRelacionados=fasesRelacionados,
                    proyecto=proyecto,lista=lista,fasesRelacionadosSucesoras=fasesRelacionadosSucesoras,
                    conTipo=conTipo,
                    atributos=atributos,atributoValor=atributoValor,tipoItem=tipoItem,  
                    item=item,subtitulo='Revision-Item')
    @expose()
    def itemVerificado(self, id, idFase,  **nammed):
        itemUsuario=DBSession.query(ItemUsuario).filter_by(id=id).one()
        itemUsuario.estado_id=3
        DBSession.flush()
        estados=[1,2,3,4,5,8]
        itemsEnLB=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==idFase).filter(ItemUsuario.estado_id.in_(estados)).order_by(ItemUsuario.id).all()
        faseConLB=0
        for itemP in itemsEnLB:
            if itemP.estado_id!=3:
                faseConLB=1
        if faseConLB==0:
            fase=DBSession.query(Fase).filter_by(id=idFase).one()
            fase.estado_id=4
            DBSession.flush()
               
        redirect( '/item/itemList/'+idFase )    
        flash( '''Item Aprobado! %s''')
 
    
    
    
    def calcularImpacto(self, idItemActual, ItemsCalculados, CalcImpacto):
        itemActual = DBSession.query(ItemUsuario).filter_by(id=idItemActual).one()
        ItemsCalculados.append(itemActual.id)
        #itemsRelacionados = DBSession.query(RelacionItem).filter(or_(RelacionItem.sucesor_item_id == itemActual.id, RelacionItem.antecesor_item_id == itemActual.id)).filter(and_(~RelacionItem.antecesor_item_id.in_(ItemsCalculados), ~RelacionItem.antecesor_item_id.in_(ItemsCalculados))).order_by(RelacionItem.id).all()
        itemsRelacionados = DBSession.query(RelacionItem).filter_by(estado_id=1).filter(or_(RelacionItem.sucesor_item_id == itemActual.id, RelacionItem.antecesor_item_id == itemActual.id)).order_by(RelacionItem.id).all()

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
        # OBTIENE LOS ATRIBUTOS DEL TIPO DE ITEM
        conTipo=0
        atributos=""
        tipoItem=""
        atributoValor=[]
        if (itemUsuario.tipo_item_id!=None):
            conTipo=1
            tipo=DBSession.query(TipoItemUsuario).filter_by(id=itemUsuario.tipo_item_id).one()
            tipoItem=tipo.descripcion
            atributos=DBSession.query(TipoItemUsuarioAtributos).filter_by(tipo_item_id=tipo.id).order_by(TipoItemUsuarioAtributos.id).all()
            
        
            for i, atri in enumerate(atributos):
                atributoValor.append(DBSession.query(TipoItemUsuarioAtributosValor).filter_by(item_usuario_id=itemUsuario.id).filter_by(atributo_id=atri.id).one())
        if (conTipo==0):
            tipoItem="General"
        
        ###FIN OBTIENE LOS ATRIBUTOS DEL TIPO DE ITEM
        
        
        
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
                    conTipo=conTipo,
                    atributos=atributos,atributoValor=atributoValor,tipoItem=tipoItem,
                    fase=fase,itemsCalculados=itemsCalculados,currentPage=currentPage,
                    proyecto=proyecto, calculoImpacto=calculoImpacto,
                    item=item,subtitulo='ABM-Item')
              
  
    @expose('gestionitem.templates.item.historialItem')
    def historialItem(self,idItem, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        
        #CONSULTA ALA BD
        itemActual=DBSession.query(ItemUsuario).filter_by(id=idItem).one()
        ####AGREGAR LUEGO EN ITEM INFO!!!!
        conTipo=0
        atributos=""
        tipoItem=""
        atributoValor=[]
        if (itemActual.tipo_item_id!=None):
            conTipo=1
            tipo=DBSession.query(TipoItemUsuario).filter_by(id=itemActual.tipo_item_id).one()
            tipoItem=tipo.descripcion
            atributos=DBSession.query(TipoItemUsuarioAtributos).filter_by(tipo_item_id=tipo.id).order_by(TipoItemUsuarioAtributos.id).all()
            
        
            for i, atri in enumerate(atributos):
                atributoValor.append(DBSession.query(TipoItemUsuarioAtributosValor).filter_by(item_usuario_id=itemActual.id).filter_by(atributo_id=atri.id).one())
        if (conTipo==0):
            tipoItem="General"
        
           
        fase=DBSession.query(Fase).filter_by(id=itemActual.fase_id).one()
        
        
        fasesDelUsuario=DBSession.query(UsuarioFaseRol).filter_by(fase_id=fase.id).filter_by(user_id=user.user_id).all()
        
        esDesarrollador=0
        esAprobador=0
        
        for fg in fasesDelUsuario:
            if(fg.rol.group_name=="Desarrollador"):
                esDesarrollador=1
            if(fg.rol.group_name=="Aprobador"):
                esAprobador=1
        
        itemsAnteriores=DBSession.query(ItemUsuario).filter(ItemUsuario.id!=itemActual.id).filter_by(cod_item=itemActual.cod_item).filter_by(fase_id=itemActual.fase_id).order_by(ItemUsuario.version).all()
        
        filtro=named.get('filtros','')
        if (filtro!=""):
            if filtro.isdigit():
                itemsAnteriores=DBSession.query(ItemUsuario).filter(ItemUsuario.id!=itemActual.id).filter_by(cod_item=itemActual.cod_item).filter_by(fase_id=itemActual.fase_id).filter(ItemUsuario.version==int(filtro)).order_by(ItemUsuario.version).all()
            else:
                itemsAnteriores=DBSession.query(ItemUsuario).filter(ItemUsuario.id!=itemActual.id).filter_by(cod_item=itemActual.cod_item).filter_by(fase_id=itemActual.fase_id).filter(ItemUsuario.descripcion.like('%'+str(filtro)+'%')).order_by(ItemUsuario.version).all()
            
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        #from webhelpers import paginate
        count = itemsAnteriores.__len__()
        page =int( named.get( 'page', '1'))
        currentPage = paginate.Page(
            itemsAnteriores, page, item_count=count, 
            items_per_page=3,
        )
        
        
        itemsAnteriores = currentPage.items
        expresion=str(named.get( 'expresion'))
        expre_cad=expresion
        filtro=""
        item=itemActual
        muestraBoton="false"
        return dict(page='Historial-Item',esDesarrollador=esDesarrollador,esAprobador=esAprobador,user=user,itemsAnteriores=itemsAnteriores,conTipo=conTipo,
                    atributos=atributos,atributoValor=atributoValor,tipoItem=tipoItem,
                    muestraBoton=muestraBoton,
                    named=named,filtro=filtro,
                    fase=fase,item=item,  
                    proyecto=proyecto,currentPage = currentPage,subtitulo='Historial-Item')
        
        
    @expose('gestionitem.templates.item.listaItemsElim')
    def listaItemsElim(self,idFase, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user'] 
        #CONSULTA ALA BD
        
        fasesDelUsuario=DBSession.query(UsuarioFaseRol).filter_by(fase_id=idFase).filter_by(user_id=user.user_id).all()
        
        esDesarrollador=0 
        esAprobador=0
        
        for fg in fasesDelUsuario:
            if(fg.rol.group_name=="Desarrollador"):
                esDesarrollador=1
            if(fg.rol.group_name=="Aprobador"):
                esAprobador=1
        
        fase=DBSession.query(Fase).filter_by(id=idFase).one()
        estados=[1,2,3,4,5,8]
        itemsElimFase=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==fase.id).filter_by(estado_id=7).order_by(ItemUsuario.id).all()
        itemsEnProd=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==fase.id).filter(ItemUsuario.estado_id.in_(estados)).order_by(ItemUsuario.id).all()
        filtro=named.get('filtros','')
        if (filtro!=""):
                itemsElimFase=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==fase.id).filter_by(estado_id=7).filter(ItemUsuario.descripcion.like('%'+str(filtro)+'%')).order_by(ItemUsuario.id).all()   
        proyecto=DBSession.query(Proyecto).filter_by(id=fase.proyecto_id).one()
        #from webhelpers import paginate
        count = itemsElimFase.__len__()
        page =int( named.get( 'page', '1'))
        currentPage = paginate.Page(
            itemsElimFase, page, item_count=count, 
            items_per_page=3,
        )
        itemsEnProduccion=[]
        for itemP in itemsEnProd:
            itemsEnProduccion.append(itemP.cod_item)
        
        
        expresion=str(named.get( 'expresion'))
        expre_cad=expresion
        filtro=""
        muestraBoton="false"
        return dict(page='Historial-Item',esDesarrollador=esDesarrollador,esAprobador=esAprobador , user=user,itemsEnProduccion=itemsEnProduccion,
                    muestraBoton=muestraBoton,itemsEnProd=itemsEnProd,
                    named=named,filtro=filtro,itemsElimFase=itemsElimFase,
                    fase=fase,  
                    proyecto=proyecto,currentPage = currentPage,subtitulo='Items Eliminados')
        
    @expose()
    def revivirItem(self,idItem, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user'] 
        itemElim=DBSession.query(ItemUsuario).filter_by(id=idItem).one()
        itemsOtrasVersiones=DBSession.query(ItemUsuario).filter_by(cod_item=itemElim.cod_item).order_by(ItemUsuario.version).all()  
        versionUltima=itemsOtrasVersiones[-1].version
        versionActual=versionUltima+1
        
      
        
        
        listaIds=DBSession.query(ItemUsuario).order_by(ItemUsuario.id)
        fase=DBSession.query(Fase).filter_by(id=itemElim.fase_id).one()
        if (listaIds.count()>0):
            listaTemp=listaIds[-1]
            id=listaTemp.id + 1
        else: 
            id=1                            
        
        archivosAnteriores=DBSession.query(ArchivosAdjuntos).filter_by(item_usuario_id=itemElim.id).all()
        for newFile in archivosAnteriores:
            new_file2 = ArchivosAdjuntos(nombre=newFile.nombre, archivo=newFile.archivo,item_usuario_id=id)
            DBSession.add(new_file2)
            DBSession.flush()
        if (itemElim.tipo_item_id!=None):
                new = ItemUsuario()
                new.id=id                              
                new.tipo_item_id = itemElim.tipo_item_id
                new.fase_id = itemElim.fase_id
                new.numero_cod = itemElim.numero_cod
                new.cod_item=itemElim.cod_item
                new.prioridad=itemElim.prioridad
                new.descripcion=itemElim.descripcion
                new.version=versionActual
                new.estado_id=1
                
                DBSession.add( new )
                DBSession.flush()
                
                atributos=DBSession.query(TipoItemUsuarioAtributos).filter_by(tipo_item_id=itemElim.tipo_item_id).order_by(TipoItemUsuarioAtributos.id).all()
                idAtributos=[]
                for i, atri in enumerate(atributos):
                    idAtributos.append(atri.id)
                listaValor=DBSession.query(TipoItemUsuarioAtributosValor).filter_by(item_usuario_id=itemElim.id).filter(TipoItemUsuarioAtributosValor.atributo_id.in_(idAtributos)).order_by(TipoItemUsuarioAtributosValor.id).all()
                if type(idAtributos) == list:
                    for i, valor in enumerate(listaValor):
                        new2 = TipoItemUsuarioAtributosValor(
                        item_usuario_id = id,
                        atributo_id = idAtributos[i],
                        valor=valor.valor
                        )
                        DBSession.add( new2 )
                else:
                    new2 = TipoItemUsuarioAtributosValor(
                        item_usuario_id = id,
                        atributo_id = idAtributos,
                        valor=listaValor
                        )
                    DBSession.add( new2 )
        elif(itemElim.tipo_item_id==None):
            new = ItemUsuario()
            new.id=id,                              
            new.fase_id = itemElim.fase_id,
            new.cod_item= itemElim.cod_item,
            new.numero_cod = itemElim.numero_cod,
            new.prioridad= itemElim.prioridad,
            new.descripcion= itemElim.descripcion,
            new.estado_id=1,
            new.version=versionActual,
            new.tipo_item_generico = 1
            DBSession.add( new )
            DBSession.flush()
        
     
        itemNuevo=DBSession.query(ItemUsuario).filter_by(id=id).one()
        
        if fase.numero_fase==1:
            itemNuevo.estado_id=2
            DBSession.flush()
        fase.estado_id=2
        DBSession.flush()
        redirect( '/item/itemList/'+str(itemNuevo.fase_id) )
        flash( '''Tipo Item Agregado! %s''')    
       
    
    
    @expose()
    def revertirItemSinLB( self,idItemActual,idItemAnterior,  **named):
        itemActual=DBSession.query(ItemUsuario).filter_by(id=idItemActual).one()
        itemAnterior=DBSession.query(ItemUsuario).filter_by(id=idItemAnterior).one()
        itemActual.estado_id=6
        DBSession.flush()
        #Obtiene los items relacionados
        relacionesActual = DBSession.query(RelacionItem).filter_by(estado_id=1).filter(or_(RelacionItem.sucesor_item_id == itemActual.id, RelacionItem.antecesor_item_id == itemActual.id)).order_by(RelacionItem.id).all()
        relaciones_antecesores=[]
        relaciones_sucesores=[]
        for i, relActual in enumerate(relacionesActual):
            relaciones_antecesores.append(relActual.antecesor_item_id)
            relaciones_sucesores.append(relActual.sucesor_item_id)
            relActual.estado_id=2
            DBSession.flush()
        itemsRelacionados = DBSession.query(ItemUsuario).filter(or_(ItemUsuario.id.in_(relaciones_antecesores),ItemUsuario.id.in_(relaciones_sucesores))).all()
        for i, itemActual in enumerate(itemsRelacionados):
            
            if (itemActual.estado_id==3) or (itemActual.estado_id==5):
                itemActual.estado_id=4
                DBSession.flush()
        version=itemActual.version
        version=version+1        
        listaIds=DBSession.query(ItemUsuario).order_by(ItemUsuario.id)
        if (listaIds.count()>0):
            listTemp=listaIds[-1]
            id=listTemp.id + 1
        else: 
            id=1
        try:
            userfile = DBSession.query(ArchivosAdjuntos).filter_by(item_usuario_id=itemActual.id).all()
            for archivo in userfile:
                DBSession.delete(archivo)
        except:
            userfile = ""
    
        archivosAnteriores=DBSession.query(ArchivosAdjuntos).filter_by(item_usuario_id=itemAnterior.id).all()
        for newFile in archivosAnteriores:
            new_file2 = ArchivosAdjuntos(nombre=newFile.nombre, archivo=newFile.archivo,item_usuario_id=id)
            DBSession.add(new_file2)
            DBSession.flush()                                
        if (itemActual.tipo_item_id!=None):
            new = ItemUsuario()
            new.id=id                              
            new.tipo_item_id = itemAnterior.tipo_item_id
            new.fase_id = itemAnterior.fase_id
            new.numero_cod = itemAnterior.numero_cod
            new.cod_item=itemAnterior.cod_item
            new.prioridad=itemAnterior.prioridad
            new.descripcion=itemAnterior.descripcion
            new.version=version
            new.estado_id=2
            
            DBSession.add( new )
            DBSession.flush()
            
            atributos=DBSession.query(TipoItemUsuarioAtributos).filter_by(tipo_item_id=itemActual.tipo_item_id).order_by(TipoItemUsuarioAtributos.id).all()
            idAtributos=[]
            for i, atri in enumerate(atributos):
                idAtributos.append(atri.id)
            listaValor=DBSession.query(TipoItemUsuarioAtributosValor).filter_by(item_usuario_id=itemAnterior.id).filter(TipoItemUsuarioAtributosValor.atributo_id.in_(idAtributos)).order_by(TipoItemUsuarioAtributosValor.id).all()
            if type(idAtributos) == list:
                for i, valor in enumerate(listaValor):
                    new2 = TipoItemUsuarioAtributosValor(
                    item_usuario_id = id,
                    atributo_id = idAtributos[i],
                    valor=valor.valor
                    )
                    DBSession.add( new2 )
            else:
                new2 = TipoItemUsuarioAtributosValor(
                    item_usuario_id = id,
                    atributo_id = idAtributos,
                    valor=listaValor
                    )
                DBSession.add( new2 )
        elif(itemActual.tipo_item_id==None):
            new = ItemUsuario()
            new.id=id,                              
            new.fase_id = itemAnterior.fase_id,
            new.cod_item= itemAnterior.cod_item,
            new.numero_cod = itemAnterior.numero_cod,
            new.prioridad= itemAnterior.prioridad,
            new.descripcion= itemAnterior.descripcion,
            new.estado_id=2,
            new.version=version,
            new.tipo_item_generico=1,
            DBSession.add( new )
            DBSession.flush()
        
        for i, relNueva in enumerate(relacionesActual):
            newRel = RelacionItem()
            if (relNueva.antecesor_item_id!=itemActual.id):
                newRel.antecesor_item_id=relNueva.antecesor_item_id
            else:
                newRel.antecesor_item_id=id
            if (relNueva.sucesor_item_id!=itemActual.id):
                newRel.sucesor_item_id=relNueva.sucesor_item_id
            else:
                newRel.sucesor_item_id=id
            newRel.tipo=relNueva.tipo
            newRel.estado_id=1
            DBSession.add(newRel)
            DBSession.flush()
        
        
        redirect( '/item/itemList/'+str(itemActual.fase_id) )
        flash( '''Tipo Item Agregado! %s''')    
        
    
    
    @expose()
    def revertirItemLB( self,idItemActual,idItemAnterior,  **named):
        #Obtiene el id del Item a modificar
        itemActual=DBSession.query(ItemUsuario).filter_by(id=idItemActual).one()
        if (itemActual.estado_id==5):
            lbActualAnt=itemActual.linea_base_ant
            lbAC=DBSession.query(LineaBase).filter_by(id=itemActual.linea_base_id).one()
            lbAC.estado_id=5
            DBSession.flush()
            itemAnterior=DBSession.query(ItemUsuario).filter_by(id=idItemAnterior).one()
            itemActual.estado_id=6
            DBSession.flush()
            #Obtiene los items relacionados
            relacionesActual = DBSession.query(RelacionItem).filter_by(estado_id=1).filter(or_(RelacionItem.sucesor_item_id == itemActual.id, RelacionItem.antecesor_item_id == itemActual.id)).order_by(RelacionItem.id).all()
            relaciones_antecesores=[]
            relaciones_sucesores=[]
            for i, relActual in enumerate(relacionesActual):
                relaciones_antecesores.append(relActual.antecesor_item_id)
                relaciones_sucesores.append(relActual.sucesor_item_id)
                relActual.estado_id=2
                DBSession.flush()
            itemsRelacionados = DBSession.query(ItemUsuario).filter(or_(ItemUsuario.id.in_(relaciones_antecesores),ItemUsuario.id.in_(relaciones_sucesores))).all()
            for i, itemActual in enumerate(itemsRelacionados):
                
                if (itemActual.estado_id==3) or (itemActual.estado_id==5):
                    itemActual.estado_id=4
                    DBSession.flush()
                    lineaBase=DBSession.query(LineaBase).filter_by(id=itemActual.linea_base_id)
                    lineaBase.estado_id=4
                    DBSession.flush()
            version=itemActual.version
            version=version+1        
            listaIds=DBSession.query(ItemUsuario).order_by(ItemUsuario.id)
            if (listaIds.count()>0):
                listTemp=listaIds[-1]
                id=listTemp.id + 1
            else: 
                id=1
            try:
                userfile = DBSession.query(ArchivosAdjuntos).filter_by(item_usuario_id=itemActual.id).all()
                for archivo in userfile:
                    DBSession.delete(archivo)
            except:
                userfile = ""
        
            archivosAnteriores=DBSession.query(ArchivosAdjuntos).filter_by(item_usuario_id=itemAnterior.id).all()
            for newFile in archivosAnteriores:
                new_file2 = ArchivosAdjuntos(nombre=newFile.nombre, archivo=newFile.archivo,item_usuario_id=id)
                DBSession.add(new_file2)
                DBSession.flush()                                
            if (itemActual.tipo_item_id!=None):
                new = ItemUsuario()
                new.id=id                              
                new.tipo_item_id = itemAnterior.tipo_item_id
                new.fase_id = itemAnterior.fase_id
                new.numero_cod = itemAnterior.numero_cod
                new.cod_item=itemAnterior.cod_item
                new.prioridad=itemAnterior.prioridad
                new.descripcion=itemAnterior.descripcion
                new.version=version
                new.linea_base_ant=lbActualAnt
                new.estado_id=2
                
                DBSession.add( new )
                DBSession.flush()
                
                atributos=DBSession.query(TipoItemUsuarioAtributos).filter_by(tipo_item_id=itemActual.tipo_item_id).order_by(TipoItemUsuarioAtributos.id).all()
                idAtributos=[]
                for i, atri in enumerate(atributos):
                    idAtributos.append(atri.id)
                listaValor=DBSession.query(TipoItemUsuarioAtributosValor).filter_by(item_usuario_id=itemAnterior.id).filter(TipoItemUsuarioAtributosValor.atributo_id.in_(idAtributos)).order_by(TipoItemUsuarioAtributosValor.id).all()
                if type(idAtributos) == list:
                    for i, valor in enumerate(listaValor):
                        new2 = TipoItemUsuarioAtributosValor(
                        item_usuario_id = id,
                        atributo_id = idAtributos[i],
                        valor=valor.valor
                        )
                        DBSession.add( new2 )
                else:
                    new2 = TipoItemUsuarioAtributosValor(
                        item_usuario_id = id,
                        atributo_id = idAtributos,
                        valor=listaValor
                        )
                    DBSession.add( new2 )
            elif(itemActual.tipo_item_id==None):
                new = ItemUsuario()
                new.id=id,                              
                new.fase_id = itemAnterior.fase_id,
                new.cod_item= itemAnterior.cod_item,
                new.numero_cod = itemAnterior.numero_cod,
                new.prioridad= itemAnterior.prioridad,
                new.descripcion= itemAnterior.descripcion,
                new.estado_id=2,
                new.linea_base_ant=lbActualAnt,
                new.version=version,
                new.tipo_item_generico=1,
                DBSession.add( new )
                DBSession.flush()
            
            for i, relNueva in enumerate(relacionesActual):
                newRel = RelacionItem()
                if (relNueva.antecesor_item_id!=itemActual.id):
                    newRel.antecesor_item_id=relNueva.antecesor_item_id
                else:
                    newRel.antecesor_item_id=id
                if (relNueva.sucesor_item_id!=itemActual.id):
                    newRel.sucesor_item_id=relNueva.sucesor_item_id
                else:
                    newRel.sucesor_item_id=id
                newRel.tipo=relNueva.tipo
                newRel.estado_id=1
                DBSession.add(newRel)
                DBSession.flush()
        
        
        redirect( '/item/itemList/'+str(itemActual.fase_id) )
        flash( '''Tipo Item Agregado! %s''')
        
        
    @expose()
    def revertirItem( self,idItemActual,idItemAnterior,  **named):
        #Obtiene el id del Item a modificar
        itemActual=DBSession.query(ItemUsuario).filter_by(id=idItemActual).one()
        if (itemActual.estado_id!=5):
            redirect( '/item/revertirItemSinLB/'+idItemActual+'/'+idItemAnterior)
        else:
            redirect( '/item/avisoRevertirItemLB/'+idItemActual+'/'+idItemAnterior)
            lbActualAnt=itemActual.linea_base_ant
            lbAC=DBSession.query(LineaBase).filter_by(id=itemActual.linea_base_id).one()
            lbAC.estado_id=5
            DBSession.flush()
            itemAnterior=DBSession.query(ItemUsuario).filter_by(id=idItemAnterior).one()
            itemActual.estado_id=6
            DBSession.flush()
            #Obtiene los items relacionados
            relacionesActual = DBSession.query(RelacionItem).filter_by(estado_id=1).filter(or_(RelacionItem.sucesor_item_id == itemActual.id, RelacionItem.antecesor_item_id == itemActual.id)).order_by(RelacionItem.id).all()
            relaciones_antecesores=[]
            relaciones_sucesores=[]
            for i, relActual in enumerate(relacionesActual):
                relaciones_antecesores.append(relActual.antecesor_item_id)
                relaciones_sucesores.append(relActual.sucesor_item_id)
                relActual.estado_id=2
                DBSession.flush()
            itemsRelacionados = DBSession.query(ItemUsuario).filter(or_(ItemUsuario.id.in_(relaciones_antecesores),ItemUsuario.id.in_(relaciones_sucesores))).all()
            for i, itemActual in enumerate(itemsRelacionados):
                
                if (itemActual.estado_id==3) or (itemActual.estado_id==5):
                    itemActual.estado_id=4
                    DBSession.flush()
                    lineaBase=DBSession.query(LineaBase).filter_by(id=itemActual.linea_base_id)
                    lineaBase.estado_id=4
                    DBSession.flush()
            version=itemActual.version
            version=version+1        
            listaIds=DBSession.query(ItemUsuario).order_by(ItemUsuario.id)
            if (listaIds.count()>0):
                listTemp=listaIds[-1]
                id=listTemp.id + 1
            else: 
                id=1
            try:
                userfile = DBSession.query(ArchivosAdjuntos).filter_by(item_usuario_id=itemActual.id).all()
                for archivo in userfile:
                    DBSession.delete(archivo)
            except:
                userfile = ""
        
            archivosAnteriores=DBSession.query(ArchivosAdjuntos).filter_by(item_usuario_id=itemAnterior.id).all()
            for newFile in archivosAnteriores:
                new_file2 = ArchivosAdjuntos(nombre=newFile.nombre, archivo=newFile.archivo,item_usuario_id=id)
                DBSession.add(new_file2)
                DBSession.flush()                                
            if (itemActual.tipo_item_id!=None):
                new = ItemUsuario()
                new.id=id                              
                new.tipo_item_id = itemAnterior.tipo_item_id
                new.fase_id = itemAnterior.fase_id
                new.numero_cod = itemAnterior.numero_cod
                new.cod_item=itemAnterior.cod_item
                new.prioridad=itemAnterior.prioridad
                new.descripcion=itemAnterior.descripcion
                new.version=version
                new.linea_base_ant=lbActualAnt
                new.estado_id=2
                
                DBSession.add( new )
                DBSession.flush()
                
                atributos=DBSession.query(TipoItemUsuarioAtributos).filter_by(tipo_item_id=itemActual.tipo_item_id).order_by(TipoItemUsuarioAtributos.id).all()
                idAtributos=[]
                for i, atri in enumerate(atributos):
                    idAtributos.append(atri.id)
                listaValor=DBSession.query(TipoItemUsuarioAtributosValor).filter_by(item_usuario_id=itemAnterior.id).filter(TipoItemUsuarioAtributosValor.atributo_id.in_(idAtributos)).order_by(TipoItemUsuarioAtributosValor.id).all()
                if type(idAtributos) == list:
                    for i, valor in enumerate(listaValor):
                        new2 = TipoItemUsuarioAtributosValor(
                        item_usuario_id = id,
                        atributo_id = idAtributos[i],
                        valor=valor.valor
                        )
                        DBSession.add( new2 )
                else:
                    new2 = TipoItemUsuarioAtributosValor(
                        item_usuario_id = id,
                        atributo_id = idAtributos,
                        valor=listaValor
                        )
                    DBSession.add( new2 )
            elif(itemActual.tipo_item_id==None):
                new = ItemUsuario()
                new.id=id,                              
                new.fase_id = itemAnterior.fase_id,
                new.cod_item= itemAnterior.cod_item,
                new.numero_cod = itemAnterior.numero_cod,
                new.prioridad= itemAnterior.prioridad,
                new.descripcion= itemAnterior.descripcion,
                new.estado_id=2,
                new.linea_base_ant=lbActualAnt,
                new.version=version,
                new.tipo_item_generico=1,
                DBSession.add( new )
                DBSession.flush()
            
            for i, relNueva in enumerate(relacionesActual):
                newRel = RelacionItem()
                if (relNueva.antecesor_item_id!=itemActual.id):
                    newRel.antecesor_item_id=relNueva.antecesor_item_id
                else:
                    newRel.antecesor_item_id=id
                if (relNueva.sucesor_item_id!=itemActual.id):
                    newRel.sucesor_item_id=relNueva.sucesor_item_id
                else:
                    newRel.sucesor_item_id=id
                newRel.tipo=relNueva.tipo
                newRel.estado_id=1
                DBSession.add(newRel)
                DBSession.flush()
        
        
        redirect( '/item/itemList/'+str(itemActual.fase_id) )
        flash( '''Tipo Item Agregado! %s''')