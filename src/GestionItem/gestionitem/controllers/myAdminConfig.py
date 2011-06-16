'''
Created on 09/05/2011

@author: Rudy Vallejos
'''
from tgext.admin.config import AdminConfig, CrudRestControllerConfig
from sprox.formbase import AddRecordForm, EditableForm
from formencode import Schema
from formencode.validators import FieldsMatch
from tw.forms import PasswordField, TextField, TextArea
from gestionitem.model.auth import User, Rol, Permission

#from repoze.what.predicates import in_group
from sprox.tablebase import TableBase
from sprox.fillerbase import TableFiller, EditFormFiller
from sprox.fillerbase import RecordFiller
from repoze.what import authorize
from tw.forms.fields import MultipleSelectField
from tgext.admin.tgadminconfig import TGAdminConfig






form_validator =  Schema(chained_validators=(FieldsMatch('password',
                                                         'verify_password',
                                                         messages={'invalidNoMatch':
                                                         'Passwords do not match'}),))
class UserForm(AddRecordForm):
    __model__ = User
    __omit_fields__        = ['_password', 'created', 'user_id', 'town_id']
    __require_fields__     = ['user_name', 'email_address','password']
    __field_order__        = ['user_name', 'email_address', 'display_name', 'password', 'verify_password','groups']
    __limit_fields__       = ['user_name']
    __base_validator__     = form_validator
    email_address          = TextField
    display_name           = TextField('descripcion')
    verify_password        = PasswordField('verify_password')
    
     
    
class User_table_type(TableBase):
    __entity__ = User
    __limit_fields__ = ['user_name', 'email_address','groups', 'created']
    __headers__ ={'user_name':'usuario','groups':'Rol', 'created':'Fecha de creacion','email_address':'email'}
    __url__ = '../user.json' #this just tidies up the URL a bit

class User_table_filler_type(TableFiller):
    __entity__ = User
    __limit_fields__ = ['user_id', 'user_name', 'email_address' ,'groups', 'created']

class User_EditForm(EditableForm):
    __entity__ = User
    __omit_fields__        = ['_password',  'created', 'user_id', 'town_id']
    __require_fields__     = ['user_name', 'email_address','password']
    __field_order__        = ['user_name', 'email_address', 'display_name', 'password', 'verify_password','groups']
    __limit_fields__       = ['user_name']
    __base_validator__     = form_validator
    email_address          = TextField
    verify_password        = PasswordField('verify_password')
    
    
    
class User_EditFormFiller(EditFormFiller):
    __entity__ = User
    
    def get_value(self, *args, **kw):
        v = super(User_EditFormFiller, self).get_value(*args, **kw)
        del v['password']
        return v

class UserCrudConfig(CrudRestControllerConfig):
    new_form_type = UserForm
    table_type = User_table_type
    table_filler_type = User_table_filler_type
    edit_form_type = User_EditForm
    edit_filler_type = User_EditFormFiller



class GroupTable(TableBase):
    __entity__ = Rol 
    __limit_fields__ = ['group_name', 'permissions', 'created']
    __headers__ ={'group_name':'nombre','permissions':'permisos', 'created':'Fecha de creacion'} 
    
    
    __url__ = '../groups.json'
    
class GroupTableFiller(TableFiller):
    __entity__ = Rol
    __limit_fields__ = ['group_id', 'group_name' , 'permissions','created']
    
    
    
class GroupNewForm(AddRecordForm):
    __entity__ = Rol
    __limit_fields__ = ['group_name', 'permissions']
    __omit_fields__        = ['created', 'town_id']
#    group_name = TextField("Nombre")

    
class GroupEditForm(EditableForm):
    __entity__ = Rol
    __omit_fields__        = ['group_id',  'created']
    __limit_fields__ = ['group_id', 'group_name', 'permissions','users']
    __field_order__ = ['group_name', 'permissions']
#    group_name = TextField("Nombre")

    
class Group_EditFormFiller(EditFormFiller):
    __entity__ = Rol
    def get_value(self, *args, **kw):
        v = super(Group_EditFormFiller, self).get_value(*args, **kw)
        return v


class GroupControllerConfig(CrudRestControllerConfig):
    table_type = GroupTable
    table_filler_type = GroupTableFiller
    new_form_type = GroupNewForm
    edit_form_type = GroupEditForm
    edit_filler_type = Group_EditFormFiller
    


class PermissionTable(TableBase):
    __entity__ = Permission 
    __limit_fields__ = ['permission_name', 'description']
    __url__ = '../permissions.json'    
    
class PermissionTableFiller(TableFiller):
    __entity__ = Permission
    __limit_fields__ = ['permission_id','permission_name', 'description']
    
class PermissionNewForm(AddRecordForm):
    __entity__ = Permission
    __limit_fields__ = ['permission_name', 'description']
    description = TextField
    
    
    
class PermissionEditForm(EditableForm):
    __entity__ = Permission
    __limit_fields__ = ['permission_name', 'description']
    description = TextArea
    description.rows = 3
    description.cols = 27
    
class PermissionEditFiller(RecordFiller):
    __entity__ = Permission
    
class PermissionControllerConfig(CrudRestControllerConfig):
    table_type = PermissionTable
    table_filler_type = PermissionTableFiller
    new_form_type = PermissionNewForm
    edit_form_type = PermissionEditForm
    edit_filler_type = PermissionEditFiller
    



class MyAdminConfig(AdminConfig):#AdminConfig
    allow_only = authorize.in_group('Administrador')
    default_index_template = "genshi:gestionitem.templates.adminTmpl.index"
    
    user = UserCrudConfig
    rol = GroupControllerConfig
    permission = PermissionControllerConfig




