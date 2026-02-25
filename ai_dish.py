# ai_dish.py
import os

# =========================
# AIスイッチ（今はOFF）
# =========================
AI_ENABLED = False  # ← ここをTrueに戻せば将来AI復活

# =========================
# 判定（今は常に使わない）
# =========================
def needs_ai(raw: str, cleaned: str) -> bool:
    return False


# =========================
# 補正（今はそのまま返す）
# =========================
def ai_refine_dish_name(raw_title: str, cleaned_title: str) -> str:
    """
    AIなしモード
    """
    return (cleaned_title or raw_title or "").strip()