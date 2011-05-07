import pylons
from datetime import datetime
from tg.controllers import RestController, redirect
from pylons import request
from tg.decorators import expose, validate, with_trailing_slash
from gestionitem.model import DBSession, metadata, Recurso, TipoItemUsuario
from formencode.validators import DateConverter, Int, NotEmpty

class TipoRestController(RestController):
    
    @expose('gestionitem.templates.rest.tipoItemUsuario')
    def tipoItemUsuario(self, **named):
        tiposItemUs=DBSession.query(TipoItemUsuario).order_by( TipoItemUsuario.id )
        from webhelpers import paginate
        count = tiposItemUs.count()
        page =int( named.get( 'page', '1' ))
        currentPage = paginate.Page(
            tiposItemUs, page, item_count=count,
            items_per_page=3,
        )
        tiposItemUs = currentPage.items

        return dict(page='tipoItemUsuario',
                    tiposItemUs=tiposItemUs, 
                    subtitulo='ABM-TipoItemUsuario',currentPage = currentPage)

    
   # @expose('json')
    #def get_one(self, movie_id):
     #   movies = DBSession.query(Movie).get(movie_id)
      #  return dict(movie=movie)
