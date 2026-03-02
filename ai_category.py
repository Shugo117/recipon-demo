import os
import json
from typing import Optional, List, Dict

from openai import OpenAI


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def needs_ai_category(title: Optional[str]) -> bool:
    t = (title or "").strip()
    if not t:
        return False

    # 「ボール」「ボウル」だけAI判定
    return ("ボウル" in t) or ("ボール" in t)


def ai_suggest_categories(title: str, category_keys: List[str], top_k: int = 3) -> Optional[Dict[str, object]]:
    if not title:
        return None

    prompt = f"""あなたはレシピ分類アシスタントです。
次の料理名を、与えられたカテゴリの中から最も適切な候補を最大{top_k}個選んでください。

料理名: {title}

カテゴリ一覧:
{json.dumps(category_keys, ensure_ascii=False)}

出力は必ずJSONのみ。
形式:
{{"candidates":["カテゴリ1","カテゴリ2"],"reason":"短い理由（1文）"}}"""

    try:
        resp = client.responses.create(
            model="gpt-5.2",
            input=prompt,
        )
        text = (resp.output_text or "").strip()
        if not text:
            return None

        data = json.loads(text)
        cands = data.get("candidates")
        reason = data.get("reason")

        if not isinstance(cands, list) or not cands:
            return None

        keyset = set(category_keys)
        cleaned: List[str] = []
        for c in cands:
            if isinstance(c, str) and c in keyset and c not in cleaned:
                cleaned.append(c)

        if not cleaned:
            return None

        if not isinstance(reason, str):
            reason = ""

        return {"candidates": cleaned[:top_k], "reason": reason[:120]}

    except Exception:
        return None