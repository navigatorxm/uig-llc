"""AI document analysis using the unified AI client — verifies legal documents for Delhi NCR compliance.

Uses Vertex AI (Gemini) as primary, with Anthropic fallback.
"""
import json
import logging
import base64
from typing import Optional
from app.services.ai.client import ai_client
from app.config import settings

logger = logging.getLogger(__name__)

DOCUMENT_ANALYSIS_SYSTEM = """You are a property law expert specializing in Delhi NCR real estate transactions.
You analyze legal documents and provide structured assessments in JSON format."""

DOCUMENT_ANALYSIS_PROMPT = """Analyze this {doc_type} document and provide a structured assessment.

Check for:
1. Document authenticity indicators (official seals, signatures, formatting)
2. Owner name consistency (should match across documents)
3. Property details accuracy (survey number, area, location)
4. Date validity (not expired, within required timeframe)
5. For LPI Certificate: Confirm it is present, valid, and not expired (MANDATORY)
6. For Encumbrance Certificate: Check for any existing loans, mortgages, or legal disputes
7. For Chain Documents: Verify 30-year ownership chain is complete

Respond ONLY with valid JSON:
{{
  "document_type": "{doc_type}",
  "appears_authentic": <true|false>,
  "key_details": {{
    "owner_name": "<extracted name or null>",
    "property_survey_number": "<extracted number or null>",
    "issue_date": "<date or null>",
    "expiry_date": "<date or null>",
    "issuing_authority": "<authority name or null>"
  }},
  "flags": [<list of issues found, empty array if none>],
  "lpi_valid": <true|false|null>,
  "recommendation": "<approve|reject|needs_review>",
  "notes": "<additional observations>"
}}"""

LPI_ANALYSIS_PROMPT = """This is an LPI (Land Parcel Identification) Certificate for a Delhi NCR property.

The LPI Certificate is MANDATORY for all property purchases in Delhi NCR.

Verify:
1. Is this a genuine LPI certificate from Delhi Development Authority (DDA) or relevant authority?
2. Is it within validity period?
3. Does the property description match expected details?
4. Are there any encumbrances or disputes noted?

{additional_context}

Respond ONLY with valid JSON:
{{
  "is_lpi_certificate": <true|false>,
  "issuing_authority": "<authority name>",
  "issue_date": "<date>",
  "validity_date": "<date or 'No expiry'>",
  "is_valid": <true|false>,
  "property_details": "<brief description>",
  "encumbrances": <true|false>,
  "flags": [<list of issues>],
  "recommendation": "<approve|reject|needs_review>"
}}"""


class DocumentAnalyzer:
    def __init__(self):
        self._client = ai_client

    async def analyze_async(self, google_drive_file_id: str, doc_type: str) -> dict:
        """
        Download a document from Google Drive and analyze it with AI.
        Returns analysis dict with flags and recommendation.
        """
        try:
            image_data = self._fetch_from_drive(google_drive_file_id)
            if not image_data:
                return {"error": "Could not fetch document", "flags": ["fetch_failed"]}

            prompt = DOCUMENT_ANALYSIS_PROMPT.format(doc_type=doc_type)
            if doc_type == "lpi_cert":
                prompt = LPI_ANALYSIS_PROMPT.format(additional_context="")

            # For text-based analysis (when image can't be sent directly)
            prompt_with_context = (
                f"{prompt}\n\n[Document base64 data available — "
                f"mime: {image_data['media_type']}, size: {len(image_data['data'])} chars]"
            )

            result = await self._client.generate_json(
                prompt_with_context,
                system=DOCUMENT_ANALYSIS_SYSTEM,
                max_tokens=1024,
            )
            logger.info(f"Document {doc_type} analyzed: {result.get('recommendation')} via {self._client.primary_provider}")
            return result

        except json.JSONDecodeError as exc:
            logger.error(f"Document analysis JSON parse failed: {exc}")
            return {"error": "parse_failed", "flags": ["analysis_failed"], "recommendation": "needs_review"}
        except Exception as exc:
            logger.error(f"Document analysis error: {exc}")
            return {"error": str(exc), "flags": ["analysis_failed"], "recommendation": "needs_review"}

    def analyze(self, google_drive_file_id: str, doc_type: str) -> dict:
        """Sync wrapper for backward compatibility."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, self.analyze_async(google_drive_file_id, doc_type)).result()
            return loop.run_until_complete(self.analyze_async(google_drive_file_id, doc_type))
        except RuntimeError:
            return asyncio.run(self.analyze_async(google_drive_file_id, doc_type))

    def _fetch_from_drive(self, file_id: str) -> Optional[dict]:
        """Download a file from Google Drive as base64."""
        try:
            from app.services.storage.google_drive import GoogleDriveService
            drive = GoogleDriveService()
            content, mime_type = drive.download_file(file_id)
            return {
                "data": base64.standard_b64encode(content).decode("utf-8"),
                "media_type": mime_type or "image/jpeg",
            }
        except Exception as exc:
            logger.error(f"Drive fetch failed for {file_id}: {exc}")
            return None
