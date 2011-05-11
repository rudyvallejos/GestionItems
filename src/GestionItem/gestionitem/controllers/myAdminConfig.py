'''
Created on 09/05/2011

@author: Rudy Vallejos
'''
from tgext.admin.config import AdminConfig, CrudRestControllerConfig
from sprox.formbase import AddRecordForm
from formencode import Schema
from formencode.validators import FieldsMatch
from tw.forms import PasswordField, TextField 
from gestionitem.model.auth import User
from repoze.what import authorize
from sprox.tablebase import TableBase
from sprox.fillerbase import TableFiller


form_validator =  Schema(chained_validators=(FieldsMatch('password',
                                                         'verify_password',
                                                         messages={'invalidNoMatch':
                                                         'Passwords do not match'}),))
class RegistrationForm(AddRecordForm):
    __model__ = User
    __omit_fields__        = ['_password', 'groups', 'created', 'user_id', 'town_id']
    __require_fields__     = ['user_name', 'email_address','password']
    __field_order__        = ['user_name', 'email_address', 'display_name', 'password', 'verify_password']
    __base_validator__     = form_validator
    email_address          = TextField
    display_name           = TextField
    verify_password        = PasswordField('verify_password')

class table_type(TableBase):
    __entity__ = User
    __limit_fields__ = ['user_name', 'email_address','groups', 'created']
    __url__ = '../user.json' #this just tidies up the URL a bit

class table_filler_type(TableFiller):
    __entity__ = User
    __limit_fields__ = ['user_id', 'user_name', 'email_address','groups' , 'created']






class UserCrudConfig(CrudRestControllerConfig):
    new_form_type = RegistrationForm
    table_type = table_type
    table_filler_type = table_filler_type

class MyAdminConfig(AdminConfig):
    allow_only = authorize.in_group('Administrador')
    user = UserCrudConfig



