"""Local-only, synthetic-data-first manufacturing operations development API."""
import json, os, sqlite3, threading
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app=FastAPI(title="Generic AM Operations",version="0.4.0")
DB=Path(os.getenv("AM_DEV_DB",str(Path(__file__).resolve().parent.parent/"local_data"/"development.sqlite3")))
LOCK=threading.RLock()
MODULES={
 "CRM":["Company","Contact","Stage","Next Action"],"Customers":["Customer","Industry","Contact"],"RFQs":["RFQ","Customer","Material","Quantity","Status"],"Work Orders":["Order","Customer","Material","Quantity","Status"],"Builds":["Build","Work Order ID","Machine","Material","Powder Lot ID","Operator ID","Status"],"Parts":["Part ID","Build ID","Part Revision","Inspection Status"],"Powder Inventory":["Material","Lot Label","Quantity (kg)","Status","Supplier Certificate"],"Powder Transactions":["Source Lot ID","Destination Lot ID","Build ID","Action","Quantity (kg)"],"Equipment":["Asset","Type","Status","Next Service"],"Inspections":["Part ID","Instrument ID","Result","Inspector ID"],"NCR":["Record","Part ID","Issue","Containment","Disposition","Status","Owner"],"CAPA":["Record","Source NCR ID","Root Cause","Action","Effectiveness","Status","Owner"],"Documents":["Document","Revision","Status","Owner","Effective Date"],"Procedures":["Procedure","Revision","Status","Owner","Effective Date"],"Personnel":["Person ID","Display Name","Role","Active"],"Training Materials":["Course","Document ID","Revision","Assessment Method"],"Training Records":["Person ID","Course ID","Result","Qualified Until","Assessor"],"Suppliers":["Supplier","Approval Status","Scope"],"Audits":["Audit","Scope","Finding","Status"],"Risk Register":["Risk","Process","Severity","Mitigation","Status"],"Complaints":["Complaint","Product","Assessment","Status"],"Change Control":["Change","Affected Record","Reason","Approval Status"],"Calibration":["Equipment ID","Calibration Date","Due Date","Status"],"Management Review":["Meeting","Review Date","Actions","Status"],"Validation":["Protocol","System or Process","Evidence","Status"],"Shipping":["Shipment","Part ID","Release Status","CoC Reference"]}
GUIDES={
 "Powder Inventory":"Receive lots with certificate references; quarantine until reviewed. Never overwrite lot identity. Use Powder Transactions to record movements and consumption.",
 "Powder Transactions":"Record source and destination lot IDs for transfer or mixing, or a build ID for consumption. Transactions are append-only in this prototype.",
 "Builds":"Link each build to a work order, machine, powder lot and qualified operator. IDs refer to existing records.",
 "Parts":"Create a part record linked to its originating build; inspections and shipments refer back to the part ID.",
 "Personnel":"Create fictional development personnel, assign roles, then document training and qualification in Training Records.",
 "Training Records":"Associate a person with a training material, assessment result, assessor and qualification expiration. Training is informational in v0.4.0, not an enforced authorization gate.",
 "NCR":"Record issue, containment and disposition. Open a CAPA when systemic correction is necessary; do not assume closure implies approval.",
 "CAPA":"Link to NCR, record root cause and action, then verify effectiveness before controlled closure. Formal approval is not enforced yet.",
 "Documents":"Track document title, revision and status. Electronic approval and immutable version storage remain future work.",
 "Procedures":"Track controlled procedures and effective dates; see the built-in manual for general workflows.",
 "Inspections":"Record part reference, instrument, result and inspector; acceptance decisions require separately validated controls.",
 "Validation":"Capture validation protocol references and evidence for IQ/OQ/PQ or software validation, where applicable."}

def connect():
 DB.parent.mkdir(parents=True,exist_ok=True)
 c=sqlite3.connect(DB,timeout=10);c.row_factory=sqlite3.Row
 c.execute("PRAGMA foreign_keys=ON")
 c.execute("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT,module TEXT NOT NULL,body TEXT NOT NULL,created_utc TEXT NOT NULL)")
 c.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT,record_id INTEGER,module TEXT,action TEXT,at_utc TEXT,details TEXT)")
 c.commit();return c

def stamp():return datetime.now(timezone.utc).isoformat()
class RecordIn(BaseModel):
 fields:dict[str,str]=Field(default_factory=dict)

def validate_module(module):
 if module not in MODULES:raise HTTPException(404,"Unknown module")

def get_record(c,module,id):
 r=c.execute("SELECT * FROM records WHERE module=? AND id=?",(module,id)).fetchone()
 if not r:raise HTTPException(422,f"Referenced {module} ID {id} does not exist")
 return r

def check_links(c,module,fields):
 refs={"Builds":{"Work Order ID":"Work Orders","Powder Lot ID":"Powder Inventory","Operator ID":"Personnel"},"Parts":{"Build ID":"Builds"},"Powder Transactions":{"Source Lot ID":"Powder Inventory","Destination Lot ID":"Powder Inventory","Build ID":"Builds"},"Inspections":{"Part ID":"Parts","Instrument ID":"Equipment","Inspector ID":"Personnel"},"NCR":{"Part ID":"Parts"},"CAPA":{"Source NCR ID":"NCR"},"Training Materials":{"Document ID":"Documents"},"Training Records":{"Person ID":"Personnel","Course ID":"Training Materials"},"Calibration":{"Equipment ID":"Equipment"},"Shipping":{"Part ID":"Parts"}}
 for field,target in refs.get(module,{}).items():
  val=fields.get(field,"").strip()
  if val:
   if not val.isdigit():raise HTTPException(422,f"{field} must be an existing numeric record ID")
   get_record(c,target,int(val))
 if module=="Powder Transactions":
  if not (fields.get("Source Lot ID") or fields.get("Destination Lot ID") or fields.get("Build ID")):raise HTTPException(422,"Powder transaction requires a linked lot or build")

@app.get("/",response_class=HTMLResponse)
def home():return (Path(__file__).parent/"ui.html").read_text(encoding="utf-8")
@app.get("/health")
def health():return {"status":"ok","persistence":True,"version":"0.4.0","local_only":True}
@app.get("/api/modules")
def modules():return {"modules":MODULES,"guides":GUIDES}
@app.get("/api/records/{module}")
def list_records(module:str):
 validate_module(module)
 with LOCK:
  with connect() as c:
   return [{"id":r["id"],"created_utc":r["created_utc"],**json.loads(r["body"])} for r in c.execute("SELECT * FROM records WHERE module=? ORDER BY id DESC",(module,))]
@app.post("/api/records/{module}",status_code=201)
def create_record(module:str,data:RecordIn):
 validate_module(module)
 allowed=MODULES[module]
 if not data.fields.get(allowed[0],"").strip():raise HTTPException(422,f"{allowed[0]} is required")
 if any(k not in allowed for k in data.fields):raise HTTPException(422,"Unexpected field")
 fields={k:str(data.fields.get(k,"")).strip()[:500] for k in allowed}
 with LOCK:
  with connect() as c:
   check_links(c,module,fields)
   cur=c.execute("INSERT INTO records(module,body,created_utc) VALUES(?,?,?)",(module,json.dumps(fields),stamp()))
   c.execute("INSERT INTO events(record_id,module,action,at_utc,details) VALUES(?,?,?,?,?)",(cur.lastrowid,module,"created",stamp(),"Development record created"))
   return {"id":cur.lastrowid,**fields}
@app.get("/api/events")
def events():
 with LOCK:
  with connect() as c:return [dict(r) for r in c.execute("SELECT * FROM events ORDER BY id DESC LIMIT 200")]
@app.get("/api/trace/part/{part_id}")
def part_trace(part_id:int):
 with LOCK:
  with connect() as c:
   part=get_record(c,"Parts",part_id); p=json.loads(part["body"])
   build=None;powder=None;transactions=[]
   if p.get("Build ID"):
    b=get_record(c,"Builds",int(p["Build ID"]));build={"id":b["id"],**json.loads(b["body"])}
    if build.get("Powder Lot ID"):
     lot=get_record(c,"Powder Inventory",int(build["Powder Lot ID"]));powder={"id":lot["id"],**json.loads(lot["body"])}
    for t in c.execute("SELECT * FROM records WHERE module='Powder Transactions'"):
     f=json.loads(t["body"])
     if f.get("Build ID")==str(b["id"]) or (powder and f.get("Source Lot ID")==str(powder["id"])):transactions.append({"id":t["id"],**f})
   linked={}
   for module,field in [("Inspections","Part ID"),("NCR","Part ID"),("Shipping","Part ID")]:
    linked[module]=[{"id":r["id"],**json.loads(r["body"])} for r in c.execute("SELECT * FROM records WHERE module=?",(module,)) if json.loads(r["body"]).get(field)==str(part_id)]
   return {"part":{"id":part_id,**p},"build":build,"powder_lot":powder,"powder_transactions":transactions,"linked_records":linked,"warning":"Development genealogy; not a validated traceability record"}
@app.get("/api/manual")
def manual():return {"intro":"Development-only software. Use numeric record IDs to link records. Do not enter real or sensitive data.","pages":{m:GUIDES.get(m,f"Create and review generic {m.lower()} records. First field required. Linked records must use numeric IDs when present.") for m in MODULES},"standards":"Supports development of quality workflows; does not establish AS9100 or ISO 13485 compliance."}
