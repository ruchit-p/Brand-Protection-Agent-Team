"""
Image Analysis Tool for Agno Agent

This tool enables the agent to analyze images scraped by Firecrawl
using Gemini 2.0 Flash's multimodal capabilities for brand protection.
"""

import os
import base64
import requests
from typing import Optional, List, Dict, Any
from io import BytesIO
from PIL import Image
from agno.tools import Toolkit

try:
    from google.generativeai import GenerativeModel
    import google.generativeai as genai
except ImportError:
    raise ImportError("`google-generativeai` not installed. Please install using `pip install google-generativeai`")


class ImageAnalyzerTools(Toolkit):
    """
    Toolkit for analyzing images using Gemini 2.0 Flash's multimodal capabilities.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Image Analyzer toolkit.
        
        Args:
            api_key: The Google Gemini API key (optional if set in environment)
        """
        super().__init__(name="image_analyzer_tools")
        
        # Use API key from parameters or environment variable
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set. Please set it in .env file or pass it as parameter.")
        
        # Initialize the Gemini client (updated API for newer versions)
        genai.configure(api_key=self.api_key)
        self.model_name = "gemini-2.0-flash"
        self.model = GenerativeModel(self.model_name)
        
        # Register the functions
        self.register(self.analyze_brand_image)
        self.register(self.compare_brand_images)
        self.register(self.detect_logo_usage)
        self.register(self.analyze_product_similarity)
        
    def _download_image(self, image_url: str) -> Optional[bytes]:
        """
        Download an image from a URL.
        
        Args:
            image_url: The URL of the image to download
            
        Returns:
            The image bytes or None if download failed
        """
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            return None
    
    def analyze_brand_image(self, image_url: str, brand_name: str, prompt_override: Optional[str] = None) -> str:
        """
        Analyze a single image for brand elements using Gemini 2.0 Flash.
        
        Args:
            image_url: The URL of the image to analyze
            brand_name: The name of the brand to look for
            prompt_override: Optional custom prompt for specialized analysis
            
        Returns:
            Analysis of brand elements in the image
        """
        # Download the image
        image_data = self._download_image(image_url)
        if not image_data:
            return f"Error: Could not download image from {image_url}"
        
        # Default prompt for brand analysis
        prompt = prompt_override or f"""
        As a brand protection expert with a STRICT zero-trust approach, analyze this image for elements related to the brand '{brand_name}'.
        You must start with the assumption that this image contains NO brand infringement and only change that assessment with clear, unambiguous evidence.

        Identify the following with absolute certainty:
        1. Is the EXACT brand name '{brand_name}' directly visible as text in the image? If so, provide precise location and context.
        2. Are there any logos or trademarks that are IDENTICAL to official '{brand_name}' brand assets? Similarity is not sufficient - they must be exact matches.
        3. Are there products in the image that are VERIFIED to be from the '{brand_name}' brand? Do not speculate based on appearance alone.
        4. Is there anything in this image that DEFINITIVELY infringes on the '{brand_name}' brand with 100% certainty?

        For each point, clearly distinguish between:
        - Confirmed evidence (what you can verify with absolute certainty)
        - Possible indicators (similarities that aren't definitive)
        - Absence of evidence

        Use precise language and avoid all speculation. When uncertain, explicitly state that the evidence is inconclusive.
        Remember: in a zero-trust framework, the default position is that NO infringement exists.
        """
        
        try:
            # Create multimodal request with the image - updated for latest API
            contents = [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(image_data).decode("utf-8")}}
            ]
            
            response = self.model.generate_content(contents=contents, generation_config={"temperature": 0.2})
            
            return f"## Brand Image Analysis for '{brand_name}'\n\n{response.text}"
            
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
    
    def compare_brand_images(self, original_url: str, suspected_url: str, brand_name: str) -> str:
        """
        Compare an original brand image with a suspected infringing image.
        
        Args:
            original_url: The URL of the original brand image
            suspected_url: The URL of the suspected infringing image
            brand_name: The name of the brand being protected
            
        Returns:
            Comparative analysis between the two images
        """
        # Download both images
        original_data = self._download_image(original_url)
        suspected_data = self._download_image(suspected_url)
        
        if not original_data:
            return f"Error: Could not download original image from {original_url}"
        if not suspected_data:
            return f"Error: Could not download suspected image from {suspected_url}"
        
        prompt = f"""
        You are a brand protection specialist comparing two images with a STRICT zero-trust approach:
        1. The first image is from the original '{brand_name}' brand website.
        2. The second image is from a suspected website.

        Compare these images with extreme precision and identify:
        - Only EXACT visual matches in design, color schemes, and layout - note when elements are similar but not identical
        - Any elements that are proven to be direct copies (not just similar) of brand elements
        - VERIFIED instances of logo or trademark usage - not just similar graphics
        - Product representations that are IDENTICAL, not just comparable
        - Overall assessment of infringement based ONLY on concrete evidence

        Rate the similarity on a scale of 1-10, where:
        1-3: Minor coincidental similarities
        4-6: Notable similarities that may not be intentional
        7-8: Substantial similarities that suggest potential infringement
        9-10: Unmistakable evidence of direct copying

        Begin with a score of 1 by default and only increase based on verifiable evidence. Clearly separate definitive evidence from speculation.
        Do not make assumptions about intent without clear evidence.
        Similar is NOT the same as identical - only identical elements should be flagged as potential infringement.
        """
        
        try:
            # Create multimodal request with both images - updated for latest API
            contents = [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(original_data).decode("utf-8")}},
                {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(suspected_data).decode("utf-8")}}
            ]
            
            response = self.model.generate_content(contents=contents, generation_config={"temperature": 0.2})
            
            return f"## Brand Image Comparison for '{brand_name}'\n\n{response.text}"
            
        except Exception as e:
            return f"Error comparing images: {str(e)}"
    
    def detect_logo_usage(self, logo_url: str, screenshot_url: str, brand_name: str) -> str:
        """
        Detect usage of a brand logo within a screenshot.
        
        Args:
            logo_url: The URL of the brand's official logo
            screenshot_url: The URL of a screenshot to analyze
            brand_name: The name of the brand
            
        Returns:
            Analysis of logo usage in the screenshot
        """
        # Download both images
        logo_data = self._download_image(logo_url)
        screenshot_data = self._download_image(screenshot_url)
        
        if not logo_data:
            return f"Error: Could not download logo image from {logo_url}"
        if not screenshot_data:
            return f"Error: Could not download screenshot from {screenshot_url}"
        
        prompt = f"""
        As a brand protection expert with a STRICT zero-trust approach, you need to identify potential unauthorized use of the '{brand_name}' logo:
        1. The first image shows the official logo of the '{brand_name}' brand.
        2. The second image is a screenshot from a website that might be using this logo.

        Analyze the screenshot with extreme precision and:
        - Identify if and EXACTLY where the '{brand_name}' logo appears - it must be a direct match, not just similar
        - Document any modifications in precise detail (colors, proportions, quality)
        - Do not make assumptions about whether usage is authorized - simply document the appearance
        - Provide exact regions where the logo appears

        Begin with the assumption that no logo is present and only confirm detection when the evidence is unambiguous.
        If a similar but not identical logo is found, clearly distinguish the differences.
        Avoid speculation and focus strictly on visual evidence.
        Remember: the burden of proof is to demonstrate that a logo IS present, not that it MIGHT be present.
        """
        
        try:
            # Create multimodal request with both images - updated for latest API
            contents = [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(logo_data).decode("utf-8")}},
                {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(screenshot_data).decode("utf-8")}}
            ]
            
            response = self.model.generate_content(contents=contents, generation_config={"temperature": 0.2})
            
            return f"## Logo Usage Detection for '{brand_name}'\n\n{response.text}"
            
        except Exception as e:
            return f"Error detecting logo usage: {str(e)}"
    
    def analyze_product_similarity(self, original_url: str, suspected_url: str, product_name: str) -> str:
        """
        Compare original product images with suspected copycat products.
        
        Args:
            original_url: The URL of the original product image
            suspected_url: The URL of the suspected copycat product
            product_name: The name of the product being analyzed
            
        Returns:
            Analysis of product similarities and potential counterfeiting
        """
        # Download both images
        original_data = self._download_image(original_url)
        suspected_data = self._download_image(suspected_url)
        
        if not original_data:
            return f"Error: Could not download original product image from {original_url}"
        if not suspected_data:
            return f"Error: Could not download suspected product image from {suspected_url}"
        
        prompt = f"""
        You are a product authenticity expert comparing two product images with a STRICT zero-trust approach:
        1. The first image shows the authentic '{product_name}'.
        2. The second image shows a suspected similar product.

        Analyze with extreme precision and identify:
        - Only EXACT matches in product design, shape, color, and packaging - any deviation must be noted
        - Specific elements that are IDENTICAL, not just similar
        - Definitive evidence of copying versus coincidental similarities
        - Objective quality indicators, not subjective assessments

        Rate the similarity on a scale of 1-10, where:
        1-3: Distinct products with minor coincidental similarities
        4-6: Products with notable similarities that may be industry-standard
        7-8: Products with substantial similarities suggesting potential copying
        9-10: Products that are virtually identical copies

        Begin with a score of 1 by default and only increase with verifiable evidence.
        A high score (9-10) should only be given when there is no reasonable doubt that the product is a direct copy.
        Clearly separate confirmed evidence from possibilities or assumptions.
        Many products in the same category may share common features - this alone is NOT evidence of infringement.
        """
        
        try:
            # Create multimodal request with both images - updated for latest API
            contents = [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(original_data).decode("utf-8")}},
                {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(suspected_data).decode("utf-8")}}
            ]
            
            response = self.model.generate_content(contents=contents, generation_config={"temperature": 0.2})
            
            return f"## Product Similarity Analysis for '{product_name}'\n\n{response.text}"
            
        except Exception as e:
            return f"Error analyzing product similarity: {str(e)}"
