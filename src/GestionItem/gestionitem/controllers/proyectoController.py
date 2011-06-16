'''
Created on 06/05/2011

@author: Rudy Vallejos
'''
from gestionitem.lib.base import BaseController
from gestionitem.model.proyecto import Proyecto , EstadoProyecto, Fase, UsuarioFaseRol
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
    __omit_fields__ = ['id','estadoObj','fecha_creacion']
    

add_Proyecto_form = AddProyecto(DBSession)



class ProyectoController(BaseController):
    allow_only = not_anonymous(msg='Solo usuarios registrados pueden acceder a los proyectos')
    
    @expose()
    def index(self):
        """Handle the front-page."""
        redirect('/proyecto/lista')
        
    
    @expose(template='gestionitem.templates.proyectoTmpl.lista')
    def lista(self, **named):
        identity = request.environ.get('repoze.who.identity')

#        mostrarDefinir= False
#        mostrarFases = False
        proyectos = []


        id = identity['user']
        for grupo in id.groups:
            if(grupo.group_name =='Administrador'):
                proyectos =DBSession.query(Proyecto).all()
            
            if(grupo.group_name =='LiderProyecto'):
                proyectosLider =DBSession.query(Proyecto).filter(Proyecto.id_lider == id.user_id).all()
                for proyect in proyectosLider:
                    if(proyect in proyectos):
                        proyect.setDefinir()
                        indice= proyectos.index(proyect)
                        proyectos[indice] = proyect
                        
                    else:
                        proyect.setDefinir()
                        proyectos.append(proyect)
                            
                    
                
    
            if(grupo.group_name =='Desarrollador' or grupo.group_name =='Aprobador'):
                lp=[]
                
                ufrs = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.user_id==id.user_id).all()
                for ufr in ufrs:
                    if(ufr.fase.proyecto_id in lp or ufr.fase.proyectoObj in proyectos ):
                        ufr.fase.proyectoObj.setmostrarFases()
                        indice = proyectos.index(ufr.fase.proyectoObj)
                        proyectos[indice] = ufr.fase.proyectoObj
                    else:
                        lp.append(ufr.fase.proyecto_id)
                        proyect1 =DBSession.query(Proyecto).filter(Proyecto.id==ufr.fase.proyecto_id).one()
                        proyect1.setmostrarFases()
                        proyectos.append(proyect1)
             
        
        from webhelpers import paginate
        if(grupo.group_name =='Desarrollador' or grupo.group_name =='Aprobador'):
            count = proyectos.__len__()
        else:    
            count = proyectos.__len__()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            proyectos, page, item_count=count,
            items_per_page=5,
        )
        proyectos = currentPage.items
        return dict(page='Lista de proyectos',
                    proyectos=proyectos, 
                    subtitulo='Proyectos',
                    currentPage = currentPage)
        
        
    @expose('gestionitem.templates.proyectoTmpl.nuevo')
    @require(All(in_group('Administrador'), has_permission('crear proyecto'),
                 msg='Debe poseer Rol "Administrador" para crear nuevos proyectos'))
    def nuevo(self):
        """Handle the front-page."""
        lideres = DBSession.query(User).join((Rol, User.groups)).filter(Rol.group_name =='LiderProyecto').all()
#        tmpl_context.add_Proyecto_form = add_Proyecto_form

        return dict(
            page='Nuevo Proyecto',
            lideres = lideres
        )
               


    @expose()
    @require(All(in_group('Administrador'), has_permission('crear proyecto'),
                 msg='Debe poseer Rol "Administrador" para crear nuevos proyectos'))
    def add_proyecto( self, descripcion, lider, **named ):
        """Registra un proyecto nuevo """
        new = Proyecto(
            descripcion = descripcion,
            id_lider = lider,
            estado = 1,
        )
        DBSession.add( new )
        flash( '''Proyecto Registrado: %s'''%( descripcion, ))
        redirect( './index' )
        
    
    @expose(template="gestionitem.templates.proyectoTmpl.editar")
    @require(All(in_group('Administrador'), has_permission('editar proyecto'),
                 msg='Debe poseer Rol "Administrador" editar proyectos'))
    def editar(self,id):
        proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
#        usuarios=DBSession.query(User).filter(User.user_id != proyecto.lider.user_id)
        if proyecto.lider !=None:
            usuarios = DBSession.query(User).join((Rol, User.groups)).filter(Rol.group_name =='LiderProyecto').filter(User.user_id != proyecto.lider.user_id).all()
        else:
            usuarios = DBSession.query(User).join((Rol, User.groups)).filter(Rol.group_name =='LiderProyecto')
            
        return dict(page='Editar Proyecto',
                    id=id,
                    proyecto=proyecto,
                    subtitulo='ABM-Proyecto',
                    usuarios = usuarios)
    
    
    @expose()
    @require(All(in_group('Administrador'), has_permission('editar proyecto'),
                 msg='Debe poseer Rol "Administrador" editar proyectos'))    
    def actualizar( self, id, descripcion,id_user ,submit ):
        """Create a new movie record"""
        proyecto = DBSession.query(Proyecto).filter_by(id=id).one()
        proyecto.descripcion = descripcion
        proyecto.id_lider = id_user
        
        DBSession.flush()
        
        redirect( '/proyecto' )
        
    
    @expose()
    @require(in_group('Administrador', msg='Debe poseer Rol "Administrador" eliminar proyectos') )
    @require(All(in_group('Administrador'), has_permission('eliminar proyecto'),
                 msg='Debe poseer Rol "Administrador" eliminar proyectos'))
    def eliminar(self,id):
        DBSession.delete(DBSession.query(Proyecto).filter_by(id=id).one())
        redirect( '/proyecto' )    


        
    @expose(template="gestionitem.templates.proyectoTmpl.proyectoDef")
    @require(All(in_group('LiderProyecto'), has_permission('definir proyecto'),
                 msg='Debe poseer Rol "LiderProyecto" para definir proyectos'))
    def proyectoDef(self, id, **named):
        fases = DBSession.query(Fase).filter(Fase.proyecto_id == id)
        
#        if fases.count()== 0:
#           mostrarLink= False
#        else:
#            mostrarLink = True
        proyecto_id = id
                
        return dict(page='Definir Proyecto',
                    proyecto_id = proyecto_id,  
#                    mostrarLink = mostrarLink,
                    subtitulo='Definir Proyecto'
                    )
    
    
    @expose(template="gestionitem.templates.proyectoTmpl.faseList")
    @require(All(in_group('LiderProyecto'), has_permission('definir proyecto'),
                 msg='Debe poseer Rol "LiderProyecto" para definir fases'))
    def definir_fase(self, id, **named):
        identity = request.environ.get('repoze.who.identity')
#        mostrarNuevo = False
#        mostrarAsigUsu= False
#        mostrarEditar = False
#        mostrarEliminar = False
        fases = []
        
        iduser = identity['user']
        
        for grupo in iduser.groups:
            if(grupo.group_name =='LiderProyecto'):
#                mostrarNuevo = True
#                mostrarEditar = True
#                mostrarEliminar = True
#                mostrarAsigUsu = True
                fases = DBSession.query(Fase).filter(Fase.proyecto_id == id).all()
            elif(grupo.group_name =='Desarrollador' or grupo.group_name =='Aprobador'):
                ufrs = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.user_id==iduser.user_id).all()
                for ufr in ufrs:
                    if(str(ufr.fase.proyecto_id) == id):
                        fase1=DBSession.query(Fase).filter(Fase.id==ufr.fase_id).one()
                        if(fase1 in fases):
                            pass
                        else:
                            fases.append(fase1)
                        
                
        
        proyecto_id = id
        
        from webhelpers import paginate
#        if(grupo.group_name =='Desarrollador' or grupo.group_name =='Aprobador'):
#            count = fases.__len__()
#        else:    
        count = fases.__len__()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            fases, page, item_count=count,
            items_per_page=5,
        )
        fases = currentPage.items
        return dict(page='Lista de fases',
                    fases = fases,
                    proyecto_id = proyecto_id,  
                    subtitulo = 'fases',
#                    mostrarNuevo = mostrarNuevo,
#                    mostrarEditar = mostrarEditar,
#                    mostrarEliminar = mostrarEliminar,
#                    mostrarAsigUsu = mostrarAsigUsu,
                    currentPage = currentPage)
        
    
    
    @expose(template="gestionitem.templates.proyectoTmpl.agregar_fase")
    @require(All(in_group('LiderProyecto'), has_permission('crear fase'),
                 msg='Debe poseer Rol "LiderProyecto" para agregar fases'))
    def agregar_fase(self, id):
        identity = request.environ.get('repoze.who.identity')
        user = identity['user']
        proyecto =  DBSession.query(Proyecto).filter(Proyecto.id == id).one()
        fase =  DBSession.query(Fase).filter(Fase.proyecto_id== proyecto.id).all()
        codigos=[]
        for i, cod in enumerate(fase):
            codigos.append(cod.codigo_fase)
            codigos.append(",")
        return dict(page='Nueva Fase',
                    proyecto = proyecto,user=user ,codigos=codigos)
        
    
    @expose()
    @require(All(in_group('LiderProyecto'), has_permission('crear fase'),
                 msg='Debe poseer Rol "LiderProyecto" para agregar fases'))
    def save_fase(self, id, descripcion_proyecto, nombre_fase,codFase, submit):
        fases = DBSession.query(Fase).filter(Fase.proyecto_id == id)
        num = fases.count() + 1
        
        new = Fase(descripcion = nombre_fase,
                   proyecto_id = id,
                   numero_fase = num,
                   estado_id   = 1,
                   codigo_fase = codFase
                   )
        DBSession.add( new )
        flash( '''Fase Registrada: %s'''%( nombre_fase, ))
        redirect( '/proyecto/definir_fase/'+id )
        
    
    @expose("gestionitem.templates.proyectoTmpl.editar_fase")
    @require(All(in_group('LiderProyecto'), has_permission('editar fase'),
                 msg='Debe poseer Rol "LiderProyecto" para editar fases'))
    def editar_fase(self,id):
        fase = DBSession.query(Fase).filter(Fase.id == id).one()
        return dict(page='Editar fase',
                    id=id,
                    fase=fase,
                    subtitulo='ABM-Fase')
        
           
    @expose() 
    @require(All(in_group('LiderProyecto'), has_permission('editar fase'),
                 msg='Debe poseer Rol "LiderProyecto" para editar fases'))   
    def actualizar_fase(self, id, descripcion_proyecto, nombre_fase, numero_fase, submit):
        fase = DBSession.query(Fase).filter(Fase.id == id).one()
        fase.descripcion = nombre_fase
        fase.numero_fase = numero_fase
        DBSession.flush()
        redirect('/proyecto/definir_fase/'+ str(fase.proyecto_id))
        
    
    @expose()
    @require(All(in_group('LiderProyecto'), has_permission('eliminar fase'),
                 msg='Debe poseer Rol "LiderProyecto" para eliminar fases'))
    def eliminar_fase(self,id):
        fase = DBSession.query(Fase).filter(Fase.id == id).one()
        id_proyecto = fase.proyecto_id
        DBSession.delete(fase)
        redirect( '/proyecto/definir_fase/'+ str(id_proyecto) )    
        
    
    @expose("gestionitem.templates.proyectoTmpl.usuario_faseList")
    @require(in_group('LiderProyecto', msg='Debe poseer Rol "LiderProyecto" para listar usuarios') )
    def usuario_faseList(self, id, **named):
        usuarioFaseRols =DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.fase_id == id).all()
        for ufr in usuarioFaseRols:
            if ufr.usuario==None:
                DBSession.delete(ufr)
                DBSession.flush()
        usuarioFaseRol = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.fase_id == id).all()
        fase = DBSession.query(Fase).filter(Fase.id == id).one() 
        from webhelpers import paginate
        count = usuarioFaseRol.__len__()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            usuarioFaseRol, page, item_count=count,
            items_per_page = 5,
        )
        usuarioFaseRol = currentPage.items
        descripcion = fase.descripcion
        
        return dict(page='Usuarios de fase '+ descripcion,
                    usuariofaserol = usuarioFaseRol,
                    descripcion = descripcion,
                    fase_id =id,
                    subtitulo = 'Usuarios de fase',
                    proyecto_id = fase.proyecto_id,
                    currentPage = currentPage
                    ) 
    
    @expose("gestionitem.templates.proyectoTmpl.agregarUsuarioFase")
    @require(All(in_group('LiderProyecto'), has_permission('asignar desarrollador'),
                 msg='LiderProyecto" para agregar usuarios'))
    def agregar_usuario_fase(self, id):
        usuarios = DBSession.query(User).join((Rol, User.groups)).filter(or_(Rol.group_name =='Aprobador',Rol.group_name =='Desarrollador')).all()
        roles   = DBSession.query(Rol).filter(or_(Rol.group_name =='Aprobador',Rol.group_name =='Desarrollador')).all()
        fase = DBSession.query(Fase).filter(Fase.id == id).one()
        
        return dict(page='Asignar Usuario a fase '+ fase.descripcion,
                    usuarios = usuarios,
                    roles = roles,
                    proyecto_id = id,
                    fase = fase) 
        
    @expose()
    @require(All(in_group('LiderProyecto'), has_permission('asignar desarrollador'),
                 msg='Debe poseer Rol "LiderProyecto" para agregar usuarios'))
    def save_usuario_fase(self, fase, user, rol, submit):
        new = UsuarioFaseRol(user_id = user,
                                 fase_id = fase,
                                 rol_id  = rol
                                 ) 
        DBSession.add(new)
        redirect('/proyecto/usuario_faseList/'+ fase)
        
        
    @expose()
    @require(All(in_group('LiderProyecto'), has_permission('eliminar desarrollador'),
                 msg='Debe poseer Rol "LiderProyecto" para eliminar usuarios'))    
    def eliminar_usuario_fase(self, ufr):
        usuarioFaseRol = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.id==ufr).one()
        fase = usuarioFaseRol.fase_id     
        DBSession.delete(usuarioFaseRol)                                   
        redirect('/proyecto/usuario_faseList/'+ str(fase))
        
    @expose("gestionitem.templates.proyectoTmpl.editarUsuarioFase")
    @require(All(in_group('LiderProyecto'), has_permission('editar desarrollador'),
                 msg='Debe poseer Rol "LiderProyecto" para editar usuarios'))
    def editar_usuario_fase(self, ufr):
        usuarioFaseRol = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.id==ufr).one()
        fase = DBSession.query(Fase).filter(Fase.id==usuarioFaseRol.fase_id).one()
        usuario = DBSession.query(User).filter(User.user_id==usuarioFaseRol.user_id).one()
        rol = DBSession.query(Rol).filter(Rol.group_id==usuarioFaseRol.rol_id).one()
        roles = DBSession.query(Rol).filter(or_(Rol.group_name =='Aprobador',Rol.group_name =='Desarrollador')).all()
        return dict(page='Editar Usuario de fase'+ fase.descripcion,
                    fase = fase,
                    usuario= usuario,
                    roles = roles,
                    rol = rol,
                    ufr = usuarioFaseRol)
        
    @expose()
    @require(All(in_group('LiderProyecto'), has_permission('editar desarrollador'),
                 msg='Debe poseer Rol "LiderProyecto" para editar usuarios'))
    def actualizar_usuario_fase(self, fase, ufr, rol, submit):
        usuarioFaseRol = DBSession.query(UsuarioFaseRol).filter(UsuarioFaseRol.id==ufr).one()
        usuarioFaseRol.rol_id = rol
        DBSession.flush()
        redirect('/proyecto/usuario_faseList/'+ fase)
        
        
        
    
         
     
                                            
                                                
    
    
    
    
        



