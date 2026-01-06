"""
AI Delay Risk Diagnosis API router.
Uses OpenAI API to analyze route data and provide insights.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import os
import httpx

# Load .env file
load_dotenv()

router = APIRouter()


class RouteSegment(BaseModel):
    railway: Optional[str] = None
    from_station: Optional[str] = None
    to_station: Optional[str] = None
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None

class DiagnosisRequest(BaseModel):
    segments: List[Dict[str, Any]]
    risk: Optional[Dict[str, Any]] = None
    crowd: Optional[Dict[str, Any]] = None
    venue_warnings: Optional[Dict[str, Any]] = None
    delay_warnings: Optional[List[Dict[str, Any]]] = None


@router.post("/diagnose")
async def diagnose_delay_risk(request: DiagnosisRequest):
    """
    Use AI to analyze route data and provide delay risk diagnosis.
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    # Build context from route data
    segments_text = []
    for seg in request.segments:
        railway = seg.get("railway", "不明")
        from_st = seg.get("from", "?")
        to_st = seg.get("to", "?")
        dep = seg.get("departure_time", "?")
        arr = seg.get("arrival_time", "?")
        segments_text.append(f"- {railway}: {from_st} ({dep}) → {to_st} ({arr})")
    
    route_info = "\n".join(segments_text)
    
    # Risk info
    risk_info = ""
    if request.risk and request.risk.get("reasons"):
        risk_level = request.risk.get("level", "LOW")
        reasons = request.risk.get("reasons", [])
        risk_info = f"\n\n【遅延リスク情報】レベル: {risk_level}\n"
        for r in reasons:
            railway = r.get("railway", "")
            rate = r.get("rate", r.get("display", ""))
            risk_info += f"- {railway}: {rate}\n"
    
    # Crowd info
    crowd_info = ""
    if request.crowd and request.crowd.get("level") != "UNKNOWN":
        crowd_level = request.crowd.get("level", "LOW")
        crowd_score = request.crowd.get("score", 0)
        crowd_info = f"\n\n【駅混雑度】平均乗降客数: {crowd_score:,}人/日 ({crowd_level})"
    
    # Venue warnings
    venue_info = ""
    if request.venue_warnings:
        transfers = request.venue_warnings.get("transfer_warnings", [])
        if transfers:
            venue_info = "\n\n【イベント情報】"
            for v in transfers:
                venue_info += f"\n- {v.get('station')}駅近くに{v.get('venue')} (収容: {v.get('capacity', 0):,}人)"
    
    # Delay warnings
    delay_info = ""
    if request.delay_warnings:
        delay_info = "\n\n【リアルタイム遅延】"
        for d in request.delay_warnings:
            delay_info += f"\n- {d.get('railway')}: {d.get('reason', '遅延中')}"
    
    # Determine risk level for prompt variation
    risk_level = request.risk.get("level", "LOW") if request.risk else "LOW"
    
    # Build different prompts based on risk level
    if risk_level == "HIGH":
        tone_instruction = """⚠️ 警告モード ⚠️
このルートは遅延リスクが高いです。ユーザーに注意を促し、代替案や対策を推奨してください。
トーンは緊急性を持たせつつ、具体的な対策を提示してください。"""
        format_instruction = """以下の形式で回答してください（Markdown形式）：
### ⚠️ 警告
（なぜこのルートが危険か、1-2文）

### 具体的リスク
- （箇条書き2-3個）

### 推奨対策
- （箇条書き2-3個、時間に余裕を持つ、代替ルートなど）"""
    
    elif risk_level == "MEDIUM":
        tone_instruction = """⚡ 注意モード ⚡
このルートには注意が必要です。リスクを認識しつつ、過度な心配は不要であることを伝えてください。
トーンは穏やかですが、念のための対策を提案してください。"""
        format_instruction = """以下の形式で回答してください（Markdown形式）：
### 💡 状況説明
（現状のリスクを簡潔に、1-2文）

### 気をつけるポイント
- （箇条書き2個）

### 念のための対策
- （箇条書き1-2個）"""
    
    else:  # LOW
        tone_instruction = """✅ 安心モード ✅
このルートは問題ありません！ユーザーを安心させ、快適な移動をサポートしてください。
トーンはポジティブで、安心感を与えてください。"""
        format_instruction = """以下の形式で回答してください（Markdown形式）：
### 状況
（問題ない旨を1文で）

### このルートの良い点
- （箇条書き1-2個）

### 快適に過ごすヒント
- （任意、1個）"""

    prompt = f"""{tone_instruction}

【経路情報】
{route_info}
{risk_info}{crowd_info}{venue_info}{delay_info}

{format_instruction}

回答は200文字以内で、実用的なアドバイスを心がけてください。
出力はMarkdown形式で、箇条書きは「-」を使用してください。セクション間の空行は最小限にしてください。"""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "あなたは日本の鉄道遅延リスクを分析する専門家です。簡潔で実用的なアドバイスを提供します。"},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 400,
                    "temperature": 0.7
                }
            )
            
            if response.status_code != 200:
                error_detail = response.json().get("error", {}).get("message", "Unknown error")
                raise HTTPException(status_code=response.status_code, detail=f"OpenAI API error: {error_detail}")
            
            result = response.json()
            diagnosis = result["choices"][0]["message"]["content"]
            
            return {
                "diagnosis": diagnosis,
                "model": "gpt-4o-mini"
            }
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI診断がタイムアウトしました")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI診断エラー: {str(e)}")
