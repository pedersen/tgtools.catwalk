"""
Catwalk Module

Classes:
Name                               Description
Catwalk

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
from sprox.sprockets import SprocketCache
from sprox.providerselector import SAORMSelector

from decorators import validate, crudErrorCatcher, validate
from catwalk.resources import CatwalkCss

from webhelpers.html.builder import literal

class BaseController(TGController):
    """Basis TurboGears controller class which is derived from
    TGController
    """
    sprocketCacheType = SprocketCache

    sprockets = None
    def __init__(self, session, metadata=None, *args, **kwargs):
        self.session = session
        #initialize the sa provider so we can get information about the classes
        self.provider = SAORMSelector.get_provider(None, session.bind, session=session)
        #initialize model view cache
        self.sprockets = self.sprocketCacheType(session, metadata)

    def _get_value(self, config_name, model_name, **kw):
        pylons.c.models_view = self.models_view
        CatwalkCss.inject()
        key = config_name+'__'+model_name
        sprocket = self.sprockets[key]
        value = sprocket.filler.get_value(kw)
        pylons.c.widget  = sprocket.view.__widget__
        return value

    def _get_model_view(self):
        """get the highest level view"""
        sprocket = self.sprockets['model_view']
        self.models_value = sprocket.filler.get_value()
        self.models_view  = sprocket.view.__widget__
        self.models_dict  = dict(models_value=self.models_value)

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        try:
            return TGController.__call__(self, environ, start_response)
        finally:
            pass

class CatwalkModel(BaseController):

    def _listing(self, model_name):
        value = self._get_value('listing', model_name)
        return dict(value=value, model_name=model_name, action=None, root_catwalk='../../', root_model='./')

    @expose('genshi:catwalk.templates.base')
    def default(self, model_name, action=None, *args, **kw):
        self._get_model_view()

        if action is None:
            if not pylons.request.path_info.endswith('/'):
                redirect(pylons.request.path_info+'/')
            return self._listing(model_name)

        if action in ['add', 'metadata']:
            self.start_response = pylons.request.start_response
            return self._perform_call(None, dict(url=action+'/'+model_name, params=kw))

        elif action == 'create':
            self.start_response = pylons.request.start_response
            r = self._perform_call(None, dict(url='create/'+model_name, params=kw))
            if isinstance(r, literal):
                return r
            redirect(str('../'+model_name))
        return self.edit(model_name, action, *args, **kw)

    @expose('genshi:catwalk.templates.base')
    def metadata(self, model_name, **kw):
        value = self._get_value('metadata', model_name)
        return dict(value=value, model_name=model_name, action=None, root_catwalk='../../', root_model='./')

    @expose('genshi:catwalk.templates.base')
    def add(self, model_name, **kw):
        value = self._get_value('add', model_name, values=kw)
        #flash('something')
        return dict(value=value, model_name=model_name, action='create', root_catwalk='../../', root_model='./')

    @expose('genshi:catwalk.templates.base')
    def edit(self, model_name, *args, **kw):
        if args[-1] == 'update':
            return self.update(model_name, *args[:-1], **kw)
        if args[-1] == 'delete':
            return self.delete(model_name, *args[:-1], **kw)
        #assign all of the pks to the session for extraction
        model = self.provider.get_entity(model_name)
        pks = self.provider.get_primary_fields(model)
        for i, pk in  enumerate(pks):
            if pk not in kw and i < len(args):
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
        model = self.provider.get_entity(model_name)
        pks = self.provider.get_primary_fields(model)
        params = pylons.request.params.copy()
        for i, pk in  enumerate(pks):
            if pk not in kw and i < len(args):
                params[pk] = args[i]

        self.provider.update(model, params=params)
        redirect('./')

    @expose()
    @validate(error_handler=add)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.IntegrityError, error_handler=add)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.ProgrammingError, error_handler=add)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.DataError, error_handler=add)
    def create(self, model_name, **kw):
        model = self.provider.get_entity(model_name)
        params = pylons.request.params.copy()

        self.provider.create(model, params=kw)
        raise redirect('../')

    @expose()
    def delete(self, model_name, *args, **kw):
        model = self.provider.get_entity(model_name)
        pks = self.provider.get_primary_fields(model)
        kw = {}
        for i, pk in  enumerate(pks):
            kw[pk] = args[i]

        self.provider.delete(model, params=kw)
        redirect('../')

class Catwalk(BaseController):
    catwalkModelType = CatwalkModel
    def __init__(self, session, *args, **kwargs):
        self.model = self.catwalkModelType(session)
        super(Catwalk, self).__init__(session, *args, **kwargs)

    @expose('genshi:catwalk.templates.index')
    def index(self):
        self._get_model_view()
        if not pylons.request.path_info.endswith('/'):
            redirect(pylons.request.path_info+'/')
        pylons.c.models_view = self.models_view
        CatwalkCss.inject()

        pylons.c.main_view=Widget("widget")
        d =self.models_dict
        d['secured'] = (hasattr(self, 'allow_only') and self.allow_only != None)
        return d

