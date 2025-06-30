# AI-Powered Dynamic Modern Slavery Assessment Backend
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime, timedelta
import os
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
import logging

app = Flask(__name__)
CORS(app)

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'your_news_api_key_here')
WORLD_BANK_API_BASE = "https://api.worldbank.org/v2"
ILO_API_BASE = "https://www.ilo.org/api"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIInsightGenerator:
    """AI-powered insight generation using OpenAI"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    async def generate_country_risk_analysis(self, country: str, company_context: str = "") -> Dict[str, Any]:
        """Generate comprehensive country risk analysis using AI"""
        prompt = f"""
        Analyze modern slavery and labor rights risks for {country} in the context of {company_context}.
        
        Provide a structured analysis including:
        1. Current modern slavery prevalence and trends
        2. Key risk factors (economic, governance, enforcement)
        3. Industry-specific vulnerabilities
        4. Recent developments and policy changes
        5. Specific recommendations for supply chain monitoring
        
        Format as JSON with numerical risk scores (0-100) and detailed explanations.
        """
        
        return await self._call_openai_structured(prompt, "country_risk_analysis")
    
    async def generate_industry_risk_profile(self, industry: str, countries: List[str]) -> Dict[str, Any]:
        """Generate industry-specific risk profile"""
        prompt = f"""
        Analyze modern slavery and forced labor risks in the {industry} industry, 
        particularly in operations across {', '.join(countries)}.
        
        Include:
        1. Industry-specific vulnerabilities and common exploitation patterns
        2. Supply chain complexity and transparency challenges
        3. High-risk processes and geographic hotspots
        4. Regulatory landscape and compliance requirements
        5. Best practices and mitigation strategies
        
        Provide risk scores and actionable insights in JSON format.
        """
        
        return await self._call_openai_structured(prompt, "industry_risk_profile")
    
    async def analyze_company_supply_chain(self, company: str, industry: str, countries: List[str]) -> Dict[str, Any]:
        """Generate company-specific supply chain risk analysis"""
        prompt = f"""
        Conduct a comprehensive modern slavery risk assessment for {company}, 
        a {industry} company operating in {', '.join(countries)}.
        
        Analyze:
        1. Company's current exposure to modern slavery risks
        2. Supply chain vulnerability assessment
        3. Effectiveness of existing policies and practices
        4. Country-specific operational risks
        5. Industry benchmarking and peer comparison
        6. Regulatory compliance gaps
        7. Actionable mitigation recommendations
        
        Include risk scores, timeline for implementation, and priority ranking.
        Return structured JSON data.
        """
        
        return await self._call_openai_structured(prompt, "company_supply_chain_analysis")
    
    async def generate_news_sentiment_analysis(self, company: str, news_articles: List[Dict]) -> Dict[str, Any]:
        """Analyze news sentiment and extract key insights"""
        articles_text = "\n".join([f"Title: {article.get('title', '')}\nContent: {article.get('description', '')}" 
                                  for article in news_articles[:5]])
        
        prompt = f"""
        Analyze the following news articles about {company} for modern slavery, 
        labor rights, and supply chain risks:
        
        {articles_text}
        
        Provide:
        1. Overall sentiment score (0-100, where 0=very negative, 100=very positive)
        2. Key themes and concerns identified
        3. Specific incidents or allegations mentioned
        4. Company's response and actions taken
        5. Risk implications for investors and stakeholders
        6. Monitoring recommendations
        
        Return structured JSON analysis.
        """
        
        return await self._call_openai_structured(prompt, "news_sentiment_analysis")
    
    async def generate_mitigation_recommendations(self, risk_assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific, actionable mitigation recommendations"""
        prompt = f"""
        Based on this modern slavery risk assessment: {json.dumps(risk_assessment, indent=2)}
        
        Generate 8-12 specific, actionable recommendations including:
        1. Immediate actions (0-3 months)
        2. Short-term initiatives (3-12 months)
        3. Long-term strategic changes (1-3 years)
        
        For each recommendation include:
        - Specific action description
        - Implementation timeline
        - Resource requirements
        - Expected impact on risk reduction
        - Success metrics
        - Priority level (Critical/High/Medium/Low)
        
        Return as structured JSON array.
        """
        
        return await self._call_openai_structured(prompt, "mitigation_recommendations")
    
    async def _call_openai_structured(self, prompt: str, analysis_type: str) -> Dict[str, Any]:
        """Make structured API call to OpenAI"""
        try:
            data = {
                'model': 'gpt-4',
                'messages': [
                    {
                        'role': 'system',
                        'content': f'You are an expert in modern slavery risk assessment and supply chain compliance. '
                                 f'Provide detailed, actionable analysis in valid JSON format for {analysis_type}. '
                                 f'Include numerical risk scores and specific recommendations.'
                    },
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 2000,
                'temperature': 0.3
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=self.headers,
                    json=data,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        
                        # Extract JSON from response
                        try:
                            # Try to parse as JSON directly
                            return json.loads(content)
                        except json.JSONDecodeError:
                            # Extract JSON from markdown code blocks if present
                            import re
                            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                            if json_match:
                                return json.loads(json_match.group(1))
                            else:
                                # Fallback: return structured error
                                return {
                                    'error': 'Failed to parse AI response',
                                    'raw_content': content,
                                    'analysis_type': analysis_type
                                }
                    else:
                        logger.error(f"OpenAI API error: {response.status}")
                        return {'error': f'OpenAI API error: {response.status}'}
                        
        except Exception as e:
            logger.error(f"AI analysis error for {analysis_type}: {str(e)}")
            return {'error': str(e), 'analysis_type': analysis_type}

class DataEnrichmentService:
    """Service to fetch and enrich data from various APIs"""
    
    @staticmethod
    async def fetch_world_bank_data(country: str) -> Dict[str, Any]:
        """Fetch economic and governance data from World Bank"""
        try:
            indicators = [
                'NY.GDP.PCAP.CD',  # GDP per capita
                'SL.UEM.TOTL.ZS',  # Unemployment rate
                'SI.POV.GINI',     # GINI index
                'CC.EST',          # Control of corruption
                'RL.EST',          # Rule of law
                'GE.EST'           # Government effectiveness
            ]
            
            data = {}
            for indicator in indicators:
                url = f"{WORLD_BANK_API_BASE}/country/{country}/indicator/{indicator}"
                params = {'format': 'json', 'per_page': 1, 'date': '2020:2023'}
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params, timeout=10) as response:
                        if response.status == 200:
                            result = await response.json()
                            if len(result) > 1 and result[1]:
                                latest_data = result[1][0]
                                data[indicator] = {
                                    'value': latest_data.get('value'),
                                    'date': latest_data.get('date')
                                }
            
            return data
            
        except Exception as e:
            logger.error(f"World Bank API error for {country}: {str(e)}")
            return {}
    
    @staticmethod
    async def fetch_news_data(company: str, keywords: List[str] = None) -> List[Dict[str, Any]]:
        """Fetch recent news about company and labor issues"""
        if not keywords:
            keywords = ['modern slavery', 'forced labor', 'labor violations', 'supply chain']
        
        try:
            if NEWS_API_KEY and NEWS_API_KEY != "your_news_api_key_here":
                search_query = f'"{company}" AND ({" OR ".join(keywords)})'
                
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': search_query,
                    'apiKey': NEWS_API_KEY,
                    'language': 'en',
                    'sortBy': 'relevancy',
                    'pageSize': 10,
                    'from': (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params, timeout=15) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result.get('articles', [])
            
            return []
            
        except Exception as e:
            logger.error(f"News API error for {company}: {str(e)}")
            return []
    
    @staticmethod
    async def enrich_company_data(company: str) -> Dict[str, Any]:
        """Enrich company data using various sources and AI"""
        try:
            # This would integrate with company databases, SEC filings, etc.
            # For now, we'll use AI to generate insights based on public knowledge
            ai_generator = AIInsightGenerator(OPENAI_API_KEY)
            
            prompt = f"""
            Provide comprehensive company profile data for {company} including:
            1. Primary industry and business model
            2. Major countries of operation and manufacturing
            3. Revenue estimate and company size
            4. Known supply chain practices and policies
            5. Historical labor-related incidents or initiatives
            6. ESG and sustainability commitments
            7. Regulatory compliance record
            
            Return structured JSON data with specific, factual information.
            """
            
            company_data = await ai_generator._call_openai_structured(prompt, "company_profile")
            return company_data
            
        except Exception as e:
            logger.error(f"Company data enrichment error for {company}: {str(e)}")
            return {}

class ModernSlaveryRiskAssessment:
    """Main risk assessment orchestrator"""
    
    def __init__(self):
        self.ai_generator = AIInsightGenerator(OPENAI_API_KEY)
        self.data_service = DataEnrichmentService()
    
    async def conduct_comprehensive_assessment(self, company: str) -> Dict[str, Any]:
        """Conduct a comprehensive modern slavery risk assessment"""
        try:
            logger.info(f"Starting comprehensive assessment for {company}")
            
            # Step 1: Enrich company data
            logger.info("Enriching company data...")
            company_data = await self.data_service.enrich_company_data(company)
            
            if 'error' in company_data:
                return {'error': 'Failed to gather company information', 'details': company_data}
            
            # Step 2: Extract operational context
            countries = company_data.get('countries_of_operation', [])
            industry = company_data.get('industry', 'unknown')
            
            if not countries:
                countries = ['United States']  # Default assumption
            
            # Step 3: Parallel data gathering
            logger.info("Gathering risk data...")
            tasks = [
                self.ai_generator.generate_country_risk_analysis(country, f"{company} operations") 
                for country in countries
            ]
            tasks.append(self.ai_generator.generate_industry_risk_profile(industry, countries))
            tasks.append(self.ai_generator.analyze_company_supply_chain(company, industry, countries))
            tasks.append(self.data_service.fetch_news_data(company))
            
            # Add World Bank data for each country
            for country in countries:
                tasks.append(self.data_service.fetch_world_bank_data(country))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Step 4: Process results
            country_analyses = results[:len(countries)]
            industry_analysis = results[len(countries)]
            company_analysis = results[len(countries) + 1]
            news_articles = results[len(countries) + 2]
            world_bank_data = results[len(countries) + 3:]
            
            # Step 5: Generate news sentiment analysis
            logger.info("Analyzing news sentiment...")
            news_sentiment = await self.ai_generator.generate_news_sentiment_analysis(company, news_articles)
            
            # Step 6: Calculate overall risk scores
            risk_scores = self._calculate_risk_scores(
                country_analyses, industry_analysis, company_analysis, news_sentiment
            )
            
            # Step 7: Generate mitigation recommendations
            logger.info("Generating recommendations...")
            recommendations = await self.ai_generator.generate_mitigation_recommendations(risk_scores)
            
            # Step 8: Compile comprehensive assessment
            assessment = {
                'company_name': company,
                'assessment_date': datetime.utcnow().isoformat(),
                'methodology': 'AI-powered dynamic risk assessment using real-time data integration',
                
                'company_profile': company_data,
                
                'overall_risk_assessment': risk_scores,
                
                'country_analysis': {
                    countries[i]: {
                        **country_analyses[i],
                        'world_bank_data': world_bank_data[i] if i < len(world_bank_data) else {}
                    }
                    for i in range(len(countries))
                    if not isinstance(country_analyses[i], Exception)
                },
                
                'industry_analysis': industry_analysis if not isinstance(industry_analysis, Exception) else {},
                
                'supply_chain_analysis': company_analysis if not isinstance(company_analysis, Exception) else {},
                
                'news_and_sentiment': {
                    'sentiment_analysis': news_sentiment,
                    'recent_articles': news_articles[:5],
                    'monitoring_alerts': self._generate_monitoring_alerts(news_sentiment)
                },
                
                'recommendations': recommendations if not isinstance(recommendations, Exception) else [],
                
                'risk_factors': self._extract_key_risk_factors(country_analyses, industry_analysis, company_analysis),
                
                'compliance_requirements': await self._generate_compliance_requirements(countries, industry),
                
                'assessment_quality': {
                    'data_completeness': self._calculate_data_completeness(company_data, country_analyses),
                    'confidence_level': self._calculate_confidence_level(risk_scores),
                    'last_updated': datetime.utcnow().isoformat(),
                    'next_review_date': (datetime.utcnow() + timedelta(days=90)).isoformat()
                }
            }
            
            logger.info(f"Assessment completed for {company}")
            return assessment
            
        except Exception as e:
            logger.error(f"Assessment failed for {company}: {str(e)}")
            return {
                'error': 'Assessment failed',
                'company_name': company,
                'details': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _calculate_risk_scores(self, country_analyses, industry_analysis, company_analysis, news_sentiment):
        """Calculate overall risk scores from AI analyses"""
        try:
            # Extract risk scores from AI analyses
            country_scores = []
            for analysis in country_analyses:
                if isinstance(analysis, dict) and 'risk_score' in analysis:
                    country_scores.append(analysis['risk_score'])
            
            avg_country_risk = sum(country_scores) / len(country_scores) if country_scores else 50
            
            industry_risk = industry_analysis.get('overall_risk_score', 50) if isinstance(industry_analysis, dict) else 50
            company_risk = company_analysis.get('overall_risk_score', 50) if isinstance(company_analysis, dict) else 50
            sentiment_impact = 100 - news_sentiment.get('sentiment_score', 50) if isinstance(news_sentiment, dict) else 25
            
            # Calculate weighted final score
            final_risk = (
                avg_country_risk * 0.4 +
                industry_risk * 0.3 +
                company_risk * 0.2 +
                sentiment_impact * 0.1
            )
            
            return {
                'overall_risk_score': round(final_risk, 1),
                'risk_category': self._categorize_risk(final_risk),
                'country_risk_average': round(avg_country_risk, 1),
                'industry_risk': round(industry_risk, 1),
                'company_specific_risk': round(company_risk, 1),
                'news_sentiment_impact': round(sentiment_impact, 1),
                'risk_factors': {
                    'governance_risk': avg_country_risk > 70,
                    'industry_vulnerability': industry_risk > 60,
                    'company_exposure': company_risk > 60,
                    'negative_publicity': sentiment_impact > 30
                }
            }
            
        except Exception as e:
            logger.error(f"Risk score calculation error: {str(e)}")
            return {
                'overall_risk_score': 50,
                'risk_category': 'Medium',
                'error': 'Risk calculation failed'
            }
    
    def _categorize_risk(self, score):
        """Categorize risk level"""
        if score >= 80:
            return 'Critical'
        elif score >= 65:
            return 'High'
        elif score >= 45:
            return 'Medium'
        elif score >= 25:
            return 'Low'
        else:
            return 'Very Low'
    
    def _extract_key_risk_factors(self, country_analyses, industry_analysis, company_analysis):
        """Extract key risk factors from analyses"""
        risk_factors = []
        
        # Extract from country analyses
        for analysis in country_analyses:
            if isinstance(analysis, dict) and 'key_risks' in analysis:
                risk_factors.extend(analysis['key_risks'])
        
        # Extract from industry analysis
        if isinstance(industry_analysis, dict) and 'risk_factors' in industry_analysis:
            risk_factors.extend(industry_analysis['risk_factors'])
        
        # Extract from company analysis
        if isinstance(company_analysis, dict) and 'risk_factors' in company_analysis:
            risk_factors.extend(company_analysis['risk_factors'])
        
        return list(set(risk_factors))  # Remove duplicates
    
    def _generate_monitoring_alerts(self, news_sentiment):
        """Generate monitoring alerts based on news sentiment"""
        alerts = []
        
        if isinstance(news_sentiment, dict):
            sentiment_score = news_sentiment.get('sentiment_score', 50)
            
            if sentiment_score < 30:
                alerts.append({
                    'level': 'High',
                    'message': 'Negative media coverage detected - immediate review recommended',
                    'action': 'Conduct urgent supply chain audit'
                })
            elif sentiment_score < 50:
                alerts.append({
                    'level': 'Medium',
                    'message': 'Mixed media coverage - monitor developments',
                    'action': 'Enhanced monitoring for 90 days'
                })
        
        return alerts
    
    async def _generate_compliance_requirements(self, countries, industry):
        """Generate compliance requirements using AI"""
        prompt = f"""
        Generate specific compliance requirements for a {industry} company 
        operating in {', '.join(countries)} regarding modern slavery and labor rights.
        
        Include:
        1. Mandatory reporting requirements by jurisdiction
        2. Industry-specific regulations and standards
        3. International frameworks and conventions
        4. Certification and audit requirements
        5. Documentation and record-keeping obligations
        6. Timeline and deadlines for compliance
        
        Return structured JSON with specific requirements and deadlines.
        """
        
        return await self.ai_generator._call_openai_structured(prompt, "compliance_requirements")
    
    def _calculate_data_completeness(self, company_data, country_analyses):
        """Calculate data completeness score"""
        total_sections = 5
        completed_sections = 0
        
        if company_data and 'industry' in company_data:
            completed_sections += 1
        if company_data and 'countries_of_operation' in company_data:
            completed_sections += 1
        if any(not isinstance(analysis, Exception) for analysis in country_analyses):
            completed_sections += 1
        if len(country_analyses) > 0:
            completed_sections += 1
        if company_data:
            completed_sections += 1
        
        return round((completed_sections / total_sections) * 100, 1)
    
    def _calculate_confidence_level(self, risk_scores):
        """Calculate confidence level in assessment"""
        if 'error' in risk_scores:
            return 'Low'
        elif risk_scores.get('overall_risk_score', 0) > 0:
            return 'High'
        else:
            return 'Medium'

# Initialize global assessment service
assessment_service = ModernSlaveryRiskAssessment()

@app.route('/assess')
async def assess_company():
    """Main assessment endpoint - now fully AI-powered"""
    try:
        company_name = request.args.get('company', '').strip()
        if not company_name:
            return jsonify({'error': 'Company name is required'}), 400
        
        logger.info(f"Starting assessment for: {company_name}")
        
        # Conduct comprehensive AI-powered assessment
        assessment = await assessment_service.conduct_comprehensive_assessment(company_name)
        
        return jsonify(assessment)
        
    except Exception as e:
        logger.error(f"Assessment endpoint error: {str(e)}")
        return jsonify({
            'error': 'Assessment failed',
            'details': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '4.0 - AI Powered',
        'features': [
            'Dynamic AI-powered risk assessment',
            'Real-time data integration',
            'OpenAI-generated insights and analysis',
            'Live news sentiment analysis',
            'World Bank economic data integration',
            'Automated compliance requirement generation',
            'Dynamic company profiling',
            'Contextual risk scoring'
        ],
        'ai_capabilities': [
            'Country risk analysis',
            'Industry vulnerability assessment',
            'Supply chain risk mapping',
            'News sentiment analysis',
            'Mitigation recommendations',
            'Compliance requirement generation'
        ],
        'data_sources': [
            'OpenAI GPT-4 for analysis and insights',
            'World Bank API for economic indicators',
            'News API for real-time media monitoring',
            'AI-generated company profiling',
            'Dynamic risk factor identification'
        ]
    })

@app.route('/capabilities')
def get_capabilities():
    """Get AI capabilities and supported analyses"""
    return jsonify({
        'ai_analysis_types': [
            'country_risk_analysis',
            'industry_risk_profile', 
            'company_supply_chain_analysis',
            'news_sentiment_analysis',
            'mitigation_recommendations',
            'compliance_requirements'
        ],
        'data_enrichment': [
            'World Bank economic indicators',
            'Real-time news monitoring',
            'AI-generated company profiles',
            'Dynamic risk factor identification'
        ],
        'supported_industries': [
            'Any industry - AI analyzes based on context',
            'Dynamic industry risk profiling',
            'Cross-industry comparative analysis'
        ],
        'supported_countries': [
            'Global coverage - AI analyzes any country',
            'World Bank data integration',
            'Country-specific risk factors'
        ]
    })

if __name__ == '__main__':
    print("=" * 80)
    print("🤖 Starting AI-Powered Modern Slavery Assessment Backend v4.0")
    print("=" * 80)
    print("🧠 AI Capabilities:")
    print("   • Dynamic risk assessment using OpenAI GPT-4")
    print("   • Real-time data integration and enrichment")
    print("   • Contextual analysis and insight generation")
    print("   • Automated recommendation generation")
    print("   • Live news sentiment monitoring")
    print("\n📊 Data Sources:")
    print("   • OpenAI for analysis and insights")
    print("   • World Bank API for economic data")
    print("   • News API for media monitoring")
    print("   • AI-generated company profiling")
    print("\n🚀 Key Features:")
    print("   • No hard-coded data - everything AI-generated")
    print("   • Dynamic country and industry analysis")
    print("   • Real-time risk assessment")
    print("   • Contextual recommendations")
    print("   • Comprehensive compliance mapping")
    print("\n⚠️  Configuration Required:")
    print("   • Set OPENAI_API_KEY environment variable")
    print("   • Set NEWS_API_KEY environment variable (optional)")
    print("=" * 80)
    
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)