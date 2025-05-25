"""Simplified competitor and opportunity analysis service."""

import uuid
from typing import List, Dict, Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai_service import AIService


class AnalysisService:
    """Service layer for competitor and opportunity analysis."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIService()

    async def validate_document_access(self, user_id: UUID, document_ids: List[UUID]) -> List[UUID]:
        """Placeholder that simply returns provided document IDs."""
        return document_ids

    async def analyze_competitors(
        self,
        user_id: UUID,
        document_ids: List[UUID],
        competitors: List[str],
        analysis_type: str = "positioning",
    ) -> Dict[str, Any]:
        """Very simple competitor analysis based on document text."""
        await self.ai_service.initialize()

        combined_text = ""
        for doc_id in document_ids:
            content = await self.ai_service.get_document_content(doc_id)
            if content:
                combined_text += " " + content.get("text", "")

        text_lower = combined_text.lower()
        competitor_results = []
        for name in competitors:
            lower = name.lower()
            mentions = text_lower.count(lower)
            snippet = None
            if mentions:
                idx = text_lower.find(lower)
                snippet = combined_text[max(0, idx - 50) : idx + 50]
            competitor_results.append({
                "name": name,
                "mentions": mentions,
                "snippet": snippet,
            })

        analysis = {
            "competitive_landscape": f"{sum(1 for r in competitor_results if r['mentions'] > 0)} of {len(competitors)} competitors mentioned",
            "analysis_type": analysis_type,
            "recommendations": [
                f"Research {r['name']}" for r in competitor_results if r["mentions"] == 0
            ],
        }

        return {"analysis": analysis, "competitors": competitor_results}

    async def identify_opportunities(
        self,
        user_id: UUID,
        document_ids: List[UUID],
        market_context: Optional[str] = None,
        analysis_depth: str = "basic",
    ) -> Dict[str, Any]:
        """Extract simple opportunity statements from document text."""
        await self.ai_service.initialize()

        combined_text = ""
        for doc_id in document_ids:
            content = await self.ai_service.get_document_content(doc_id)
            if content:
                combined_text += " " + content.get("text", "")

        import re

        sentences = re.split(r"[.!?]\s+", combined_text)
        keywords = ["opportunity", "trend", "gap", "growth", "demand", "innovation"]
        opportunities = []
        for sentence in sentences:
            lower = sentence.lower()
            if any(k in lower for k in keywords):
                title = " ".join(sentence.strip().split()[:5])
                opportunities.append({
                    "type": "text_insight",
                    "title": title,
                    "description": sentence.strip(),
                    "potential_impact": "medium",
                    "implementation_complexity": "medium",
                    "timeline": "6-12 months",
                })

        seen = set()
        unique_ops = []
        for opp in opportunities:
            if opp["title"] not in seen:
                seen.add(opp["title"])
                unique_ops.append(opp)

        recommendations = [f"Explore {opp['title']}" for opp in unique_ops[:3]]

        return {
            "opportunities": unique_ops,
            "strategic_recommendations": recommendations,
            "analysis_depth": analysis_depth,
            "market_context": market_context,
        }
