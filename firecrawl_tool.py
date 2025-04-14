"""
Firecrawl tool for Agno Agent

This tool enables the agent to scrape web pages for content analysis,
including HTML, markdown, and images, to help with brand detection.
"""

import os
import json
import tempfile
import uuid
from typing import Dict, List, Any, Optional, Tuple
from agno.tools import Toolkit

try:
    from firecrawl import FirecrawlApp
except ImportError:
    raise ImportError("`firecrawl-py` not installed. Please install using `pip install firecrawl-py`")


class FirecrawlTools(Toolkit):
    """
    Firecrawl toolkit for web scraping and content analysis.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        formats: Optional[List[str]] = None,
        limit: int = 10,
        scrape: bool = True,
        crawl: bool = True,
        api_url: Optional[str] = None,
        session_id: Optional[str] = None,
        image_analyzer = None,
    ):
        """
        Initialize the Firecrawl toolkit.
        
        Args:
            api_key: The API key for Firecrawl
            formats: List of formats to scrape (e.g., ["markdown", "html", "screenshot"])
            limit: Maximum number of pages to crawl
            scrape: Whether to enable the scrape function
            crawl: Whether to enable the crawl function
            api_url: Custom API URL for self-hosted Firecrawl instances
            session_id: Session ID for organizing results in separate folders
            image_analyzer: Reference to image analyzer for automatic analysis
        """
        super().__init__(name="firecrawl_tools")

        # Use API key from parameters or environment variable
        self.api_key: Optional[str] = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY not set. Please set it in .env file or pass it as parameter.")

        # Set default formats if none provided
        self.formats: List[str] = formats or ["markdown", "html", "screenshot"]
        self.limit: int = limit
        
        # Keep a reference to the image analyzer for automatic analysis
        self.image_analyzer = image_analyzer
        
        # Create a unique session ID if not provided
        self.session_id = session_id or str(uuid.uuid4())
        
        # Initialize the session directory in storage
        self.storage_dir = "/Users/ruchitpatel/Projects/agnoagent/storage"
        self.session_dir = os.path.join(self.storage_dir, f"session_{self.session_id}")
        self.image_dir = os.path.join(self.session_dir, "images")
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(self.image_dir, exist_ok=True)
        
        # Keep track of images for analysis
        self.last_scrape_images = {}
        
        # Initialize the Firecrawl app
        if api_url:
            self.app: FirecrawlApp = FirecrawlApp(api_key=self.api_key, api_url=api_url)
        else:
            self.app: FirecrawlApp = FirecrawlApp(api_key=self.api_key)

        # Register the functions based on the configuration
        if scrape:
            self.register(self.scrape_website)
            self.register(self.scrape_with_brand_detection)
        if crawl:
            self.register(self.crawl_website)
        
        # Register new image-specific functions
        self.register(self.get_brand_screenshots)
        self.register(self.scrape_brand_logo)

    def scrape_website(self, url: str, brand_name: Optional[str] = None) -> str:
        """
        Scrape a website for content analysis, optionally looking for a specific brand.
        
        Args:
            url: The URL to scrape
            brand_name: Optional brand name to look for in the content
            
        Returns:
            A summary of the scraping results with brand analysis if a brand name was provided
        """
        if not url:
            return "Error: No URL provided"

        # Prepare parameters for scraping
        params = {
            "formats": self.formats,
            "onlyMainContent": True,  # Focus on main content for better analysis
            "removeBase64Images": False  # Keep images for brand detection
        }

        try:
            # Perform the scraping
            scrape_result = self.app.scrape_url(url, params=params)
            
            # Create a more URL-friendly key
            image_key = url.replace('://', '_').replace('/', '_').replace('?', '_').replace('=', '_').replace('&', '_')
            
            # Store screenshot URL for later use if available
            if "screenshot" in scrape_result:
                screenshot_url = scrape_result["screenshot"]
                self.last_scrape_images[image_key] = {
                    "url": url,
                    "screenshot_url": screenshot_url,
                    "image_type": "screenshot",
                    "brand_name": brand_name
                }
                
                # Save screenshot info to session directory
                screenshot_info_path = os.path.join(self.image_dir, f"{image_key}_info.json")
                with open(screenshot_info_path, "w") as f:
                    json.dump(self.last_scrape_images[image_key], f, indent=2)
                
                # Automatically analyze screenshot if image_analyzer is available
                if self.image_analyzer and brand_name:
                    try:
                        analysis_result = self.image_analyzer.analyze_brand_image(
                            image_url=screenshot_url,
                            brand_name=brand_name
                        )
                        # Save analysis to session directory
                        analysis_path = os.path.join(self.image_dir, f"{image_key}_analysis.md")
                        with open(analysis_path, "w") as f:
                            f.write(analysis_result)
                    except Exception as e:
                        print(f"Error auto-analyzing image: {e}")
            
            # Format the results for easy reading in the chat
            result_summary = f"## Scraping Results for {url}\n\n"
            
            # Add page metadata
            if "metadata" in scrape_result:
                metadata = scrape_result["metadata"]
                result_summary += "### Page Information\n"
                result_summary += f"- Title: {metadata.get('title', 'N/A')}\n"
                result_summary += f"- Description: {metadata.get('description', 'N/A')}\n"
                result_summary += f"- Language: {metadata.get('language', 'N/A')}\n\n"
            
            # If a brand name was provided, search for it in the content
            if brand_name:
                result_summary += f"### Brand Analysis for '{brand_name}'\n"
                brand_found = False
                
                # Check in markdown content
                if "markdown" in scrape_result:
                    markdown_content = scrape_result["markdown"].lower()
                    brand_name_lower = brand_name.lower()
                    if brand_name_lower in markdown_content:
                        brand_found = True
                        count = markdown_content.count(brand_name_lower)
                        result_summary += f"- Found {count} mentions of '{brand_name}' in the page content\n"
                
                # Note if screenshots were captured (for image analysis)
                if "screenshot" in scrape_result:
                    result_summary += f"- Screenshot was captured for visual brand analysis\n"
                    if self.image_analyzer:
                        result_summary += f"- Screenshot automatically analyzed for brand elements\n"
                    result_summary += f"- Image key for reference: {image_key}\n"
                
                if not brand_found:
                    result_summary += f"- No direct text mentions of '{brand_name}' found in the content\n"
                
                result_summary += "\n"
            
            # Summarize content types available
            result_summary += "### Available Content\n"
            for format_type in self.formats:
                if format_type in scrape_result:
                    if format_type == "markdown":
                        char_count = len(scrape_result["markdown"])
                        result_summary += f"- Markdown content: {char_count} characters\n"
                    elif format_type == "html":
                        char_count = len(scrape_result["html"])
                        result_summary += f"- HTML content: {char_count} characters\n"
                    elif format_type == "screenshot":
                        result_summary += f"- Screenshot image available at: {scrape_result['screenshot']}\n"
                    else:
                        result_summary += f"- {format_type.capitalize()} content available\n"
            
            return result_summary
            
        except Exception as e:
            return f"Error scraping website: {str(e)}"
    
    def scrape_with_brand_detection(self, url: str, brand_name: str) -> str:
        """
        Optimized function for brand protection - captures screenshots and analyzes content
        specifically looking for brand presence.
        
        Args:
            url: The URL to scrape
            brand_name: Brand name to look for
            
        Returns:
            Detailed analysis focusing on brand protection
        """
        # Prepare parameters optimized for brand detection
        params = {
            "formats": ["markdown", "html", "screenshot", "links"],
            "onlyMainContent": False,  # Check the entire page for brand presence
            "actions": [
                {"type": "wait", "milliseconds": 2000},
                {"type": "screenshot", "fullPage": True}
            ]
        }
        
        try:
            # Perform the scraping
            scrape_result = self.app.scrape_url(url, params=params)
            
            # Create a more URL-friendly key
            image_key = url.replace('://', '_').replace('/', '_').replace('?', '_').replace('=', '_').replace('&', '_')
            
            # Store screenshot URL for later use
            if "screenshot" in scrape_result:
                screenshot_url = scrape_result["screenshot"]
                self.last_scrape_images[image_key] = {
                    "url": url,
                    "screenshot_url": screenshot_url,
                    "image_type": "screenshot",
                    "brand_name": brand_name
                }
                
                # Save screenshot info to session directory
                screenshot_info_path = os.path.join(self.image_dir, f"{image_key}_info.json")
                with open(screenshot_info_path, "w") as f:
                    json.dump(self.last_scrape_images[image_key], f, indent=2)
                
                # Automatically analyze screenshot if image_analyzer is available
                if self.image_analyzer:
                    try:
                        analysis_result = self.image_analyzer.analyze_brand_image(
                            image_url=screenshot_url,
                            brand_name=brand_name
                        )
                        # Save analysis to session directory
                        analysis_path = os.path.join(self.image_dir, f"{image_key}_analysis.md")
                        with open(analysis_path, "w") as f:
                            f.write(analysis_result)
                    except Exception as e:
                        print(f"Error auto-analyzing image: {e}")
            
            # Check for brand presence in text content
            brand_mentions = 0
            brand_name_lower = brand_name.lower()
            
            if "markdown" in scrape_result:
                markdown_content = scrape_result["markdown"].lower()
                brand_mentions = markdown_content.count(brand_name_lower)
            
            # Format results with focus on brand protection
            result = f"## Brand Protection Analysis for {url}\n\n"
            result += f"### Brand: {brand_name}\n\n"
            
            # Text analysis results
            result += "### Text Analysis\n"
            if brand_mentions > 0:
                result += f"- Found {brand_mentions} mentions of '{brand_name}' in the page content\n"
            else:
                result += f"- No text mentions of '{brand_name}' found in the content\n"
            
            # Screenshot info
            if "screenshot" in scrape_result:
                result += "\n### Visual Analysis\n"
                result += f"- Full page screenshot captured for visual brand analysis\n"
                result += f"- Screenshot URL: {scrape_result['screenshot']}\n"
                result += f"- Image key for reference: {image_key}\n"
                if self.image_analyzer:
                    result += f"- Screenshot automatically analyzed for brand elements\n"
                    # When both sites have been scraped, automatically compare them
                    if len(self.last_scrape_images) > 1 and self.image_analyzer:
                        result += f"- Automatic comparison of screenshots being performed\n"
            
            # Link analysis for potential further crawling
            if "links" in scrape_result and scrape_result["links"]:
                result += "\n### Related Pages\n"
                result += f"- Found {len(scrape_result['links'])} links on the page that could be analyzed further\n"
                result += "- Top 5 internal links:\n"
                
                # Show top 5 internal links that might contain brand content
                internal_links = [link for link in scrape_result["links"] if url in link][:5]
                for link in internal_links:
                    result += f"  - {link}\n"
            
            # After both sites have been scraped, automatically compare them
            if len(self.last_scrape_images) > 1 and self.image_analyzer:
                # Get URLs of two most recent screenshots
                screenshot_urls = [info["screenshot_url"] for info in list(self.last_scrape_images.values())[-2:]]
                if len(screenshot_urls) >= 2:
                    try:
                        # Perform comparison analysis
                        comparison_result = self.image_analyzer.compare_brand_images(
                            original_url=screenshot_urls[0],
                            suspected_url=screenshot_urls[1],
                            brand_name=brand_name
                        )
                        
                        # Save comparison to session directory
                        comparison_path = os.path.join(self.session_dir, f"brand_comparison_{brand_name}.md")
                        with open(comparison_path, "w") as f:
                            f.write(comparison_result)
                        
                        # Add reference to comparison in the result
                        result += f"\n### Automatic Brand Comparison\n"
                        result += f"- An automatic comparison of the original and suspected websites has been performed\n"
                        result += f"- Comparison report saved to session directory: {os.path.basename(comparison_path)}\n"
                    except Exception as e:
                        print(f"Error comparing images: {e}")
            
            return result
            
        except Exception as e:
            return f"Error performing brand detection: {str(e)}"

    def crawl_website(self, url: str, brand_name: Optional[str] = None, limit: Optional[int] = None) -> str:
        """
        Crawl a website and its subpages, optionally searching for a specific brand.
        
        Args:
            url: The URL to crawl
            brand_name: Optional brand name to look for across pages
            limit: Maximum number of pages to crawl (overrides the default)
            
        Returns:
            A summary of the crawling results with brand analysis if a brand name was provided
        """
        if not url:
            return "Error: No URL provided"

        # Set up crawl parameters
        params = {
            "limit": limit or self.limit,
            "scrapeOptions": {
                "formats": self.formats,
                "onlyMainContent": True
            }
        }

        try:
            # Perform the crawling (asynchronous operation)
            crawl_job = self.app.async_crawl_url(url, params=params)
            job_id = crawl_job.get("id")
            
            if not job_id:
                return f"Error: Failed to start crawl job for {url}"
                
            # Return information about the crawl job
            result = f"## Crawling Started for {url}\n\n"
            result += f"- Crawl job ID: {job_id}\n"
            result += f"- Maximum pages to crawl: {limit or self.limit}\n"
            result += f"- Scraping formats: {', '.join(self.formats)}\n"
            
            if brand_name:
                result += f"\nThe agent will search for mentions of '{brand_name}' across all crawled pages.\n"
                result += "To check the status of the crawl job, please use the job ID in a follow-up query.\n"
            
            return result
            
        except Exception as e:
            return f"Error starting crawl: {str(e)}"
    
    def get_brand_screenshots(self, image_key: Optional[str] = None) -> str:
        """
        Retrieve screenshots collected from previous scraping operations.
        
        Args:
            image_key: Optional key to retrieve a specific image, if None returns all images
            
        Returns:
            URLs of screenshots available for brand analysis
        """
        if not self.last_scrape_images:
            return "No images have been collected from previous scraping operations."
        
        if image_key and image_key in self.last_scrape_images:
            # Return specific image info
            image_info = self.last_scrape_images[image_key]
            result = f"## Screenshot from {image_info['url']}\n\n"
            result += f"- Screenshot URL: {image_info['screenshot_url']}\n"
            result += f"- Image type: {image_info['image_type']}\n"
            
            if "brand_name" in image_info:
                result += f"- Related brand: {image_info['brand_name']}\n"
            
            # Check if analysis exists
            analysis_path = os.path.join(self.image_dir, f"{image_key}_analysis.md")
            if os.path.exists(analysis_path):
                with open(analysis_path, "r") as f:
                    analysis = f.read()
                result += f"\n### Automatic Image Analysis\n"
                result += f"{analysis}\n"
            
            return result
        
        # Return all available images
        result = "## Available Screenshots for Brand Analysis\n\n"
        for key, image_info in self.last_scrape_images.items():
            result += f"### {image_info['url']}\n"
            result += f"- Image key: {key}\n"
            result += f"- Screenshot URL: {image_info['screenshot_url']}\n"
            
            if "brand_name" in image_info:
                result += f"- Related brand: {image_info['brand_name']}\n"
            
            # Check if analysis exists
            analysis_path = os.path.join(self.image_dir, f"{key}_analysis.md")
            if os.path.exists(analysis_path):
                result += f"- Image automatically analyzed for brand elements\n"
            
            result += "\n"
        
        # Check if comparison exists
        for file in os.listdir(self.session_dir):
            if file.startswith("brand_comparison_") and file.endswith(".md"):
                result += f"### Automatic Brand Comparison\n"
                result += f"- Brand comparison report: {file}\n"
                comparison_path = os.path.join(self.session_dir, file)
                with open(comparison_path, "r") as f:
                    comparison_summary = f.read().split("\n\n")[0]  # Get just the first paragraph
                result += f"- Summary: {comparison_summary}\n\n"
        
        return result
    
    def scrape_brand_logo(self, url: str, selector: str = ".logo, img[alt*='logo'], header img") -> str:
        """
        Specialized function to scrape a website looking specifically for a logo.
        
        Args:
            url: The URL to scrape
            selector: Optional CSS selector to target the logo (default looks for common logo elements)
            
        Returns:
            URL of the logo image if found
        """
        # Prepare parameters specifically for logo detection
        params = {
            "formats": ["html", "screenshot"],
            "onlyMainContent": False,  # Logo often in header/footer
            "actions": [
                {"type": "wait", "milliseconds": 2000},
                {"type": "executeJavascript", "script": f"""
                    const logoElements = document.querySelectorAll('{selector}');
                    let logoInfo = [];
                    
                    logoElements.forEach(el => {{
                        if (el.tagName.toLowerCase() === 'img') {{
                            logoInfo.push({{
                                src: el.src,
                                alt: el.alt || '',
                                width: el.width,
                                height: el.height
                            }});
                        }}
                    }});
                    
                    return JSON.stringify(logoInfo);
                """}
            ]
        }
        
        try:
            # Perform the scraping
            scrape_result = self.app.scrape_url(url, params=params)
            
            # Check for JavaScript execution results
            if "actions" in scrape_result and "javascriptReturns" in scrape_result["actions"]:
                js_returns = scrape_result["actions"]["javascriptReturns"]
                
                for js_return in js_returns:
                    if js_return.get("type") == "string":
                        try:
                            logo_info = json.loads(js_return.get("value", "[]"))
                            
                            if logo_info and len(logo_info) > 0:
                                # We found potential logos
                                # Store the first logo image
                                first_logo = logo_info[0]
                                logo_url = first_logo.get("src", "")
                                
                                if logo_url:
                                    # Create a key for this logo
                                    image_key = f"logo_{url.replace('://', '_').replace('/', '_').replace('?', '_').replace('=', '_').replace('&', '_')}"
                                    self.last_scrape_images[image_key] = {
                                        "url": url,
                                        "screenshot_url": logo_url,
                                        "image_type": "logo"
                                    }
                                    
                                    # Save logo info to session directory
                                    logo_info_path = os.path.join(self.image_dir, f"{image_key}_info.json")
                                    with open(logo_info_path, "w") as f:
                                        json.dump(self.last_scrape_images[image_key], f, indent=2)
                                    
                                    # Format the results
                                    result = f"## Logo Detected on {url}\n\n"
                                    result += f"- Found {len(logo_info)} potential logo elements\n\n"
                                    result += "### Primary Logo:\n"
                                    result += f"- URL: {logo_url}\n"
                                    result += f"- Alt text: {first_logo.get('alt', 'N/A')}\n"
                                    result += f"- Dimensions: {first_logo.get('width', 'N/A')}x{first_logo.get('height', 'N/A')}\n"
                                    result += f"- Image key: {image_key}\n\n"
                                    
                                    if len(logo_info) > 1:
                                        result += "### Additional Logos Found:\n"
                                        for i, logo in enumerate(logo_info[1:], 1):
                                            if i > 4:  # Limit to 5 logos total
                                                result += f"- Plus {len(logo_info) - 5} more logo elements...\n"
                                                break
                                            logo_url = logo.get("src", "")
                                            result += f"{i}. {logo_url}\n"
                                    
                                    return result
                        except json.JSONDecodeError:
                            pass
            
            # If we get here, no logos were found using JavaScript
            # Try a different approach - look for logo in the full page screenshot
            if "screenshot" in scrape_result:
                # Create a key for the screenshot
                image_key = f"screenshot_{url.replace('://', '_').replace('/', '_').replace('?', '_').replace('=', '_').replace('&', '_')}"
                self.last_scrape_images[image_key] = {
                    "url": url,
                    "screenshot_url": scrape_result["screenshot"],
                    "image_type": "screenshot_for_logo"
                }
                
                # Save screenshot info to session directory
                screenshot_info_path = os.path.join(self.image_dir, f"{image_key}_info.json")
                with open(screenshot_info_path, "w") as f:
                    json.dump(self.last_scrape_images[image_key], f, indent=2)
                
                result = f"## No Direct Logo Elements Found on {url}\n\n"
                result += "- Could not identify specific logo images using automatic detection\n"
                result += "- A full page screenshot was captured for manual logo inspection\n"
                result += f"- Screenshot URL: {scrape_result['screenshot']}\n"
                result += f"- Image key: {image_key}\n\n"
                result += "You can use the ImageAnalyzer tool to visually inspect this screenshot for logo elements."
                return result
                
            return "No logo elements or screenshots could be captured from the website."
            
        except Exception as e:
            return f"Error scraping for logo: {str(e)}"
