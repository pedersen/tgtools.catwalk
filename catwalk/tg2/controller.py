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
from tg.flash import flash, get_flash
from dbsprockets.modelsprockets import ModelSprockets

from catwalk.decorators import validate, crudErrorCatcher, validate
from catwalk.resources import CatwalkCss

from dbsprockets.primitives import SAORMDBHelper as helper

from webhelpers.html.builder import literal

class BaseController(TGController):
    """Basis TurboGears controller class which is derived from
    TGController
    """
    sprockets = None
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

    sprockets = None
    def _get_value(self, config_name, model_name, **kw):
        """This thing has some side effects!"""
        pylons.c.models_view = self.models_view
        CatwalkCss.inject()
        sprocket = self.sprockets[config_name+'__'+model_name]
        value = sprocket.session.get_value(**kw)
        pylons.c.widget  = sprocket.view.__widget__
        return value

    @expose('genshi:catwalk.templates.base')
    def default(self, model_name, action=None, *args, **kw):
        if action is None:
            if not pylons.request.path_info.endswith('/'):
                redirect(pylons.request.path_info+'/')
            value = self._get_value('listing', model_name)
            return dict(value=value, model_name=model_name, action=None, root_catwalk='../../', root_model='./')
        
        if action in ['add', 'metadata']:
            self.start_response = pylons.request.start_response
            return self._perform_call(None, dict(url=action+'/'+model_name, params=kw))

        elif action == 'create':
            self.start_response = pylons.request.start_response
            r = self._perform_call(None, dict(url='create/'+model_name, params=kw))
            if isinstance(r, literal):
                return r
            redirect('../'+model_name)
        return self.edit(model_name, action, *args, **kw)

    @expose('genshi:catwalk.templates.base')
    def metadata(self, model_name, **kw):
        value = self._get_value('metadata', model_name)
        return dict(value=value, model_name=model_name, action=None, root_catwalk='../../', root_model='./')

    @expose('genshi:catwalk.templates.base')
    def add(self, model_name, **kw):
        value = self._get_value('add', model_name, values=kw)
        flash('something')
        return dict(value=value, model_name=model_name, action='create', root_catwalk='../../', root_model='./')

    @expose('genshi:catwalk.templates.base')
    def edit(self, model_name, *args, **kw):
        if args[-1] == 'update':
            return self.update(model_name, *args[:-1], **kw)
        if args[-1] == 'delete':
            return self.delete(model_name, *args[:-1], **kw)
        #assign all of the pks to the session for extraction
        model = helper.get_model(model_name, self.provider.metadata)
        table_name = helper.get_identifier(model)
        pks = self.provider.get_primary_keys(table_name)
        for i, pk in  enumerate(pks):
            kw[pk] = args[i]
        value = self._get_value('edit', model_name, **kw)
        root_model = '../'*len(pks)
        root_catwalk = root_model+'../../'
        return dict(value=value, model_name=model_name, action='update', root_catwalk=root_catwalk, root_model=root_model)

    @expose()
    @validate(error_handler=edit)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.IntegrityError, error_handler=edit)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.ProgrammingError, error_handler=edit)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.DataError, error_handler=edit)
    def update(self, model_name, *args, **kw):
        model = helper.get_model(model_name, self.provider.metadata)
        table_name = helper.get_identifier(model)
        params = pylons.request.params.copy()
        pks = self.provider.get_primary_keys(table_name)
        for i, pk in  enumerate(pks):
            params[pk] = args[i]
        self.provider.create_relationships(table_name, params)

        self.provider.edit(table_name, values=kw)
        redirect('../')

    @expose()
    @validate(error_handler=add)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.IntegrityError, error_handler=add)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.ProgrammingError, error_handler=add)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.DataError, error_handler=add)
    def create(self, model_name, **kw):
        model = helper.get_model(model_name, self.provider.metadata)
        table_name = helper.get_identifier(model)

        params = pylons.request.params.copy()
        self.provider.create_relationships(table_name, params)

        self.provider.add(table_name, values=kw)
        raise redirect('../')

    @expose()
    def delete(self, model_name, *args, **kw):
        model = helper.get_model(model_name, self.provider.metadata)
        table_name = helper.get_identifier(model)
        pks = self.provider.get_primary_keys(table_name)
        kw = {}
        for i, pk in  enumerate(pks):
            kw[pk] = args[i]

        self.provider.delete(table_name, values=kw)
        redirect('../')


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


