from decorator import decorator
from tg.decorators import validate as tgValidate
from tg.decorators import Decoration
from pylons import request
from tg.controllers import _object_dispatch, flash

class validate(tgValidate):
    def __init__(self, error_handler=None, *args,**kw):
        self.error_handler = error_handler
        self.needs_controller = True
        class Validators(object):
            def validate(self, controller, params):
                #pull the sprocket out of the cache
                sprocket = controller.im_self.sprockets[params['sprox_id']]
                #validate on it's widget
                return sprocket.view.__widget__.validate(params)
        self.validators = Validators()
        
def crudErrorCatcher(errorType=None, error_handler=None):
    def wrapper(func, self, *args, **kwargs):
        """Decorator Wrapper function"""
        try:
            value = func(self, *args, **kwargs)
        except errorType, e:
            message=None
            if hasattr(e,"message"):
                message=e.message
            if isinstance(message,str):
                try:
                    message=message.decode('utf-8')
                except:
                    message=None
            if message:
                flash(message,status="status_alert")
                return self._perform_call(None, dict(url=error_handler.__name__+'/'+'/'.join(args), params=kwargs))
        return value
    return decorator(wrapper)
