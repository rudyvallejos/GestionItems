from gestionitem.lib.base import BaseController
from tg import expose,request
from tg import redirect
from sqlalchemy import or_
from gestionitem.model import DBSession
from gestionitem.model.proyecto import ItemUsuario,Fase,LineaBase,Proyecto,TipoItemUsuario,TipoItemUsuarioAtributos
from repoze.what.predicates import not_anonymous, in_group, has_permission, All
from tg.decorators import require


class LineaBaseController(BaseController):
    
    
    @expose(template="gestionitem.templates.lineaBase.generar_linea_base")
    @require(All(in_group('LiderProyecto', msg='Debe poseer Rol "LiderProyecto" para generar lineas bases'),
                 has_permission('Gestionar linea base', msg='Debe poseer Permiso "Generar linea base" para agregar fases')))

    def generar_linea_base(self,idfase,**named):
        #items = DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==idfase).filter(ItemUsuario.estado_id==2).all()
        expresion=""
        
        itemSeleccionado=DBSession.query(ItemUsuario).filter_by(id=-1)
        itemselect=named.get( 'itemselect','0')
        
        fase=DBSession.query(Fase).filter(Fase.id==idfase).one()
        
        if (itemselect!=0 ):
            try:
                itemselect=int(itemselect)
                itemselect=[itemselect]
                itemSeleccionado=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(itemselect)).order_by(ItemUsuario.id)
            except:
                itemSeleccionado=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(itemselect)).order_by(ItemUsuario.id)
        
        submit=named.get( 'submit')
        
        if(submit=="Buscar"): 
            expresion=named.get( 'filtros')
            expre_cad=expresion
            items=DBSession.query(ItemUsuario).filter(ItemUsuario.estado_id==8).filter(ItemUsuario.fase_id==idfase).filter(or_(ItemUsuario.descripcion.like('%'+str(expre_cad)+'%'),(ItemUsuario.cod_item.like('%'+str(expre_cad)+'%')))).order_by(ItemUsuario.id)
        else:
            items = DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==idfase).filter(ItemUsuario.estado_id==8).all()
            
        
        return dict(items=items,fase=fase,filtro=expresion, itemSeleccionado=itemSeleccionado)
    
    @expose()
    def guardar_linea_base(self, faseid,**named):
        
        itemselect = named.get('itemselect')
            
        try:
            itemselect=int(itemselect)
            itemselect=[itemselect]
            itemseleccionados = DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(itemselect)).all()
        
            listaIds=DBSession.query(LineaBase).order_by(LineaBase.id)
            if (listaIds.count()>0):
                list=listaIds[-1]
                id=list.id + 1
            else: 
                id=1    
        
            lb = LineaBase(id = int(id),
                           version = 1,
                           estado_id = 1,
                           fase_id = int(faseid)) 
            DBSession.add(lb)
            DBSession.flush()
        
            for item in itemseleccionados:
                lbAnterior=item.linea_base_ant
                itemsEnLbAnterior= DBSession.query(ItemUsuario).filter(ItemUsuario.linea_base_ant==lbAnterior).all()
                for itemLbAnt in itemsEnLbAnterior:
                    if itemLbAnt.estado_id==5:
                        itemLbAnt.estado_id=3
                        itemLbAnt.linea_base_id= id
                        itemLbAnt.linea_base_ant = id
                item.estado_id = 3
                item.linea_base_id = id
                item.linea_base_ant = id
                DBSession.flush()
        except :
            itemseleccionados = DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(itemselect)).all()
            listaIds=DBSession.query(LineaBase).order_by(LineaBase.id)
            if (listaIds.count()>0):
                list=listaIds[-1]
                id=list.id + 1
            else: 
                id=1    
        
            lb = LineaBase(id = int(id),
                           version = 1,
                           estado_id = 1,
                           fase_id = int(faseid)) 
            DBSession.add(lb)
            DBSession.flush()
        
            for item in itemseleccionados:
                lbAnterior=item.linea_base_ant
                itemsEnLbAnterior= DBSession.query(ItemUsuario).filter(ItemUsuario.linea_base_ant==lbAnterior).all()
                for itemLbAnt in itemsEnLbAnterior:
                    if itemLbAnt.estado_id==5:
                        itemLbAnt.estado_id=3
                        itemLbAnt.linea_base_id= id
                        itemLbAnt.linea_base_ant = id
                item.estado_id = 3
                item.linea_base_id = id
                item.linea_base_ant = id
                DBSession.flush()

        estados=[1,2,3,4,5,8]
        itemsEnLB=DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==faseid).filter(ItemUsuario.estado_id.in_(estados)).order_by(ItemUsuario.id).all()
        faseConLB=0
        for itemP in itemsEnLB:
            if itemP.estado_id!=3:
                faseConLB=1
        if faseConLB==0:
            fase=DBSession.query(Fase).filter_by(id=faseid).one()
            fase.estado_id=4
            DBSession.flush()
       
        redirect('/item/itemList/'+faseid)
        
    @expose(template="gestionitem.templates.lineaBase.lista_linea_base")
    def listar_linea_base(self, idproyecto,idfase, **named):
        
        expresion=""
       
        submit=named.get( 'submit')
        
        if(submit=="Buscar"): 
            expresion=named.get( 'filtro')
            
            if expresion.isdigit():
                lista=DBSession.query(LineaBase).filter(LineaBase.fase_id==idfase).filter(LineaBase.id == int(expresion)).all()
            else:
                lista=DBSession.query(LineaBase).filter(LineaBase.fase_id==idfase).all()
        else:
            lista=DBSession.query(LineaBase).filter(LineaBase.fase_id==idfase).all()
        
        
        fase = DBSession.query(Fase).filter(Fase.id == idfase).one()
        proyecto = DBSession.query(Proyecto).filter(Proyecto.id == idproyecto).one()
        
        
        from webhelpers import paginate
        #count = items.count()
        count = lista.__len__()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            lista, page, item_count=count, 
            items_per_page=2,
        )
        
        lista = currentPage.items
        
        return dict(lista=lista, fase=fase, proyecto=proyecto,filtro=expresion, currentPage=currentPage, page=page)
    
    
    @expose(template="gestionitem.templates.lineaBase.lista_items_x_linea_base")
    def items_linea_base(self, lb_id, idfase, **named):
        
       
        expresion=""
        
        submit=named.get( 'submit')
        
        if(submit=="Buscar"): 
            expresion=named.get( 'filtro')
            expre_cad=expresion
            items=DBSession.query(ItemUsuario).filter(ItemUsuario.estado_id==3).filter(ItemUsuario.linea_base_id==lb_id).filter(or_(ItemUsuario.descripcion.like('%'+str(expre_cad)+'%'),(ItemUsuario.cod_item.like('%'+str(expre_cad)+'%')))).all()
        else:
            items = DBSession.query(ItemUsuario).filter(ItemUsuario.linea_base_id == lb_id).all()
        
        
        fase = DBSession.query(Fase).filter(Fase.id == idfase).one()
        lineabase = DBSession.query(LineaBase).filter(LineaBase.id == lb_id).one()
        
        from webhelpers import paginate
        #count = items.count()
        count = items.__len__()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            items, page, item_count=count, 
            items_per_page=2,
        )
        items = currentPage.items
        
        return dict(items=items, fase=fase, filtro=expresion, lineabase=lineabase, page = page, currentPage=currentPage)
    
    @expose(template="gestionitem.templates.lineaBase.cerrar_linea_base_abierta")
    def cerrar_linea_base_abierta(self,idFase, **named):
        
        identity = request.environ.get('repoze.who.identity')
        user = identity['user'] 
        #CONSULTA ALA BD
        lbSolicitadas=DBSession.query(LineaBase).filter(LineaBase.estado_id == 2).filter(LineaBase.fase_id==idFase).all()
        itemsLBSol=[]
        for idLB in lbSolicitadas:
            items=DBSession.query(ItemUsuario).filter(ItemUsuario.linea_base_id==idLB.id).filter(ItemUsuario.estado_id==5).all()
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
                lbSolicitadas=DBSession.query(LineaBase).filter(LineaBase.estado_id == 2).filter(LineaBase.fase_id==idFase).filter_by(id=filtro).order_by(LineaBase.id).all()
            else:
                lbSolicitadas=DBSession.query(LineaBase).filter(LineaBase.estado_id == 2).filter(LineaBase.fase_id==idFase).filter(LineaBase.descripcion.like('%'+str(filtro)+'%')).order_by(LineaBase.id).all()
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
        from webhelpers import paginate
        count = items.__len__()
        page =int( named.get( 'page', '1'))
        currentPage = paginate.Page(
            items, page, item_count=count, 
            items_per_page=3,
        )
        
        muestraBoton="false"
        return dict(page='Solicitudes de Apertura',user=user,itemsLBSol=itemsLBSol,muestraBoton=muestraBoton,lbSolicitadas=lbSolicitadas,named=named,filtro=filtro,itemSelec=itemSelec,items=items,
                    fase=fase,  
                    proyecto=proyecto,currentPage = currentPage,subtitulo='Solicitudes de Apertura')
        
    @expose()  
    def accionSolicitud( self, idFase, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        
        lbs=DBSession.query(LineaBase).filter_by(fase_id=idFase).filter_by(estado_id = 2).all()
        for lb in lbs:
            accion=named.get(str(lb.id),'')
            if (accion!="") and (accion=="Cerrar"):
                lb.estado_id=1
                DBSession.flush()
                ###Cambia Estado del Item
                items=DBSession.query(ItemUsuario).filter_by(linea_base_id=lb.id).all()
                for item in items:
                    if(item.estado_id == 5):
                        item.estado_id=3
                        DBSession.flush
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
        fase=DBSession.query(Fase).filter_by(id=idFase).one()
                  
        redirect( '/item/itemList/'+str(fase.id) )
        
    @expose(template="gestionitem.templates.proyectoTmpl.listar_proyectos_definidos")
    def listar_proyectos_definidos(self, idfaseDestino,**named):
        
        
        submit=named.get( 'submit')
        
        if(submit=="Buscar"): 
            expresion=named.get( 'filtros')
            expre_cad=expresion
            proyectos = DBSession.query(Proyecto).filter(Proyecto.descripcion.like('%'+str(expre_cad)+'%')).all()
        else:
            proyectos = DBSession.query(Proyecto).all()
        
        
        
        return dict(proyecto=proyectos, filtro='', proy = '1', idfaseDestino=idfaseDestino)
    
    @expose(template="gestionitem.templates.proyectoTmpl.listar_fases_definidas")
    def listar_fases_definidas(self, idfaseDestino,idproyecto, **named):
        expre_cad=""
        proyecto = DBSession.query(Proyecto).filter_by(id= idproyecto).one()
        
        submit=named.get( 'submit')
        
        if(submit=="Buscar"): 
            expresion=named.get( 'filtros')
            expre_cad=expresion
            fases = DBSession.query(Fase).filter(Fase.proyecto_id == idproyecto).filter(Fase.descripcion.like('%'+str(expre_cad)+'%')).all()
        else:
            fases = DBSession.query(Fase).filter(Fase.proyecto_id == idproyecto).all()
        return dict(proyecto=proyecto, fases=fases, filtro = expre_cad, idfaseDestino=idfaseDestino)
    
    @expose(template="gestionitem.templates.proyectoTmpl.importar_tipoItems_proyecto")
    def importar_tipoItems_proyecto(self, idfaseDestino,idfase, **named):
        
        #proyecto= DBSession.query(Proyecto).filter(Proyecto.id == idproyecto).one()
        itemSeleccionado=DBSession.query(TipoItemUsuario).filter_by(id=-1)
        
        itemselect=named.get( 'itemselect','0')
        
        if (itemselect!=0 ):
            
            try:
                itemselect=int(itemselect)
                itemselect=[itemselect]
                itemSeleccionado=DBSession.query(TipoItemUsuario).filter(TipoItemUsuario.id.in_(itemselect)).order_by(TipoItemUsuario.id)
                
            except:
                itemSeleccionado=DBSession.query(TipoItemUsuario).filter(TipoItemUsuario.id.in_(itemselect)).order_by(TipoItemUsuario.id)
        
        fase= DBSession.query(Fase).filter(Fase.id == idfase).one()
        
        proyecto = DBSession.query(Proyecto).filter(Proyecto.id == fase.proyecto_id).one()
        
        submit=named.get('submit')
        
        if(submit=="Buscar"): 
            expresion=named.get( 'filtros')
            expre_cad=expresion
            itemUsuarios = DBSession.query(TipoItemUsuario).filter(TipoItemUsuario.fase_id == idfase).filter(or_(TipoItemUsuario.descripcion.like('%'+str(expre_cad)+'%'),(TipoItemUsuario.codigo.like('%'+str(expre_cad)+'%')))).all()
        else:
            itemUsuarios = DBSession.query(TipoItemUsuario).filter(TipoItemUsuario.fase_id == idfase).all()
        
        
            
        
        return dict(listaItemUser=itemUsuarios, proyecto=proyecto, itemSeleccionado=itemSeleccionado, filtro = "",fase=fase)
        
    @expose()
    def guardar_items_importados(self,idfaseDestino,**named):
        
         
        itemselect = named.get('itemselect')
            
        try:
            itemselect=int(itemselect)
            itemselect=[itemselect]
            tipoItemSeleccionado = DBSession.query(TipoItemUsuario).filter(TipoItemUsuario.id.in_(itemselect)).all()
         
            
            listaIds=DBSession.query(TipoItemUsuario).order_by(TipoItemUsuario.id)
            if (listaIds.count()>0):
                list=listaIds[-1]
                id=list.id + 1
            else: 
                id=1    
        
            ti = TipoItemUsuario(id = int(id),
                                 descripcion = tipoItemSeleccionado.descripcion,
                                 codigo = tipoItemSeleccionado.codigo,
                                 fase_id = idfaseDestino)#el parametro pasado aca debe ir.
            DBSession.add(ti)
            DBSession.flush()
            
            for atributo in tipoItemSeleccionado.atributos:
                
                at = TipoItemUsuarioAtributos(nombre_atributo = atributo.nombre_atributo,
                                              tipo_item_id= int(id),
                                              tipo_id=atributo.tipo_id
                                              )
                           
                DBSession.add(at)
                DBSession.flush()
            
        except:
            
            itemseleccionados = DBSession.query(TipoItemUsuario).filter(TipoItemUsuario.id.in_(itemselect)).all()
            
            for tipoItemSelect in  itemseleccionados:
                
                listaIds=DBSession.query(TipoItemUsuario).order_by(TipoItemUsuario.id)
                if (listaIds.count()>0):
                    list=listaIds[-1]
                    id=list.id + 1
                else: 
                    id=1    
            
                ti = TipoItemUsuario(id = int(id),
                                     descripcion = tipoItemSelect.descripcion,
                                     codigo = tipoItemSelect.codigo,
                                     fase_id = idfaseDestino)#el parametro pasado aca debe ir.
                DBSession.add(ti)
                DBSession.flush()
                
                
                
                for atributo in tipoItemSelect.atributos:
                    
                    at = TipoItemUsuarioAtributos(nombre_atributo = atributo.nombre_atributo,
                                                  tipo_item_id= int(id),
                                                  tipo_id=atributo.tipo_id
                                                  )
                               
                    DBSession.add(at)
                    DBSession.flush()
        
    redirect("/tipoItems/tipoItemUsuario/${idfaseDestino}/lista")
    
    