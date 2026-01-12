"""
AI Delay Risk Diagnosis API router.
Uses OpenAI API to analyze route data and provide insights.
"""
from fastapi import APIRouter, HTTPException
import httpx

from core.config import OPENAI_API_KEY, OPENAI_API_URL
from core.http_client import build_auth_header, OPENAI_TIMEOUT
from schemas.ai import DiagnosisRequest, DiagnosisResponse
from templates.ai_prompts import SYSTEM_PROMPT, build_diagnosis_prompt

router = APIRouter()


def _build_context_from_request(request: DiagnosisRequest) -> tuple[str, str, str, str, str, str]:
    """
    Extract and format context information from the diagnosis request.
    
    Returns:
        Tuple of (route_info, risk_info, crowd_info, venue_info, delay_info, risk_level)
    """
    # Build route segments text
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
    risk_level = "LOW"
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
    
    return route_info, risk_info, crowd_info, venue_info, delay_info, risk_level


@router.post("/diagnose")
async def diagnose_delay_risk(request: DiagnosisRequest):
    """
    Use AI to analyze route data and provide delay risk diagnosis.
    """
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    # Build context from request
    route_info, risk_info, crowd_info, venue_info, delay_info, risk_level = \
        _build_context_from_request(request)
    
    # Build prompt using template
    prompt = build_diagnosis_prompt(
        route_info=route_info,
        risk_info=risk_info,
        crowd_info=crowd_info,
        venue_info=venue_info,
        delay_info=delay_info,
        risk_level=risk_level
    )

    try:
        async with httpx.AsyncClient(timeout=OPENAI_TIMEOUT) as client:
            response = await client.post(
                OPENAI_API_URL,
                headers=build_auth_header(OPENAI_API_KEY),
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
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
            
            return DiagnosisResponse(
                diagnosis=diagnosis,
                model="gpt-4o-mini"
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI診断がタイムアウトしました")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI診断エラー: {str(e)}")
