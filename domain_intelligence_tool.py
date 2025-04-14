"""
Domain Intelligence Tool for Agno Agent

A custom tool that provides domain intelligence capabilities:
- Generates typosquatting variants for a domain
- Performs WHOIS lookups
- Extracts DNS records (A, MX, TXT)
"""

import whois
import dns.resolver
import json
from typing import List, Dict, Any

def generate_typo_variants(domain_base: str) -> List[str]:
    """
    Generate typosquatting variants for a domain name.
    
    Args:
        domain_base: The base domain name (without TLD)
        
    Returns:
        A list of variant domain names
    """
    variants = set()
    
    # Variant 1: Remove one character at each position
    for i in range(len(domain_base)):
        variant = domain_base[:i] + domain_base[i+1:]
        if variant:
            variants.add(variant)
    
    # Variant 2: Swap adjacent characters
    for i in range(len(domain_base) - 1):
        variant_list = list(domain_base)
        variant_list[i], variant_list[i+1] = variant_list[i+1], variant_list[i]
        variants.add("".join(variant_list))
    
    return list(variants)

def get_dns_records(domain: str) -> Dict[str, List[str]]:
    """
    Retrieve A, MX, and TXT DNS records for a domain.
    
    Args:
        domain: The domain to query
        
    Returns:
        Dictionary with DNS record types and values
    """
    records = {}
    
    # Lookup A records
    try:
        answers = dns.resolver.resolve(domain, 'A')
        records['A'] = [rdata.to_text() for rdata in answers]
    except Exception:
        records['A'] = []
    
    # Lookup MX records
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        records['MX'] = [rdata.exchange.to_text() for rdata in answers]
    except Exception:
        records['MX'] = []
    
    # Lookup TXT records
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        records['TXT'] = [rdata.to_text() for rdata in answers]
    except Exception:
        records['TXT'] = []
    
    return records

def check_domain_registration(domain: str) -> Dict[str, Any]:
    """
    Check if a domain is registered using WHOIS lookup.
    
    Args:
        domain: The domain to check
        
    Returns:
        Dictionary with registration information
    """
    result = {
        "domain": domain,
        "registered": False,
        "creation_date": None,
        "registrar": None,
        "dns_records": None
    }
    
    try:
        w = whois.whois(domain)
        # Check if a creation_date field exists (indicating registration)
        if w.creation_date:
            result["registered"] = True
            result["creation_date"] = str(w.creation_date)
            result["registrar"] = w.registrar
            result["dns_records"] = get_dns_records(domain)
    except Exception:
        # WHOIS lookup error or domain not registered
        pass
        
    return result

def check_typosquatting(domain: str) -> Dict[str, Any]:
    """
    Check for typosquatting variants of a domain.
    
    Args:
        domain: The domain to check (e.g., "example.com")
        
    Returns:
        Dictionary with results of typosquatting checks
    """
    # Separate the base name and TLD
    if '.' in domain:
        parts = domain.split('.')
        base = parts[0]
        tld = ".".join(parts[1:])
    else:
        base = domain
        tld = ""
    
    variants = generate_typo_variants(base)
    results = {
        "original_domain": domain,
        "variants_checked": [],
        "registered_variants": []
    }
    
    for variant in variants:
        # Form the full domain variant
        test_domain = f"{variant}.{tld}" if tld else variant
        results["variants_checked"].append(test_domain)
        
        registration_info = check_domain_registration(test_domain)
        if registration_info["registered"]:
            results["registered_variants"].append(registration_info)
    
    return results

# Define the tool functions that will be exposed to Agno
def domain_intelligence(domain: str) -> str:
    """
    Analyze a domain for typosquatting and perform domain intelligence.
    
    Args:
        domain: The domain to analyze (e.g., "example.com")
        
    Returns:
        String representation of analysis results including registration status and DNS records
    """
    # First get the registration info
    registration_info = check_domain_registration(domain)
    
    # Format a human-readable response as a string
    result = f"Domain Intelligence Report for {domain}:\n\n"
    
    # Registration information
    result += "Registration Information:\n"
    if registration_info["registered"]:
        result += f"- Status: Registered\n"
        result += f"- Creation Date: {registration_info['creation_date']}\n"
        result += f"- Registrar: {registration_info['registrar']}\n"
        
        # DNS Records
        result += "\nDNS Records:\n"
        dns_records = registration_info["dns_records"]
        if dns_records:
            if dns_records["A"]:
                result += f"- A Records: {', '.join(dns_records['A'])}\n"
            if dns_records["MX"]:
                result += f"- MX Records: {', '.join(dns_records['MX'])}\n"
            if dns_records["TXT"]:
                result += f"- TXT Records: {', '.join(dns_records['TXT'])}\n"
    else:
        result += "- Status: Not registered or lookup failed\n"
    
    # Check for typosquatting only if specifically requested
    # This is to avoid excessive lookups for every query
    if "typo" in domain.lower() or "squat" in domain.lower():
        result += "\nTyposquatting Analysis:\n"
        typosquatting_results = check_typosquatting(domain)
        variants_count = len(typosquatting_results["variants_checked"])
        registered_count = len(typosquatting_results["registered_variants"])
        
        result += f"- Generated {variants_count} variant domains\n"
        result += f"- Found {registered_count} registered variant domains\n"
        
        if registered_count > 0:
            result += "\nRegistered typosquatting domains:\n"
            for variant in typosquatting_results["registered_variants"]:
                result += f"- {variant['domain']} (Registrar: {variant['registrar']})\n"
    
    return result
