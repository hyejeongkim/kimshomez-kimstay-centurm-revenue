# -*- coding: utf-8 -*-
"""revenue 정산 마스터 백엔드 (SSOT).

- 기존 index.html(UI)을 서빙한다.
- 월별 정산 데이터를 서버에 영속 저장(/data/month/{YYYY-MM}.json) → revenue가 마스터.
- index.html 은 localStorage 대신(병행) 이 API와 동기화하여 모든 앱이 같은 데이터를 공유한다.
- 개인정보(계좌/연락처/주민)는 저장하지 않는다(rooms[]에는 금액·조정만).
"""
import json
import os
import re
import time
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

BASE = Path(__file__).resolve().parent.parent          # repo root (index.html 위치)
DATA = Path(os.getenv("DATA_DIR", str(BASE / "data")))
MONTH_DIR = DATA / "month"
MONTH_DIR.mkdir(parents=True, exist_ok=True)

ADMIN_KEY = os.getenv("REVENUE_ADMIN_KEY", "rev-change-me")
CORS = os.getenv("CORS_ORIGINS",
                 "https://revenue.kimshomez.com,https://members.kimshomez.com,"
                 "https://customers.kimshomez.com,https://payroll.kimshomez.com,"
                 "http://localhost:8090,http://127.0.0.1:8090").split(",")

app = FastAPI(title="revenue settlement master")
app.add_middleware(CORSMiddleware, allow_origins=CORS, allow_methods=["*"],
                   allow_headers=["*"], allow_credentials=False)


def _valid(month: str) -> bool:
    return bool(re.match(r"^\d{4}-\d{2}$", month or ""))


def _path(month: str) -> Path:
    return MONTH_DIR / f"{month}.json"


def _is_admin(key: str) -> bool:
    import hmac
    return hmac.compare_digest(key or "", ADMIN_KEY)


@app.get("/api/health")
def health():
    return {"ok": True, "service": "revenue-master", "months": len(list(MONTH_DIR.glob("*.json")))}


@app.get("/api/months")
def months():
    out = []
    for p in sorted(MONTH_DIR.glob("*.json"), reverse=True):
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
            out.append({"month": r.get("month"), "version": r.get("version"),
                        "updated_at": r.get("updated_at")})
        except Exception:
            continue
    return {"months": out}


@app.get("/api/month/{month}")
def get_month(month: str):
    if not _valid(month):
        raise HTTPException(400, "month 형식은 YYYY-MM")
    p = _path(month)
    if not p.exists():
        return {"month": month, "exists": False, "data": None}
    r = json.loads(p.read_text(encoding="utf-8"))
    return {"month": month, "exists": True, "version": r.get("version"),
            "updated_at": r.get("updated_at"), "data": r.get("data")}


@app.put("/api/month/{month}")
async def put_month(month: str, request: Request, x_admin_key: str = Header(default="")):
    if not _valid(month):
        raise HTTPException(400, "month 형식은 YYYY-MM")
    if not _is_admin(x_admin_key):
        raise HTTPException(401, "관리자 키가 필요합니다.")
    body = await request.json()
    data = body.get("data", body)
    prev = json.loads(_path(month).read_text(encoding="utf-8")) if _path(month).exists() else {}
    rec = {"month": month, "data": data, "version": int(prev.get("version", 0)) + 1,
           "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    _path(month).write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "month": month, "version": rec["version"], "updated_at": rec["updated_at"]}


@app.get("/")
def index():
    return FileResponse(BASE / "index.html")


@app.get("/{path:path}")
def static_or_index(path: str):
    f = BASE / path
    if f.is_file() and BASE in f.resolve().parents:
        return FileResponse(f)
    # SPA 폴백
    return FileResponse(BASE / "index.html")
