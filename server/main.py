# -*- coding: utf-8 -*-
"""revenue 정산 마스터 백엔드 (SSOT).

- 기존 index.html(UI)을 서빙한다.
- 월별 정산 데이터를 서버에 영속 저장(/data/month/{YYYY-MM}.json) → revenue가 마스터.
- index.html 은 localStorage 와 병행해 이 API 와 동기화한다.
- 개인정보(계좌/연락처/주민)는 저장하지 않는다(rooms[]에는 금액·조정만).

■ 데이터 손실 방지(2026-08)
- 저장(PUT/PATCH) 전 항상 자동 백업(/data/month/_bak).
- 빈/급격히 축소된 데이터는 거부(force 아니면) → 실수 리셋으로 통째 손실되는 것 방지.
- 정산확정(lock): 확정된 월은 저장 거부(force 아니면) → 최종본 보호.
- 시트별 병합 저장(PATCH): 임시저장이 다른 시트를 지우지 않음.
- 백업 목록/복구 API.
"""
import json
import os
import re
import time
import shutil
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

BASE = Path(__file__).resolve().parent.parent          # repo root (index.html 위치)
DATA = Path(os.getenv("DATA_DIR", str(BASE / "data")))
MONTH_DIR = DATA / "month"
BAK_DIR = MONTH_DIR / "_bak"
LOCKS_PATH = DATA / "locks.json"
MONTH_DIR.mkdir(parents=True, exist_ok=True)
BAK_DIR.mkdir(parents=True, exist_ok=True)

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


# ---------- 정산확정(잠금) ----------
def _load_locks() -> set:
    try:
        return set(json.loads(LOCKS_PATH.read_text(encoding="utf-8")))
    except Exception:
        return set()


def _save_locks(s: set) -> None:
    LOCKS_PATH.write_text(json.dumps(sorted(s), ensure_ascii=False), encoding="utf-8")


# ---------- 백업/복구 ----------
def _backup(month: str, tag: str = "") -> str:
    p = _path(month)
    if not p.exists():
        return ""
    try:
        ts = time.strftime("%Y%m%d_%H%M%S")
        dst = BAK_DIR / f"{month}_{ts}{('_' + tag) if tag else ''}.json"
        shutil.copy2(p, dst)
        baks = sorted(BAK_DIR.glob(f"{month}_*.json"))
        for old in baks[:-40]:          # 월별 최근 40개 보관
            try:
                old.unlink()
            except Exception:
                pass
        return dst.name
    except Exception:
        return ""


def _size(obj) -> int:
    try:
        return len(json.dumps(obj, ensure_ascii=False))
    except Exception:
        return 0


def _empty(data) -> bool:
    if data is None:
        return True
    if isinstance(data, (dict, list, str)) and len(data) == 0:
        return True
    return False


def _read(month: str) -> dict:
    p = _path(month)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _write(month: str, data) -> dict:
    prev = _read(month)
    rec = {"month": month, "data": data,
           "version": int(prev.get("version", 0)) + 1,
           "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    _path(month).write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    return rec


@app.get("/api/health")
def health():
    return {"ok": True, "service": "revenue-master",
            "months": len(list(MONTH_DIR.glob("*.json"))), "locks": sorted(_load_locks())}


@app.get("/api/months")
def months():
    out = []
    locks = _load_locks()
    for p in sorted(MONTH_DIR.glob("*.json"), reverse=True):
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
            out.append({"month": r.get("month"), "version": r.get("version"),
                        "updated_at": r.get("updated_at"),
                        "locked": r.get("month") in locks})
        except Exception:
            continue
    return {"months": out}


@app.get("/api/month/{month}")
def get_month(month: str):
    if not _valid(month):
        raise HTTPException(400, "month 형식은 YYYY-MM")
    p = _path(month)
    if not p.exists():
        return {"month": month, "exists": False, "data": None, "locked": month in _load_locks()}
    r = json.loads(p.read_text(encoding="utf-8"))
    return {"month": month, "exists": True, "version": r.get("version"),
            "updated_at": r.get("updated_at"), "data": r.get("data"),
            "locked": month in _load_locks()}


@app.put("/api/month/{month}")
async def put_month(month: str, request: Request, x_admin_key: str = Header(default="")):
    """월 전체 저장. 손실 방지: 잠금 거부 + 빈/급축소 거부(force 제외) + 저장 전 백업."""
    if not _valid(month):
        raise HTTPException(400, "month 형식은 YYYY-MM")
    if not _is_admin(x_admin_key):
        raise HTTPException(401, "관리자 키가 필요합니다.")
    body = await request.json()
    data = body.get("data", body)
    force = bool(body.get("force"))
    if month in _load_locks() and not force:
        raise HTTPException(409, f"{month} 정산확정(잠금)됨 — 확정 해제 후 저장하세요. 데이터는 보호됨.")
    prev = _read(month)
    prev_data = prev.get("data")
    # 리셋/손실 방지: 기존 데이터가 있는데 새 데이터가 비었거나 30% 미만으로 급축소 → 거부
    if prev_data and not force:
        if _empty(data):
            raise HTTPException(409, "빈 데이터 저장 거부 — 기존 데이터 보호(리셋 방지). 새로 시작하려면 force=true.")
        if _size(data) < _size(prev_data) * 0.3:
            raise HTTPException(409, "데이터가 급격히 축소되어 저장을 막았습니다(손실 방지). 의도된 것이면 force=true.")
    bak = _backup(month)                       # 저장 전 백업
    rec = _write(month, data)
    return {"ok": True, "month": month, "version": rec["version"],
            "updated_at": rec["updated_at"], "backup": bak}


@app.patch("/api/month/{month}/sheet")
async def patch_sheet(month: str, request: Request, x_admin_key: str = Header(default="")):
    """시트별 임시저장: {sheet, value} 를 기존 data 에 병합(다른 시트 보존)."""
    if not _valid(month):
        raise HTTPException(400, "month 형식은 YYYY-MM")
    if not _is_admin(x_admin_key):
        raise HTTPException(401, "관리자 키가 필요합니다.")
    body = await request.json()
    sheet = body.get("sheet")
    value = body.get("value")
    force = bool(body.get("force"))
    if not sheet:
        raise HTTPException(400, "sheet 이름이 필요합니다.")
    if month in _load_locks() and not force:
        raise HTTPException(409, f"{month} 정산확정(잠금)됨 — 확정 해제 후 저장하세요.")
    prev = _read(month)
    data = prev.get("data")
    if not isinstance(data, dict):
        data = {} if data in (None, "") else {"_root": data}
    _backup(month, tag="sheet")                # 병합 전 백업
    data[sheet] = value                        # 해당 시트만 갱신(나머지 시트 보존)
    rec = _write(month, data)
    return {"ok": True, "month": month, "sheet": sheet, "version": rec["version"],
            "updated_at": rec["updated_at"]}


@app.post("/api/month/{month}/confirm")
def confirm_month(month: str, x_admin_key: str = Header(default="")):
    """정산확정: 잠금 → 이후 저장 거부(최종본 보호)."""
    if not _valid(month):
        raise HTTPException(400, "month 형식은 YYYY-MM")
    if not _is_admin(x_admin_key):
        raise HTTPException(401, "관리자 키가 필요합니다.")
    _backup(month, tag="confirm")
    s = _load_locks(); s.add(month); _save_locks(s)
    return {"ok": True, "confirmed": month, "locks": sorted(s)}


@app.post("/api/month/{month}/unlock")
def unlock_month(month: str, x_admin_key: str = Header(default="")):
    """정산확정 해제(수정 허용)."""
    if not _is_admin(x_admin_key):
        raise HTTPException(401, "관리자 키가 필요합니다.")
    s = _load_locks(); s.discard(month); _save_locks(s)
    return {"ok": True, "unlocked": month, "locks": sorted(s)}


@app.get("/api/month/{month}/backups")
def list_backups(month: str, x_admin_key: str = Header(default="")):
    if not _is_admin(x_admin_key):
        raise HTTPException(401, "관리자 키가 필요합니다.")
    baks = sorted(BAK_DIR.glob(f"{month}_*.json"), reverse=True)
    return {"month": month, "backups": [{"name": b.name, "size": b.stat().st_size} for b in baks[:40]]}


@app.post("/api/month/{month}/restore")
async def restore_month(month: str, request: Request, x_admin_key: str = Header(default="")):
    """백업으로 복구. body={backup_name}. 복구 전 현재본도 백업."""
    if not _is_admin(x_admin_key):
        raise HTTPException(401, "관리자 키가 필요합니다.")
    body = await request.json()
    name = body.get("backup_name", "")
    src = BAK_DIR / name
    if not name or not src.exists() or not src.name.startswith(f"{month}_"):
        raise HTTPException(404, "백업 파일 없음")
    _backup(month, tag="prerestore")
    r = json.loads(src.read_text(encoding="utf-8"))
    rec = _write(month, r.get("data"))
    return {"ok": True, "restored_from": name, "version": rec["version"]}


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
