from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import get_auth_context, require_roles
from app.models.enums import UserRole
from app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    AnswerEvaluationRequest,
    AnswerEvaluationResponse,
    QuestionGenerationRequest,
    QuestionGenerationResponse,
)
from app.services.generation_service import GenerationService


router = APIRouter(prefix="/ai", tags=["ai"])
manager_only = require_roles(UserRole.PROJECT_MANAGER)


@router.post("/questions/generate", response_model=QuestionGenerationResponse)
async def generate_questions(
    payload: QuestionGenerationRequest,
    _=Depends(manager_only),
) -> QuestionGenerationResponse:
    service = GenerationService()
    result = await service.generate_questions(
        jd=payload.jd,
        resume=payload.resume,
        stage=payload.stage,
        role_seniority=payload.role_seniority,
        previous_answers=payload.previous_answers,
        count=payload.count,
    )
    return QuestionGenerationResponse(
        questions=result.questions,
        engine=result.engine,
        fallback_used=result.fallback_used,
    )


@router.post("/answers/evaluate", response_model=AnswerEvaluationResponse)
async def evaluate_answer(
    payload: AnswerEvaluationRequest,
    _=Depends(manager_only),
) -> AnswerEvaluationResponse:
    service = GenerationService()
    result = await service.evaluate_answer(
        question=payload.question,
        answer=payload.answer,
        rubric=payload.rubric,
    )
    return AnswerEvaluationResponse(
        score=result.score,
        confidence=result.confidence,
        classification=result.classification,
        reasons=result.reasons,
        engine=result.engine,
        fallback_used=result.fallback_used,
    )


@router.post("/chat", response_model=AIChatResponse)
async def ai_chat(
    payload: AIChatRequest,
    auth=Depends(get_auth_context),
) -> AIChatResponse:
    """Conversational AI assistant for hiring managers and candidates.
    Accessible by both PM and CANDIDATE roles.
    """
    service = GenerationService()
    result = await service.chat(
        messages=[{"role": m.role, "content": m.content} for m in payload.messages],
        context=payload.context,
    )
    return AIChatResponse(
        reply=result.reply,
        engine=result.engine,
        fallback_used=result.fallback_used,
    )
