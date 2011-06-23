from sqlalchemy import ForeignKey, Column, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Unicode, Integer, DateTime, String, CHAR,LargeBinary
from datetime import datetime
from sqlalchemy.orm import relation

from gestionitem.model import DeclarativeBase, metadata


__all__ = ['Proyecto', 'Fase']


#usuario_fase_tabla = Table('usarios_fase', metadata,
#    Column('user_id', Integer, ForeignKey('tg_user.user_id',
#        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
#    Column('fase_id', Integer, ForeignKey('fase.id',
#        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
#)


class EstadoProyecto(DeclarativeBase):
    __tablename__ = 'estado_proyecto'

    #column definitions
    descripcion = Column(Unicode(100), unique=True, nullable=False)
    id = Column(Integer, autoincrement=True, primary_key=True)
    
class EstadoFase(DeclarativeBase):
    __tablename__ = 'estado_fase'
    
    descripcion = Column(Unicode(100), unique=True, nullable=False)
    id = Column(Integer, autoincrement=True, primary_key=True)



class Proyecto(DeclarativeBase):
    __tablename__ = 'proyecto'
    
    
    id = Column(Integer, autoincrement=True, primary_key=True)

    descripcion = Column(Unicode(100), unique=True, nullable = False)

    estado = Column(Integer, ForeignKey('estado_proyecto.id'), nullable = False)
    estadoObj = relation('EstadoProyecto',foreign_keys = estado )
    fecha_creacion = Column(DateTime, default = datetime.now)
    id_lider = Column(Integer, ForeignKey('tg_user.user_id'), nullable = False)
    lider = relation('User',foreign_keys = id_lider )
    
    __mostrarDefinir = False
    __mostrarFases = False
    
    def setDefinir(self):
        self.__mostrarDefinir = True
        
    def getDefinir(self):
        return self.__mostrarDefinir
    
    def setmostrarFases(self):
        self.__mostrarFases = True
        
    def getmostrarFases(self):
        return self.__mostrarFases
    
    def isDefinible(self):
        if self.fases.__len__() > 0:
            for fase in self.fases:
                if fase.estado_id != 1:
                    return False
            return True
        return False
                
                
        return False
        
    def isRedefinible(self):
        for fase in self.fases:
            if fase.estado_id==2 or fase.estado_id==4 or fase.estado_id==3:
                return False
        return True
    

class EstadoRelacion(DeclarativeBase):
    __tablename__ = 'estado_relacion'
    id = Column("id",Integer, autoincrement=True, primary_key=True)
    descripcion = Column("descripcion", String(100), unique=False, nullable=False)
    
class TipoRelacion(DeclarativeBase):
    __tablename__ = 'tipo_relacion'
    
    id = Column("id",Integer, autoincrement=True, primary_key=True)
    descripcion = Column("descripcion", String(100), unique=False, nullable=False)
  
class Fase(DeclarativeBase):
    __tablename__ = 'fase'
    id = Column(Integer, autoincrement=True, primary_key=True)
    descripcion = Column(Unicode(100), unique=True, nullable=False)
    numero_fase = Column(Integer, nullable=False)
    estado_id = Column(Integer, ForeignKey('estado_fase.id'), nullable=False)
    estadoObj = relation('EstadoFase', foreign_keys=estado_id)
    proyecto_id = Column(Integer, ForeignKey('proyecto.id'), nullable=False)
    proyectoObj = relation('Proyecto', foreign_keys=proyecto_id, backref='fases')
    codigo_fase = Column("codigo_fase", String(10), unique=False, nullable=False)
    
class EstadoItem(DeclarativeBase):
    __tablename__ = 'estado_item'
    id = Column("id",Integer, autoincrement=True, primary_key=True)

    descripcion = Column("descripcion", String(100), unique=True, nullable=False)

class EstadoLineaBase(DeclarativeBase):
    __tablename__ = 'estado_linea_base'
    id = Column("id",Integer, autoincrement=True, primary_key=True)
    descripcion = Column("descripcion", String(100), unique=True, nullable=False)
   


class RelacionItem(DeclarativeBase):
    __tablename__ = 'relacion_item'
    
    id = Column("id",Integer, autoincrement=True, primary_key=True)
    antecesor_item_id = Column("antecesor_item_id", Integer, ForeignKey('item_usuario.id'), nullable=False)
    sucesor_item_id = Column("sucesor_item_id", Integer, ForeignKey('item_usuario.id'), nullable=False)
    tipo = Column("tipo_id", Integer, ForeignKey('tipo_relacion.id'), nullable=False)
    estado_id = Column("estado_id", Integer, ForeignKey('estado_relacion.id'), nullable=False)

    #tipoItemUsuarioAtributos = relationship(TipoItemUsuarioAtributos, backref=backref('tipo', order_by=id))
class UsuarioFaseRol(DeclarativeBase):
    __tablename__ = 'usuario_fase_rol'

    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey('tg_user.user_id'), nullable = False)
    usuario = relation('User', foreign_keys = user_id)
    fase_id = Column(Integer, ForeignKey('fase.id', onupdate="CASCADE", ondelete="CASCADE"), nullable = False)
    fase = relation('Fase', foreign_keys = fase_id)
    rol_id = Column(Integer, ForeignKey('tg_group.group_id'), nullable = False)
    rol = relation('Rol', foreign_keys = rol_id)

class LineaBase(DeclarativeBase):
    __tablename__ = 'linea_base'
    
    id = Column("id",Integer, primary_key=True)
    version = Column("version",Integer)
    estado_id = Column("estado_id",Integer, ForeignKey('estado_linea_base.id'),nullable=False)
    estado = relationship(EstadoLineaBase, order_by=EstadoLineaBase.id, backref="estado_linea_base")
    fase_id = Column("fase_id", Integer, ForeignKey('fase.id'), nullable=False)
    fase = relationship(Fase, order_by=Fase.id, backref="faseid")
    descripcion = Column("descripcion", String(200), unique=False, nullable=False)
    comentario = Column("comentario", String(100), unique=False, nullable=False)
    apertura = Column("apertura", CHAR, unique=False, nullable=False)
    usuario_sol = Column("usuario_sol", String(100), unique=False, nullable=False)


class TipoItemUsuarioAtributosValor(DeclarativeBase):
    __tablename__ = 'tipo_item_usuario_valor'
    id = Column("id",Integer, autoincrement=True, primary_key=True)
    valor = Column("valor", String(100), unique=True, nullable=False)
    item_usuario_id = Column("item_usuario_id", Integer, ForeignKey('item_usuario.id'), nullable=False)
    atributo_id = Column("atributo_id", Integer, ForeignKey('tipo_item_usuario_atributos.id'), nullable=False)
    
class Tipo(DeclarativeBase):
    __tablename__ = 'tipo'
    
    
    id = Column("id",Integer, autoincrement=True, primary_key=True)

    descripcion = Column("descripcion", String(100), unique=True, nullable=False)
    #tipoItemUsuarioAtributos = relationship(TipoItemUsuarioAtributos, backref=backref('tipo', order_by=id))


class TipoItemUsuarioAtributos(DeclarativeBase):
    __tablename__ = 'tipo_item_usuario_atributos'
    id = Column("id",Integer, autoincrement=True, primary_key=True)

    nombre_atributo = Column("nombre_atributo", String(100), unique=True, nullable=False)

    tipo_item_id = Column("tipo_item_id", Integer, ForeignKey('tipo_item_usuario.id'), nullable=False)
    tipo_id = Column("tipo_id", Integer, ForeignKey('tipo.id'), nullable=False)
    tipo = relationship(Tipo, order_by=Tipo.id, backref="tipo_item_usuario_atributos")
    valor = relationship(TipoItemUsuarioAtributosValor, order_by=TipoItemUsuarioAtributosValor.atributo_id, backref="tipo_item_usuario_valor")


class TipoItemUsuario(DeclarativeBase):
    __tablename__ = 'tipo_item_usuario'
    
    
    id = Column("id",Integer, autoincrement=True, primary_key=True)

    descripcion = Column("descripcion", String(100), unique=True, nullable=False)

    fase_id = Column("fase_id", Integer, ForeignKey('fase.id'), nullable=False)
    
    codigo = Column("codigo", String(5), unique=True, nullable=False)

    
    atributos = relationship(TipoItemUsuarioAtributos, order_by=TipoItemUsuarioAtributos.id, backref="tipo_item_usuario_atributos")
    






class ItemUsuario(DeclarativeBase):
    __tablename__ = 'item_usuario'
    
    id = Column("id",Integer, autoincrement=True, primary_key=True)
    tipo_item_id = Column("tipo_item_id", Integer, ForeignKey('tipo_item_usuario.id'), nullable=False)
    tipo_item_generico = Column("tipo_item_generico", Integer, nullable=True)
    fase_id = Column("fase_id", Integer, ForeignKey('fase.id'), nullable=False)
    linea_base_id = Column("linea_base_id", Integer, ForeignKey('linea_base.id'), nullable=False)
    cod_item = Column("cod_item", String(20), unique=False, nullable=False)
    numero_cod = Column("numero_cod", Integer, nullable=True)
    prioridad = Column("prioridad",Integer)
    descripcion = Column("descripcion", String(200), unique=False, nullable=False)
    observacion = Column("observaciones", String(100), unique=False, nullable=False)
    version = Column("version_item",Integer, nullable=True)
    estado_id = Column("estado_id", Integer, ForeignKey('estado_item.id'), nullable=False)
    fase = relationship(Fase, order_by=Fase.id, backref="fase")
    estado = relationship(EstadoItem, order_by=EstadoItem.id, backref="estado_item")
    linea_base = relationship(LineaBase, order_by=LineaBase.id, backref="linea_base")   
    tipo = relationship(TipoItemUsuario, order_by=TipoItemUsuario.id, backref="tipo_item_usuario")
    linea_base_ant = Column("linea_base_ant", Integer, nullable=False)


class ArchivosAdjuntos(DeclarativeBase):
    __tablename__ = 'archivos_ajuntos'
 
    id      =   Column(Integer, autoincrement=True, primary_key=True)
    
    nombre    =   Column(String(100), nullable=False) 
    
    archivo = Column(LargeBinary)

    item_usuario_id =   Column(Integer, ForeignKey('item_usuario.id'))
   
