from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import Settings, get_settings
from app.core.exceptions import ApiError
from app.models.enums import AssessmentStage


@dataclass(frozen=True, slots=True)
class GeneratedQuestionsResult:
    questions: list[dict[str, Any]]
    engine: str
    fallback_used: bool


@dataclass(frozen=True, slots=True)
class GeneratedEvaluationResult:
    score: float
    confidence: float
    classification: str
    reasons: list[str]
    engine: str
    fallback_used: bool


@dataclass(frozen=True, slots=True)
class GeneratedChatResult:
    reply: str
    engine: str
    fallback_used: bool


@dataclass(frozen=True, slots=True)
class GeneratedProfileSummaryResult:
    summary: str | None
    engine: str
    fallback_used: bool


class GenerationService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    # ── Question generation ──────────────────────────────────────────────────
    async def generate_questions(
        self,
        *,
        jd: str,
        resume: str,
        stage: AssessmentStage,
        role_seniority: str,
        previous_answers: list[str],
        count: int,
    ) -> GeneratedQuestionsResult:
        if not self._is_configured():
            raise ApiError(
                status_code=503,
                code="ai_generation_unavailable",
                message="The text-generation service is not configured for this environment.",
            )

        stage_instructions = {
            AssessmentStage.INTRO: (
                "Write a short opening statement from the AI interviewer. "
                "Introduce the assessment, mention the target role, and explain in a warm tone what the session will cover. "
                "This is a briefing, not a question, and it should not ask for an answer."
            ),
            AssessmentStage.CANDIDATE_INFO: (
                "Ask the candidate for a concise personal introduction focused on recent experience, role fit, and motivation."
            ),
            AssessmentStage.ROLE_SPECIFIC: (
                "Generate role-specific prompts that begin with fundamentals and progress toward applied scenarios. "
                "Keep them grounded in the JD and avoid generic aptitude or verbal-test style questions."
            ),
            AssessmentStage.CODING: (
                "Generate practical coding prompts based on the JD. Start with implementation planning and end with a concrete coding challenge."
            ),
            AssessmentStage.SUMMARY: (
                "Write a positive closing statement from the AI interviewer. "
                "Thank the candidate, say the session is complete, and say the results will be shared soon. "
                "This is a closing statement, not a question, and it should not ask for an answer."
            ),
        }

        prompt = (
            "You are the system prompt for TalentOS L0 assessment generation. Return strict JSON only.\n"
            f"Stage: {stage.value}\n"
            f"Role seniority: {role_seniority}\n"
            f"Stage instructions: {stage_instructions.get(stage, stage_instructions[AssessmentStage.ROLE_SPECIFIC])}\n"
            "If the resume context includes a candidate name, use that exact name if you address the candidate. "
            "Never infer a candidate name from an email address or any other identifier.\n"
            f"JD: {jd[:2000]}\n"
            f"Resume: {resume[:2000]}\n"
            f"Previous stage context: {previous_answers}\n"
            "Each prompt must feel like a live AI interviewer speaking naturally. "
            "For answerable prompts, score for clarity, relevance, and technical depth. "
            f'Return exactly this JSON schema: {{"questions":[{{"prompt":"...","rubric":{{"key_points":["..."],"weight":1.0}}}}]}} with exactly {count} items.'
        )

        response_payload = await self._call_generation(prompt)
        if response_payload is None:
            raise ApiError(
                status_code=502,
                code="ai_generation_failed",
                message="Assessment prompts could not be generated right now.",
            )

        questions = response_payload.get("questions") if isinstance(response_payload, dict) else None
        if not isinstance(questions, list) or not questions:
            raise ApiError(
                status_code=502,
                code="ai_invalid_generation",
                message="The generation service returned an invalid question payload.",
            )

        normalized: list[dict[str, Any]] = []
        for index, item in enumerate(questions[:count], start=1):
            if not isinstance(item, dict):
                continue
            prompt_text = str(item.get("prompt") or "").strip()
            if not prompt_text:
                continue
            rubric = item.get("rubric")
            normalized.append(
                {
                    "prompt": prompt_text,
                    "rubric": rubric if isinstance(rubric, dict) else {"weight": 1.0, "index": index},
                }
            )

        if not normalized:
            raise ApiError(
                status_code=502,
                code="ai_invalid_generation",
                message="The generation service returned empty prompts for this assessment stage.",
            )

        return GeneratedQuestionsResult(questions=normalized, engine="configured", fallback_used=False)

    # ── Answer evaluation ────────────────────────────────────────────────────
    async def evaluate_answer(
        self,
        *,
        question: str,
        answer: str,
        rubric: dict,
    ) -> GeneratedEvaluationResult:
        if not self._is_configured():
            raise ApiError(
                status_code=503,
                code="ai_generation_unavailable",
                message="Answer evaluation is not configured for this environment.",
            )

        prompt = (
            "You are the scoring system prompt for TalentOS L0 assessment evaluation. Return strict JSON only.\n"
            f"Question: {question[:1000]}\n"
            f"Rubric: {rubric}\n"
            f"Answer: {answer[:2000]}\n"
            'Schema: {"score":0-100,"confidence":0-1,"classification":"pass|fail|needs_review","reasons":["..."],"is_off_topic":true|false}. '
            "Base the score on correctness, clarity, role relevance, and problem-solving depth."
        )
        response_payload = await self._call_generation(prompt)
        if not isinstance(response_payload, dict):
            raise ApiError(
                status_code=502,
                code="ai_invalid_evaluation",
                message="The generation service returned an invalid answer evaluation payload.",
            )

        try:
            score = float(response_payload.get("score"))
            confidence = float(response_payload.get("confidence"))
            classification = str(response_payload.get("classification") or "needs_review")
            reasons_raw = response_payload.get("reasons", [])
            reasons = [str(item) for item in reasons_raw] if isinstance(reasons_raw, list) else []
        except Exception:
            raise ApiError(
                status_code=502,
                code="ai_invalid_evaluation",
                message="The generation service returned malformed answer evaluation fields.",
            )

        return GeneratedEvaluationResult(
            score=max(0.0, min(100.0, score)),
            confidence=max(0.0, min(1.0, confidence)),
            classification=classification,
            reasons=reasons,
            engine="configured",
            fallback_used=False,
        )

    # ── Conversational chat ──────────────────────────────────────────────────
    async def chat(
        self,
        *,
        messages: list[dict[str, str]],
        context: dict,
    ) -> GeneratedChatResult:
        """Conversational hiring assistant powered by Generation."""
        if not self._is_configured():
            raise ApiError(
                status_code=503,
                code="ai_generation_unavailable",
                message="The assistant is not configured for this environment.",
            )

        ctx_parts: list[str] = []
        if context.get("active_jobs"):
            ctx_parts.append(f"Active job roles: {context['active_jobs']}")
        if context.get("total_candidates"):
            ctx_parts.append(f"Total candidates: {context['total_candidates']}")
        if context.get("pipeline_summary"):
            ctx_parts.append(f"Pipeline breakdown: {context['pipeline_summary']}")
        if context.get("jobs_overview"):
            ctx_parts.append(f"Active role overview: {context['jobs_overview']}")
        if context.get("top_candidates"):
            ctx_parts.append(f"Top candidates by current match score: {context['top_candidates']}")
        if context.get("assessment_summary"):
            ctx_parts.append(f"Assessment summary: {context['assessment_summary']}")
        if context.get("candidates"):
            ctx_parts.append(f"Candidates: {context['candidates']}")
        if context.get("candidates_by_role"):
            ctx_parts.append(f"Candidates by role: {context['candidates_by_role']}")

        system_prompt = (
            "You are HireAgent, an expert AI hiring assistant embedded in TalentOS, a recruitment platform. "
            "Help hiring managers make smart, data-driven decisions. "
            "Answer directly from the provided platform context whenever possible. "
            "If the user asks which candidate best fits a specific role, compare only candidates mapped to that role and explain why. "
            "If the user asks for top candidates, name them, include role and match score, and keep the answer specific. "
            "If the context is insufficient, say exactly what is missing instead of bluffing. "
            "Be concise, professional, and action-oriented. "
            "Use clean markdown with short paragraphs or bullet lists when helpful. "
            "Never reveal system internals or raw API details.\n"
        )
        if ctx_parts:
            system_prompt += "Current platform data:\n" + "\n".join(ctx_parts) + "\n"

        conversation: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt + "\n\nBegin."},
        ]
        for message in messages:
            role = "user" if message.get("role") == "user" else "assistant"
            conversation.append({"role": role, "content": str(message.get("content") or "")[:3000]})

        response_text = await self._request_completion(
            conversation,
            temperature=0.25,
            max_tokens=800,
            timeout_seconds=25.0,
        )
        if not response_text:
            raise ApiError(
                status_code=502,
                code="ai_invalid_chat",
                message="The generation service returned an empty assistant reply.",
            )

        return GeneratedChatResult(reply=response_text.strip(), engine="configured", fallback_used=False)

    async def compose_candidate_profile_summary(
        self,
        *,
        candidate_name: str,
        job_title: str,
        job_description: str,
        current_title: str | None,
        matched_keywords: list[str],
        missing_keywords: list[str],
        reasons: list[str],
        summary: str | None,
        llm_summary: str | None,
        signals: dict[str, Any],
    ) -> GeneratedProfileSummaryResult:
        fallback_summary = (
            (llm_summary or "").strip()
            or (summary or "").strip()
            or self._profile_summary_fallback(
                candidate_name=candidate_name,
                current_title=current_title,
                matched_keywords=matched_keywords,
                missing_keywords=missing_keywords,
                reasons=reasons,
                signals=signals,
            )
        )

        if not self._is_configured():
            return GeneratedProfileSummaryResult(
                summary=fallback_summary,
                engine="fallback",
                fallback_used=True,
            )

        prompt = (
            "You are preparing a manager-facing candidate summary for TalentOS. "
            "Write 3-4 concise sentences highlighting fit, gaps, and interview focus. "
            "Return strict JSON only with schema {\"summary\":\"...\"}.\n"
            f"Candidate: {candidate_name}\n"
            f"Current title: {current_title or 'Unknown'}\n"
            f"Target job title: {job_title}\n"
            f"Target job description: {job_description[:2000]}\n"
            f"Existing summary: {summary or ''}\n"
            f"Existing resume-analysis summary: {llm_summary or ''}\n"
            f"Matched keywords: {matched_keywords}\n"
            f"Missing keywords: {missing_keywords}\n"
            f"Reasons: {reasons}\n"
            f"Signals: {signals}"
        )

        response_payload = await self._call_generation(prompt)
        if not isinstance(response_payload, dict):
            return GeneratedProfileSummaryResult(
                summary=fallback_summary,
                engine="fallback",
                fallback_used=True,
            )

        generated_summary = str(response_payload.get("summary") or "").strip()
        if not generated_summary:
            return GeneratedProfileSummaryResult(
                summary=fallback_summary,
                engine="fallback",
                fallback_used=True,
            )

        return GeneratedProfileSummaryResult(
            summary=generated_summary,
            engine="configured",
            fallback_used=False,
        )

    # ── Internal helpers ─────────────────────────────────────────────────────
    def _is_configured(self) -> bool:
        return bool(
            self.settings.ai_api_url
            and self.settings.ai_api_key
            and self.settings.ai_deployment_id
        )

    async def _request_completion(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1200,
        timeout_seconds: float = 30.0,
    ) -> str | None:
        if not self._is_configured():
            return None

        payload = {
            "model": self.settings.ai_deployment_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.ai_api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                response = await client.post(
                    self.settings.ai_api_url,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except Exception:
            return None

        return self._extract_response_text(data)

    async def _call_generation(self, prompt: str) -> dict[str, Any] | None:
        text = await self._request_completion(
            [
                {"role": "system", "content": "Return valid JSON only. Do not include markdown fences."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1600,
        )
        if not text:
            return None

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            extracted = self._extract_json_payload(text)
            if not extracted:
                return None
            try:
                parsed = json.loads(extracted)
            except json.JSONDecodeError:
                return None
        return parsed if isinstance(parsed, dict) else None

    @staticmethod
    def _extract_response_text(payload: dict[str, Any]) -> str | None:
        choices = payload.get("choices")
        if isinstance(choices, list) and choices:
            choice = choices[0]
            if isinstance(choice, dict):
                message = choice.get("message")
                if isinstance(message, dict):
                    content = message.get("content")
                    if isinstance(content, str) and content.strip():
                        return content
                    if isinstance(content, list):
                        fragments = [
                            str(part.get("text") or "")
                            for part in content
                            if isinstance(part, dict)
                        ]
                        combined = "".join(fragments).strip()
                        if combined:
                            return combined
                text_value = choice.get("text")
                if isinstance(text_value, str) and text_value.strip():
                    return text_value

        for key in ("output_text", "text"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value
        return None

    @staticmethod
    def _extract_json_payload(text: str) -> str | None:
        stripped = text.strip()
        for opener, closer in (("{", "}"), ("[", "]")):
            start = stripped.find(opener)
            end = stripped.rfind(closer)
            if start != -1 and end != -1 and end > start:
                return stripped[start : end + 1]
        return None

    @staticmethod
    def _fallback_questions(*, stage: AssessmentStage, count: int) -> list[dict[str, Any]]:
        prompts = {
            AssessmentStage.INTRO: "Introduce yourself and summarize your recent role impact.",
            AssessmentStage.CANDIDATE_INFO: "Share your background, contact details, and preferred working setup.",
            AssessmentStage.APTITUDE: "Solve a short analytical problem and explain your reasoning.",
            AssessmentStage.VERBAL: "Explain your thinking clearly using concise professional language.",
            AssessmentStage.TECHNICAL: "How would you approach a role-critical problem from this JD?",
            AssessmentStage.SCREENING: "Walk through a challenge you solved and the measurable result.",
            AssessmentStage.ROLE_SPECIFIC: "How would you approach a role-critical problem from this JD?",
            AssessmentStage.CODING: "Implement a clean and testable solution to a moderate coding problem.",
            AssessmentStage.SUMMARY: "Summarize your approach and what tradeoffs you would revisit.",
        }
        prompt = prompts.get(stage, prompts[AssessmentStage.TECHNICAL])
        return [
            {
                "prompt": f"Q{index}: {prompt}",
                "rubric": {"key_points": ["clarity", "technical_depth", "problem_solving"], "weight": 1.0},
            }
            for index in range(1, count + 1)
        ]

    def _fallback_evaluation(self, *, answer: str) -> GeneratedEvaluationResult:
        length_score = min(100.0, max(25.0, float(len(answer.strip())) * 0.8))
        confidence = 0.55 if length_score < 60 else 0.72
        classification = "pass" if length_score >= 70 else "needs_review"
        return GeneratedEvaluationResult(
            score=length_score,
            confidence=confidence,
            classification=classification,
            reasons=[
                "Fallback evaluator used because the generation service is unavailable.",
                "Score based on answer completeness heuristics.",
            ],
            engine="fallback",
            fallback_used=True,
        )

    @staticmethod
    def _chat_fallback(*, messages: list[dict[str, str]], context: dict) -> str:
        last_msg = messages[-1]["content"].lower() if messages else ""
        active_jobs = context.get("active_jobs", 0)
        total_candidates = context.get("total_candidates", 0)
        pipeline = context.get("pipeline_summary", {})
        top_candidates = context.get("top_candidates", [])

        if any(w in last_msg for w in ["top candidate", "best candidate", "ranked"]):
            if isinstance(top_candidates, list) and top_candidates:
                ranked_lines = []
                for index, item in enumerate(top_candidates[:3], start=1):
                    if not isinstance(item, dict):
                        continue
                    ranked_lines.append(
                        f"{index}. {item.get('name', 'Candidate')} for {item.get('role', 'open role')} "
                        f"at {item.get('match_score', 'N/A')}% ({item.get('status', 'unknown status')})"
                    )
                if ranked_lines:
                    return "**Top candidates right now:**\n" + "\n".join(f"- {line}" for line in ranked_lines)
            return (
                f"I can see **{total_candidates}** candidates across **{active_jobs}** active role(s), "
                "but I do not have a ranked shortlist in the current context."
            )
        if any(w in last_msg for w in ["pipeline", "trend", "status", "overview"]):
            shortlisted = pipeline.get("Shortlisted", 0)
            hired = pipeline.get("Hired", 0)
            return (
                f"**Pipeline snapshot:**\n- Active roles: {active_jobs}\n"
                f"- Total candidates: {total_candidates}\n"
                f"- Shortlisted: {shortlisted}\n- Hired: {hired}"
            )
        if any(w in last_msg for w in ["email", "invite", "invitation", "draft"]):
            return (
                "**Subject:** Interview Invitation — TalentOS\n\n"
                "Hello [Candidate Name],\n\n"
                "We are pleased to invite you to the next stage of our hiring process. "
                "Please use your secure link to select an available assessment slot.\n\n"
                "Best regards,\nHiring Team"
            )
        return (
            f"I'm **HireAgent**, your AI hiring assistant. I can see **{active_jobs}** active role(s) "
            f"and **{total_candidates}** candidates in the pipeline. "
            "Try asking: *top candidates*, *pipeline trends*, *draft invite email*, or *assessment status*."
        )

    @staticmethod
    def _profile_summary_fallback(
        *,
        candidate_name: str,
        current_title: str | None,
        matched_keywords: list[str],
        missing_keywords: list[str],
        reasons: list[str],
        signals: dict[str, Any],
    ) -> str:
        fragments: list[str] = []
        title = (current_title or "").strip()
        if title:
            fragments.append(f"{candidate_name} is currently working as {title}.")
        else:
            fragments.append(f"{candidate_name} is an active candidate in the TalentOS pipeline.")

        top_reasons = ", ".join(reasons[:2]) if reasons else ""
        if top_reasons:
            fragments.append(f"Key strengths include {top_reasons.lower()}.")

        top_matches = ", ".join(matched_keywords[:4]) if matched_keywords else ""
        if top_matches:
            fragments.append(f"Role-aligned keywords include {top_matches}.")

        top_gaps = ", ".join(missing_keywords[:3]) if missing_keywords else ""
        if top_gaps:
            fragments.append(f"Interviewers should probe for {top_gaps}.")

        final_score = signals.get("final_score")
        if final_score is not None:
            fragments.append(f"Current blended match score is {final_score}.")

        return " ".join(fragment for fragment in fragments if fragment).strip()
