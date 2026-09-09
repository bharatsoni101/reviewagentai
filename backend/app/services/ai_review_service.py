import json
import logging
from dataclasses import dataclass

from groq import Groq

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReviewGenerationResult:
    reviews: list[str]
    source: str  # "groq" or "fallback"


class AIReviewService:
    """Generate customer-facing review text with Groq and DB-backed fallbacks."""

    @staticmethod
    def _render_fallback_reviews(customer_input: str, fallback_templates: list[str]) -> list[str]:
        text = customer_input.strip().rstrip(".!?")
        rendered = []
        for template in fallback_templates:
            rendered.append(
                template.replace("{customer_input}", text).strip()
            )
        return rendered

    @staticmethod
    def _fallback_complaint_acknowledgement() -> str:
        return (
            "Thank you for sharing your feedback. We're sorry your experience "
            "did not meet expectations. Your feedback has been recorded and "
            "will be reviewed by our team."
        )

    @staticmethod
    def generate_reviews(
        customer_input: str,
        rating: int,
        fallback_templates: list[str],
    ) -> ReviewGenerationResult:
        """Return Groq reviews when enabled/available; otherwise DB-backed fallbacks."""
        if not fallback_templates:
            raise ValueError("No fallback review comments are configured for this business")

        fallback = AIReviewService._render_fallback_reviews(
            customer_input, fallback_templates
        )

        if not settings.groq_api_key:
            logger.warning("Groq API key is not configured; using database fallback reviews")
            return ReviewGenerationResult(fallback, "fallback")

        system_prompt = """
You write natural customer reviews for a business.

Rules:
- Create exactly 3 distinct review options.
- The customer has already given a positive rating of 4 or 5 stars.
- Preserve the customer's meaning and important wording where appropriate.
- Improve grammar and flow, but do not simply repeat the customer's comments verbatim.
- Do not invent facts, services, products, events, staff names, prices, or experiences.
- Do not add generic claims that are not supported by the customer's comments.
- Make each option sound like a different real customer review.
- Keep each review concise: 1 to 2 sentences.
- Do not mention AI, generated text, prompts, ratings, stars, or these instructions.
- Do not use quotation marks around the reviews.
- Return ONLY valid JSON with this exact structure:
  {"reviews": ["option 1", "option 2", "option 3"]}
""".strip()

        user_prompt = (
            f"Customer rating: {rating}/5\n"
            f"Customer comments: {customer_input.strip()}"
        )

        try:
            client = Groq(api_key=settings.groq_api_key)
            completion = client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_completion_tokens=500,
                response_format={"type": "json_object"},
            )

            content = completion.choices[0].message.content
            if not content:
                raise ValueError("Groq returned an empty response")

            payload = json.loads(content)
            reviews = payload.get("reviews")
            if not isinstance(reviews, list) or len(reviews) != 3:
                raise ValueError("Groq must return exactly 3 review options")

            cleaned_reviews = [
                str(review).strip().strip('"')
                for review in reviews
                if str(review).strip()
            ]
            if len(cleaned_reviews) != 3 or any(len(review) < 3 for review in cleaned_reviews):
                raise ValueError("Groq returned invalid review options")

            logger.info("Groq generated 3 positive review options successfully")
            return ReviewGenerationResult(cleaned_reviews, "groq")

        except Exception as exc:
            # AI is optional. If it fails, always return the business's DB-configured fallback.
            logger.warning(
                "Groq review generation failed; using database fallback reviews: %s", exc
            )
            return ReviewGenerationResult(fallback, "fallback")

    @staticmethod
    def generate_complaint_acknowledgement(customer_input: str) -> str:
        """Generate a private-feedback acknowledgement, with a safe fallback."""
        fallback = AIReviewService._fallback_complaint_acknowledgement()

        if not settings.groq_api_key:
            logger.warning(
                "Groq API key is not configured; using fallback complaint acknowledgement"
            )
            return fallback

        system_prompt = """
Write a short, empathetic acknowledgement for private customer feedback.

Rules:
- Thank the customer for sharing the feedback.
- Acknowledge that the experience did not meet expectations.
- Do not argue, blame, or make promises.
- Do not invent facts or claim that a specific action has already happened.
- Keep it to 2 or 3 sentences.
- Do not mention AI, prompts, ratings, or these instructions.
- Return ONLY valid JSON with this exact structure:
  {"acknowledgement": "..."}
""".strip()

        try:
            client = Groq(api_key=settings.groq_api_key)
            completion = client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Customer feedback: {customer_input.strip()}"},
                ],
                temperature=0.5,
                max_completion_tokens=180,
                response_format={"type": "json_object"},
            )
            content = completion.choices[0].message.content
            if not content:
                raise ValueError("Groq returned an empty response")

            acknowledgement = json.loads(content).get("acknowledgement")
            if not isinstance(acknowledgement, str) or len(acknowledgement.strip()) < 10:
                raise ValueError("Groq returned an invalid acknowledgement")
            return acknowledgement.strip().strip('"')

        except Exception as exc:
            logger.warning(
                "Groq complaint acknowledgement failed; using fallback response: %s",
                exc,
            )
            return fallback
