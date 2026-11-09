from fastapi.testclient import TestClient
from app.main import app

def test_gui_sections():
 html=TestClient(app).get('/').text
 for label in ('Training Records','Powder Transactions','NCR','CAPA','Traceability','Page Help','Slate'):
  assert label in html
