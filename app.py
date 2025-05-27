# Enhanced AI-Powered Modern Slavery Assessment Backend
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
            
            # Step 4: Gather news data
            news_data = self.search_news_incidents(company_name)
            print(f"Found {len(news_data)} news articles")
            
            # Step 5: AI-powered comprehensive analysis
            company_data = {
                'profile': profile,
                'geographic_risk': {'score': geo_risk_score, 'details': geo_details},
                'industry_risk': {'score': industry_risk_score, 'details': industry_details},
                'news': news_data
            }
            
            print("Performing AI-powered comprehensive analysis...")
            ai_analysis = self.comprehensive_ai_analysis(company_data)
            
            # Step 6: Format final response
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
                'data_sources': {
                    'news_articles': len(news_data),
                    'geographic_data': len(profile.get('operating_countries', [])),
                    'industry_data': len(profile.get('all_industries', []))
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
        'message': 'Enhanced AI-Powered Modern Slavery Assessment API',
        'features': [
            'GPT-4o powered intelligent analysis',
            'Enhanced geographic risk calculation',
            'Advanced industry risk detection',
            'Comprehensive company profiling',
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
    print("   - Advanced geographic & industry risk calculation")
    print("   - AI-powered specific risk analysis")
    print("   - Differentiated scoring (15-95 range)")
    print("   - Fixed risk level thresholds for better differentiation")
    print("🌐 Ready for comprehensive AI-powered assessments!")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)