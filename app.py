# Enhanced AI-Powered Modern Slavery Assessment Backend with Industry Benchmarking & Mapping
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin, urlparse
import sqlite3
from datetime import datetime, timedelta
import json
import numpy as np
from collections import defaultdict
import os

app = Flask(__name__)
CORS(app)

# Configuration - Read environment variables fresh each time they're needed
def get_api_keys():
    """Get fresh API keys from environment variables"""
    return {
        'openai': os.getenv("OPENAI_API_KEY", ""),
        'serper': os.getenv("SERPER_API_KEY", ""),
        'news': os.getenv("NEWS_API_KEY", "")
    }

# DEBUG: Let's see what Railway actually provides
print("🔧 DEBUG: All environment variables with 'API' in name:")
for key, value in os.environ.items():
    if 'API' in key.upper():
        print(f"   {key}: {value[:15]}..." if value else f"   {key}: EMPTY")

print(f"🔧 DEBUG: Total environment variables: {len(os.environ)}")

# Test API keys at startup
api_keys = get_api_keys()
OPENAI_API_KEY = api_keys['openai']
SERPER_API_KEY = api_keys['serper']
NEWS_API_KEY = api_keys['news']

# Risk Intelligence Database
COUNTRY_RISK_INDEX = {
    "North Korea": 90, "Eritrea": 87, "Mauritania": 85, "Saudi Arabia": 82,
    "Turkey": 80, "Tajikistan": 78, "United Arab Emirates": 76, "Russia": 74,
    "Afghanistan": 95, "Myanmar": 88, "Iran": 85, "Pakistan": 83, "India": 81,
    "China": 79, "Nigeria": 77, "Iraq": 75, "Democratic Republic of Congo": 93,
    "Libya": 91, "Yemen": 89, "Syria": 87, "Cambodia": 84, "Bangladesh": 82,
    "Thailand": 78, "Malaysia": 76, "Philippines": 74, "Vietnam": 72,
    "Indonesia": 70, "Mexico": 68, "Brazil": 65, "South Africa": 63,
    "Egypt": 75, "Morocco": 60, "Jordan": 58, "Lebanon": 73,
    "United States": 15, "Canada": 12, "United Kingdom": 13, "Australia": 14,
    "Germany": 11, "France": 12, "Japan": 16, "South Korea": 18,
    "Netherlands": 8, "Sweden": 7, "Norway": 6, "Denmark": 5,
    "Switzerland": 9, "Finland": 8, "New Zealand": 10, "Singapore": 20
}

INDUSTRY_RISK_INDEX = {
    "Fast Fashion": 98, "Textiles and Apparel": 95, "Garment Manufacturing": 96, 
    "Agriculture and Food": 92, "Electronics Manufacturing": 85, "Construction": 80, 
    "Mining and Extractives": 88, "Fishing and Seafood": 92, "Palm Oil": 93, 
    "Cocoa": 91, "Cotton": 89, "Timber": 86, "Brick Making": 94,
    "Solar Panel Manufacturing": 87, "Lithium Battery": 84, "Footwear": 90, 
    "Sportswear": 88, "Athletic Apparel": 88, "Fashion": 85,
    "Manufacturing": 75, "Automotive": 65, "Retail": 60, "E-commerce": 55,
    "Technology Services": 25, "Financial Services": 20, "Professional Services": 15, 
    "Healthcare": 30, "Education": 25, "Software": 20, "Pharmaceuticals": 25,
    "Hospitality and Tourism": 50, "Food Processing": 70, "Beverages": 45,
    "Consumer Goods": 55, "Luxury Goods": 70
}

def clean_json_response(ai_response):
    """Clean AI response to extract valid JSON"""
    if not ai_response:
        return None
        
    cleaned = ai_response.strip()
    
    # Remove markdown code blocks
    if cleaned.startswith('```json'):
        cleaned = cleaned[7:]
    elif cleaned.startswith('```'):
        cleaned = cleaned[3:]
    
    if cleaned.endswith('```'):
        cleaned = cleaned[:-3]
    
    return cleaned.strip()

class EnhancedModernSlaveryAssessment:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def call_openai_api(self, messages, max_tokens=1500, temperature=0.1):
        """OpenAI API call with fresh API key"""
        try:
            # Get fresh API key each time
            current_openai_key = os.getenv("OPENAI_API_KEY", "")
            
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {current_openai_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-4o",
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=45)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"OpenAI API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None
    
    def get_company_profile(self, company_name):
        """Enhanced company profile with AI intelligence"""
        try:
            print(f"Building comprehensive profile for {company_name}...")
            
            messages = [
                {"role": "system", "content": """You are a world-class business intelligence analyst with deep expertise in global supply chains, corporate structures, and modern slavery risks. You have access to comprehensive knowledge about companies, their operations, controversies, and business practices up to your knowledge cutoff."""},
                {"role": "user", "content": f"""
                Provide comprehensive intelligence about {company_name}:
                
                REQUIRED ANALYSIS:
                1. Headquarters country
                2. Primary industry/business model
                3. ALL countries where they have significant operations (manufacturing, sourcing, offices, suppliers)
                4. ALL industry sectors and business lines they operate in
                5. Employee count (approximate)
                6. Business model and supply chain structure
                7. Any known controversies, labor issues, or modern slavery concerns
                8. Risk factors specific to their business model
                
                Be specific about:
                - Manufacturing locations and supplier countries
                - High-risk business practices (fast fashion, agricultural sourcing, etc.)
                - Any known labor controversies or investigations
                - Supply chain complexity and transparency
                
                Respond with ONLY valid JSON:
                {{
                    "headquarters": "country name",
                    "primary_industry": "specific industry/business model",
                    "operating_countries": ["country1", "country2", "country3", "country4", "country5", "country6"],
                    "all_industries": ["industry1", "industry2", "industry3", "industry4"],
                    "employees": number_or_null,
                    "business_model": "detailed description of how they operate",
                    "supply_chain_complexity": "high|medium|low",
                    "known_controversies": ["controversy1", "controversy2"],
                    "risk_indicators": ["risk1", "risk2", "risk3"]
                }}
                """}
            ]
            
            ai_response = self.call_openai_api(messages, max_tokens=800, temperature=0.1)
            
            if ai_response:
                try:
                    cleaned_response = clean_json_response(ai_response)
                    profile = json.loads(cleaned_response)
                    profile['name'] = company_name
                    print(f"Successfully built comprehensive profile for {company_name}")
                    return profile
                except json.JSONDecodeError as e:
                    print(f"Error parsing company profile: {e}")
                    print(f"AI Response: {ai_response}")
            
            # Fallback profile
            return {
                "name": company_name,
                "headquarters": "Unknown",
                "primary_industry": "Unknown", 
                "operating_countries": [],
                "all_industries": [],
                "employees": None,
                "business_model": f"Profile for {company_name}",
                "supply_chain_complexity": "medium",
                "known_controversies": [],
                "risk_indicators": []
            }
            
        except Exception as e:
            print(f"Error building company profile: {e}")
            return {"name": company_name, "operating_countries": [], "all_industries": []}
    
    def calculate_geographic_risk(self, countries, headquarters):
        """Enhanced geographic risk with proper headquarters weighting"""
        if not countries and not headquarters:
            return 50, ["No geographic data available"]
        
        # Headquarters gets 60% weight, operating countries get 40%
        hq_risk = COUNTRY_RISK_INDEX.get(headquarters, 50) if headquarters else 50
        
        if countries:
            # Remove headquarters from operating countries to avoid double counting
            operating_countries = [c for c in countries if c != headquarters]
            if operating_countries:
                country_scores = [COUNTRY_RISK_INDEX.get(country, 50) for country in operating_countries]
                avg_operating_risk = sum(country_scores) / len(country_scores)
                # 60% headquarters, 40% average of operating countries
                final_score = int(0.6 * hq_risk + 0.4 * avg_operating_risk)
            else:
                final_score = hq_risk
        else:
            final_score = hq_risk
        
        # Generate risk details
        risk_details = []
        if headquarters:
            hq_score = COUNTRY_RISK_INDEX.get(headquarters, 50)
            if hq_score > 75:
                risk_details.append(f"High-risk headquarters: {headquarters} (score: {hq_score})")
            elif hq_score > 50:
                risk_details.append(f"Medium-risk headquarters: {headquarters} (score: {hq_score})")
            else:
                risk_details.append(f"Low-risk headquarters: {headquarters} (score: {hq_score})")
        
        for country in countries:
            if country != headquarters:
                score = COUNTRY_RISK_INDEX.get(country, 50)
                if score > 75:
                    risk_details.append(f"High-risk operations: {country} (score: {score})")
                elif score > 50:
                    risk_details.append(f"Medium-risk operations: {country} (score: {score})")
        
        return final_score, risk_details
    
    def calculate_industry_risk(self, industries, business_model):
        """Enhanced industry risk calculation with business model consideration"""
        if not industries:
            return 50, ["No industry data available"]
        
        industry_scores = []
        risk_details = []
        
        # Check for high-risk business model keywords
        high_risk_keywords = {
            "fast fashion": 95,
            "ultra fast fashion": 98,
            "disposable fashion": 95,
            "agricultural": 85,
            "garment": 90,
            "textile": 85,
            "manufacturing": 70,
            "mining": 88,
            "construction": 80
        }
        
        business_model_lower = business_model.lower() if business_model else ""
        for keyword, score in high_risk_keywords.items():
            if keyword in business_model_lower:
                industry_scores.append(score)
                risk_details.append(f"High-risk business model: {keyword} (score: {score})")
        
        # Match industries to risk index
        for industry in industries:
            best_score = 50
            best_match = None
            
            for risk_industry, score in INDUSTRY_RISK_INDEX.items():
                # More aggressive matching for better detection
                industry_words = industry.lower().split()
                risk_words = risk_industry.lower().split()
                
                # Check for any word matches or substring matches
                if (any(word in risk_industry.lower() for word in industry_words) or
                    any(word in industry.lower() for word in risk_words) or
                    industry.lower() in risk_industry.lower() or 
                    risk_industry.lower() in industry.lower()):
                    
                    if abs(score - 50) > abs(best_score - 50):  # Find most extreme score
                        best_match = risk_industry
                        best_score = score
            
            if best_match and best_score != 50:
                industry_scores.append(best_score)
                if best_score > 80:
                    risk_details.append(f"Very high risk industry: {best_match} (score: {best_score})")
                elif best_score > 60:
                    risk_details.append(f"High risk industry: {best_match} (score: {best_score})")
                elif best_score > 40:
                    risk_details.append(f"Medium risk industry: {best_match} (score: {best_score})")
                else:
                    risk_details.append(f"Low risk industry: {best_match} (score: {best_score})")
        
        # Take the highest risk score (most concerning industry)
        final_score = max(industry_scores) if industry_scores else 50
        return final_score, risk_details
    
    # Manufacturing Locations and Mapping
    def get_manufacturing_locations(self, company_name, operating_countries):
        """Get detailed manufacturing location data using AI and free APIs"""
        try:
            print(f"Getting manufacturing locations for {company_name}...")
            
            # Use AI to get specific manufacturing locations
            messages = [
                {"role": "system", "content": "You are a supply chain expert with detailed knowledge of manufacturing locations globally."},
                {"role": "user", "content": f"""
                Provide specific manufacturing and operational locations for {company_name}.
                
                Focus on:
                1. Manufacturing facilities (factories, plants, production sites)
                2. Major supplier locations
                3. Distribution centers
                4. Key operational hubs
                
                For each location provide:
                - City, Country
                - Facility type (manufacturing, supplier, distribution, etc.)
                - Products/services produced there
                - Approximate workforce size if known
                
                Respond with ONLY valid JSON:
                {{
                    "manufacturing_sites": [
                        {{
                            "city": "city name",
                            "country": "country name",
                            "facility_type": "manufacturing|supplier|distribution|office",
                            "products": "what's produced/handled here",
                            "workforce_size": "approximate number or range",
                            "risk_level": "high|medium|low"
                        }}
                    ]
                }}
                """}
            ]
            
            ai_response = self.call_openai_api(messages, max_tokens=1500, temperature=0.1)
            
            if ai_response:
                try:
                    cleaned_response = clean_json_response(ai_response)
                    location_data = json.loads(cleaned_response)
                    
                    # Enhance with geocoding and risk data
                    enhanced_locations = []
                    for site in location_data.get('manufacturing_sites', []):
                        coordinates = self.geocode_location(f"{site['city']}, {site['country']}")
                        
                        # Add country risk level
                        country_risk = COUNTRY_RISK_INDEX.get(site['country'], 50)
                        
                        enhanced_site = {
                            **site,
                            'coordinates': coordinates,
                            'country_risk_score': country_risk,
                            'country_risk_level': self.score_to_level(country_risk)
                        }
                        
                        enhanced_locations.append(enhanced_site)
                    
                    return enhanced_locations
                    
                except json.JSONDecodeError as e:
                    print(f"Error parsing location data: {e}")
            
            # Fallback: create basic locations from operating countries
            fallback_locations = []
            for country in operating_countries[:10]:  # Limit to 10 for performance
                coords = self.geocode_location(country)
                if coords:
                    fallback_locations.append({
                        "city": "Major City",
                        "country": country,
                        "facility_type": "operations",
                        "products": "Various operations",
                        "workforce_size": "Unknown",
                        "coordinates": coords,
                        "country_risk_score": COUNTRY_RISK_INDEX.get(country, 50),
                        "country_risk_level": self.score_to_level(COUNTRY_RISK_INDEX.get(country, 50))
                    })
            
            return fallback_locations
            
        except Exception as e:
            print(f"Error getting manufacturing locations: {e}")
            return []

    def geocode_location(self, location_query):
        """Geocode location using free OpenStreetMap Nominatim API"""
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': location_query,
                'format': 'json',
                'limit': 1
            }
            headers = {
                'User-Agent': 'ModernSlaveryAssessmentTool/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            time.sleep(1)  # Respect rate limits
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return {
                        "lat": float(data[0]['lat']),
                        "lng": float(data[0]['lon'])
                    }
            
            return None
            
        except Exception as e:
            print(f"Error geocoding {location_query}: {e}")
            return None

    def generate_supply_chain_map_data(self, manufacturing_locations, company_name):
        """Generate data for supply chain mapping visualization"""
        try:
            map_data = {
                "company_name": company_name,
                "total_locations": len(manufacturing_locations),
                "risk_summary": {
                    "high_risk_sites": len([s for s in manufacturing_locations if s.get('country_risk_score', 50) > 75]),
                    "medium_risk_sites": len([s for s in manufacturing_locations if 50 <= s.get('country_risk_score', 50) <= 75]),
                    "low_risk_sites": len([s for s in manufacturing_locations if s.get('country_risk_score', 50) < 50])
                },
                "locations": manufacturing_locations,
                "risk_heatmap": self.generate_risk_heatmap(manufacturing_locations),
                "supply_chain_tiers": self.categorize_supply_chain_tiers(manufacturing_locations)
            }
            
            return map_data
            
        except Exception as e:
            print(f"Error generating map data: {e}")
            return {"locations": manufacturing_locations}

    def generate_risk_heatmap(self, locations):
        """Generate risk heatmap data for visualization"""
        risk_zones = {}
        
        for location in locations:
            country = location.get('country')
            risk_score = location.get('country_risk_score', 50)
            
            if country not in risk_zones:
                risk_zones[country] = {
                    "country": country,
                    "risk_score": risk_score,
                    "site_count": 0,
                    "facility_types": []
                }
            
            risk_zones[country]["site_count"] += 1
            if location.get('facility_type') not in risk_zones[country]["facility_types"]:
                risk_zones[country]["facility_types"].append(location.get('facility_type'))
        
        return list(risk_zones.values())

    def categorize_supply_chain_tiers(self, locations):
        """Categorize locations into supply chain tiers"""
        tiers = {
            "tier_1": [],  # Direct suppliers/own facilities
            "tier_2": [],  # Suppliers' suppliers
            "tier_3": []   # Third-tier suppliers
        }
        
        for location in locations:
            facility_type = location.get('facility_type', '').lower()
            
            if facility_type in ['manufacturing', 'office', 'headquarters']:
                tiers["tier_1"].append(location)
            elif facility_type in ['supplier', 'distribution']:
                tiers["tier_2"].append(location)
            else:
                tiers["tier_3"].append(location)
        
        return tiers

    # Dynamic Industry Benchmarking
    def get_ai_industry_analysis(self, primary_industry, all_industries):
        """Use OpenAI to get comprehensive industry analysis"""
        try:
            messages = [
                {"role": "system", "content": """You are a world-class ESG and supply chain risk analyst with comprehensive knowledge of industry benchmarks, modern slavery risks, and corporate compliance across all sectors globally. You have access to extensive databases of corporate performance, industry standards, and regulatory requirements."""},
                {"role": "user", "content": f"""
                Provide comprehensive industry benchmarking intelligence for: {primary_industry}
                Related sectors: {', '.join(all_industries) if all_industries else 'None'}
                
                I need CURRENT, REALISTIC industry intelligence including:
                
                1. MODERN SLAVERY RISK ASSESSMENT:
                - Typical risk score range for this industry (15-95 scale)
                - Most common modern slavery risks specific to this sector
                - Geographic hotspots where this industry typically operates
                
                2. INDUSTRY PERFORMANCE BENCHMARKS:
                - Average modern slavery risk score for companies in this sector
                - Percentage of companies with strong vs weak policies
                - Typical audit completion rates and compliance levels
                
                3. PEER COMPANIES & BEST PRACTICES:
                - 8-10 major companies in this industry (global leaders)
                - Companies known for best practices in labor standards
                - Companies that have faced modern slavery issues
                
                4. REGULATORY LANDSCAPE:
                - Key regulations affecting this industry
                - Emerging compliance requirements
                - Industry-specific due diligence standards
                
                5. SUPPLY CHAIN CHARACTERISTICS:
                - Typical supply chain complexity (high/medium/low)
                - Common supplier countries and regions
                - Most vulnerable points in the supply chain
                
                Be specific to the actual industry, not generic. Use real company names and current industry knowledge.
                
                Respond with ONLY valid JSON:
                {{
                    "industry_name": "{primary_industry}",
                    "risk_profile": {{
                        "average_risk_score": number_between_15_and_95,
                        "risk_score_range": {{"min": number, "max": number}},
                        "risk_level_distribution": {{"low": percentage, "medium": percentage, "high": percentage}}
                    }},
                    "common_risks": ["risk1", "risk2", "risk3", "risk4", "risk5"],
                    "geographic_hotspots": ["country1", "country2", "country3", "country4"],
                    "peer_companies": {{
                        "industry_leaders": ["company1", "company2", "company3", "company4"],
                        "best_practice_companies": ["company1", "company2"],
                        "companies_with_issues": ["company1", "company2"]
                    }},
                    "regulatory_landscape": ["regulation1", "regulation2", "regulation3"],
                    "supply_chain_complexity": "high|medium|low",
                    "vulnerable_supply_chain_points": ["point1", "point2", "point3"],
                    "industry_best_practices": ["practice1", "practice2", "practice3", "practice4"],
                    "performance_benchmarks": {{
                        "policy_coverage": "percentage of companies with policies",
                        "audit_completion": "typical audit rates",
                        "transparency_level": "industry transparency rating"
                    }}
                }}
                """}
            ]
            
            ai_response = self.call_openai_api(messages, max_tokens=2000, temperature=0.1)
            
            if ai_response:
                try:
                    cleaned_response = clean_json_response(ai_response)
                    return json.loads(cleaned_response)
                except json.JSONDecodeError as e:
                    print(f"Error parsing AI industry analysis: {e}")
            
            return None
            
        except Exception as e:
            print(f"Error in AI industry analysis: {e}")
            return None

    def get_industry_esg_data(self, industry):
        """Get ESG performance data using free APIs"""
        try:
            # Use GDELT to find ESG-related news for the industry
            gdelt_url = "https://api.gdeltproject.org/api/v2/doc/doc"
            
            params = {
                'query': f'"{industry}" AND ("ESG" OR "sustainability" OR "labor practices" OR "supply chain" OR "modern slavery")',
                'mode': 'timelinevol',
                'timespan': '1year',
                'format': 'json'
            }
            
            response = requests.get(gdelt_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyze ESG sentiment and frequency
                total_mentions = sum(int(item.get('count', 0)) for item in data.get('timeline', []))
                
                return {
                    'esg_news_volume': total_mentions,
                    'esg_sentiment': 'high' if total_mentions > 100 else 'medium' if total_mentions > 20 else 'low',
                    'recent_esg_focus': total_mentions > 50
                }
            
            return {'esg_news_volume': 0, 'esg_sentiment': 'low'}
            
        except Exception as e:
            print(f"Error getting ESG data: {e}")
            return {}

    def get_supply_chain_incidents_data(self, industry):
        """Get supply chain incident data for industry benchmarking"""
        try:
            # Search multiple sources for supply chain incidents
            total_incidents = 0
            recent_incidents = 0
            
            # GDELT for incident tracking
            gdelt_url = "https://api.gdeltproject.org/api/v2/doc/doc"
            
            incident_queries = [
                f'"{industry}" AND ("forced labor" OR "modern slavery" OR "labor violation")',
                f'"{industry}" AND ("supply chain audit" OR "factory inspection" OR "labor investigation")'
            ]
            
            for query in incident_queries:
                params = {
                    'query': query,
                    'mode': 'timelinevol',
                    'timespan': '2years',
                    'format': 'json'
                }
                
                response = requests.get(gdelt_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    timeline = data.get('timeline', [])
                    
                    for item in timeline:
                        count = int(item.get('count', 0))
                        total_incidents += count
                        
                        # Check if recent (last 6 months)
                        date_str = item.get('date', '')
                        if date_str and len(date_str) >= 8:
                            try:
                                item_date = datetime.strptime(date_str[:8], '%Y%m%d')
                                if item_date > datetime.now() - timedelta(days=180):
                                    recent_incidents += count
                            except ValueError:
                                pass
                
                time.sleep(0.5)  # Rate limiting
            
            # Calculate industry incident risk level
            incident_risk = 'high' if total_incidents > 100 else 'medium' if total_incidents > 20 else 'low'
            
            return {
                'total_incidents_2years': total_incidents,
                'recent_incidents_6months': recent_incidents,
                'incident_risk_level': incident_risk,
                'incident_trend': 'increasing' if recent_incidents > total_incidents * 0.3 else 'stable'
            }
            
        except Exception as e:
            print(f"Error getting supply chain incidents data: {e}")
            return {}

    def synthesize_industry_benchmark(self, industry_intel, esg_data, incidents_data):
        """Combine all data sources into comprehensive benchmark"""
        try:
            if not industry_intel:
                return None
            
            # Calculate dynamic industry average based on AI analysis
            base_score = industry_intel.get('risk_profile', {}).get('average_risk_score', 55)
            
            # Adjust based on ESG sentiment and incidents
            esg_adjustment = 0
            if esg_data.get('esg_sentiment') == 'high':
                esg_adjustment = -5  # Lower risk if high ESG focus
            elif esg_data.get('esg_sentiment') == 'low':
                esg_adjustment = 5   # Higher risk if low ESG focus
            
            # Adjust based on incidents
            incident_adjustment = 0
            if incidents_data.get('incident_risk_level') == 'high':
                incident_adjustment = 8
            elif incidents_data.get('incident_risk_level') == 'low':
                incident_adjustment = -3
            
            adjusted_industry_score = max(15, min(95, base_score + esg_adjustment + incident_adjustment))
            
            return {
                "matched_industry": industry_intel.get('industry_name'),
                "industry_average_score": adjusted_industry_score,
                "data_sources": ["OpenAI Industry Intelligence", "GDELT ESG Analysis", "GDELT Incident Analysis"],
                "peer_companies": industry_intel.get('peer_companies', {}).get('industry_leaders', []),
                "industry_common_risks": industry_intel.get('common_risks', []),
                "industry_best_practices": industry_intel.get('industry_best_practices', []),
                "regulatory_focus": industry_intel.get('regulatory_landscape', []),
                "supply_chain_complexity": industry_intel.get('supply_chain_complexity', 'medium'),
                "performance_insights": {
                    "risk_distribution": industry_intel.get('risk_profile', {}).get('risk_level_distribution', {}),
                    "esg_sentiment": esg_data.get('esg_sentiment', 'unknown'),
                    "incident_analysis": incidents_data
                },
                "benchmark_quality": "high" if industry_intel and esg_data else "medium",
                "last_updated": datetime.now().strftime("%Y-%m-%d")
            }
            
        except Exception as e:
            print(f"Error synthesizing benchmark: {e}")
            return None

    def get_dynamic_industry_benchmark(self, company_name, primary_industry, all_industries):
        """Get real industry benchmarking data using AI and free APIs"""
        try:
            print(f"Getting dynamic industry benchmark for {primary_industry}...")
            
            # Step 1: Use OpenAI to get comprehensive industry intelligence
            industry_intelligence = self.get_ai_industry_analysis(primary_industry, all_industries)
            
            # Step 2: Get ESG/CSR data from free sources
            esg_data = self.get_industry_esg_data(primary_industry)
            
            # Step 3: Get incident data
            incidents_data = self.get_supply_chain_incidents_data(primary_industry)
            
            # Step 4: Combine all data for comprehensive benchmark
            benchmark = self.synthesize_industry_benchmark(
                industry_intelligence, esg_data, incidents_data
            )
            
            return benchmark
            
        except Exception as e:
            print(f"Error getting dynamic industry benchmark: {e}")
            return None

    def calculate_dynamic_percentile(self, company_score, industry_avg, risk_distribution):
        """Calculate percentile based on actual industry distribution"""
        try:
            if not risk_distribution:
                # Fallback to simple calculation
                return self.calculate_percentile(company_score, industry_avg)
            
            # Use actual distribution if available
            low_pct = risk_distribution.get('low', 30)
            medium_pct = risk_distribution.get('medium', 50)
            high_pct = risk_distribution.get('high', 20)
            
            if company_score <= 35:
                return f"Top {low_pct}% (Low Risk)"
            elif company_score <= 65:
                return f"Middle {medium_pct}% (Medium Risk)"
            else:
                return f"Bottom {high_pct}% (High Risk)"
                
        except Exception as e:
            return "Percentile calculation unavailable"

    def calculate_percentile(self, company_score, industry_avg):
        """Calculate approximate percentile ranking"""
        # Simplified percentile calculation
        if company_score <= industry_avg - 20:
            return "Top 10%"
        elif company_score <= industry_avg - 10:
            return "Top 25%"
        elif company_score <= industry_avg + 5:
            return "Average (50th percentile)"
        elif company_score <= industry_avg + 15:
            return "Below average (75th percentile)"
        else:
            return "Bottom 10%"

    def generate_industry_comparison(self, company_score, company_industries, primary_industry):
        """Generate dynamic industry comparison"""
        try:
            # Get dynamic benchmark data
            benchmark_data = self.get_dynamic_industry_benchmark(
                "", primary_industry, company_industries
            )
            
            if not benchmark_data:
                return None
            
            industry_avg = benchmark_data['industry_average_score']
            performance_vs_peers = "above average" if company_score < industry_avg else "below average"
            score_difference = abs(company_score - industry_avg)
            
            # Calculate percentile based on industry distribution
            percentile = self.calculate_dynamic_percentile(
                company_score, 
                industry_avg, 
                benchmark_data.get('performance_insights', {}).get('risk_distribution', {})
            )
            
            return {
                "matched_industry": benchmark_data['matched_industry'],
                "industry_average_score": industry_avg,
                "company_score": company_score,
                "performance_vs_peers": performance_vs_peers,
                "score_difference": score_difference,
                "percentile_ranking": percentile,
                "peer_companies": benchmark_data['peer_companies'],
                "industry_common_risks": benchmark_data['industry_common_risks'],
                "industry_best_practices": benchmark_data['industry_best_practices'],
                "regulatory_focus": benchmark_data['regulatory_focus'],
                "benchmark_insights": self.generate_benchmark_insights(
                    company_score, industry_avg, performance_vs_peers, benchmark_data
                ),
                "data_quality": benchmark_data.get('benchmark_quality', 'medium'),
                "last_updated": benchmark_data.get('last_updated')
            }
            
        except Exception as e:
            print(f"Error generating dynamic industry comparison: {e}")
            return None

    def generate_benchmark_insights(self, company_score, industry_avg, performance, benchmark_data):
        """Generate insights based on dynamic benchmark data"""
        insights = []
        
        score_diff = abs(company_score - industry_avg)
        
        if performance == "above average":
            insights.append(f"Company risk score is {score_diff} points below industry average of {industry_avg}")
            insights.append("Performance is better than typical industry peers")
            
            # Add specific insights based on benchmark data
            if benchmark_data.get('performance_insights', {}).get('esg_sentiment') == 'high':
                insights.append("Industry has high ESG focus - company aligns with positive trend")
        else:
            insights.append(f"Company risk score is {score_diff} points above industry average of {industry_avg}")
            insights.append("Higher risk profile requires attention to industry-specific challenges")
            
            # Add specific improvement areas
            if benchmark_data.get('industry_common_risks'):
                top_risk = benchmark_data['industry_common_risks'][0]
                insights.append(f"Focus on industry's top risk: {top_risk}")
        
        # Add regulatory insights
        if benchmark_data.get('regulatory_focus'):
            insights.append(f"Key regulatory focus: {', '.join(benchmark_data['regulatory_focus'][:2])}")
        
        return insights

    # Enhanced API Data Collection
    def get_economic_indicators(self, countries):
        """Get economic data from World Bank API (free)"""
        try:
            economic_data = {}
            
            for country in countries[:5]:  # Limit for performance
                # World Bank API for GDP per capita
                wb_url = f"https://api.worldbank.org/v2/country/{country}/indicator/NY.GDP.PCAP.CD"
                params = {'format': 'json', 'date': '2022:2023', 'per_page': 1000}
                
                response = requests.get(wb_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 1 and data[1]:
                        gdp_data = data[1][0] if data[1] else None
                        if gdp_data and gdp_data.get('value'):
                            economic_data[country] = {
                                'gdp_per_capita': gdp_data['value'],
                                'year': gdp_data['date'],
                                'economic_risk_factor': 'high' if gdp_data['value'] < 5000 else 'medium' if gdp_data['value'] < 15000 else 'low'
                            }
                
                time.sleep(0.5)  # Rate limiting
            
            return economic_data
            
        except Exception as e:
            print(f"Error getting economic indicators: {e}")
            return {}

    def get_enhanced_news_data(self, company_name):
        """Get enhanced news data using GDELT (free)"""
        try:
            # GDELT Global Knowledge Graph API (free)
            gdelt_url = "https://api.gdeltproject.org/api/v2/doc/doc"
            
            params = {
                'query': f'{company_name} AND ("forced labor" OR "modern slavery" OR "human trafficking" OR "labor rights")',
                'mode': 'artlist',
                'maxrecords': 10,
                'format': 'json'
            }
            
            response = requests.get(gdelt_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                enhanced_news = []
                for article in articles:
                    enhanced_news.append({
                        'title': article.get('title', ''),
                        'url': article.get('url', ''),
                        'date': article.get('seendate', ''),
                        'domain': article.get('domain', ''),
                        'language': article.get('language', ''),
                        'tone': article.get('tone', 0),  # GDELT tone score
                        'source_country': article.get('sourcecountry', '')
                    })
                
                return enhanced_news
            
            return []
            
        except Exception as e:
            print(f"Error getting GDELT news data: {e}")
            return []

    def enhance_assessment_with_apis(self, company_name, operating_countries):
        """Enhance assessment with all free API data"""
        try:
            print("Enhancing assessment with additional API data...")
            
            enhanced_data = {
                'economic_indicators': self.get_economic_indicators(operating_countries),
                'enhanced_news': self.get_enhanced_news_data(company_name),
            }
            
            # Generate additional risk insights from API data
            api_risk_factors = self.analyze_api_risk_factors(enhanced_data)
            
            enhanced_data['api_risk_factors'] = api_risk_factors
            enhanced_data['data_sources_used'] = [
                'World Bank Economic Data',
                'GDELT News Analysis',
                'OpenStreetMap Geocoding'
            ]
            
            return enhanced_data
            
        except Exception as e:
            print(f"Error enhancing with APIs: {e}")
            return {}

    def analyze_api_risk_factors(self, enhanced_data):
        """Analyze risk factors from API data"""
        risk_factors = []
        
        # Economic risk analysis
        economic_data = enhanced_data.get('economic_indicators', {})
        for country, data in economic_data.items():
            if data.get('economic_risk_factor') == 'high':
                risk_factors.append({
                    'factor': f'Low GDP per capita in {country}',
                    'impact': 'medium',
                    'evidence': f'GDP per capita: ${data.get("gdp_per_capita", 0):,.0f} indicates economic vulnerability'
                })
        
        return risk_factors
    
    def comprehensive_ai_analysis(self, company_data):
        """Enhanced AI analysis with more aggressive and specific scoring"""
        try:
            profile = company_data['profile']
            geographic_risk = company_data['geographic_risk']
            industry_risk = company_data['industry_risk']
            
            # Build comprehensive context for AI
            context_prompt = f"""
            COMPREHENSIVE MODERN SLAVERY RISK ASSESSMENT
            
            COMPANY: {profile['name']}
            
            DETAILED COMPANY INTELLIGENCE:
            - Headquarters: {profile.get('headquarters', 'Unknown')}
            - Primary Industry: {profile.get('primary_industry', 'Unknown')}
            - Business Model: {profile.get('business_model', 'Unknown')}
            - Supply Chain Complexity: {profile.get('supply_chain_complexity', 'Unknown')}
            - Operating Countries: {profile.get('operating_countries', [])}
            - All Industries: {profile.get('all_industries', [])}
            - Employees: {profile.get('employees', 'Unknown')}
            - Known Controversies: {profile.get('known_controversies', [])}
            - Risk Indicators: {profile.get('risk_indicators', [])}
            
            CALCULATED RISK CONTEXT:
            - Geographic Risk: {geographic_risk['score']}/100 - {geographic_risk['details']}
            - Industry Risk: {industry_risk['score']}/100 - {industry_risk['details']}
            
            ASSESSMENT INSTRUCTIONS:
            You are the world's leading expert on modern slavery risk assessment. Provide a comprehensive, specific, and accurate assessment based on:
            
            1. The company's actual business practices and controversies
            2. Industry-specific vulnerabilities (fast fashion, agriculture, manufacturing, etc.)
            3. Geographic risks from operations in high-risk countries
            4. Supply chain complexity and transparency
            5. Known incidents, investigations, or concerns
            
            SCORING GUIDELINES - BE SPECIFIC AND DIFFERENTIATED:
            - Fast fashion companies (Shein, H&M, etc.): 70-95 (very high risk)
            - Agricultural/food companies with complex supply chains: 60-85
            - Sportswear/apparel with overseas manufacturing: 60-80  
            - Technology companies with ethical practices: 15-35
            - Pharmaceutical companies: 20-40
            - Companies with strong ESG/B-Corp credentials: 15-40
            - Companies with known modern slavery issues: 75-95
            - Companies with transparent, ethical supply chains: 15-45
            
            Focus on ACTUAL RISKS not theoretical ones. Be specific about the company's business model and practices.
            
            Respond with ONLY valid JSON (no markdown):
            {{
                "overall_risk_score": integer_15_to_95,
                "overall_risk_level": "low|medium|high|very-high",
                "confidence_level": "high|medium|low",
                "category_scores": {{
                    "policy_governance": integer_0_to_100,
                    "due_diligence": integer_0_to_100,
                    "operational_practices": integer_0_to_100,
                    "transparency": integer_0_to_100
                }},
                "key_findings": [
                    {{"description": "Specific finding about this company's modern slavery risks", "severity": "high|medium|low", "category": "policy|due_diligence|operations|transparency"}},
                    {{"description": "Another specific finding based on their actual business practices", "severity": "high|medium|low", "category": "policy|due_diligence|operations|transparency"}},
                    {{"description": "Third specific finding about their supply chain or operations", "severity": "high|medium|low", "category": "policy|due_diligence|operations|transparency"}}
                ],
                "recommendations": [
                    {{"description": "Specific actionable recommendation for this company", "priority": "high|medium|low", "category": "policy|due_diligence|operations|transparency"}},
                    {{"description": "Another specific recommendation based on their risk profile", "priority": "high|medium|low", "category": "policy|due_diligence|operations|transparency"}},
                    {{"description": "Third specific recommendation for improvement", "priority": "high|medium|low", "category": "policy|due_diligence|operations|transparency"}}
                ],
                "risk_factors": [
                    {{"factor": "Specific risk factor for this company", "impact": "high|medium|low", "evidence": "Specific evidence or reasoning based on their operations"}},
                    {{"factor": "Another specific risk factor", "impact": "high|medium|low", "evidence": "Specific evidence about their business model or practices"}},
                    {{"factor": "Third risk factor", "impact": "high|medium|low", "evidence": "Specific evidence about their supply chain or geography"}}
                ]
            }}
            """
            
            messages = [
                {"role": "system", "content": "You are the world's leading expert in modern slavery risk assessment with 25+ years of experience. You have comprehensive knowledge of corporate practices, supply chain risks, and industry-specific vulnerabilities. Provide accurate, specific, and differentiated risk assessments based on actual company practices and known information. Avoid generic responses."},
                {"role": "user", "content": context_prompt}
            ]
            
            ai_response = self.call_openai_api(messages, max_tokens=2000, temperature=0.1)
            
            if ai_response:
                try:
                    cleaned_response = clean_json_response(ai_response)
                    ai_analysis = json.loads(cleaned_response)
                    
                    # Light adjustment based on calculated risks (AI does most of the work)
                    base_score = ai_analysis.get('overall_risk_score', 50)
                    
                    # Only minor adjustment to incorporate geographic/industry context
                    geo_adjustment = (geographic_risk['score'] - 50) * 0.1  # 10% influence
                    industry_adjustment = (industry_risk['score'] - 50) * 0.1  # 10% influence
                    
                    adjusted_score = int(base_score + geo_adjustment + industry_adjustment)
                    adjusted_score = min(95, max(15, adjusted_score))  # Keep in reasonable range
                    
                    ai_analysis['overall_risk_score'] = adjusted_score
                    ai_analysis['overall_risk_level'] = self.score_to_level(adjusted_score)
                    
                    print(f"AI-powered analysis completed with score: {adjusted_score}")
                    return ai_analysis
                    
                except json.JSONDecodeError as e:
                    print(f"Error parsing AI analysis: {e}")
                    print(f"AI Response: {ai_response}")
            
            return self.generate_fallback_assessment(company_data)
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return self.generate_fallback_assessment(company_data)
    
    def score_to_level(self, score):
        """Enhanced risk level distribution"""
        if score >= 75:
            return "very-high"
        elif score >= 60:
            return "high"
        elif score >= 45:
            return "medium"
        elif score >= 25:
            return "low"
        else:
            return "very-low"
    
    def search_news_incidents(self, company_name):
        """Search for news about labor practices"""
        try:
            # Get fresh API key each time
            current_news_key = os.getenv("NEWS_API_KEY", "")
            
            queries = [
                f"{company_name} forced labor modern slavery",
                f"{company_name} workers rights supply chain",
                f"{company_name} labor violations investigation"
            ]
            
            news_results = []
            for query in queries[:2]:
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': query,
                    'sortBy': 'publishedAt',
                    'pageSize': 3,
                    'apiKey': current_news_key,
                    'language': 'en',
                    'from': (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')  # 2 years
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    news_data = response.json()
                    for article in news_data.get('articles', []):
                        news_results.append({
                            'title': article['title'],
                            'url': article['url'], 
                            'description': article['description'],
                            'publishedAt': article['publishedAt'],
                            'source': article['source']['name']
                        })
                
                time.sleep(0.5)
            
            return news_results
            
        except Exception as e:
            print(f"Error searching news: {e}")
            return []
    
    def assess_company(self, company_name):
        """Main comprehensive assessment function"""
        try:
            print(f"Starting AI-powered assessment for: {company_name}")
            
            # Step 1: Build comprehensive company profile with AI
            profile = self.get_company_profile(company_name)
            print(f"Profile: {profile.get('name')} - {profile.get('primary_industry')}")
            
            # Step 2: Calculate enhanced geographic risk
            geo_risk_score, geo_details = self.calculate_geographic_risk(
                profile.get('operating_countries', []),
                profile.get('headquarters')
            )
            print(f"Geographic risk: {geo_risk_score}")
            
            # Step 3: Calculate enhanced industry risk
            industry_risk_score, industry_details = self.calculate_industry_risk(
                profile.get('all_industries', []),
                profile.get('business_model', '')
            )
            print(f"Industry risk: {industry_risk_score}")
            
            # Step 4: Get manufacturing locations and map data
            manufacturing_locations = self.get_manufacturing_locations(
                company_name, 
                profile.get('operating_countries', [])
            )
            
            supply_chain_map = self.generate_supply_chain_map_data(
                manufacturing_locations, 
                company_name
            )
            
            # Step 5: Gather news data
            news_data = self.search_news_incidents(company_name)
            print(f"Found {len(news_data)} news articles")
            
            # Step 6: Enhanced API data
            enhanced_api_data = self.enhance_assessment_with_apis(
                company_name,
                profile.get('operating_countries', [])
            )
            
            # Step 7: AI-powered comprehensive analysis
            company_data = {
                'profile': profile,
                'geographic_risk': {'score': geo_risk_score, 'details': geo_details},
                'industry_risk': {'score': industry_risk_score, 'details': industry_details},
                'news': news_data
            }
            
            print("Performing AI-powered comprehensive analysis...")
            ai_analysis = self.comprehensive_ai_analysis(company_data)
            
            # Step 8: Generate industry benchmarking
            industry_comparison = self.generate_industry_comparison(
                ai_analysis['overall_risk_score'],
                profile.get('all_industries', []),
                profile.get('primary_industry')
            )
            
            # Merge API risk factors with existing risk factors
            if enhanced_api_data.get('api_risk_factors'):
                existing_factors = ai_analysis.get('risk_factors', [])
                combined_factors = existing_factors + enhanced_api_data['api_risk_factors']
                ai_analysis['risk_factors'] = combined_factors
            
            # Step 9: Format final response
            final_assessment = {
                'company_name': company_name,
                'assessment_id': f"ASSESS_{int(time.time())}",
                'assessment_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                
                'overall_risk_level': ai_analysis['overall_risk_level'],
                'overall_risk_score': ai_analysis['overall_risk_score'],
                'confidence_level': ai_analysis.get('confidence_level', 'high'),
                
                'category_scores': ai_analysis.get('category_scores', {}),
                'geographic_risk': {
                    'score': geo_risk_score,
                    'level': self.score_to_level(geo_risk_score),
                    'operating_countries': profile.get('operating_countries', []),
                    'details': geo_details
                },
                'industry_risk': {
                    'score': industry_risk_score,
                    'level': self.score_to_level(industry_risk_score),
                    'industries': profile.get('all_industries', []),
                    'details': industry_details
                },
                
                'key_findings': ai_analysis.get('key_findings', []),
                'recommendations': ai_analysis.get('recommendations', []),
                'risk_factors': ai_analysis.get('risk_factors', []),
                'risk_indicators': [f['description'] for f in ai_analysis.get('key_findings', [])],  # For frontend compatibility
                
                'company_profile': profile,
                'manufacturing_locations': manufacturing_locations,
                'supply_chain_map': supply_chain_map,
                'industry_benchmarking': industry_comparison,
                'enhanced_data': enhanced_api_data,
                
                'data_sources': {
                    'news_articles': len(news_data),
                    'geographic_data': len(profile.get('operating_countries', [])),
                    'industry_data': len(profile.get('all_industries', [])),
                    'manufacturing_sites': len(manufacturing_locations),
                    'api_sources': len(enhanced_api_data.get('data_sources_used', []))
                },
                
                'status': 'completed'
            }
            
            print(f"AI-powered assessment completed for {company_name}")
            return final_assessment
            
        except Exception as e:
            print(f"Error in comprehensive assessment: {e}")
            return {
                'error': f'Assessment failed: {str(e)}',
                'company_name': company_name,
                'status': 'failed'
            }
    
    def generate_fallback_assessment(self, company_data):
        """Generate fallback assessment if AI fails"""
        profile = company_data.get('profile', {})
        geo_risk = company_data.get('geographic_risk', {}).get('score', 50)
        industry_risk = company_data.get('industry_risk', {}).get('score', 50)
        
        fallback_score = int((geo_risk + industry_risk) / 2)
        
        return {
            "overall_risk_score": fallback_score,
            "overall_risk_level": self.score_to_level(fallback_score),
            "confidence_level": "low",
            "category_scores": {
                "policy_governance": fallback_score,
                "due_diligence": fallback_score,
                "operational_practices": fallback_score,
                "transparency": fallback_score
            },
            "key_findings": [
                {"description": "AI analysis unavailable - using baseline risk assessment", "severity": "medium", "category": "system"},
                {"description": f"Geographic risk: {geo_risk}/100 based on operating countries", "severity": "medium", "category": "geographic"},
                {"description": f"Industry risk: {industry_risk}/100 based on business sectors", "severity": "medium", "category": "industry"}
            ],
            "recommendations": [
                {"description": "Conduct comprehensive supply chain audit", "priority": "high", "category": "due_diligence"},
                {"description": "Implement modern slavery monitoring systems", "priority": "medium", "category": "operations"}
            ],
            "risk_factors": [
                {"factor": "Limited assessment data available", "impact": "medium", "evidence": "AI analysis unavailable"},
                {"factor": "Geographic risk factors", "impact": "medium", "evidence": f"Operations in countries with risk score {geo_risk}"}
            ]
        }

# Flask API endpoints
@app.route('/assess', methods=['POST'])
def assess_company():
    try:
        data = request.get_json()
        company_name = data.get('company_name')
        
        if not company_name:
            return jsonify({'error': 'Company name required'}), 400
        
        print(f"Received assessment request for: {company_name}")
        
        assessor = EnhancedModernSlaveryAssessment()
        result = assessor.assess_company(company_name)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test-openai', methods=['GET'])
def test_openai():
    try:
        assessor = EnhancedModernSlaveryAssessment()
        response = assessor.call_openai_api([
            {"role": "user", "content": "Hello, please respond with 'Enhanced AI OpenAI system working correctly!'"}
        ], max_tokens=20)
        
        if response:
            return jsonify({"status": "success", "response": response})
        else:
            return jsonify({"status": "failed", "error": "No response from OpenAI"})
            
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@app.route('/health', methods=['GET'])
def get_status():
    # Get fresh API keys directly from environment
    current_openai_key = os.getenv("OPENAI_API_KEY", "")
    current_serper_key = os.getenv("SERPER_API_KEY", "")
    current_news_key = os.getenv("NEWS_API_KEY", "")
    
    return jsonify({
        'status': 'healthy',
        'message': 'Enhanced AI-Powered Modern Slavery Assessment API with Industry Benchmarking & Mapping',
        'features': [
            'GPT-4o powered intelligent analysis',
            'Dynamic industry benchmarking with real data',
            'Global manufacturing mapping',
            'Enhanced geographic risk calculation',
            'Advanced industry risk detection',
            'Comprehensive company profiling',
            'Supply chain visualization',
            'Free API data integration (World Bank, GDELT, OpenStreetMap)',
            'Differentiated risk scoring (15-95 range)',
            'Company-specific intelligence gathering'
        ],
        'api_keys_configured': {
            'openai': bool(current_openai_key and len(current_openai_key) > 20),
            'serper': bool(current_serper_key and len(current_serper_key) > 10),
            'news_api': bool(current_news_key and len(current_news_key) > 10)
        }
    })

@app.route('/debug-health', methods=['GET'])
def debug_health():
    # Get fresh API keys directly from environment
    current_openai_key = os.getenv("OPENAI_API_KEY", "")
    current_serper_key = os.getenv("SERPER_API_KEY", "")
    current_news_key = os.getenv("NEWS_API_KEY", "")
    
    return jsonify({
        'OPENAI_API_KEY_value': current_openai_key[:15] if current_openai_key else 'EMPTY',
        'OPENAI_API_KEY_length': len(current_openai_key),
        'OPENAI_API_KEY_bool': bool(current_openai_key),
        'length_check': len(current_openai_key) > 20,
        'combined_check': bool(current_openai_key and len(current_openai_key) > 20),
        'SERPER_API_KEY_bool': bool(current_serper_key),
        'NEWS_API_KEY_bool': bool(current_news_key),
        'startup_would_show': "✅" if current_openai_key and len(current_openai_key) > 20 else "❌",
        'environment_check': {
            'OPENAI_in_environ': 'OPENAI_API_KEY' in os.environ,
            'total_environ_vars': len(os.environ),
            'api_vars_in_environ': [k for k in os.environ.keys() if 'API' in k.upper()]
        }
    })

@app.route('/debug-env', methods=['GET'])
def debug_env():
    return jsonify({
        'openai_present': 'OPENAI_API_KEY' in os.environ,
        'openai_length': len(os.environ.get('OPENAI_API_KEY', '')),
        'openai_starts_with': os.environ.get('OPENAI_API_KEY', '')[:15] if os.environ.get('OPENAI_API_KEY') else 'NONE',
        'all_api_vars': {k: v[:15] + "..." if v and len(v) > 15 else v for k, v in os.environ.items() if 'API' in k.upper()}
    })

@app.route('/search/companies', methods=['GET'])
def search_companies():
    query = request.args.get('q', '')
    suggestions = [
        {"name": query, "description": "Exact match", "industry": "Various"},
        {"name": f"{query} Inc.", "description": "Corporation", "industry": "Technology"},
        {"name": f"{query} Corporation", "description": "Large corporation", "industry": "Manufacturing"}
    ]
    return jsonify({"companies": suggestions})

if __name__ == '__main__':
    print("🚀 Enhanced AI-Powered Modern Slavery Assessment API Starting...")
    print("📡 Backend running on: http://localhost:5000")
    
    # Check API keys at startup using fresh reads
    startup_openai_key = os.getenv("OPENAI_API_KEY", "")
    startup_serper_key = os.getenv("SERPER_API_KEY", "")
    startup_news_key = os.getenv("NEWS_API_KEY", "")
    
    print("🔑 OpenAI API Key configured:", "✅" if startup_openai_key and len(startup_openai_key) > 20 else "❌")
    print("🔑 Serper API Key configured:", "✅" if startup_serper_key and len(startup_serper_key) > 10 else "❌")
    print("🔑 News API Key configured:", "✅" if startup_news_key and len(startup_news_key) > 10 else "❌")
    print("🧠 Using GPT-4o for intelligent, differentiated risk assessment")
    print("🎯 Enhanced Features:")
    print("   - Comprehensive company intelligence gathering")
    print("   - Dynamic industry benchmarking with real data")
    print("   - Global manufacturing mapping with geocoding")
    print("   - Advanced geographic & industry risk calculation")
    print("   - AI-powered specific risk analysis")
    print("   - Free API integration (World Bank, GDELT, OpenStreetMap)")
    print("   - Supply chain visualization and mapping")
    print("   - Differentiated scoring (15-95 range)")
    print("   - Fixed risk level thresholds for better differentiation")
    print("🌐 Ready for comprehensive AI-powered assessments with mapping and benchmarking!")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)