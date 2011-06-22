from gestionitem.lib.base import BaseController
from tg import expose
from tg import redirect
from sqlalchemy import or_
from gestionitem.model import DBSession
from gestionitem.model.proyecto import ItemUsuario,Fase,LineaBase


class LineaBaseController(BaseController):
    
    
    @expose(template="gestionitem.templates.lineaBase.generar_linea_base")
    def generar_linea_base(self,idfase,**named):
        #items = DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==idfase).filter(ItemUsuario.estado_id==2).all()
        filtro=""
        
        itemSeleccionado=DBSession.query(ItemUsuario).filter_by(id=-1)
        itemSelec=named.get( 'itemselect','0')
        
        fase=DBSession.query(Fase).filter(Fase.id==idfase).one()
        
        if (itemSelec!=0 ):
            itemSeleccionado=DBSession.query(ItemUsuario).filter(ItemUsuario.id.in_(itemSelec)).order_by(ItemUsuario.id)
        
        
        submit=named.get( 'submit')
        
        if(submit=="Buscar"): 
            expresion=named.get( 'filtros')
            expre_cad=expresion
            items=DBSession.query(ItemUsuario).filter(ItemUsuario.estado_id==8).filter(ItemUsuario.fase_id==idfase).filter(or_(ItemUsuario.descripcion.like('%'+str(expre_cad)+'%'),(ItemUsuario.cod_item.like('%'+str(expre_cad)+'%')))).order_by(ItemUsuario.id)
        else:
            items = DBSession.query(ItemUsuario).filter(ItemUsuario.fase_id==idfase).filter(ItemUsuario.estado_id==8).all()
            
        
        return dict(items=items,fase=fase,filtro=filtro, itemSeleccionado=itemSeleccionado)
    
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

        
        
        redirect('/item/itemList/'+faseid)
    