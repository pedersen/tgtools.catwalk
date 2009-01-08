"""
Catwalk Module

Classes:
Name                               Description
Catwalk

Copywrite (c) 2008 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
from sprox.dojo.sprockets import DojoSprocketCache
from catwalk.tg2.controller import CatwalkCss, BaseController, Catwalk, CatwalkModel
from webhelpers.html.builder import literal
from tg import expose, redirect
import pylons

class DojoCatwalkModel(CatwalkModel):
    sprocketCacheType = DojoSprocketCache

    def _listing(self, model_name):
        pylons.c.models_view = self.models_view
        CatwalkCss.inject()
        key = 'listing__'+model_name
        sprocket = self.sprockets[key]
        pylons.c.widget  = sprocket.view.__widget__

        return dict(value=None, model_name=model_name, action=None, root_catwalk='../../', root_model='./')

    @expose('genshi:catwalk.templates.base')
    def default(self, model_name, action=None, *args, **kw):
        if action in ['data']:
            self.start_response = pylons.request.start_response
            return self._perform_call(None, dict(url=action+'/'+model_name, params=kw))
        return super(DojoCatwalkModel, self).default(model_name, action, *args, **kw)

    @expose('json')
    def data(self, model_name, **kw):
        key = 'listing__'+model_name
        sprocket = self.sprockets[key]
        value = sprocket.filler.get_value(**kw)
        return value

class DojoCatwalk(Catwalk):
    sprocketCacheType = DojoSprocketCache
    catwalkModelType = DojoCatwalkModel

