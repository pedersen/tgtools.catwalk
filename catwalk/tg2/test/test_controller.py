import os, sys
from catwalk.test.base import setup_database
import catwalk
from tg.test_stack import TestConfig, app_from_config
from tg.util import Bunch

root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, root)

paths=Bunch(
            root=root,
            controllers=os.path.join(root, 'controllers'),
            static_files=os.path.join(root, 'public'),
            templates=os.path.join(root, 'templates')
            )

base_config = TestConfig(folder = 'rendering',
                         values = {'use_sqlalchemy': True,
                                   'model':catwalk.tg2.test.model,
                                   'session':catwalk.test.model.DBSession,
                                   'pylons.helpers': Bunch(),
                                   'use_legacy_renderer': False,
                                   # this is specific to mako
                                   # to make sure inheritance works
                                   'use_dotted_templatenames': True,
                                   'paths':paths,
                                   'package':catwalk.tg2.test,
                                   'sqlalchemy.url':'sqlite://'
                                   }
                         )

class TestCatwalkController:
    def __init__(self, *args, **kargs):
        #TestWSGIController.__init__(self, *args, **kargs)
        self.app = app_from_config(base_config)

        #make_app(RootController)

    def test_index(self):
        resp = self.app.get('/catwalk/')
        assert 'Document' in resp, resp

    def _test_list_documents(self):
        resp = self.app.get('/catwalk/model/Document').follow()
        assert 'asdfasdf' in resp, resp

    def _test_documents_new(self):
        resp = self.app.get('/catwalk/model/Document/new')
        assert """<td>
        String(length=500, convert_unicode=False, assert_unicode=None)
    </td>
</tr>
<tr class="even">
    <td>
        address
    </td>
    <td>
        relation
    </td>
""" in resp, resp
    def test_documents_metadata(self):
        resp = self.app.get('/catwalk/model/Document/metadata')
        assert """<td>
        String(length=500, convert_unicode=False, assert_unicode=None)
    </td>
</tr>
<tr class="even">
    <td>
        address
    </td>
    <td>
        relation
    </td>
""" in resp, resp
