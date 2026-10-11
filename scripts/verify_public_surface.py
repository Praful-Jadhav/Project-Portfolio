#!/usr/bin/env python3
"""Validate public portfolio integrity and evidence packets for material content changes."""
import json, os, re, subprocess, sys
from html.parser import HTMLParser
from pathlib import Path

MATERIAL={"index.html","styles.css","README.md","AGENTS.md",".github/workflows/public-integrity.yml","scripts/verify_public_surface.py","tests/test_public_surface.py"}
HEADINGS=("## Claim and risk","## Scope and acceptance criteria","## Verification plan and results","## Validation plan and results","## Public safety and privacy","## Limitations and open items","## Recovery and rollback","## Evidence and tested revision")
STATUSES={"DRAFT","IN_PROGRESS","BLOCKED","FAILED","VERIFIED","VALIDATED","ACCEPTED","ACCEPTED_RISK","DEFERRED"}

class Links(HTMLParser):
 def __init__(self):
  super().__init__(); self.ids=set(); self.hrefs=[]; self.title=False; self.main=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if "id" in a: self.ids.add(a["id"])
  if tag=="a" and a.get("href"): self.hrefs.append(a["href"])
  if tag=="title": self.title=True
  if tag=="main": self.main=True

def validate_packet(text,path="<packet>"):
 errors=[]; m=re.search(r"(?im)^Status:\s*([A-Z_]+)\s*$",text); status=m.group(1) if m else None
 if status not in STATUSES: errors.append(path+": missing/invalid Status")
 for field,pat in (("Task ID",r"(?im)^Task ID:\s*\S+"),("Accountable owner",r"(?im)^Accountable owner:\s*\S+"),("Risk tier",r"(?im)^Risk tier:\s*(R0|R1|R2|R3)\b")):
  if not re.search(pat,text): errors.append(path+": missing "+field)
 for h in HEADINGS:
  m=re.search(r"(?m)^"+re.escape(h)+r"\s*$",text)
  if not m: errors.append(path+": missing section "+h); continue
  n=re.search(r"(?m)^##\s+",text[m.end():]); end=m.end()+n.start() if n else len(text); body=text[m.end():end].strip()
  if len(re.sub(r"\s+|[>#*_\-\[\]]","",body))<18: errors.append(path+": empty section "+h)
  if re.search(r"(?i)\b(TODO|TBD|PLACEHOLDER|FILL\s+IN|WRITE\s+HERE)\b",body): errors.append(path+": unresolved placeholder in "+h)
 if status in {"VERIFIED","VALIDATED","ACCEPTED"}:
  for x in ("Verification status: PASS","Validation status: PASS","Independent read-back: PASS"):
   if not re.search(r"(?im)^"+re.escape(x)+r"\s*$",text): errors.append(path+": cannot be "+status+" without "+x)
  if not re.search(r"(?im)^Tested revision:\s*[0-9a-f]{7,40}\s*$",text): errors.append(path+": accepted status needs tested SHA")
  if not re.search(r"(?im)^Acceptance authority:\s*\S+",text): errors.append(path+": accepted status needs acceptance authority")
 return errors

def changed_files(name,event):
 if name=="pull_request":
  base=event.get("pull_request",{}).get("base",{}).get("sha")
  if not base: raise ValueError("missing PR base SHA")
  exists=subprocess.run(["git","cat-file","-e",base+"^{commit}"],capture_output=True,text=True)
  if exists.returncode!=0: subprocess.run(["git","fetch","--quiet","--no-tags","origin",base],check=True,capture_output=True,text=True)
  cmd=["git","diff","--name-only",base+"...HEAD"]
 elif name=="push":
  before,after=event.get("before",""),event.get("after","HEAD")
  cmd=(["git","ls-tree","-r","--name-only",after] if not before or set(before)=={"0"} else ["git","diff","--name-only",before,after])
 else: return []
 r=subprocess.run(cmd,check=True,capture_output=True,text=True)
 return [x.strip() for x in r.stdout.splitlines() if x.strip()]

def check_site():
 p=Path("index.html")
 if not p.exists(): return ["index.html is missing"]
 text=p.read_text(encoding="utf-8")
 parser=Links(); parser.feed(text)
 errors=[]
 if "<!doctype html>" not in text.lower(): errors.append("index.html must declare HTML doctype")
 if not parser.title: errors.append("page title is missing")
 if not parser.main: errors.append("main landmark is missing")
 if not Path("styles.css").exists(): errors.append("styles.css is missing")
 for href in parser.hrefs:
  if href.startswith("#") and href[1:] not in parser.ids: errors.append("broken page anchor: "+href)
  elif href and not href.startswith(("http://","https://","mailto:","tel:","#")) and not Path(href.split("#")[0]).exists():
   errors.append("missing local link target: "+href)
 if re.search(r"(?i)\b(Lorem ipsum|TODO|TBD|PLACEHOLDER|YOUR_NAME|example\.com)\b",text): errors.append("placeholder or demo text detected in public HTML")
 return errors

def main():
 errors=check_site()
 name=os.environ.get("GITHUB_EVENT_NAME","")
 if name in {"pull_request","push"}:
  try:
   event=json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8")); files=changed_files(name,event)
  except Exception as e: errors.append("cannot establish candidate diff: "+str(e)); files=[]
  material=[p for p in files if p in MATERIAL and not p.startswith("docs/evidence/")]
  if material:
   packets=[p for p in files if p.startswith("docs/evidence/") and p.endswith(".md")]
   if not packets: errors.append("material publication change requires docs/evidence/*.md packet")
   for p in packets:
    try: errors.extend(validate_packet(Path(p).read_text(encoding="utf-8"),p))
    except Exception as e: errors.append(p+": cannot read packet: "+str(e))
 if errors:
  print("FAIL: "+str(len(errors))+" issue(s)")
  for e in errors: print("- "+e)
  return 1
 print("PASS: public page integrity and applicable evidence packet checks.")
 print("This does not prove factual claims or replace rendered browser review.")
 return 0
if __name__=="__main__": raise SystemExit(main())
