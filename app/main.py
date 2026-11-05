import os, uuid, secrets
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel, Field
app=FastAPI(title="ARCHITECT PRIME AI Actions",version="1.0.0",
    servers=[{"url":os.getenv("PUBLIC_BASE_URL","https://YOUR-DOMAIN.example")}])
db={}
def auth(x_api_key: str|None=Header(default=None)):
    key=os.getenv("ARCHITECT_API_KEY")
    if not key: raise HTTPException(503,"API key not configured")
    if not x_api_key or not secrets.compare_digest(x_api_key,key):
        raise HTTPException(401,"Invalid API key")
class Project(BaseModel):
    name:str=Field(min_length=2)
    country:str=Field(min_length=2)
    city:str|None=None
    building_type:str
    site_area_m2:float|None=Field(default=None,gt=0)
    floor_area_m2:float|None=Field(default=None,gt=0)
    budget:float|None=Field(default=None,ge=0)
    currency:str|None=None
    geology_verified:bool=False
    seismic_verified:bool=False
    codes_verified:bool=False
class Concept(BaseModel):
    name:str
    function:float=Field(ge=0,le=10)
    cost:float=Field(ge=0,le=10)
    climate:float=Field(ge=0,le=10)
    buildability:float=Field(ge=0,le=10)
    aesthetics:float=Field(ge=0,le=10)
class Comparison(BaseModel):
    project_id:str
    concepts:list[Concept]=Field(min_length=2,max_length=5)
class Line(BaseModel):
    item:str
    quantity:float=Field(ge=0)
    unit:str
    unit_price:float=Field(ge=0)
    source:str
class Estimate(BaseModel):
    project_id:str
    currency:str
    price_date:str
    lines:list[Line]=Field(min_length=1)
    contingency_pct:float=Field(default=15,ge=0,le=100)
def project(pid):
    if pid not in db:raise HTTPException(404,"Unknown project")
    return db[pid]
@app.get("/health")
def health():return {"status":"ok","storage":"ephemeral","cad_bim":False}
@app.post("/projects",dependencies=[Depends(auth)])
def create_project(data:Project):
    pid=str(uuid.uuid4());db[pid]=data.model_dump()
    return {"project_id":pid,"gate":"G1_pending","project":db[pid],
      "notice":"Concept only; not for construction"}
@app.get("/projects/{project_id}",dependencies=[Depends(auth)])
def get_project(project_id:str):
    return {"project_id":project_id,"project":project(project_id)}
@app.post("/concepts/compare",dependencies=[Depends(auth)])
def compare(req:Comparison):
    project(req.project_id)
    w={"function":.3,"cost":.2,"climate":.2,"buildability":.2,"aesthetics":.1}
    ranked=sorted([{"name":c.name,"score":round(sum(getattr(c,k)*v for k,v in w.items()),2)}
       for c in req.concepts],key=lambda x:x["score"],reverse=True)
    return {"ranking":ranked,"weights":w,"gate":"G1_pending",
       "caveat":"Scores are subjective inputs, not validated engineering results"}
@app.post("/estimates/calculate",dependencies=[Depends(auth)])
def estimate(req:Estimate):
    project(req.project_id)
    rows=[{"item":x.item,"total":round(x.quantity*x.unit_price,2),"source":x.source}
      for x in req.lines]
    subtotal=round(sum(x["total"] for x in rows),2)
    return {"rows":rows,"subtotal":subtotal,
      "total":round(subtotal*(1+req.contingency_pct/100),2),
      "currency":req.currency,"price_date":req.price_date,"gate":"G3_pending",
      "caveat":"Arithmetic only; input prices unverified"}
@app.get("/projects/{project_id}/qa",dependencies=[Depends(auth)])
def qa(project_id:str):
    p=project(project_id);issues=[]
    for k in ("site_area_m2","floor_area_m2","geology_verified","seismic_verified","codes_verified"):
        if not p.get(k):issues.append({"field":k,"severity":"high" if k.endswith("verified") else "medium"})
    return {"issues":issues,"status":"input_screen_only",
      "caveat":"Not a code, fire, seismic or structural safety review"}
