import json
import os
import time
from mcp.server.fastmcp import FastMCP

DB = "pet.json"

mcp = FastMCP(
    "pet-server",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8000)),
)

def load_pet():
    if not os.path.exists(DB):
        return {
            "name": "小D",
            "hunger": 50,
            "mood": 50,
            "coins": 10,
            "last": time.time(),
        }
    with open(DB, "r", encoding="utf-8") as f:
        return json.load(f)

def save_pet(p):
    p["last"] = time.time()
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=2)

def apply_decay(p):
    now = time.time()
    steps = int((now - p.get("last", now)) // 600)
    if steps > 0:
        p["hunger"] = max(0, p["hunger"] - steps)
        p["mood"] = max(0, p["mood"] - steps // 2)
        p["last"] = now
    return p

@mcp.tool()
def pet_status() -> dict:
    """查看宠物当前状态：名字、饱食、心情、金币。"""
    p = load_pet()
    p = apply_decay(p)
    save_pet(p)
    return p

@mcp.tool()
def feed_pet() -> dict:
    """喂宠物：消耗1金币，饱食+10，心情+2。"""
    p = load_pet()
    p = apply_decay(p)
    if p["coins"] < 1:
        save_pet(p)
        return {"ok": False, "msg": "金币不够，先陪它玩赚点金币吧", "pet": p}
    p["coins"] -= 1
    p["hunger"] = min(100, p["hunger"] + 10)
    p["mood"] = min(100, p["mood"] + 2)
    save_pet(p)
    return {"ok": True, "msg": "喂饱了", "pet": p}

@mcp.tool()
def play_with_pet() -> dict:
    """陪宠物玩：心情+10，饱食-5，赚1金币。"""
    p = load_pet()
    p = apply_decay(p)
    p["mood"] = min(100, p["mood"] + 10)
    p["hunger"] = max(0, p["hunger"] - 5)
    p["coins"] += 1
    save_pet(p)
    return {"ok": True, "msg": "玩得很开心", "pet": p}

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
