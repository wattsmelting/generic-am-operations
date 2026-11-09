import os, tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from app import main

def test_health_and_modules():
 c=TestClient(main.app)
 assert c.get('/health').json()['persistence'] is True
 assert 'Training Records' in c.get('/api/modules').json()['modules']
 assert c.get('/').status_code==200

def test_persistence_links_and_genealogy(tmp_path,monkeypatch):
 monkeypatch.setattr(main,'DB',tmp_path/'test.sqlite3')
 c=TestClient(main.app)
 def add(m,**fields):
  r=c.post('/api/records/'+m,json={'fields':fields});assert r.status_code==201,r.text;return r.json()['id']
 lot=add('Powder Inventory',Material='Fictional alloy',**{'Lot Label':'DEMO-LOT'})
 person=add('Personnel',**{'Person ID':'DEMO-PERSON'})
 order=add('Work Orders',Order='DEMO-ORDER')
 build=add('Builds',Build='DEMO-BUILD',**{'Work Order ID':str(order),'Powder Lot ID':str(lot),'Operator ID':str(person)})
 part=add('Parts',**{'Part ID':'DEMO-PART','Build ID':str(build)})
 add('Inspections',**{'Part ID':str(part),'Result':'Demo pass'})
 t=c.get(f'/api/trace/part/{part}').json()
 assert t['powder_lot']['id']==lot
 assert t['build']['id']==build
 assert len(t['linked_records']['Inspections'])==1
 assert len(c.get('/api/events').json())==6
 assert len(c.get('/api/records/Parts').json())==1

def test_reject_invalid_links(tmp_path,monkeypatch):
 monkeypatch.setattr(main,'DB',tmp_path/'test.sqlite3')
 c=TestClient(main.app)
 assert c.post('/api/records/Parts',json={'fields':{'Part ID':'DEMO','Build ID':'999'}}).status_code==422
 assert c.post('/api/records/Powder Transactions',json={'fields':{'Action':'transfer'}}).status_code==422
