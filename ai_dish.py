# ai_dish.py
import os
import time
import hashlib
from openai import OpenAI

client = OpenAI()

# AIを使う/使わない（環境変数でOFFれる）
# 例: set EIGA_AI=0 で無効化
AI_ENABLED = os.getenv("EIGA_AI", "1") == "1"

# キャッシュ（同じ入力は再課金しない）
_cache = {}
CACHE_SECONDS = 7 * 24 * 60 * 60  # 7日

def _key(raw: str, cleaned: str) -> str:
    s = (raw or "") + "||" + (cleaned or "")
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def needs_ai(raw: str, cleaned: str) -> bool:
    """
    お主の正規表現/JSON-LD抽出が優秀なので、
    「怪しい時だけ」AIに回すゲート。
    """
    c = (cleaned or "").strip()
    r = (raw or "").strip()

    if not c:
        return True
    if len(c) < 2 or len(c) > 25:
        return True

    # ゴミ語が残ってるっぽい
    bad_words = ["レシピ", "作り方", "人気", "簡単", "献立", "材料", "手順", "動画", "おすすめ"]
    if any(w in c for w in bad_words):
        return True

    # 記号が残ってる/装飾っぽい
    bad_chars = ["|", "｜", "【", "】", "『", "』", "「", "」", "#", "★", "/", "／"]
    if any(ch in c for ch in bad_chars):
        return True

    # rawとの差が大きすぎる（切りすぎ/残りすぎの可能性）
    if r and (len(r) - len(c) > 35):
        return True

    return False

def ai_refine_dish_name(raw_title: str, cleaned_title: str) -> str:
    """
    raw/cleanedをもとに「料理名だけ」を1つ返す。
    ここで表記ゆれ（やきうどん→焼うどん）も寄せる。
    """
    if not AI_ENABLED:
        return (cleaned_title or "").strip()

    raw_title = (raw_title or "").strip()
    cleaned_title = (cleaned_title or "").strip()

    k = _key(raw_title, cleaned_title)
    now = time.time()

    if k in _cache:
        val, ts = _cache[k]
        if now - ts < CACHE_SECONDS:
            return val

    prompt = f"""
あなたはレシピ名の正規化担当です。
次の raw / cleaned を見て、最終的な「料理名」だけを1つ返してください。

条件:
- 出力は料理名のみ（説明禁止）
- サイト名、人名、【】、( )、人気/簡単/レシピ/作り方等は除去
- 表記ゆれは自然な料理名へ（例: やきうどん→焼うどん）
- 「〜のレシピ」「〜 作り方」などは料理名だけにする

raw: {raw_title}
cleaned: {cleaned_title}
""".strip()

    try:
        resp = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )
        out = resp.output[0].content[0].text.strip()
    except Exception:
        out = cleaned_title or raw_title

    # 最低限の保険：空ならcleanedへ
    if not out:
        out = cleaned_title or raw_title

    _cache[k] = (out, now)
    return out