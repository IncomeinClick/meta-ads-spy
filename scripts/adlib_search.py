#!/usr/bin/env python3
"""Meta Ad Library search helper for the `meta-ads-spy` skill.

Queries the OFFICIAL Ad Library API (ads_archive) for ACTIVE ads, computes how
long each has been running (the "winner" signal — nobody keeps paying to run a
losing ad for months), and returns clean JSON for the agent to analyze.

Requires the user's OWN Meta access token AFTER they've done identity
confirmation at facebook.com/id (one-time; see the course welcome email).

Token resolution order:
  1. env  META_ADS_TOKEN
  2. file ~/.config/meta-ads-spy/token

Usage:
  adlib_search.py --query "คอลลาเจน" --country TH
  adlib_search.py --page-id 1234567890 --country TH      # cleaner: search a known competitor page
"""
import argparse, json, os, urllib.request, urllib.parse, urllib.error
from datetime import date
from pathlib import Path

GRAPH = "https://graph.facebook.com/v21.0/ads_archive"
FIELDS = ",".join([
    "id", "page_id", "page_name", "ad_creative_bodies", "ad_creative_link_titles",
    "ad_creative_link_descriptions", "ad_delivery_start_time", "ad_delivery_stop_time",
    "ad_snapshot_url", "publisher_platforms",
])


def load_token():
    t = os.environ.get("META_ADS_TOKEN")
    if t:
        return t.strip()
    p = Path.home() / ".config" / "meta-ads-spy" / "token"
    if p.exists():
        return p.read_text().strip()
    return None


def err(code, message):
    print(json.dumps({"error": code, "message": message}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", help="keyword to search in ad text")
    ap.add_argument("--page-id", help="search a specific competitor page id (cleaner than keyword)")
    ap.add_argument("--country", default="TH", help="2-letter country (default TH)")
    ap.add_argument("--limit", type=int, default=120, help="max ads to pull")
    a = ap.parse_args()

    token = load_token()
    if not token:
        return err("no_token",
                   "ยังไม่ได้ตั้งค่า Meta token — สร้าง FB app + ยืนยันตัวตนที่ facebook.com/id "
                   "แล้วเก็บ token ไว้ที่ ~/.config/meta-ads-spy/token (ดูวิธีในอีเมลต้อนรับคอร์ส)")
    if not a.query and not a.page_id:
        return err("no_input", "ต้องระบุ --query หรือ --page-id อย่างน้อยหนึ่งอย่าง")

    params = {
        "access_token": token,
        "ad_reached_countries": json.dumps([a.country]),
        "ad_active_status": "ACTIVE",     # only ads still running = strongest winner signal
        "ad_type": "ALL",                 # commercial ads (not just political)
        "fields": FIELDS,
        "limit": min(a.limit, 250),
    }
    if a.query:
        params["search_terms"] = a.query
    if a.page_id:
        params["search_page_ids"] = json.dumps([a.page_id])

    url = GRAPH + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=40) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        if "2332002" in body or "library/api" in body:
            return err("identity_not_confirmed",
                       "ยังยิง Ad Library API ไม่ได้ — ต้องยืนยันตัวตนที่ facebook.com/id ก่อน "
                       "(ครั้งเดียว รอ 1-3 วัน) ตามขั้นตอนในอีเมลต้อนรับ")
        if "190" in body or "OAuthException" in body:
            return err("token_expired",
                       "Meta token หมดอายุหรือใช้ไม่ได้ — สร้าง token ใหม่ (แบบ long-lived) "
                       "แล้วอัปเดตที่ ~/.config/meta-ads-spy/token")
        return err("api_error", body[:400])

    ads = list(data.get("data", []))
    pages = 0
    while len(ads) < a.limit and data.get("paging", {}).get("next") and pages < 4:
        try:
            with urllib.request.urlopen(data["paging"]["next"], timeout=40) as r:
                data = json.loads(r.read())
            ads.extend(data.get("data", []))
            pages += 1
        except Exception:
            break

    today = date.today()
    out = []
    for ad in ads:
        st = ad.get("ad_delivery_start_time")
        days = None
        if st:
            try:
                days = (today - date.fromisoformat(st[:10])).days
            except Exception:
                pass
        bodies = ad.get("ad_creative_bodies") or []
        out.append({
            "page_name": ad.get("page_name"),
            "page_id": ad.get("page_id"),
            "days_running": days,
            "start_date": st[:10] if st else None,
            "body": (bodies[0] if bodies else "")[:600],
            "titles": ad.get("ad_creative_link_titles") or [],
            "platforms": ad.get("publisher_platforms") or [],
            "snapshot_url": ad.get("ad_snapshot_url"),
        })

    # Longest-running first (None last). This is the raw winner ranking; the agent
    # still has to dedupe by ANGLE and pick diverse big ideas from this list.
    out.sort(key=lambda x: (x["days_running"] is None, -(x["days_running"] or 0)))

    print(json.dumps({
        "count": len(out),
        "country": a.country,
        "query": a.query,
        "page_id": a.page_id,
        "ads": out,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
