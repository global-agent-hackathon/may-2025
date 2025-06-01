"""
Groq API integration for generating SEO tips and insights
"""
import os
from typing import Dict, List, Any, Optional
import logging
import json

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

logger = logging.getLogger(__name__)

def generate_seo_tips(site_data: Dict[str, Any], api_key: Optional[str] = None) -> List[str]:
    """
    Generate SEO tips based on site analysis data
    
    Args:
        site_data: Dictionary containing website analysis data
        api_key: Optional Groq API key
        
    Returns:
        List of SEO tips and recommendations
    """
    try:
        if api_key and GROQ_AVAILABLE:
            return generate_ai_seo_tips(site_data, api_key)
        else:
            return generate_rule_based_tips(site_data)
            
    except Exception as e:
        logger.error(f"Error generating SEO tips: {e}")
        return generate_rule_based_tips(site_data)

def generate_ai_seo_tips(site_data: Dict[str, Any], api_key: str) -> List[str]:
    """
    Generate AI-powered SEO tips using Groq
    """
    try:
        client = Groq(api_key=api_key)
        
        # Prepare site data for AI analysis
        analysis_prompt = create_seo_analysis_prompt(site_data)
        
        # Get AI recommendations
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert SEO consultant with 10+ years of experience. 
                    Analyze the provided website data and give specific, actionable SEO recommendations. 
                    Focus on high-impact improvements that can be implemented quickly.
                    Provide exactly 8-12 specific recommendations."""
                },
                {
                    "role": "user",
                    "content": analysis_prompt
                }
            ],
            model="llama3-8b-8192",
            temperature=0.3,
            max_tokens=1024,
        )
        
        # Parse AI response
        ai_response = chat_completion.choices[0].message.content
        tips = parse_ai_tips(ai_response)
        
        # Combine with rule-based tips for comprehensive coverage
        rule_tips = generate_rule_based_tips(site_data)
        
        # Merge and deduplicate
        all_tips = tips + rule_tips
        unique_tips = []
        seen = set()
        
        for tip in all_tips:
            tip_key = tip.lower()[:50]  # Use first 50 chars as key
            if tip_key not in seen:
                unique_tips.append(tip)
                seen.add(tip_key)
        
        logger.info(f"Generated {len(unique_tips)} AI-powered SEO tips")
        return unique_tips[:12]  # Return top 12 tips
        
    except Exception as e:
        logger.error(f"Groq AI error: {e}")
        return generate_rule_based_tips(site_data)

def create_seo_analysis_prompt(site_data: Dict[str, Any]) -> str:
    """Create detailed prompt for AI SEO analysis"""
    
    prompt = f"""
    Analyze this website's SEO performance and provide specific recommendations:

    WEBSITE DATA:
    - URL: {site_data.get('url', 'N/A')}
    - Title: {site_data.get('title', 'Missing')}
    - Meta Description: {site_data.get('meta_description', 'Missing')}
    - Page Load Time: {site_data.get('page_load_time', 0)} seconds
    - Word Count: {site_data.get('word_count', 0)} words
    - Mobile Friendly: {site_data.get('mobile_friendly', False)}
    - HTTPS: {site_data.get('has_ssl', False)}
    - Image Count: {site_data.get('image_count', 0)}
    - Internal Links: {site_data.get('internal_links', 0)}
    - External Links: {site_data.get('external_links', 0)}
    
    TECHNICAL DATA:
    - Has Canonical URL: {site_data.get('has_canonical', False)}
    - Has Open Graph: {site_data.get('has_og_tags', False)}
    - Has Schema Markup: {site_data.get('has_schema', False)}
    - Gzip Enabled: {site_data.get('has_gzip', False)}
    
    HEADING STRUCTURE:
    {format_headings_data(site_data.get('headings', {}))}
    
    REQUIREMENTS:
    1. Identify the top 3 critical issues affecting SEO performance
    2. Provide specific, actionable recommendations for each issue
    3. Include technical SEO improvements where applicable
    4. Suggest content optimization strategies
    5. Recommend on-page SEO enhancements
    6. Address mobile and performance concerns
    7. Include competitive positioning advice
    8. Provide implementation priority (High/Medium/Low)
    
    Format each recommendation as a clear, actionable tip starting with an action verb.
    """
    
    return prompt

def format_headings_data(headings: Dict[str, int]) -> str:
    """Format heading structure data for AI analysis"""
    if not headings:
        return "No heading structure detected"
    
    formatted = []
    for level, count in headings.items():
        formatted.append(f"  - {level.upper()}: {count} headings")
    
    return "\n".join(formatted)

def parse_ai_tips(ai_response: str) -> List[str]:
    """
    Parse the AI response into a list of clean SEO tips
    
    Args:
        ai_response: Raw text response from the AI
        
    Returns:
        List of cleaned SEO tips
    """
    tips = []
    # Split by common numbering/formatting patterns
    for line in ai_response.split('\n'):
        # Remove numbering and bullet points
        clean_line = line.strip()
        for prefix in ('. ', ') ', '- ', '* ', '• '):
            if clean_line.startswith(prefix):
                clean_line = clean_line[len(prefix):]
                break
                
        # Only include substantial recommendations
        if clean_line and len(clean_line) > 30:
            tips.append(clean_line)
    
    return tips

def generate_rule_based_tips(site_data: Dict[str, Any]) -> List[str]:
    """
    Generate basic SEO tips based on common rules
    
    Args:
        site_data: Dictionary containing website analysis data
        
    Returns:
        List of SEO tips
    """
    tips = []
    
    # Title recommendations
    title = site_data.get('title', '')
    if not title:
        tips.append("Add a proper title tag with target keywords (50-60 characters)")
    elif len(title) > 60:
        tips.append("Shorten title tag to under 60 characters for better display in search results")
    
    # Meta description
    meta_desc = site_data.get('meta_description', '')
    if not meta_desc:
        tips.append("Add a compelling meta description (150-160 characters) to improve click-through rates")
    elif len(meta_desc) > 160:
        tips.append("Shorten meta description to under 160 characters for better search results display")
    
    # Mobile friendliness
    if not site_data.get('mobile_friendly', False):
        tips.append("Optimize website for mobile devices (Google uses mobile-first indexing)")
    
    # SSL certificate
    if not site_data.get('has_ssl', False):
        tips.append("Install SSL certificate to enable HTTPS (ranking factor and improves security)")
    
    # Page speed
    load_time = site_data.get('page_load_time', 0)
    if load_time > 3:
        tips.append(f"Improve page load time (current: {load_time}s, target: under 3s)")
    
    # Content length
    word_count = site_data.get('word_count', 0)
    if word_count < 300:
        tips.append("Increase content length (aim for at least 300 words for better ranking potential)")
    elif word_count > 1500:
        tips.append("Consider breaking up long content into multiple pages or adding better content structure")
    
    # Heading structure
    headings = site_data.get('headings', {})
    if not headings.get('h1', 0):
        tips.append("Add a single H1 tag with primary keywords")
    elif headings.get('h1', 0) > 1:
        tips.append("Reduce to only one H1 tag per page for better SEO structure")
    
    # Images
    if site_data.get('image_count', 0) > 0 and not site_data.get('has_alt_tags', False):
        tips.append("Add alt text to all images for accessibility and SEO benefits")
    
    # Internal linking
    if site_data.get('internal_links', 0) < 5:
        tips.append("Add more internal links to important pages to improve site structure and link equity flow")
    
    return tips[:12]  # Return maximum 12 tips