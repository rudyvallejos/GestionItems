'''
Created on 06/05/2011

@author: Rudy Vallejos
'''
from gestionitem.lib.base import BaseController
from gestionitem.model.proyecto import Proyecto , EstadoProyecto, Fase, UsuarioFaseRol, EstadoFase
from gestionitem.model import DBSession
from gestionitem.model.auth import User, Rol
from tg import expose, flash, tmpl_context, validate, redirect
from sprox.formbase import AddRecordForm
from tg import request
from sqlalchemy.sql.expression import or_
from repoze.what.predicates import not_anonymous, in_group, has_permission, All
from tg.decorators import require



class AddProyecto(AddRecordForm):
    __model__ = Proyecto
    __omit_fields__ = ['id', 'estadoObj', 'fecha_creacion']
    

add_Proyecto_form = AddProyecto(DBSession)



class ProyectoController(BaseController):
    allow_only = not_anonymous(msg='Solo usuarios registrados pueden acceder a los proyectos')
    
    @expose()
    def index(self, **named):
        """Handle the front-page."""
        redirect('/proyecto/lista')
        
    
    @expose(template='gestionitem.templates.proyectoTmpl.lista')
    def lista(self, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        expresion = named.get('expresion')
        orden = named.get('submit')
        proyectos = []
        

        id = identity['user']
        for grupo in id.groups:
            if(grupo.group_name == 'Administrador'):
                if(orden == None or orden == 'Listar Todos'):
                    proyectos = DBSession.query(Proyecto).all()
                    muestraBoton = "false"
                elif(orden == 'Buscar' and expresion != None):
                    proyectoxlider = DBSession.query(Proyecto).join((User, Proyecto.lider)).filter(User.user_name.like('%' + expresion + '%')).order_by(Proyecto.descripcion).all()
                    proyectoxdescripcion = DBSession.query(Proyecto).filter(Proyecto.descripcion.like('%' + expresion + '%')).order_by(Proyecto.descripcion).all()
                    proyectoxestado = DBSession.query(Proyecto).join((EstadoProyecto, Proyecto.estadoObj)).filter(EstadoProyecto.descripcion.like('%' + expresion + '%')).order_by(Proyecto.descripcion).all()
                    proyectos = proyectoxdescripcion + proyectoxlider + proyectoxestado
                    muestraBoton = "true"
            
            if(grupo.group_name == 'LiderProyecto'):
                if(orden == None or orden == 'Listar Todos'):
                    proyectosLider = DBSession.query(Proyecto).filter(Proyecto.id_lider == id.user_id).all()
                    muestraBoton = "false"
                elif(orden == 'Buscar' and expresion != None):
                    proyectoxlider = DBSession.query(Proyecto).join((User, Proyecto.lider)).filter(User.user_name.like('%' + expresion + '%')).filter(Proyecto.id_lider == id.user_id).order_by(Proyecto.descripcion).all()
                    proyectoxdescripcion = DBSession.query(Proyecto).filter(Proyecto.descripcion.like('%' + expresion + '%')).filter(Proyecto.id_lider == id.user_id).order_by(Proyecto.descripcion).all()
                    proyectoxestado = DBSession.query(Proyecto).join((EstadoProyecto, Proyecto.estadoObj)).filter(EstadoProyecto.descripcion.like('%' + expresion + '%')).filter(Proyecto.id_lider == id.user_id).order_by(Proyecto.descripcion).all()
                    proyectosLider = proyectoxdescripcion + proyectoxlider + proyectoxestado
                    muestraBoton = "true"
                elif(orden):
                    proyectosLider = DBSession.query(Proyecto).filter(Proyecto.id_lider == id.user_id).all()
                    muestraBoton = "false"
                    
                
                for proyect in proyectosLider:
                    if(proyect in proyectos):
                        proyect.setDefinir()
                        proyect.setmostrarFases()
                        indice = proyectos.index(proyect)
                        proyectos[indice] = proyect
                        
                    else:
                        proyect.setDefinir()
                        proyect.setmostrarFases()
                        proyectos.append(proyect)
                        
            
            if(grupo.group_name == 'Desarrollador' or grupo.group_name == 'Aprobador'):
                proyectosDesarrollador = []
                ufrs = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.user_id == id.user_id).all()
               
                if(orden == None or orden == 'Listar Todos'): 
                    for ufr in ufrs:
                        fase = DBSession.query(Fase).filter(Fase.id == ufr.fase_id).one()
                        proyectosDesarrollador.append(fase.proyectoObj) 
                    proyectosDesarrolladorset = set(proyectosDesarrollador)
                    proyectosDesarrollador = list(proyectosDesarrolladorset)
                    muestraBoton = "false"
                    
                elif(orden == 'Buscar' and expresion != None):
                    proyectoxlider = DBSession.query(Proyecto).join((User, Proyecto.lider)).filter(User.user_name.like('%' + expresion + '%')).order_by(Proyecto.descripcion).all()
                    proyectoxdescripcion = DBSession.query(Proyecto).filter(Proyecto.descripcion.like('%' + expresion + '%')).order_by(Proyecto.descripcion).all()
                    proyectoxestado = DBSession.query(Proyecto).join((EstadoProyecto, Proyecto.estadoObj)).filter(EstadoProyecto.descripcion.like('%' + expresion + '%')).order_by(Proyecto.descripcion).all()
                    proyectosaux = proyectoxlider + proyectoxdescripcion + proyectoxestado
                    proyectosauxset = set(proyectosaux)
                    proyectosaux = list(proyectosauxset)
                    
                    for ufr in ufrs:
                        if ufr.fase.proyectoObj in proyectosaux :
                            proyectosDesarrollador.append(ufr.fase.proyectoObj) 
                    proyectosDesarrolladorset = set(proyectosDesarrollador)
                    proyectosDesarrollador = list(proyectosDesarrolladorset)
                    muestraBoton = "true"
                    
                if proyectos.__len__() > 0:
                    for proyecto1 in proyectosDesarrollador:
                        if proyecto1 in proyectos:
                            proyecto1.setmostrarFases()
                        else:
                            proyecto1.setmostrarFases()
                            proyectos.append(proyecto1)
                        
                
                else:
                    proyectos = proyectosDesarrollador
                    for proyecto12 in proyectos:
                        proyecto12.setmostrarFases()
                     
                
    
                            
        proset = set(proyectos)
        proyectos = list(proset)
        
        from webhelpers import paginate
        
        count = proyectos.__len__()
        page = int(named.get('page', '1'))
        currentPage = paginate.Page(
            proyectos, page, item_count=count,
            items_per_page=5,
        )
        proyectos = currentPage.items
        return dict(page='Lista de proyectos',
                    proyectos=proyectos,
                    subtitulo='Proyectos',
                    user=user,
                    muestraBoton=muestraBoton,
                    currentPage=currentPage)
        
        
        
    @expose('gestionitem.templates.proyectoTmpl.nuevo')
    @require(All(in_group('Administrador'), has_permission('crear proyecto'),
                 msg='Debe poseer Rol "Administrador" para crear nuevos proyectos'))
    def nuevo(self):
        """Handle the front-page."""
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        lideres = DBSession.query(User).join((Rol, User.groups)).filter(Rol.group_name == 'LiderProyecto').all()
        nombreProyectos = []
        proyectos = DBSession.query(Proyecto).all()
        for proyecto in proyectos:
            nombreProyectos.append(proyecto.descripcion)
            nombreProyectos.append(",")
        return dict(
            page='Nuevo Proyecto',
            lideres=lideres,
            nombreProyectos=nombreProyectos,
            user=user
        )
               


    @expose()
    @require(All(in_group('Administrador'), has_permission('crear proyecto'),
                 msg='Debe poseer Rol "Administrador" para crear nuevos proyectos'))
    def add_proyecto(self, descripcion, lider, **named):
        """Registra un proyecto nuevo """
        new = Proyecto(
            descripcion=descripcion,
            id_lider=lider,
            estado=1,
        )
        DBSession.add(new)
        flash('''Proyecto Registrado: %s''' % (descripcion,))
        redirect('./index')
        
    
    @expose(template="gestionitem.templates.proyectoTmpl.editar")
    @require(All(in_group('Administrador'), has_permission('editar proyecto'),
                 msg='Debe poseer Rol "Administrador" editar proyectos'))
    def editar(self, id):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        
        proyecto = DBSession.query(Proyecto).filter_by(id=id).one()

        if proyecto.lider != None:
            usuarios = DBSession.query(User).join((Rol, User.groups)).filter(Rol.group_name == 'LiderProyecto').filter(User.user_id != proyecto.lider.user_id).all()
        else:
            usuarios = DBSession.query(User).join((Rol, User.groups)).filter(Rol.group_name == 'LiderProyecto')
            
        return dict(page='Editar Proyecto',
                    id=id,
                    proyecto=proyecto,
                    subtitulo='ABM-Proyecto',
                    user=user,
                    usuarios=usuarios)
    
    
    @expose()
    @require(All(in_group('Administrador'), has_permission('editar proyecto'),
                 msg='Debe poseer Rol "Administrador" editar proyectos'))    
    def actualizar(self, id, descripcion, id_user , submit):
        """Create a new movie record"""
        proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
        proyecto.descripcion = descripcion
        proyecto.id_lider = id_user
        
        DBSession.flush()
        
        redirect('/proyecto')
        
    
    @expose()
    @require(in_group('Administrador', msg='Debe poseer Rol "Administrador" eliminar proyectos'))
    @require(All(in_group('Administrador'), has_permission('eliminar proyecto'),
                 msg='Debe poseer Rol "Administrador" eliminar proyectos'))
    def eliminar(self, id):
        DBSession.delete(DBSession.query(Proyecto).filter_by(id=id).one())
        redirect('/proyecto')    
    
    @expose()    
    def cambiarEstado(self, id, estado, **named):
        proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
        proyecto.estado = estado
        DBSession.flush()
        redirect('/proyecto')


        
    @expose(template="gestionitem.templates.proyectoTmpl.proyectoDef")
    @require(All(in_group('LiderProyecto'), has_permission('definir proyecto'),
                 msg='Debe poseer Rol "LiderProyecto" para definir proyectos'))
    def proyectoDef(self, id, **named):
        fases = DBSession.query(Fase).filter(Fase.proyecto_id == id)
        
        proyecto_id = id
                
        return dict(page='Definir Proyecto',
                    proyecto_id=proyecto_id,

                    subtitulo='Definir Proyecto'
                    )
    
    
    @expose(template="gestionitem.templates.proyectoTmpl.faseList")
    @require(All(in_group('LiderProyecto'), has_permission('definir proyecto'),
                 msg='Debe poseer Rol "LiderProyecto" para definir fases'))
    def definir_fase(self, id, **named):
        identity = request.environ.get('repoze.who.identity')
        fases = []
        
        expresion = named.get('expresion')
        orden = named.get('submit')
        
        iduser = identity['user']
        
        proyecto = DBSession.query(Proyecto).filter(Proyecto.id == id).one()
        proyectoEstado = proyecto.estado
        for grupo in iduser.groups:
            if(grupo.group_name == 'LiderProyecto'):
                if(orden == None or orden == 'Listar Todos' or orden == 'Cancelar'):
                    fases = DBSession.query(Fase).filter(Fase.proyecto_id == id).all()
                    muestraBoton = "false"
                elif(orden == 'Buscar' and expresion != None):
                    fasesxdescripcion = DBSession.query(Fase).filter(Fase.proyecto_id == id).filter(Fase.descripcion.like('%' + expresion + '%')).all()
                    fasesxestado = DBSession.query(Fase).join((EstadoFase, Fase.estadoObj)).filter(Fase.proyecto_id == id).filter(EstadoFase.descripcion.like('%' + expresion + '%')).all()
                    fases = fasesxdescripcion + fasesxestado
                    muestraBoton = "true" 
                    
            elif(grupo.group_name == 'Desarrollador' or grupo.group_name == 'Aprobador'):
                ufrs = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.user_id == iduser.user_id).all()
                for ufr in ufrs:
                    if(str(ufr.fase.proyecto_id) == id):
                        fasetot = []
                        if(orden == None or orden == 'Listar Todos' or orden == 'Cancelar'):
                            fase1 = DBSession.query(Fase).filter(Fase.id == ufr.fase_id).one()
                            muestraBoton = "false"
                        elif(orden == 'Buscar' and expresion != None):
                            fase1xdescripcion = DBSession.query(Fase).filter(Fase.id == ufr.fase_id).filter(Fase.descripcion.like('%' + expresion + '%')).all()
                            fase1xestado = DBSession.query(Fase).join((EstadoFase, Fase.estadoObj)).filter(Fase.id == ufr.fase_id).filter(EstadoFase.descripcion.like('%' + expresion + '%')).all()
                            fasetot = fase1xdescripcion + fase1xestado
                            muestraBoton = "true"
                        for fase1 in fasetot :     
                            if(fase1 in fases):
                                pass
                            else:
                                fases.append(fase1)
        
        faseset = set(fases)
        fases = list(faseset)
        proyecto_id = id
        
        from webhelpers import paginate
        count = fases.__len__()
        page = int(named.get('page', '1'))
        currentPage = paginate.Page(
            fases, page, item_count=count,
            items_per_page=5,
        )
        fases = currentPage.items
        return dict(page='Lista de fases',
                    fases=fases,
                    proyecto_id=proyecto_id,
                    subtitulo='fases',
                    user=iduser,
                    proyectoEstado=proyectoEstado,
                    muestraBoton=muestraBoton,
                    currentPage=currentPage)
        
    
    
    @expose(template="gestionitem.templates.proyectoTmpl.agregar_fase")
    @require(All(in_group('LiderProyecto'), has_permission('crear fase'),
                 msg='Debe poseer Rol "LiderProyecto" para agregar fases'))
    def agregar_fase(self, id):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        proyecto = DBSession.query(Proyecto).filter(Proyecto.id == id).one()
        fase = DBSession.query(Fase).filter(Fase.proyecto_id == proyecto.id).all()
        codigos = []
        for i, cod in enumerate(fase):
            codigos.append(cod.codigo_fase)
            codigos.append(",")
        return dict(page='Nueva Fase',
                    proyecto=proyecto, user=user , codigos=codigos)
        
    
    @expose()
    @require(All(in_group('LiderProyecto'), has_permission('crear fase'),
                 msg='Debe poseer Rol "LiderProyecto" para agregar fases'))
    def save_fase(self, id, descripcion_proyecto, nombre_fase, codFase, submit):
        fases = DBSession.query(Fase).filter(Fase.proyecto_id == id)
        num = fases.count() + 1
        
        new = Fase(descripcion=nombre_fase,
                   proyecto_id=id,
                   numero_fase=num,
                   estado_id=3,
                   codigo_fase=codFase
                   )
        DBSession.add(new)
        flash('''Fase Registrada: %s''' % (nombre_fase,))
        redirect('/proyecto/definir_fase/' + id)
        
    
    @expose("gestionitem.templates.proyectoTmpl.editar_fase")
    @require(All(in_group('LiderProyecto'), has_permission('editar fase'),
                 msg='Debe poseer Rol "LiderProyecto" para editar fases'))
    def editar_fase(self, id):
        
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        fase = DBSession.query(Fase).filter(Fase.id == id).one()
        fases = DBSession.query(Fase).filter(Fase.proyecto_id == fase.proyecto_id).all()
        codigos = []
        for i, cod in enumerate(fases):
            codigos.append(cod.codigo_fase)
            codigos.append(",")
            
        return dict(page='Editar fase',
                    id=id,
                    fase=fase,
                    user=user,
                    codigos=codigos,
                    subtitulo='ABM-Fase')
        
           
    @expose() 
    @require(All(in_group('LiderProyecto'), has_permission('editar fase'),
                 msg='Debe poseer Rol "LiderProyecto" para editar fases'))   
    def actualizar_fase(self, id, descripcion_proyecto, nombre_fase, numero_fase, submit):
        fase = DBSession.query(Fase).filter(Fase.id == id).one()
        fase.descripcion = nombre_fase
        fase.numero_fase = numero_fase
#        fase.codigo_fase = codFase
        DBSession.flush()
        redirect('/proyecto/definir_fase/' + str(fase.proyecto_id))
        
    
    @expose()
    @require(All(in_group('LiderProyecto'), has_permission('eliminar fase'),
                 msg='Debe poseer Rol "LiderProyecto" para eliminar fases'))
    def eliminar_fase(self, id):
        fase = DBSession.query(Fase).filter(Fase.id == id).one()
        id_proyecto = fase.proyecto_id
        ufrs = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.fase_id == id).all()
        for ufr in ufrs:
            DBSession.delete(ufr)
        DBSession.flush()
#        itemusuarios = DBSession.query(TipoItemUsuario).filter(TipoItemUsuario.fase_id == id).all()
                    
        DBSession.delete(fase)
        fases = DBSession.query(Fase).filter(Fase.proyecto_id == id_proyecto).order_by(Fase.id).all()
        for i, fase in enumerate(fases):
            fase.numero_fase = i + 1
            DBSession.flush()
        
        
        redirect('/proyecto/definir_fase/' + str(id_proyecto))    
        
    
    @expose("gestionitem.templates.proyectoTmpl.usuario_faseList")
    @require(in_group('LiderProyecto', msg='Debe poseer Rol "LiderProyecto" para listar usuarios'))
    def usuario_faseList(self, id, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        expresion = named.get('expresion')
        orden = named.get('submit')
        
        usuarioFaseRols = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.fase_id == id).all()
        
        for ufr in usuarioFaseRols:
            if ufr.usuario == None:
                DBSession.delete(ufr)
                DBSession.flush()
        if(orden == None or orden == 'Listar Todos' or orden == 'Cancelar'):
            usuarioFaseRol = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.fase_id == id).all()
            muestraBoton = "false"
        elif(orden == 'Buscar' and expresion != None):
            usuarioxnombre = DBSession.query(UsuarioFaseRol).join((User, UsuarioFaseRol.usuario)).filter(UsuarioFaseRol.fase_id == id).filter(User.user_name.like('%' + expresion + '%')).order_by(User.user_name).all()
            usuarioxrol = DBSession.query(UsuarioFaseRol).join((Rol, UsuarioFaseRol.rol)).filter(UsuarioFaseRol.fase_id == id).filter(Rol.group_name.like('%' + expresion + '%')).all()
            usuarioFaseRol1 = usuarioxnombre + usuarioxrol
            usuarioFaseRol = set(usuarioFaseRol1)
            usuarioFaseRol = list(usuarioFaseRol)
            muestraBoton = "true"
        fase = DBSession.query(Fase).filter(Fase.id == id).one() 
        from webhelpers import paginate
        count = usuarioFaseRol.__len__()
        page = int(named.get('page', '1'))
        currentPage = paginate.Page(
            usuarioFaseRol, page, item_count=count,
            items_per_page=5,
        )
        usuarioFaseRol = currentPage.items
        descripcion = fase.descripcion
        
        return dict(page='Usuarios de fase ' + descripcion,
                    usuariofaserol=usuarioFaseRol,
                    descripcion=descripcion,
                    fase_id=id,
                    subtitulo='Usuarios de fase',
                    proyecto_id=fase.proyecto_id,
                    user=user,
                    muestraBoton=muestraBoton,
                    currentPage=currentPage
                    ) 
    
    @expose("gestionitem.templates.proyectoTmpl.agregarUsuarioFase")
    @require(All(in_group('LiderProyecto'), has_permission('asignar desarrollador'),
                 msg='LiderProyecto" para agregar usuarios'))
    def agregar_usuario_fase(self, id, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        usuarios = DBSession.query(User).join((Rol, User.groups)).filter(or_(Rol.group_name == 'Aprobador', Rol.group_name == 'Desarrollador')).all()
        roles = DBSession.query(Rol).filter(or_(Rol.group_name == 'Aprobador', Rol.group_name == 'Desarrollador')).all()
        fase = DBSession.query(Fase).filter(Fase.id == id).one()
#        usuarioFaseRol = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.fase_id == id).all()
        
        
        return dict(page='Asignar Usuario a fase ' + fase.descripcion,
                    usuarios=usuarios,
                    roles=roles,
                    proyecto_id=id,
                    user=user,
                    fase=fase) 
        
    @expose()
    @require(All(in_group('LiderProyecto'), has_permission('asignar desarrollador'),
                 msg='Debe poseer Rol "LiderProyecto" para agregar usuarios'))
    def save_usuario_fase(self, fase, user, rol, **named):
        try:
            rol = int(rol)
            try:
                usuarioFaseRol = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.fase_id == fase).filter(UsuarioFaseRol.user_id == user).filter(UsuarioFaseRol.rol_id == rol).one()
                DBSession.delete(usuarioFaseRol)
            except:
                pass
            new = UsuarioFaseRol(user_id=user,
                                    fase_id=fase,
                                    rol_id=rol
                                 ) 
            
            DBSession.add(new)
            
        except:
            
            for rol1 in rol:
                try:
                    usuarioFaseRol = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.fase_id == fase).filter(UsuarioFaseRol.user_id == user).filter(UsuarioFaseRol.rol_id == rol1).one()
                    DBSession.delete(usuarioFaseRol)
                except:
                    pass
                new = UsuarioFaseRol(user_id=user,
                                    fase_id=fase,
                                    rol_id=rol1
                                 ) 
            
                DBSession.add(new)
                
        CambiarEstadoFase = DBSession.query(Fase).filter(Fase.id == fase).one()
        CambiarEstadoFase.estado_id = 1
        redirect('/proyecto/usuario_faseList/' + fase)
        
        
    @expose()
    @require(All(in_group('LiderProyecto'), has_permission('eliminar desarrollador'),
                 msg='Debe poseer Rol "LiderProyecto" para eliminar usuarios'))    
    def eliminar_usuario_fase(self, ufr):
        usuarioFaseRol = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.id == ufr).one()
        fase = usuarioFaseRol.fase_id     
        DBSession.delete(usuarioFaseRol)         
        usuarioFaseRolcantidad = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.fase_id == fase).all()
        if usuarioFaseRolcantidad.__len__() == 0:
            faseCambiarEstado = DBSession.query(Fase).filter(Fase.id == fase).one()
            faseCambiarEstado.estado_id = 3
            DBSession.flush()
                                     
        redirect('/proyecto/usuario_faseList/' + str(fase))
        
        
    @expose("gestionitem.templates.proyectoTmpl.editarUsuarioFase")
    @require(All(in_group('LiderProyecto'), has_permission('editar desarrollador'),
                 msg='Debe poseer Rol "LiderProyecto" para editar usuarios'))
    def editar_usuario_fase(self, ufr, **named):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        usuarioFaseRol = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.id == ufr).one()
        fase = DBSession.query(Fase).filter(Fase.id == usuarioFaseRol.fase_id).one()
        usuario = DBSession.query(User).filter(User.user_id == usuarioFaseRol.user_id).one()
        rol = DBSession.query(Rol).filter(Rol.group_id == usuarioFaseRol.rol_id).one()
        roles = DBSession.query(Rol).filter(or_(Rol.group_name == 'Aprobador', Rol.group_name == 'Desarrollador')).all()
        return dict(page='Editar Usuario de fase' + fase.descripcion,
                    fase=fase,
                    usuario=usuario,
                    roles=roles,
                    rol=rol,
                    user=user,
                    ufr=usuarioFaseRol)
        
    @expose()
    @require(All(in_group('LiderProyecto'), has_permission('editar desarrollador'),
                 msg='Debe poseer Rol "LiderProyecto" para editar usuarios'))
    def actualizar_usuario_fase(self, fase, ufr,  submit, **named):
        rol =named.get('rol')
        usuarioFaseRol = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.id == ufr).one()
        user = usuarioFaseRol.user_id
        
        if rol==None:
            usuarioFaseRol = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.id == ufr).one()
            DBSession.delete(usuarioFaseRol)
        
        else:    
        
            try:
                rol = int(rol)
                try:
                    usuarioFaseRol = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.fase_id == fase).filter(UsuarioFaseRol.user_id == user).filter(UsuarioFaseRol.rol_id == rol).one()
                    DBSession.delete(usuarioFaseRol)
                except:
                    pass
                new = UsuarioFaseRol(user_id=user,
                                        fase_id=fase,
                                        rol_id=rol
                                     ) 
                
                DBSession.add(new)
                
            except:
                
                for rol1 in rol:
                    try:
                        usuarioFaseRol = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.fase_id == fase).filter(UsuarioFaseRol.user_id == user).filter(UsuarioFaseRol.rol_id == rol1).one()
                        DBSession.delete(usuarioFaseRol)
                    except:
                        pass
                    new = UsuarioFaseRol(user_id=user,
                                        fase_id=fase,
                                        rol_id=rol1
                                     ) 
                
                    DBSession.add(new)
        redirect('/proyecto/usuario_faseList/' + fase)
        
        
        
    
         
     
                                            
                                                
    
    
    
    
        



