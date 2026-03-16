import json
import logging
from openai import OpenAI
from settings.pydantic_config import settings

_log = logging.getLogger(__name__)

# Maximum characters to include in the AI prompt.
# SVM support_vectors_.tolist() can produce 100k+ characters; truncating
# prevents Groq 400 errors caused by oversized messages content.
_MAX_SUMMARY_CHARS = 4000


def _summarise_for_prompt(summary) -> str:
    """
    Convert the analysis summary dict to a concise string safe for the AI prompt.
    Strips large arrays (support vectors, raw data) that blow up the prompt size.
    """
    if summary is None:
        return "No summary available."

    if isinstance(summary, str):
        return summary[:_MAX_SUMMARY_CHARS]

    if not isinstance(summary, dict):
        return str(summary)[:_MAX_SUMMARY_CHARS]

    # Build a clean copy without large array fields
    _LARGE_KEYS = frozenset({
        "support_vectors", "head", "value_counts", "correlation_matrix",
        "visualizations", "data_types",
    })
    clean = {}
    for k, v in summary.items():
        if k in _LARGE_KEYS:
            continue
        if isinstance(v, list) and len(v) > 20:
            clean[k] = f"[{len(v)} items — truncated]"
        elif isinstance(v, dict):
            # Recurse one level to strip nested large arrays
            inner = {
                ik: (f"[{len(iv)} items — truncated]"
                     if isinstance(iv, list) and len(iv) > 20
                     else iv)
                for ik, iv in v.items()
                if ik not in _LARGE_KEYS
            }
            clean[k] = inner
        else:
            clean[k] = v

    try:
        text = json.dumps(clean, default=str)
    except Exception:
        text = str(clean)

    return text[:_MAX_SUMMARY_CHARS]


def interpret_result_with_ai(summary_text) -> str | None:
    """
    Generate a plain-language AI report from the analysis summary.

    Returns None (never raises) if:
    - GROQ_API_KEY is not set or is a placeholder
    - The Groq / AI API call fails for any reason
    - The summary is empty

    The caller (crud.create_report) wraps this in try/except as a second
    safety net, but this function itself also never raises.
    """
    # Check API key is configured
    api_key = getattr(settings, "GROQ_API_KEY", None)
    if not api_key or not api_key.strip() or api_key.lower().startswith("your_"):
        _log.debug("GROQ_API_KEY not configured — skipping AI report.")
        return None

    prompt_text = _summarise_for_prompt(summary_text)
    if not prompt_text or not prompt_text.strip():
        return None

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant for business teams. "
                        "Generate simple, easy-to-understand summaries of data "
                        "insights, suitable for presentations or dashboards. "
                        "Avoid jargon. Keep your response to 3-5 sentences."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Here are the analysis results:\n{prompt_text}",
                },
            ],
            stream=False,
        )

        return response.choices[0].message.content

    except Exception as exc:
        _log.warning(
            "interpret_result_with_ai failed: %s: %s",
            type(exc).__name__, exc,
        )
        return None
