"""
Catwalk Module

Classes:
Name                               Description
DBMechanic


Copywrite (c) 2008 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
import sqlalchemy
from tg.decorators import expose
from tg.controllers import redirect, DecoratedController
from tw.api import Widget, CSSLink, Link
import pylons
from tg import TGController, redirect

from dbsprockets.modelsprockets import ModelSprockets

from catwalk.decorators import validate
from catwalk.resources import CatwalkCss

class BaseController(TGController):
    """Basis TurboGears controller class which is derived from
    TGController
    """

    def __init__(self, provider, *args, **kwargs):
        self.provider = provider
        self.sprockets = ModelSprockets(provider)
        #initialize model view cache

        #commonly used views
        sprocket = self.sprockets['model_view']
        self.models_value = sprocket.session.get_value()
        self.models_view  = sprocket.view.__widget__
        self.models_dict  = dict(models_value=self.models_value)

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        try:
            return TGController.__call__(self, environ, start_response)
        finally:
            pass

class CatwalkModel(BaseController):

    def _get_value(self, config_name, model_name):
        """This thing has some side effects!"""
        pylons.c.models_view = self.models_view
        CatwalkCss.inject()
        sprocket = self.sprockets[config_name+'__'+model_name]
        value = sprocket.session.get_value()
        pylons.c.widget  = sprocket.view.__widget__
        return value

    @expose('genshi:catwalk.templates.base')
    def default(self, model_name, action=None, *args, **kw):
        print model_name, action
        if action is None:
            if not pylons.request.path_info.endswith('/'):
                redirect(pylons.request.path_info+'/')
            value = self._get_value('listing', model_name)
            return dict(value=value, model_name=model_name, action=None)
        if action in ['add', 'metadata', 'create']:
            return getattr(self, action)(model_name=model_name, *args, **kw)


    @expose('genshi:catwalk.templates.base')
    def metadata(self, model_name, **kw):
        value = self._get_value('metadata', model_name)
        return dict(value=value, model_name=model_name, action=None)

    @expose('genshi:catwalk.templates.base')
    def add(self, model_name, **kw):
        value = self._get_value('add', model_name, **kw)
        return dict(value=value, model_name=model_name, action='./create')

    @expose('genshi:catwalk.templates.base')
    def edit(self, model_name, **kw):
        value = self._get_value('edit', model_name)
        return dict(value=value, model_name=model_name)

    @expose()
    def create(self, model_name, **kw):
        print 'here'
        redirect('../%s'%model_name)

    def update(self, model_name, **kw):
        pass

    def delete(self, model_name, **kw):
        pass


class Catwalk(BaseController):

    def __init__(self, provider, *args, **kwargs):
        self.model = CatwalkModel(provider)
        super(Catwalk, self).__init__(provider, *args, **kwargs)

    @expose('genshi:catwalk.templates.index')
    def index(self):
        if not pylons.request.path_info.endswith('/'):
            redirect(pylons.request.path_info+'/')
        pylons.c.models_view = self.models_view
        CatwalkCss.inject()

        pylons.c.main_view=Widget("widget")
        return self.models_dict


