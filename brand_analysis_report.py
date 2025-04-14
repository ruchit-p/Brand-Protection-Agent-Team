"""
Brand Analysis Report Generator

This module generates standardized, analytical brand infringement reports
with a structured format and numerical scoring system.
"""

import os
import json
import datetime
from typing import Dict, List, Any, Optional
from agno.tools import Toolkit

class BrandAnalysisReportGenerator(Toolkit):
    """
    Toolkit for generating standardized brand infringement analysis reports.
    """

    def __init__(self, storage_dir: str):
        """
        Initialize the Brand Analysis Report Generator.
        
        Args:
            storage_dir: Directory to store generated reports
        """
        super().__init__(name="brand_analysis_report_generator")
        self.storage_dir = storage_dir
        
        # Register the report generation function
        self.register(self.generate_brand_report)
        self.register(self.calculate_infringement_score)
    
    def generate_brand_report(self, 
                             original_brand: str,
                             original_url: str,
                             suspected_url: str,
                             text_analysis: Dict[str, Any],
                             visual_analysis: Dict[str, Any],
                             additional_evidence: Optional[str] = None,
                             custom_filename: Optional[str] = None) -> str:
        """
        Generate a comprehensive brand infringement analysis report with zero-trust approach.
        
        Args:
            original_brand: Name of the original brand
            original_url: URL of the original brand's website
            suspected_url: URL of the suspected infringing website
            text_analysis: Dictionary containing text analysis data
            visual_analysis: Dictionary containing visual analysis data
            additional_evidence: Optional additional evidence or notes
            custom_filename: Optional custom filename for the report
            
        Returns:
            Path to the generated report file
        """
        # Calculate the infringement score using the zero-trust approach
        score_data = self.calculate_infringement_score(
            text_similarity=text_analysis.get("similarity_score", 0),
            visual_similarity=visual_analysis.get("similarity_score", 0),
            brand_mentions=text_analysis.get("brand_mentions", 0),
            logo_usage=visual_analysis.get("logo_present", False),
            product_similarity=visual_analysis.get("product_similarity", 0)
        )
        
        infringement_score = score_data.get("overall_score", 0)
        score_breakdown = score_data.get("score_breakdown", {})
        evidence_thresholds = score_data.get("evidence_thresholds", {})
        
        # Get current date for the report
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Create standardized report structure with zero-trust language
        report = f"""
# BRAND PROTECTION ANALYSIS REPORT (ZERO-TRUST APPROACH)

**CASE ID:** {original_brand.upper()}-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}  
**DATE:** {current_date}  
**ANALYST:** Brand Protection AI System  

## 1. EXECUTIVE SUMMARY

This report presents findings from an investigation into potential brand usage by **{suspected_url}** in relation to the **{original_brand}** brand. This analysis follows a zero-trust methodology where no infringement is assumed unless conclusively proven with direct evidence.

The investigation has calculated an **Evidence-Based Score of {infringement_score}/100**, indicating {'STRONG EVIDENCE' if infringement_score >= 80 else 'POTENTIAL EVIDENCE' if infringement_score >= 50 else 'INSUFFICIENT EVIDENCE'} of brand usage that may warrant further investigation.

## 2. SUBJECT DETAILS

| Original Brand | Website Under Analysis |
|----------------|---------------------------|
| Brand Name: **{original_brand}** | Site URL: **{suspected_url}** |
| Official URL: **{original_url}** | Analysis Date: **{current_date}** |

## 3. EVIDENCE COLLECTION

### 3.1 Textual Evidence

* **Exact Brand Name Matches:** {text_analysis.get("brand_mentions", "0")} verified instances of "{original_brand}" found
* **Context of Mentions:** {text_analysis.get("context", "No context available or insufficient data to determine context")}
* **Product Description Matches:** {text_analysis.get("product_descriptions", "No exact product description matches identified")}
* **Meta Tag Analysis:** {text_analysis.get("meta_tags", "No relevant meta tags identified")}

### 3.2 Visual Evidence

* **Verified Logo Usage:** {visual_analysis.get("logo_present", False) and "CONFIRMED: Identical logo detected" or "NOT CONFIRMED: No identical logo usage verified"}
* **Color Scheme Analysis:** {visual_analysis.get("color_scheme", "Insufficient data to conclusively determine color scheme similarity")}
* **Layout Comparison:** {visual_analysis.get("layout_similarity", "Insufficient data to conclusively determine layout similarity")}
* **Product Image Analysis:** {visual_analysis.get("product_similarity", "No identical product images confirmed")}

### 3.3 Additional Evidence

{additional_evidence or "No additional conclusive evidence collected."}

## 4. OBJECTIVE ANALYSIS

### 4.1 Pattern Identification

{text_analysis.get("pattern_analysis", "Insufficient data to establish conclusive patterns.")}

### 4.2 Factual Observations

{text_analysis.get("intent_indicators", "No conclusive evidence of intent identified. This analysis does not make assumptions about intent without direct evidence.")}

### 4.3 Potential for Consumer Confusion

Based solely on verified evidence, the potential for consumer confusion is assessed as {'HIGH' if infringement_score >= 80 else 'MODERATE' if infringement_score >= 50 else 'LOW'}.

## 5. EVIDENCE ASSESSMENT

### 5.1 Zero-Trust Scoring Methodology

The evidence score is calculated using a zero-trust methodology with very high thresholds for evidence:
* Brand name usage (25%) - Requires near-exact matches (95%+ similarity)
* Visual similarity (35%) - Requires near-identical elements (95%+ similarity)
* Product similarity (20%) - Requires near-identical products (95%+ similarity)
* Consumer confusion potential (20%) - Based solely on verified evidence

### 5.2 Evidence Score Breakdown

| Factor | Weight | Evidence Rating | Weighted Score |
|--------|--------|-----------|---------------|
| Brand Name Usage | 25% | {score_breakdown.get("text_score", 0)}/100 | {score_breakdown.get("weighted_text", 0)} |
| Visual Similarity | 35% | {score_breakdown.get("visual_score", 0)}/100 | {score_breakdown.get("weighted_visual", 0)} |
| Product Similarity | 20% | {score_breakdown.get("product_score", 0)}/100 | {score_breakdown.get("weighted_product", 0)} |
| Consumer Confusion | 20% | {score_breakdown.get("confusion_score", 0)}/100 | {score_breakdown.get("weighted_confusion", 0)} |
| **TOTAL** | **100%** | | **{infringement_score}/100** |

### 5.3 Evidence Classification

**Evidence Level:** {'STRONG' if infringement_score >= 80 else 'POTENTIAL' if infringement_score >= 50 else 'INSUFFICIENT'}

**Classification Criteria:**
* INSUFFICIENT: 0-49 - Minimal or inconclusive evidence found
* POTENTIAL: 50-79 - Some concrete evidence identified, requires further verification
* STRONG: 80-100 - Multiple verified instances of exact brand elements usage

### 5.4 Evidence Thresholds Applied

* **Text Analysis Threshold:** {evidence_thresholds.get("text_threshold", "95% for high confidence matches")}
* **Visual Analysis Threshold:** {evidence_thresholds.get("visual_threshold", "95% for high confidence matches")}
* **Logo Detection Threshold:** {evidence_thresholds.get("logo_threshold", "Exact matches only")}
* **Product Similarity Threshold:** {evidence_thresholds.get("product_threshold", "95% for high confidence matches")}

## 6. RECOMMENDATIONS

Based on the objective analysis and evidence score of **{infringement_score}/100**, the following actions are recommended:

{
    "* **Evidence Verification:** Conduct human review to confirm the multiple instances of exact brand asset usage\n* **Legal Assessment:** Consider having legal counsel review the verified evidence\n* **Evidence Preservation:** Archive all pages and evidence for potential action\n* **Ongoing Monitoring:** Establish regular monitoring of this domain" 
    if infringement_score >= 80 else 
    "* **Further Investigation:** Gather additional evidence to verify potential brand usage\n* **Human Review:** Have a human brand specialist review the evidence collected\n* **Regular Monitoring:** Continue monitoring the site for changes\n* **Documentation:** Maintain detailed records of all findings"
    if infringement_score >= 50 else
    "* **Continued Monitoring:** Consider periodic checks for changes to the site\n* **Documentation:** Maintain records of current findings\n* **No Immediate Action:** Insufficient evidence to warrant action at this time\n* **Reassess:** Consider reassessment if new evidence emerges"
}

---

*This analysis was generated by an automated brand protection system using a zero-trust methodology. All claims require human verification before any action is taken. This report makes no assumptions and only presents verified evidence.*
"""
        
        # Generate a filename for the report
        if custom_filename:
            filename = custom_filename
            if not filename.endswith('.md'):
                filename += '.md'
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"brand_infringement_report_{original_brand}_{timestamp}.md"
        
        file_path = os.path.join(self.storage_dir, filename)
        
        # Save the report
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        return f"Brand infringement analysis report generated and saved to {filename}.\n\n{report}"
    
    def calculate_infringement_score(self, 
                                    text_similarity: float, 
                                    visual_similarity: float,
                                    brand_mentions: int,
                                    logo_usage: bool,
                                    product_similarity: float) -> Dict[str, Any]:
        """
        Calculate a numerical infringement score based on multiple factors using zero-trust approach.
        
        Args:
            text_similarity: Similarity score for textual content (0-100)
            visual_similarity: Similarity score for visual elements (0-100)
            brand_mentions: Number of times the brand is mentioned
            logo_usage: Whether the original logo is used
            product_similarity: Similarity score for products (0-100)
            
        Returns:
            Dictionary with overall score and breakdown
        """
        # Calculate text score based on brand mentions (more conservative)
        # Start with 0 by default (zero-trust approach)
        if brand_mentions == 0:
            text_score = 0
        elif brand_mentions == 1:  # Single mention isn't strong evidence
            text_score = 10
        elif brand_mentions < 5:
            text_score = 20
        elif brand_mentions < 10:
            text_score = 35
        elif brand_mentions < 25:
            text_score = 50
        else:
            text_score = 70  # Even many mentions max at 70 without context
        
        # Adjust text score based on text similarity, requiring higher thresholds
        # Only high-confidence matches increase score significantly
        text_score_from_similarity = 0
        if text_similarity > 95:  # Only count near-exact matches
            text_score_from_similarity = text_similarity * 0.8
        elif text_similarity > 85:
            text_score_from_similarity = text_similarity * 0.3
        elif text_similarity > 75:
            text_score_from_similarity = text_similarity * 0.1
        
        # Use the higher of the two scores, but not both (avoid double-counting)
        adjusted_text_score = max(text_score, text_score_from_similarity)
        
        # Calculate visual score - more conservative approach
        # Visual similarity must be extremely high to count significantly
        visual_score = 0
        if visual_similarity > 95:  # Only near-identical visuals
            visual_score = visual_similarity * 0.9
        elif visual_similarity > 90:
            visual_score = visual_similarity * 0.5
        elif visual_similarity > 80:
            visual_score = visual_similarity * 0.3
        elif visual_similarity > 70:
            visual_score = visual_similarity * 0.1
        
        # Logo usage is only counted if verified as identical
        if logo_usage:
            visual_score = min(100, visual_score + 20)  # More conservative bonus
        
        # Calculate product score - more conservative approach
        product_score = 0
        if product_similarity > 95:  # Only near-identical products
            product_score = product_similarity * 0.8
        elif product_similarity > 90:
            product_score = product_similarity * 0.4
        elif product_similarity > 80:
            product_score = product_similarity * 0.2
        
        # Calculate consumer confusion score - more conservative
        confusion_factors = [
            adjusted_text_score * 0.3,
            visual_score * 0.5,  # Visual elements matter more for confusion
            product_score * 0.2
        ]
        confusion_score = sum(confusion_factors) * 0.7  # Apply dampening factor
        
        # Calculate weighted scores - adjusted weights for zero-trust
        weighted_text = adjusted_text_score * 0.25
        weighted_visual = visual_score * 0.35  # Visual evidence weighted more
        weighted_product = product_score * 0.2
        weighted_confusion = confusion_score * 0.2
        
        # Calculate overall score (0-100)
        overall_score = round(weighted_text + weighted_visual + weighted_product + weighted_confusion)
        
        # Ensure the score is within 0-100 range
        overall_score = max(0, min(100, overall_score))
        
        # Create score breakdown
        score_breakdown = {
            "text_score": round(adjusted_text_score),
            "visual_score": round(visual_score),
            "product_score": round(product_score),
            "confusion_score": round(confusion_score),
            "weighted_text": round(weighted_text),
            "weighted_visual": round(weighted_visual),
            "weighted_product": round(weighted_product),
            "weighted_confusion": round(weighted_confusion)
        }
        
        # More conservative thresholds for infringement levels
        return {
            "overall_score": overall_score,
            "score_breakdown": score_breakdown,
            "infringement_level": "HIGH" if overall_score >= 80 else "MODERATE" if overall_score >= 50 else "LOW",
            "evidence_thresholds": {
                "text_threshold": "95% for high confidence, 85% for moderate confidence",
                "visual_threshold": "95% for high confidence, 90% for moderate confidence",
                "logo_threshold": "Exact matches only",
                "product_threshold": "95% for high confidence, 90% for moderate confidence"
            }
        }
