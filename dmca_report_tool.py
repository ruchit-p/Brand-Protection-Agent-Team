"""
DMCA Report Tool for Agno Agent

This tool enables the agent to generate DMCA takedown notices based on
brand infringement evidence gathered from websites.
"""

import os
import json
import requests
import re
from datetime import datetime
from typing import Dict, Optional, Any, List
from agno.tools import Toolkit

class DmcaReportTools(Toolkit):
    """
    Toolkit for generating DMCA reports and related documentation.
    """

    def __init__(self, storage_directory: Optional[str] = None):
        """
        Initialize the DMCA Report Toolkit.
        
        Args:
            storage_directory: Directory to store generated reports (default to storage directory)
        """
        super().__init__(name="dmca_report_tools")
        
        # Set storage directory for reports
        self.storage_directory = storage_directory or "/Users/ruchitpatel/Projects/agnoagent/storage"
        
        # Create the storage directory if it doesn't exist
        os.makedirs(self.storage_directory, exist_ok=True)
        
        # Register the functions
        self.register(self.generate_dmca_notice)
        self.register(self.get_domain_info)
        self.register(self.find_contact_info)
        self.register(self.save_dmca_report)
    
    def generate_dmca_notice(self, 
                             infringing_url: str, 
                             original_url: str, 
                             brand_name: str,
                             copyright_owner: str, 
                             contact_name: str,
                             contact_email: str,
                             contact_phone: str,
                             contact_address: str,
                             infringement_details: str,
                             original_work_description: str = None) -> str:
        """
        Generate a comprehensive DMCA takedown notice.
        
        Args:
            infringing_url: URL where unauthorized content appears
            original_url: URL of the original copyrighted content
            brand_name: Name of the brand being infringed
            copyright_owner: Legal name of copyright owner (company or individual)
            contact_name: Full name of the person submitting the notice
            contact_email: Email address for correspondence
            contact_phone: Phone number for contact
            contact_address: Physical address of the copyright owner
            infringement_details: Description of the specific infringing elements
            original_work_description: Optional description of the original work
            
        Returns:
            Formatted DMCA takedown notice
        """
        # Get current date for the notice
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Extract domain name from infringing URL
        infringing_domain = self._extract_domain(infringing_url)
        
        # Get domain registrar information
        domain_info = self.get_domain_info(infringing_domain)
        
        # Use the original_work_description or generate a default one
        if not original_work_description:
            original_work_description = f"The original copyrighted work is the '{brand_name}' brand, including its name, logo, product designs, and associated elements as displayed on {original_url}."
        
        # Format the DMCA notice
        dmca_notice = f"""
# DMCA TAKEDOWN NOTICE

**Date:** {current_date}

**VIA EMAIL**

**RE: Copyright Infringement Notice - {brand_name}**

To Whom It May Concern:

This letter serves as notification under the Digital Millennium Copyright Act (DMCA), 17 USC § 512(c)(3)(A) that the following copyright infringement has occurred. I request that you immediately remove or disable access to the infringing material as described below.

## 1. Contact Information

**Copyright Owner:** {copyright_owner}
**Represented by:** {contact_name}
**Email:** {contact_email}
**Phone:** {contact_phone}
**Address:** {contact_address}

## 2. Identification of Copyrighted Work

{original_work_description}

## 3. Identification of Infringing Material

The unauthorized and infringing copy of this material can be found at:
{infringing_url}

## 4. Specific Description of Infringement

{infringement_details}

## 5. Good Faith Statement

I have a good faith belief that the use of the material in the manner complained of is not authorized by the copyright owner, its agent, or the law.

## 6. Accuracy Statement

Under penalty of perjury, I state that the information in this notification is accurate, and I am authorized to act on behalf of the owner of the exclusive right that is allegedly infringed.

## 7. Fair Use Statement

I have taken into consideration fair use aspects before sending this notice.

## 8. Request for Removal

I respectfully ask that you immediately remove or disable access to the infringing material identified above. Please notify me when this action has been taken.

Sincerely,

{contact_name}
{copyright_owner}
{contact_email}
{contact_phone}
"""
        
        # Save the DMCA notice to a file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"dmca_notice_{infringing_domain}_{timestamp}.md"
        file_path = os.path.join(self.storage_directory, file_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(dmca_notice)
        
        return f"DMCA takedown notice generated and saved to {file_name}.\n\n{dmca_notice}"
    
    def get_domain_info(self, domain: str) -> str:
        """
        Retrieve domain registration information using ICANN or WHOIS APIs.
        
        Args:
            domain: Domain name to look up
            
        Returns:
            Registration information for the domain
        """
        try:
            # For demonstration, we'll use a simplified approach
            # In production, you'd use a proper WHOIS API or the ICANN API
            
            # Simulated API call to ICANN data
            # In a real implementation, you would use:
            # url = f"https://opendata.icann.org/api/v1/console/datasets/1.0/search/?domain={domain}"
            # response = requests.get(url)
            
            # For now, we'll return a sample response
            result = f"""
## Domain Information for {domain}

### Registration Details
- **Domain:** {domain}
- **Registrar:** Sample Registrar, Inc.
- **Registration Date:** January 1, 2023
- **Expiration Date:** January 1, 2026
- **Status:** Active

### Registrant Contact
- **Organization:** Private by Design, LLC
- **Email:** registrant@{domain}
- **Country:** US

### Technical Contact
- **Email:** tech@{domain}

### Administrative Contact
- **Email:** admin@{domain}

### DMCA Agent Information
- **Agent:** Legal Department
- **Email:** legal@{domain}
"""
            # In production, parse the actual API response and format it
            
            return result
            
        except Exception as e:
            return f"Error retrieving domain information: {str(e)}"
    
    def find_contact_info(self, domain: str) -> str:
        """
        Find DMCA agent contact information for a domain.
        
        Args:
            domain: Domain to search for contact information
            
        Returns:
            DMCA agent contact information
        """
        try:
            # Real implementation would search the U.S. Copyright Office directory 
            # or website privacy/terms pages for contact info
            
            # For demonstration, return sample information
            result = f"""
## DMCA Contact Information for {domain}

### Recommended Contact Methods (in order of preference)

1. **DMCA Form:** {domain}/dmca-form
2. **Email:** dmca@{domain}
3. **Postal Mail:**
   Legal Department
   Sample Company Inc.
   123 Main Street
   Anytown, US 12345

### Notes
- Response typically within 2-3 business days
- Include all required elements of a DMCA notice for prompt processing
"""
            return result
            
        except Exception as e:
            return f"Error finding contact information: {str(e)}"
    
    def save_dmca_report(self, report_content: str, file_name: str = None) -> str:
        """
        Save a DMCA report to a file.
        
        Args:
            report_content: Content of the DMCA report
            file_name: Optional custom file name (defaults to timestamped name)
            
        Returns:
            Confirmation of the saved file
        """
        if not file_name:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"dmca_report_{timestamp}.md"
        
        # Ensure file has proper extension
        if not file_name.endswith(".md") and not file_name.endswith(".txt"):
            file_name += ".md"
        
        file_path = os.path.join(self.storage_directory, file_name)
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            
            return f"DMCA report successfully saved to {file_name} in the storage directory."
        except Exception as e:
            return f"Error saving DMCA report: {str(e)}"
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain name from a URL.
        
        Args:
            url: Full URL
            
        Returns:
            Domain name portion of the URL
        """
        # Simple regex to extract domain from URL
        match = re.search(r'(?:https?://)?(?:www\.)?([^/]+)', url)
        if match:
            return match.group(1)
        return url  # Return original URL if regex fails
