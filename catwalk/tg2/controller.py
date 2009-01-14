"""
Catwalk Module

Classes:
Name                               Description
Catwalk

Copywrite (c) 2008 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
import pylons
import sqlalchemy

from tg.decorators import expose, validate, with_trailing_slash, without_trailing_slash
from tg.controllers import redirect, TGController, RestController
from tg.flash import flash

from decorators import crudErrorCatcher
from catwalk.resources import CatwalkCss as catwalk_css

from sprox.entitiesbase import EntitiesBase
from sprox.providerselector import SAORMSelector

engine = 'genshi'
try:
    import chameleon.genshi
    import pylons.config
    if 'chameleon_genshi' in pylons.config['renderers']:
        engine = 'chameleon_genshi'
    else:
        import warnings
        warnings.warn('The renderer for \'chameleon_genshi\' templates is missing.'\
                      'Your code could run much faster if you'\
                      'add the following line in you app_cfg.py: "base_config.renderers.append(\'chameleon_genshi\')"')
except ImportError:
    pass

from sprox.fillerbase import AddFormFiller, EditFormFiller, TableFiller, AddFormFiller
from sprox.formbase import AddRecordForm, EditableForm
from sprox.tablebase import TableBase

class CatwalkModelController(RestController):
    
    table_base_type       = TableBase
    table_filler_type     = TableFiller
    edit_form_type        = EditableForm
    new_form_type         = AddRecordForm
    edit_form_filler_type = EditFormFiller
    new_form_filler_type  = AddFormFiller
    
    def __init__(self, model_name, provider, config=None):
        self.model_name = model_name

        self.provider = provider
        self.session = self.provider.session
        self.model    = self.provider.get_entity(model_name)
        self.model_name = model_name
        self.models_view = EntitiesBase(self.session)
        
        self.config = config
        
        self.table = None
        self.table_filler = None
        
        class TableType(self.table_base_type):
            __entity__ = self.model
        self.table = TableType(self.session)
        
        class TableFillerType(self.table_filler_type):
            __entity__ = self.model
        self.table_filler = TableFillerType(self.session)
        
        class EditFormType(self.edit_form_type):
            __entity__ = self.model
        self.edit_form = EditFormType(self.session)
        #assign this form to the validator
        self.put.decoration.validation.validators  = self.edit_form

        class EditFormFillerType(self.edit_form_filler_type):
            __entity__ = self.model
        self.edit_form_filler = EditFormFillerType(self.session)

        class NewFormType(self.new_form_type):
            __entity__ = self.model
        self.new_form = NewFormType(self.session)
        #assign this form to the validator
        self.post.decoration.validation.validators  = self.new_form

        class NewFormFillerType(self.new_form_filler_type):
            __entity__ = self.model
        self.new_form_filler = EditFormFillerType(self.session)

    @with_trailing_slash
    @expose(engine+':catwalk.templates.base')
    @expose('json')
    def get_all(self, *args, **kw):
        """Show all records for a given model."""
        catwalk_css.inject()
        pylons.c.models_widget = self.models_view
        
        value = self.table_filler.get_value(kw)
        
        if pylons.request.response_type == 'application/json':
            return value

        pylons.c.widget = self.table
        
        return dict(value=value, action='./', model_name=self.model_name)
    
    #xxx: add get_one
    
    #xxx: add metadata

    @without_trailing_slash
    @expose(engine+':catwalk.templates.base')
    def edit(self, *args, **kw):
        """Display a page to edit the record."""
        catwalk_css.inject()
        pylons.c.models_widget = self.models_view
        
        pylons.c.widget = self.edit_form
        pks = self.provider.get_primary_fields(self.model)
        kw = {}
        for i, pk in  enumerate(pks):
            kw[pk] = args[i]
        value = self.edit_form_filler.get_value(kw)
        value['_method'] = 'PUT'
        return dict(value=value, action='./', model_name=self.model_name)

    @without_trailing_slash
    @expose(engine+':catwalk.templates.base')
    def new(self, *args, **kw):
        """Display a page to edit the record."""
        catwalk_css.inject()
        pylons.c.models_widget = self.models_view
        
        pylons.c.widget = self.new_form
        #xxx: fix this so it gets the defaults for the form
        value = None #self.new_form_filler.get_value(kw)
        return dict(value=value, action='./', model_name=self.model_name)
    
    @expose()
    @validate(error_handler=edit)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.IntegrityError, error_handler=edit)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.ProgrammingError, error_handler=edit)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.DataError, error_handler=edit)
    def put(self, *args, **kw):
        pks = self.provider.get_primary_fields(self.model)
        params = pylons.request.params.copy()
        for i, pk in  enumerate(pks):
            if pk not in kw and i < len(args):
                params[pk] = args[i]

<<<<<<< .mine
        self.provider.update(self.model, params=kw)
=======
        self.provider.update(model, params=params)
>>>>>>> .r179
        redirect('./')

    @expose()
    @validate(error_handler=new)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.IntegrityError, error_handler=new)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.ProgrammingError, error_handler=new)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.DataError, error_handler=new)
    def post(self, **kw):
        self.provider.create(self.model, params=kw)
        raise redirect('./')

    #xxx: make this get_delete
    @expose()
    def delete(self, *args, **kw):
        pks = self.provider.get_primary_fields(self.model)
        kw = {}
        for i, pk in  enumerate(pks):
            kw[pk] = args[i]
        self.provider.delete(self.model, params=kw)
        redirect('../')

class Catwalk(TGController):
    catwalkModelControllerType = CatwalkModelController
    
    def __init__(self, session, metadata=None, *args, **kwargs):
        self.session = session
        self.provider = SAORMSelector.get_provider(session=session, metadata=metadata)
        self.model_controllers = {}
        self.models_view = EntitiesBase(session)
        super(Catwalk, self).__init__(session, *args, **kwargs)

    @with_trailing_slash
    @expose('genshi:catwalk.templates.index')
    def index(self):
        pylons.c.models_view = self.models_view
        catwalk_css.inject()
        
        return dict(secured=(hasattr(self, 'allow_only') and self.allow_only != None))

    @expose()
    def lookup(self, model_name, *args, **kw):
        if model_name not in self.model_controllers:
            self.model_controllers[model_name] = self.catwalkModelControllerType(model_name, self.provider)
        return self.model_controllers[model_name], args
