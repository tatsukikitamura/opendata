"""
AI prompt templates for delay risk diagnosis.

Separates prompt content from business logic for easier maintenance.
"""

# ==============================================================================
# System Prompt
# ==============================================================================
SYSTEM_PROMPT = "あなたは日本の鉄道遅延リスクを分析する専門家です。簡潔で実用的なアドバイスを提供します。"


# ==============================================================================
# Risk Level Prompts
# ==============================================================================

HIGH_RISK_TONE = """⚠️ 警告モード ⚠️
このルートは遅延リスクが高いです。ユーザーに注意を促し、代替案や対策を推奨してください。
トーンは緊急性を持たせつつ、具体的な対策を提示してください。"""

HIGH_RISK_FORMAT = """以下の形式で回答してください（Markdown形式）：
### ⚠️ 警告
（なぜこのルートが危険か、1-2文）

### 具体的リスク
- （箇条書き2-3個）

### 推奨対策
- （箇条書き2-3個、時間に余裕を持つ、代替ルートなど）"""


MEDIUM_RISK_TONE = """⚡ 注意モード ⚡
このルートには注意が必要です。リスクを認識しつつ、過度な心配は不要であることを伝えてください。
トーンは穏やかですが、念のための対策を提案してください。"""

MEDIUM_RISK_FORMAT = """以下の形式で回答してください（Markdown形式）：
### 💡 状況説明
（現状のリスクを簡潔に、1-2文）

### 気をつけるポイント
- （箇条書き2個）

### 念のための対策
- （箇条書き1-2個）"""


LOW_RISK_TONE = """✅ 安心モード ✅
このルートは問題ありません！ユーザーを安心させ、快適な移動をサポートしてください。
トーンはポジティブで、安心感を与えてください。"""

LOW_RISK_FORMAT = """以下の形式で回答してください（Markdown形式）：
### 状況
（問題ない旨を1文で）

### このルートの良い点
- （箇条書き1-2個）

### 快適に過ごすヒント
- （任意、1個）"""


# ==============================================================================
# Prompt Builder
# ==============================================================================

def get_prompt_by_risk_level(risk_level: str) -> tuple[str, str]:
    """
    Get tone and format instructions based on risk level.
    
    Args:
        risk_level: "HIGH", "MEDIUM", or "LOW"
    
    Returns:
        Tuple of (tone_instruction, format_instruction)
    """
    if risk_level == "HIGH":
        return HIGH_RISK_TONE, HIGH_RISK_FORMAT
    elif risk_level == "MEDIUM":
        return MEDIUM_RISK_TONE, MEDIUM_RISK_FORMAT
    else:  # LOW or default
        return LOW_RISK_TONE, LOW_RISK_FORMAT


def build_diagnosis_prompt(
    route_info: str,
    risk_info: str = "",
    crowd_info: str = "",
    venue_info: str = "",
    delay_info: str = "",
    risk_level: str = "LOW"
) -> str:
    """
    Build the complete diagnosis prompt.
    
    Args:
        route_info: Formatted route segments text
        risk_info: Risk level and reasons text
        crowd_info: Station crowdedness text
        venue_info: Nearby venue warnings text
        delay_info: Real-time delay information text
        risk_level: "HIGH", "MEDIUM", or "LOW"
    
    Returns:
        Complete prompt string
    """
    tone_instruction, format_instruction = get_prompt_by_risk_level(risk_level)
    
    return f"""{tone_instruction}

【経路情報】
{route_info}
{risk_info}{crowd_info}{venue_info}{delay_info}

{format_instruction}

回答は200文字以内で、実用的なアドバイスを心がけてください。
出力はMarkdown形式で、箇条書きは「-」を使用してください。セクション間の空行は最小限にしてください。"""
