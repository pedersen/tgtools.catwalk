import os, sys
from catwalk.test.base import setup_database, setup_records
import catwalk
from tg.test_stack import TestConfig, app_from_config
from tg.util import Bunch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catwalk.tg2.test.model import metadata, DBSession

root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, root)
test_db_path = 'sqlite:///'+root+'/test.db'
paths=Bunch(
            root=root,
            controllers=os.path.join(root, 'controllers'),
            static_files=os.path.join(root, 'public'),
            templates=os.path.join(root, 'templates')
            )

base_config = TestConfig(folder = 'rendering',
                         values = {'use_sqlalchemy': True,
                                   'model':catwalk.tg2.test.model,
                                   'session':catwalk.tg2.test.model.DBSession,
                                   'pylons.helpers': Bunch(),
                                   'use_legacy_renderer': False,
                                   # this is specific to mako
                                   # to make sure inheritance works
                                   'use_dotted_templatenames': True,
                                   'paths':paths,
                                   'package':catwalk.tg2.test,
                                   'sqlalchemy.url':test_db_path
                                  }
                         )

def setup():
    engine = create_engine(test_db_path)
    metadata.bind = engine
    metadata.drop_all()
    metadata.create_all()
    session = sessionmaker(bind=engine)()
    setup_records(session)
    session.commit()

def teardown():
    os.remove(test_db_path[10:])

class TestCatwalkController:
    def __init__(self, *args, **kargs):
        self.app = app_from_config(base_config)

    def test_index(self):
        resp = self.app.get('/catwalk/')
        assert 'Document' in resp, resp

    def _test_list_documents(self):
        resp = self.app.get('/catwalk/model/Document').follow()
        assert """<tr id="address.container" class="odd">
            <td class="labelcol">
                <label id="address.label" for="address" class="fieldlabel">Address</label>
            </td>
            <td class="fieldcol">
                <input type="text" name="address" class="textfield" id="address" value="" />
            </td>
        </tr>""" in resp, resp

    def test_documents_new(self):
        resp = self.app.get('/catwalk/model/Document/new')
        assert """<td class="fieldcol">
                <textarea id="url" name="url" class="textarea" rows="7" cols="50"></textarea>
            </td>
        </tr><tr id="address.container" class="odd">
            <td class="labelcol">
                <label id="address.label" for="address" class="fieldlabel">Address</label>
            </td>""" in resp, resp
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
