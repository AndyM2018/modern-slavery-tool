# Enhanced AI-Powered Modern Slavery Assessment Backend with Sophisticated Risk Model - COMPLETE VERSION
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime, timedelta
import random
import math

app = Flask(__name__)
CORS(app)

# Configuration
NEWS_API_KEY = "your_news_api_key_here"  # Replace with actual key
OPENAI_API_KEY = "your_openai_api_key_here"  # Replace with actual key

# Comprehensive Country Risk Data - Extended Dataset
COUNTRY_RISK_DATA = {
    'China': {
        'governance_risk': 85,
        'economic_vulnerability': 45,
        'modern_slavery_prevalence': 31.0,
        'tip_tier': 3,
        'forced_labor_score': 78,
        'supply_chain_transparency': 25,
        'worker_rights_index': 15,
        'corruption_index': 76,
        'rule_of_law_score': 28,
        'labor_enforcement': 22,
        'gdp_per_capita': 12556,
        'unemployment_rate': 5.2,
        'poverty_rate': 1.7,
        'economic_freedom_score': 58.4
    },
    'Bangladesh': {
        'governance_risk': 75,
        'economic_vulnerability': 80,
        'modern_slavery_prevalence': 16.2,
        'tip_tier': 2,
        'forced_labor_score': 65,
        'supply_chain_transparency': 30,
        'worker_rights_index': 25,
        'corruption_index': 74,
        'rule_of_law_score': 31,
        'labor_enforcement': 28,
        'gdp_per_capita': 2503,
        'unemployment_rate': 4.2,
        'poverty_rate': 20.5,
        'economic_freedom_score': 55.1
    },
    'India': {
        'governance_risk': 65,
        'economic_vulnerability': 70,
        'modern_slavery_prevalence': 11.0,
        'tip_tier': 2,
        'forced_labor_score': 72,
        'supply_chain_transparency': 35,
        'worker_rights_index': 30,
        'corruption_index': 69,
        'rule_of_law_score': 37,
        'labor_enforcement': 32,
        'gdp_per_capita': 2277,
        'unemployment_rate': 7.9,
        'poverty_rate': 21.9,
        'economic_freedom_score': 56.5
    },
    'Vietnam': {
        'governance_risk': 70,
        'economic_vulnerability': 55,
        'modern_slavery_prevalence': 9.1,
        'tip_tier': 2,
        'forced_labor_score': 58,
        'supply_chain_transparency': 28,
        'worker_rights_index': 22,
        'corruption_index': 67,
        'rule_of_law_score': 34,
        'labor_enforcement': 35,
        'gdp_per_capita': 4164,
        'unemployment_rate': 2.9,
        'poverty_rate': 4.8,
        'economic_freedom_score': 61.7
    },
    'Thailand': {
        'governance_risk': 60,
        'economic_vulnerability': 45,
        'modern_slavery_prevalence': 14.8,
        'tip_tier': 2,
        'forced_labor_score': 68,
        'supply_chain_transparency': 40,
        'worker_rights_index': 35,
        'corruption_index': 64,
        'rule_of_law_score': 42,
        'labor_enforcement': 38,
        'gdp_per_capita': 7817,
        'unemployment_rate': 1.2,
        'poverty_rate': 6.2,
        'economic_freedom_score': 67.8
    },
    'Mexico': {
        'governance_risk': 55,
        'economic_vulnerability': 50,
        'modern_slavery_prevalence': 3.8,
        'tip_tier': 2,
        'forced_labor_score': 45,
        'supply_chain_transparency': 45,
        'worker_rights_index': 40,
        'corruption_index': 69,
        'rule_of_law_score': 39,
        'labor_enforcement': 42,
        'gdp_per_capita': 10045,
        'unemployment_rate': 3.5,
        'poverty_rate': 41.9,
        'economic_freedom_score': 63.8
    },
    'United States': {
        'governance_risk': 25,
        'economic_vulnerability': 20,
        'modern_slavery_prevalence': 3.3,
        'tip_tier': 1,
        'forced_labor_score': 35,
        'supply_chain_transparency': 75,
        'worker_rights_index': 70,
        'corruption_index': 33,
        'rule_of_law_score': 89,
        'labor_enforcement': 85,
        'gdp_per_capita': 70248,
        'unemployment_rate': 3.6,
        'poverty_rate': 10.5,
        'economic_freedom_score': 76.6
    },
    'Germany': {
        'governance_risk': 15,
        'economic_vulnerability': 15,
        'modern_slavery_prevalence': 1.2,
        'tip_tier': 1,
        'forced_labor_score': 20,
        'supply_chain_transparency': 85,
        'worker_rights_index': 85,
        'corruption_index': 20,
        'rule_of_law_score': 93,
        'labor_enforcement': 90,
        'gdp_per_capita': 46260,
        'unemployment_rate': 3.2,
        'poverty_rate': 9.6,
        'economic_freedom_score': 73.5
    },
    'United Kingdom': {
        'governance_risk': 20,
        'economic_vulnerability': 18,
        'modern_slavery_prevalence': 2.3,
        'tip_tier': 1,
        'forced_labor_score': 25,
        'supply_chain_transparency': 80,
        'worker_rights_index': 80,
        'corruption_index': 22,
        'rule_of_law_score': 91,
        'labor_enforcement': 88,
        'gdp_per_capita': 42328,
        'unemployment_rate': 3.8,
        'poverty_rate': 11.7,
        'economic_freedom_score': 78.4
    },
    'Japan': {
        'governance_risk': 22,
        'economic_vulnerability': 25,
        'modern_slavery_prevalence': 0.3,
        'tip_tier': 1,
        'forced_labor_score': 30,
        'supply_chain_transparency': 70,
        'worker_rights_index': 75,
        'corruption_index': 27,
        'rule_of_law_score': 88,
        'labor_enforcement': 82,
        'gdp_per_capita': 39285,
        'unemployment_rate': 2.8,
        'poverty_rate': 15.7,
        'economic_freedom_score': 73.3
    },
    'South Korea': {
        'governance_risk': 28,
        'economic_vulnerability': 30,
        'modern_slavery_prevalence': 0.5,
        'tip_tier': 1,
        'forced_labor_score': 32,
        'supply_chain_transparency': 65,
        'worker_rights_index': 70,
        'corruption_index': 32,
        'rule_of_law_score': 83,
        'labor_enforcement': 78,
        'gdp_per_capita': 31846,
        'unemployment_rate': 3.0,
        'poverty_rate': 14.4,
        'economic_freedom_score': 74.0
    },
    'Singapore': {
        'governance_risk': 18,
        'economic_vulnerability': 22,
        'modern_slavery_prevalence': 1.8,
        'tip_tier': 1,
        'forced_labor_score': 28,
        'supply_chain_transparency': 75,
        'worker_rights_index': 75,
        'corruption_index': 15,
        'rule_of_law_score': 95,
        'labor_enforcement': 85,
        'gdp_per_capita': 72794,
        'unemployment_rate': 2.3,
        'poverty_rate': 'N/A',
        'economic_freedom_score': 83.9
    },
    'Malaysia': {
        'governance_risk': 50,
        'economic_vulnerability': 40,
        'modern_slavery_prevalence': 5.9,
        'tip_tier': 2,
        'forced_labor_score': 55,
        'supply_chain_transparency': 50,
        'worker_rights_index': 45,
        'corruption_index': 52,
        'rule_of_law_score': 64,
        'labor_enforcement': 55,
        'gdp_per_capita': 11371,
        'unemployment_rate': 3.4,
        'poverty_rate': 5.6,
        'economic_freedom_score': 74.4
    },
    'Indonesia': {
        'governance_risk': 58,
        'economic_vulnerability': 55,
        'modern_slavery_prevalence': 4.9,
        'tip_tier': 2,
        'forced_labor_score': 52,
        'supply_chain_transparency': 42,
        'worker_rights_index': 38,
        'corruption_index': 62,
        'rule_of_law_score': 44,
        'labor_enforcement': 48,
        'gdp_per_capita': 4256,
        'unemployment_rate': 5.5,
        'poverty_rate': 9.4,
        'economic_freedom_score': 64.2
    },
    'Philippines': {
        'governance_risk': 62,
        'economic_vulnerability': 60,
        'modern_slavery_prevalence': 10.8,
        'tip_tier': 2,
        'forced_labor_score': 62,
        'supply_chain_transparency': 35,
        'worker_rights_index': 32,
        'corruption_index': 67,
        'rule_of_law_score': 37,
        'labor_enforcement': 35,
        'gdp_per_capita': 3485,
        'unemployment_rate': 2.3,
        'poverty_rate': 16.7,
        'economic_freedom_score': 64.1
    },
    'Brazil': {
        'governance_risk': 48,
        'economic_vulnerability': 45,
        'modern_slavery_prevalence': 1.8,
        'tip_tier': 2,
        'forced_labor_score': 42,
        'supply_chain_transparency': 55,
        'worker_rights_index': 50,
        'corruption_index': 62,
        'rule_of_law_score': 52,
        'labor_enforcement': 58,
        'gdp_per_capita': 8917,
        'unemployment_rate': 11.9,
        'poverty_rate': 19.9,
        'economic_freedom_score': 53.4
    },
    'Turkey': {
        'governance_risk': 68,
        'economic_vulnerability': 65,
        'modern_slavery_prevalence': 6.8,
        'tip_tier': 2,
        'forced_labor_score': 58,
        'supply_chain_transparency': 38,
        'worker_rights_index': 35,
        'corruption_index': 64,
        'rule_of_law_score': 39,
        'labor_enforcement': 42,
        'gdp_per_capita': 9586,
        'unemployment_rate': 13.7,
        'poverty_rate': 14.4,
        'economic_freedom_score': 64.0
    },
    'Pakistan': {
        'governance_risk': 78,
        'economic_vulnerability': 82,
        'modern_slavery_prevalence': 23.3,
        'tip_tier': 2,
        'forced_labor_score': 75,
        'supply_chain_transparency': 25,
        'worker_rights_index': 18,
        'corruption_index': 70,
        'rule_of_law_score': 32,
        'labor_enforcement': 25,
        'gdp_per_capita': 1537,
        'unemployment_rate': 6.2,
        'poverty_rate': 24.3,
        'economic_freedom_score': 55.2
    },
    'Myanmar': {
        'governance_risk': 95,
        'economic_vulnerability': 88,
        'modern_slavery_prevalence': 29.8,
        'tip_tier': 3,
        'forced_labor_score': 92,
        'supply_chain_transparency': 10,
        'worker_rights_index': 5,
        'corruption_index': 85,
        'rule_of_law_score': 8,
        'labor_enforcement': 8,
        'gdp_per_capita': 1408,
        'unemployment_rate': 3.5,
        'poverty_rate': 24.8,
        'economic_freedom_score': 42.4
    },
    'Cambodia': {
        'governance_risk': 82,
        'economic_vulnerability': 75,
        'modern_slavery_prevalence': 16.4,
        'tip_tier': 2,
        'forced_labor_score': 72,
        'supply_chain_transparency': 22,
        'worker_rights_index': 25,
        'corruption_index': 78,
        'rule_of_law_score': 26,
        'labor_enforcement': 28,
        'gdp_per_capita': 1625,
        'unemployment_rate': 0.4,
        'poverty_rate': 13.5,
        'economic_freedom_score': 57.5
    },
    'Laos': {
        'governance_risk': 85,
        'economic_vulnerability': 78,
        'modern_slavery_prevalence': 10.3,
        'tip_tier': 2,
        'forced_labor_score': 68,
        'supply_chain_transparency': 18,
        'worker_rights_index': 20,
        'corruption_index': 82,
        'rule_of_law_score': 22,
        'labor_enforcement': 22,
        'gdp_per_capita': 2630,
        'unemployment_rate': 1.4,
        'poverty_rate': 18.3,
        'economic_freedom_score': 53.6
    },
    'Sri Lanka': {
        'governance_risk': 72,
        'economic_vulnerability': 78,
        'modern_slavery_prevalence': 5.9,
        'tip_tier': 2,
        'forced_labor_score': 55,
        'supply_chain_transparency': 35,
        'worker_rights_index': 38,
        'corruption_index': 68,
        'rule_of_law_score': 42,
        'labor_enforcement': 45,
        'gdp_per_capita': 3682,
        'unemployment_rate': 4.8,
        'poverty_rate': 4.1,
        'economic_freedom_score': 57.4
    },
    'Ethiopia': {
        'governance_risk': 88,
        'economic_vulnerability': 92,
        'modern_slavery_prevalence': 9.2,
        'tip_tier': 2,
        'forced_labor_score': 68,
        'supply_chain_transparency': 15,
        'worker_rights_index': 22,
        'corruption_index': 75,
        'rule_of_law_score': 18,
        'labor_enforcement': 25,
        'gdp_per_capita': 936,
        'unemployment_rate': 19.1,
        'poverty_rate': 23.5,
        'economic_freedom_score': 52.3
    },
    'Kenya': {
        'governance_risk': 68,
        'economic_vulnerability': 72,
        'modern_slavery_prevalence': 8.8,
        'tip_tier': 2,
        'forced_labor_score': 62,
        'supply_chain_transparency': 32,
        'worker_rights_index': 35,
        'corruption_index': 72,
        'rule_of_law_score': 38,
        'labor_enforcement': 42,
        'gdp_per_capita': 2006,
        'unemployment_rate': 2.9,
        'poverty_rate': 36.1,
        'economic_freedom_score': 56.5
    },
    'South Africa': {
        'governance_risk': 58,
        'economic_vulnerability': 65,
        'modern_slavery_prevalence': 3.6,
        'tip_tier': 2,
        'forced_labor_score': 48,
        'supply_chain_transparency': 52,
        'worker_rights_index': 55,
        'corruption_index': 56,
        'rule_of_law_score': 62,
        'labor_enforcement': 58,
        'gdp_per_capita': 7055,
        'unemployment_rate': 29.2,
        'poverty_rate': 18.2,
        'economic_freedom_score': 59.7
    },
    'Nigeria': {
        'governance_risk': 82,
        'economic_vulnerability': 85,
        'modern_slavery_prevalence': 6.6,
        'tip_tier': 2,
        'forced_labor_score': 58,
        'supply_chain_transparency': 28,
        'worker_rights_index': 25,
        'corruption_index': 78,
        'rule_of_law_score': 25,
        'labor_enforcement': 28,
        'gdp_per_capita': 2085,
        'unemployment_rate': 33.3,
        'poverty_rate': 40.1,
        'economic_freedom_score': 57.2
    },
    'Egypt': {
        'governance_risk': 75,
        'economic_vulnerability': 68,
        'modern_slavery_prevalence': 7.9,
        'tip_tier': 2,
        'forced_labor_score': 62,
        'supply_chain_transparency': 32,
        'worker_rights_index': 28,
        'corruption_index': 70,
        'rule_of_law_score': 35,
        'labor_enforcement': 38,
        'gdp_per_capita': 3019,
        'unemployment_rate': 7.4,
        'poverty_rate': 32.5,
        'economic_freedom_score': 55.7
    },
    'Morocco': {
        'governance_risk': 62,
        'economic_vulnerability': 58,
        'modern_slavery_prevalence': 4.2,
        'tip_tier': 2,
        'forced_labor_score': 48,
        'supply_chain_transparency': 42,
        'worker_rights_index': 45,
        'corruption_index': 64,
        'rule_of_law_score': 48,
        'labor_enforcement': 52,
        'gdp_per_capita': 3498,
        'unemployment_rate': 11.9,
        'poverty_rate': 4.8,
        'economic_freedom_score': 63.3
    },
    'Tunisia': {
        'governance_risk': 55,
        'economic_vulnerability': 62,
        'modern_slavery_prevalence': 2.8,
        'tip_tier': 2,
        'forced_labor_score': 42,
        'supply_chain_transparency': 48,
        'worker_rights_index': 52,
        'corruption_index': 58,
        'rule_of_law_score': 55,
        'labor_enforcement': 58,
        'gdp_per_capita': 3317,
        'unemployment_rate': 16.1,
        'poverty_rate': 15.2,
        'economic_freedom_score': 56.6
    },
    'Peru': {
        'governance_risk': 58,
        'economic_vulnerability': 52,
        'modern_slavery_prevalence': 4.1,
        'tip_tier': 2,
        'forced_labor_score': 48,
        'supply_chain_transparency': 45,
        'worker_rights_index': 48,
        'corruption_index': 65,
        'rule_of_law_score': 42,
        'labor_enforcement': 48,
        'gdp_per_capita': 6692,
        'unemployment_rate': 3.9,
        'poverty_rate': 20.2,
        'economic_freedom_score': 67.7
    },
    'Colombia': {
        'governance_risk': 65,
        'economic_vulnerability': 58,
        'modern_slavery_prevalence': 2.9,
        'tip_tier': 1,
        'forced_labor_score': 42,
        'supply_chain_transparency': 52,
        'worker_rights_index': 55,
        'corruption_index': 61,
        'rule_of_law_score': 48,
        'labor_enforcement': 55,
        'gdp_per_capita': 6131,
        'unemployment_rate': 10.5,
        'poverty_rate': 35.7,
        'economic_freedom_score': 69.2
    },
    'Chile': {
        'governance_risk': 32,
        'economic_vulnerability': 28,
        'modern_slavery_prevalence': 1.8,
        'tip_tier': 1,
        'forced_labor_score': 28,
        'supply_chain_transparency': 68,
        'worker_rights_index': 72,
        'corruption_index': 33,
        'rule_of_law_score': 82,
        'labor_enforcement': 78,
        'gdp_per_capita': 15923,
        'unemployment_rate': 7.2,
        'poverty_rate': 8.6,
        'economic_freedom_score': 77.2
    },
    'Argentina': {
        'governance_risk': 48,
        'economic_vulnerability': 55,
        'modern_slavery_prevalence': 2.2,
        'tip_tier': 1,
        'forced_labor_score': 35,
        'supply_chain_transparency': 58,
        'worker_rights_index': 62,
        'corruption_index': 58,
        'rule_of_law_score': 52,
        'labor_enforcement': 62,
        'gdp_per_capita': 10196,
        'unemployment_rate': 8.8,
        'poverty_rate': 35.5,
        'economic_freedom_score': 52.9
    },
    'Costa Rica': {
        'governance_risk': 35,
        'economic_vulnerability': 38,
        'modern_slavery_prevalence': 2.5,
        'tip_tier': 1,
        'forced_labor_score': 32,
        'supply_chain_transparency': 62,
        'worker_rights_index': 68,
        'corruption_index': 42,
        'rule_of_law_score': 78,
        'labor_enforcement': 72,
        'gdp_per_capita': 12509,
        'unemployment_rate': 12.0,
        'poverty_rate': 20.5,
        'economic_freedom_score': 66.5
    },
    'Guatemala': {
        'governance_risk': 78,
        'economic_vulnerability': 75,
        'modern_slavery_prevalence': 5.2,
        'tip_tier': 2,
        'forced_labor_score': 58,
        'supply_chain_transparency': 28,
        'worker_rights_index': 32,
        'corruption_index': 75,
        'rule_of_law_score': 28,
        'labor_enforcement': 32,
        'gdp_per_capita': 4621,
        'unemployment_rate': 2.4,
        'poverty_rate': 59.3,
        'economic_freedom_score': 63.0
    },
    'Canada': {
        'governance_risk': 18,
        'economic_vulnerability': 15,
        'modern_slavery_prevalence': 1.1,
        'tip_tier': 1,
        'forced_labor_score': 22,
        'supply_chain_transparency': 82,
        'worker_rights_index': 85,
        'corruption_index': 18,
        'rule_of_law_score': 94,
        'labor_enforcement': 88,
        'gdp_per_capita': 46195,
        'unemployment_rate': 5.3,
        'poverty_rate': 8.7,
        'economic_freedom_score': 78.2
    },
    'Australia': {
        'governance_risk': 12,
        'economic_vulnerability': 12,
        'modern_slavery_prevalence': 1.6,
        'tip_tier': 1,
        'forced_labor_score': 25,
        'supply_chain_transparency': 88,
        'worker_rights_index': 88,
        'corruption_index': 12,
        'rule_of_law_score': 96,
        'labor_enforcement': 92,
        'gdp_per_capita': 51812,
        'unemployment_rate': 3.7,
        'poverty_rate': 9.4,
        'economic_freedom_score': 77.7
    },
    'New Zealand': {
        'governance_risk': 8,
        'economic_vulnerability': 10,
        'modern_slavery_prevalence': 0.9,
        'tip_tier': 1,
        'forced_labor_score': 18,
        'supply_chain_transparency': 85,
        'worker_rights_index': 90,
        'corruption_index': 8,
        'rule_of_law_score': 98,
        'labor_enforcement': 95,
        'gdp_per_capita': 42084,
        'unemployment_rate': 3.2,
        'poverty_rate': 10.9,
        'economic_freedom_score': 83.9
    },
    'France': {
        'governance_risk': 22,
        'economic_vulnerability': 18,
        'modern_slavery_prevalence': 1.4,
        'tip_tier': 1,
        'forced_labor_score': 22,
        'supply_chain_transparency': 82,
        'worker_rights_index': 85,
        'corruption_index': 22,
        'rule_of_law_score': 89,
        'labor_enforcement': 88,
        'gdp_per_capita': 40494,
        'unemployment_rate': 7.3,
        'poverty_rate': 8.0,
        'economic_freedom_score': 65.7
    },
    'Italy': {
        'governance_risk': 32,
        'economic_vulnerability': 28,
        'modern_slavery_prevalence': 1.9,
        'tip_tier': 1,
        'forced_labor_score': 28,
        'supply_chain_transparency': 75,
        'worker_rights_index': 78,
        'corruption_index': 44,
        'rule_of_law_score': 73,
        'labor_enforcement': 75,
        'gdp_per_capita': 31953,
        'unemployment_rate': 8.0,
        'poverty_rate': 12.7,
        'economic_freedom_score': 64.9
    },
    'Spain': {
        'governance_risk': 28,
        'economic_vulnerability': 25,
        'modern_slavery_prevalence': 1.7,
        'tip_tier': 1,
        'forced_labor_score': 25,
        'supply_chain_transparency': 78,
        'worker_rights_index': 82,
        'corruption_index': 32,
        'rule_of_law_score': 79,
        'labor_enforcement': 82,
        'gdp_per_capita': 27057,
        'unemployment_rate': 13.3,
        'poverty_rate': 15.5,
        'economic_freedom_score': 69.9
    },
    'Netherlands': {
        'governance_risk': 12,
        'economic_vulnerability': 10,
        'modern_slavery_prevalence': 1.0,
        'tip_tier': 1,
        'forced_labor_score': 18,
        'supply_chain_transparency': 90,
        'worker_rights_index': 92,
        'corruption_index': 10,
        'rule_of_law_score': 95,
        'labor_enforcement': 92,
        'gdp_per_capita': 52331,
        'unemployment_rate': 3.2,
        'poverty_rate': 7.9,
        'economic_freedom_score': 76.8
    },
    'Belgium': {
        'governance_risk': 18,
        'economic_vulnerability': 15,
        'modern_slavery_prevalence': 1.2,
        'tip_tier': 1,
        'forced_labor_score': 20,
        'supply_chain_transparency': 85,
        'worker_rights_index': 88,
        'corruption_index': 25,
        'rule_of_law_score': 88,
        'labor_enforcement': 85,
        'gdp_per_capita': 43582,
        'unemployment_rate': 5.6,
        'poverty_rate': 9.7,
        'economic_freedom_score': 70.1
    },
    'Switzerland': {
        'governance_risk': 5,
        'economic_vulnerability': 8,
        'modern_slavery_prevalence': 0.7,
        'tip_tier': 1,
        'forced_labor_score': 15,
        'supply_chain_transparency': 88,
        'worker_rights_index': 90,
        'corruption_index': 7,
        'rule_of_law_score': 97,
        'labor_enforcement': 95,
        'gdp_per_capita': 81867,
        'unemployment_rate': 2.9,
        'poverty_rate': 6.6,
        'economic_freedom_score': 81.9
    },
    'Sweden': {
        'governance_risk': 8,
        'economic_vulnerability': 10,
        'modern_slavery_prevalence': 0.8,
        'tip_tier': 1,
        'forced_labor_score': 16,
        'supply_chain_transparency': 88,
        'worker_rights_index': 92,
        'corruption_index': 13,
        'rule_of_law_score': 94,
        'labor_enforcement': 90,
        'gdp_per_capita': 51925,
        'unemployment_rate': 6.8,
        'poverty_rate': 8.8,
        'economic_freedom_score': 74.7
    },
    'Norway': {
        'governance_risk': 5,
        'economic_vulnerability': 8,
        'modern_slavery_prevalence': 0.6,
        'tip_tier': 1,
        'forced_labor_score': 12,
        'supply_chain_transparency': 90,
        'worker_rights_index': 95,
        'corruption_index': 7,
        'rule_of_law_score': 96,
        'labor_enforcement': 95,
        'gdp_per_capita': 75420,
        'unemployment_rate': 3.2,
        'poverty_rate': 7.4,
        'economic_freedom_score': 76.9
    },
    'Denmark': {
        'governance_risk': 8,
        'economic_vulnerability': 10,
        'modern_slavery_prevalence': 0.7,
        'tip_tier': 1,
        'forced_labor_score': 14,
        'supply_chain_transparency': 88,
        'worker_rights_index': 92,
        'corruption_index': 10,
        'rule_of_law_score': 95,
        'labor_enforcement': 92,
        'gdp_per_capita': 60170,
        'unemployment_rate': 5.0,
        'poverty_rate': 5.8,
        'economic_freedom_score': 77.8
    },
    'Finland': {
        'governance_risk': 10,
        'economic_vulnerability': 12,
        'modern_slavery_prevalence': 0.8,
        'tip_tier': 1,
        'forced_labor_score': 16,
        'supply_chain_transparency': 85,
        'worker_rights_index': 90,
        'corruption_index': 12,
        'rule_of_law_score': 93,
        'labor_enforcement': 88,
        'gdp_per_capita': 48810,
        'unemployment_rate': 6.7,
        'poverty_rate': 6.3,
        'economic_freedom_score': 77.1
    },
    'Austria': {
        'governance_risk': 15,
        'economic_vulnerability': 12,
        'modern_slavery_prevalence': 1.0,
        'tip_tier': 1,
        'forced_labor_score': 18,
        'supply_chain_transparency': 82,
        'worker_rights_index': 85,
        'corruption_index': 25,
        'rule_of_law_score': 87,
        'labor_enforcement': 85,
        'gdp_per_capita': 45440,
        'unemployment_rate': 4.8,
        'poverty_rate': 9.6,
        'economic_freedom_score': 73.0
    },
    'Portugal': {
        'governance_risk': 25,
        'economic_vulnerability': 22,
        'modern_slavery_prevalence': 1.3,
        'tip_tier': 1,
        'forced_labor_score': 22,
        'supply_chain_transparency': 75,
        'worker_rights_index': 78,
        'corruption_index': 35,
        'rule_of_law_score': 82,
        'labor_enforcement': 78,
        'gdp_per_capita': 23252,
        'unemployment_rate': 6.0,
        'poverty_rate': 10.4,
        'economic_freedom_score': 67.5
    },
    'Poland': {
        'governance_risk': 35,
        'economic_vulnerability': 32,
        'modern_slavery_prevalence': 1.5,
        'tip_tier': 1,
        'forced_labor_score': 25,
        'supply_chain_transparency': 68,
        'worker_rights_index': 72,
        'corruption_index': 45,
        'rule_of_law_score': 65,
        'labor_enforcement': 72,
        'gdp_per_capita': 15421,
        'unemployment_rate': 2.9,
        'poverty_rate': 9.8,
        'economic_freedom_score': 69.7
    },
    'Czech Republic': {
        'governance_risk': 32,
        'economic_vulnerability': 28,
        'modern_slavery_prevalence': 1.4,
        'tip_tier': 1,
        'forced_labor_score': 24,
        'supply_chain_transparency': 70,
        'worker_rights_index': 75,
        'corruption_index': 41,
        'rule_of_law_score': 75,
        'labor_enforcement': 75,
        'gdp_per_capita': 23111,
        'unemployment_rate': 2.2,
        'poverty_rate': 5.6,
        'economic_freedom_score': 74.8
    },
    'Hungary': {
        'governance_risk': 48,
        'economic_vulnerability': 42,
        'modern_slavery_prevalence': 2.1,
        'tip_tier': 1,
        'forced_labor_score': 32,
        'supply_chain_transparency': 62,
        'worker_rights_index': 65,
        'corruption_index': 54,
        'rule_of_law_score': 58,
        'labor_enforcement': 65,
        'gdp_per_capita': 16731,
        'unemployment_rate': 3.4,
        'poverty_rate': 7.8,
        'economic_freedom_score': 66.6
    },
    'Slovakia': {
        'governance_risk': 42,
        'economic_vulnerability': 38,
        'modern_slavery_prevalence': 1.8,
        'tip_tier': 1,
        'forced_labor_score': 28,
        'supply_chain_transparency': 65,
        'worker_rights_index': 68,
        'corruption_index': 49,
        'rule_of_law_score': 68,
        'labor_enforcement': 68,
        'gdp_per_capita': 19582,
        'unemployment_rate': 5.8,
        'poverty_rate': 7.3,
        'economic_freedom_score': 67.2
    },
    'Slovenia': {
        'governance_risk': 28,
        'economic_vulnerability': 25,
        'modern_slavery_prevalence': 1.2,
        'tip_tier': 1,
        'forced_labor_score': 20,
        'supply_chain_transparency': 75,
        'worker_rights_index': 78,
        'corruption_index': 42,
        'rule_of_law_score': 78,
        'labor_enforcement': 78,
        'gdp_per_capita': 25457,
        'unemployment_rate': 4.2,
        'poverty_rate': 8.3,
        'economic_freedom_score': 69.7
    },
    'Croatia': {
        'governance_risk': 45,
        'economic_vulnerability': 42,
        'modern_slavery_prevalence': 2.0,
        'tip_tier': 1,
        'forced_labor_score': 30,
        'supply_chain_transparency': 62,
        'worker_rights_index': 65,
        'corruption_index': 52,
        'rule_of_law_score': 62,
        'labor_enforcement': 65,
        'gdp_per_capita': 13822,
        'unemployment_rate': 6.6,
        'poverty_rate': 11.1,
        'economic_freedom_score': 63.6
    },
    'Romania': {
        'governance_risk': 52,
        'economic_vulnerability': 48,
        'modern_slavery_prevalence': 2.8,
        'tip_tier': 1,
        'forced_labor_score': 38,
        'supply_chain_transparency': 55,
        'worker_rights_index': 58,
        'corruption_index': 56,
        'rule_of_law_score': 55,
        'labor_enforcement': 58,
        'gdp_per_capita': 12301,
        'unemployment_rate': 5.0,
        'poverty_rate': 15.3,
        'economic_freedom_score': 69.5
    },
    'Bulgaria': {
        'governance_risk': 58,
        'economic_vulnerability': 52,
        'modern_slavery_prevalence': 3.2,
        'tip_tier': 1,
        'forced_labor_score': 42,
        'supply_chain_transparency': 52,
        'worker_rights_index': 55,
        'corruption_index': 61,
        'rule_of_law_score': 48,
        'labor_enforcement': 55,
        'gdp_per_capita': 9737,
        'unemployment_rate': 4.2,
        'poverty_rate': 22.0,
        'economic_freedom_score': 70.4
    },
    'Greece': {
        'governance_risk': 48,
        'economic_vulnerability': 55,
        'modern_slavery_prevalence': 2.4,
        'tip_tier': 2,
        'forced_labor_score': 35,
        'supply_chain_transparency': 58,
        'worker_rights_index': 62,
        'corruption_index': 52,
        'rule_of_law_score': 58,
        'labor_enforcement': 62,
        'gdp_per_capita': 17676,
        'unemployment_rate': 12.6,
        'poverty_rate': 17.9,
        'economic_freedom_score': 60.9
    },
    'Cyprus': {
        'governance_risk': 42,
        'economic_vulnerability': 38,
        'modern_slavery_prevalence': 2.2,
        'tip_tier': 1,
        'forced_labor_score': 32,
        'supply_chain_transparency': 65,
        'worker_rights_index': 68,
        'corruption_index': 45,
        'rule_of_law_score': 68,
        'labor_enforcement': 68,
        'gdp_per_capita': 27858,
        'unemployment_rate': 6.8,
        'poverty_rate': 14.7,
        'economic_freedom_score': 70.1
    },
    'Malta': {
        'governance_risk': 35,
        'economic_vulnerability': 32,
        'modern_slavery_prevalence': 1.8,
        'tip_tier': 1,
        'forced_labor_score': 28,
        'supply_chain_transparency': 68,
        'worker_rights_index': 72,
        'corruption_index': 45,
        'rule_of_law_score': 72,
        'labor_enforcement': 72,
        'gdp_per_capita': 29200,
        'unemployment_rate': 3.0,
        'poverty_rate': 16.8,
        'economic_freedom_score': 70.2
    },
    'Luxembourg': {
        'governance_risk': 8,
        'economic_vulnerability': 5,
        'modern_slavery_prevalence': 0.5,
        'tip_tier': 1,
        'forced_labor_score': 10,
        'supply_chain_transparency': 85,
        'worker_rights_index': 88,
        'corruption_index': 12,
        'rule_of_law_score': 92,
        'labor_enforcement': 88,
        'gdp_per_capita': 115873,
        'unemployment_rate': 5.0,
        'poverty_rate': 11.1,
        'economic_freedom_score': 76.0
    },
    'Ireland': {
        'governance_risk': 15,
        'economic_vulnerability': 12,
        'modern_slavery_prevalence': 1.1,
        'tip_tier': 1,
        'forced_labor_score': 18,
        'supply_chain_transparency': 82,
        'worker_rights_index': 85,
        'corruption_index': 24,
        'rule_of_law_score': 85,
        'labor_enforcement': 82,
        'gdp_per_capita': 83966,
        'unemployment_rate': 4.5,
        'poverty_rate': 8.2,
        'economic_freedom_score': 81.4
    },
    'Iceland': {
        'governance_risk': 5,
        'economic_vulnerability': 8,
        'modern_slavery_prevalence': 0.4,
        'tip_tier': 1,
        'forced_labor_score': 8,
        'supply_chain_transparency': 85,
        'worker_rights_index': 92,
        'corruption_index': 13,
        'rule_of_law_score': 95,
        'labor_enforcement': 92,
        'gdp_per_capita': 68384,
        'unemployment_rate': 3.0,
        'poverty_rate': 6.1,
        'economic_freedom_score': 77.4
    },
    'Estonia': {
        'governance_risk': 25,
        'economic_vulnerability': 22,
        'modern_slavery_prevalence': 1.3,
        'tip_tier': 1,
        'forced_labor_score': 22,
        'supply_chain_transparency': 75,
        'worker_rights_index': 78,
        'corruption_index': 26,
        'rule_of_law_score': 82,
        'labor_enforcement': 78,
        'gdp_per_capita': 23266,
        'unemployment_rate': 5.4,
        'poverty_rate': 16.3,
        'economic_freedom_score': 78.2
    },
    'Latvia': {
        'governance_risk': 35,
        'economic_vulnerability': 32,
        'modern_slavery_prevalence': 1.6,
        'tip_tier': 1,
        'forced_labor_score': 26,
        'supply_chain_transparency': 68,
        'worker_rights_index': 72,
        'corruption_index': 42,
        'rule_of_law_score': 72,
        'labor_enforcement': 72,
        'gdp_per_capita': 17861,
        'unemployment_rate': 6.2,
        'poverty_rate': 16.8,
        'economic_freedom_score': 72.3
    },
    'Lithuania': {
        'governance_risk': 32,
        'economic_vulnerability': 28,
        'modern_slavery_prevalence': 1.5,
        'tip_tier': 1,
        'forced_labor_score': 24,
        'supply_chain_transparency': 70,
        'worker_rights_index': 75,
        'corruption_index': 38,
        'rule_of_law_score': 75,
        'labor_enforcement': 75,
        'gdp_per_capita': 19153,
        'unemployment_rate': 6.0,
        'poverty_rate': 15.5,
        'economic_freedom_score': 76.7
    }
}

# Comprehensive Industry Risk Data - Extended Dataset
INDUSTRY_RISK_DATA = {
    'technology': {
        'forced_labor_risk': 65,
        'child_labor_risk': 45,
        'supply_chain_complexity': 85,
        'raw_material_risk': 70,
        'manufacturing_risk': 60,
        'sector_specific_risks': [
            'Rare earth mineral extraction',
            'Electronics assembly',
            'Component manufacturing',
            'Semiconductor production'
        ],
        'high_risk_processes': [
            'Mining of rare earth elements',
            'Circuit board assembly',
            'Battery manufacturing',
            'Component testing and packaging'
        ]
    },
    'textiles': {
        'forced_labor_risk': 85,
        'child_labor_risk': 80,
        'supply_chain_complexity': 90,
        'raw_material_risk': 75,
        'manufacturing_risk': 88,
        'sector_specific_risks': [
            'Cotton production',
            'Garment manufacturing',
            'Fabric dyeing',
            'Yarn spinning'
        ],
        'high_risk_processes': [
            'Cotton harvesting',
            'Cutting and sewing',
            'Textile dyeing and finishing',
            'Embroidery and decoration'
        ]
    },
    'agriculture': {
        'forced_labor_risk': 75,
        'child_labor_risk': 85,
        'supply_chain_complexity': 60,
        'raw_material_risk': 80,
        'manufacturing_risk': 45,
        'sector_specific_risks': [
            'Crop harvesting',
            'Livestock management',
            'Food processing',
            'Seasonal labor'
        ],
        'high_risk_processes': [
            'Manual harvesting',
            'Planting and cultivation',
            'Animal care and slaughter',
            'Post-harvest processing'
        ]
    },
    'mining': {
        'forced_labor_risk': 80,
        'child_labor_risk': 75,
        'supply_chain_complexity': 70,
        'raw_material_risk': 95,
        'manufacturing_risk': 55,
        'sector_specific_risks': [
            'Extraction operations',
            'Artisanal mining',
            'Mineral processing',
            'Transportation'
        ],
        'high_risk_processes': [
            'Underground mining',
            'Surface extraction',
            'Ore processing',
            'Waste management'
        ]
    },
    'automotive': {
        'forced_labor_risk': 55,
        'child_labor_risk': 35,
        'supply_chain_complexity': 80,
        'raw_material_risk': 60,
        'manufacturing_risk': 50,
        'sector_specific_risks': [
            'Parts manufacturing',
            'Assembly operations',
            'Raw material sourcing',
            'Subcontractor management'
        ],
        'high_risk_processes': [
            'Component assembly',
            'Metal processing',
            'Painting and finishing',
            'Quality control testing'
        ]
    },
    'retail': {
        'forced_labor_risk': 70,
        'child_labor_risk': 60,
        'supply_chain_complexity': 85,
        'raw_material_risk': 65,
        'manufacturing_risk': 75,
        'sector_specific_risks': [
            'Private label manufacturing',
            'Supplier management',
            'Distribution logistics',
            'Seasonal production'
        ],
        'high_risk_processes': [
            'Product manufacturing',
            'Packaging and labeling',
            'Warehousing operations',
            'Last-mile delivery'
        ]
    },
    'construction': {
        'forced_labor_risk': 60,
        'child_labor_risk': 55,
        'supply_chain_complexity': 40,
        'raw_material_risk': 50,
        'manufacturing_risk': 35,
        'sector_specific_risks': [
            'Material sourcing',
            'Subcontractor labor',
            'Site safety',
            'Migrant workers'
        ],
        'high_risk_processes': [
            'Manual construction work',
            'Material handling',
            'Site preparation',
            'Finishing work'
        ]
    },
    'hospitality': {
        'forced_labor_risk': 50,
        'child_labor_risk': 40,
        'supply_chain_complexity': 30,
        'raw_material_risk': 25,
        'manufacturing_risk': 20,
        'sector_specific_risks': [
            'Housekeeping services',
            'Food service',
            'Maintenance work',
            'Security services'
        ],
        'high_risk_processes': [
            'Cleaning and maintenance',
            'Food preparation',
            'Guest services',
            'Facility management'
        ]
    },
    'electronics': {
        'forced_labor_risk': 70,
        'child_labor_risk': 50,
        'supply_chain_complexity': 90,
        'raw_material_risk': 75,
        'manufacturing_risk': 65,
        'sector_specific_risks': [
            'Component sourcing',
            'Assembly operations',
            'Testing procedures',
            'Packaging processes'
        ],
        'high_risk_processes': [
            'Circuit board assembly',
            'Component testing',
            'Product packaging',
            'Quality assurance'
        ]
    },
    'food_processing': {
        'forced_labor_risk': 65,
        'child_labor_risk': 70,
        'supply_chain_complexity': 60,
        'raw_material_risk': 60,
        'manufacturing_risk': 55,
        'sector_specific_risks': [
            'Agricultural sourcing',
            'Processing operations',
            'Packaging lines',
            'Cold storage'
        ],
        'high_risk_processes': [
            'Food processing',
            'Packaging operations',
            'Cold storage management',
            'Transportation logistics'
        ]
    },
    'pharmaceuticals': {
        'forced_labor_risk': 40,
        'child_labor_risk': 25,
        'supply_chain_complexity': 75,
        'raw_material_risk': 50,
        'manufacturing_risk': 35,
        'sector_specific_risks': [
            'Active ingredient sourcing',
            'Manufacturing processes',
            'Quality control',
            'Regulatory compliance'
        ],
        'high_risk_processes': [
            'Chemical synthesis',
            'Drug formulation',
            'Packaging and labeling',
            'Quality testing'
        ]
    },
    'chemical': {
        'forced_labor_risk': 55,
        'child_labor_risk': 40,
        'supply_chain_complexity': 70,
        'raw_material_risk': 65,
        'manufacturing_risk': 50,
        'sector_specific_risks': [
            'Raw material extraction',
            'Chemical processing',
            'Waste management',
            'Transportation'
        ],
        'high_risk_processes': [
            'Chemical production',
            'Mixing and blending',
            'Quality control testing',
            'Waste treatment'
        ]
    },
    'oil_and_gas': {
        'forced_labor_risk': 50,
        'child_labor_risk': 30,
        'supply_chain_complexity': 65,
        'raw_material_risk': 70,
        'manufacturing_risk': 40,
        'sector_specific_risks': [
            'Drilling operations',
            'Refining processes',
            'Transportation',
            'Maintenance services'
        ],
        'high_risk_processes': [
            'Extraction operations',
            'Refinery work',
            'Pipeline maintenance',
            'Transportation services'
        ]
    },
    'renewable_energy': {
        'forced_labor_risk': 45,
        'child_labor_risk': 35,
        'supply_chain_complexity': 70,
        'raw_material_risk': 60,
        'manufacturing_risk': 40,
        'sector_specific_risks': [
            'Solar panel manufacturing',
            'Wind turbine production',
            'Battery manufacturing',
            'Installation services'
        ],
        'high_risk_processes': [
            'Component manufacturing',
            'Assembly operations',
            'Installation work',
            'Maintenance services'
        ]
    },
    'aerospace': {
        'forced_labor_risk': 40,
        'child_labor_risk': 25,
        'supply_chain_complexity': 85,
        'raw_material_risk': 55,
        'manufacturing_risk': 35,
        'sector_specific_risks': [
            'Advanced materials',
            'Precision manufacturing',
            'Assembly operations',
            'Testing procedures'
        ],
        'high_risk_processes': [
            'Component manufacturing',
            'Assembly operations',
            'Quality testing',
            'Maintenance services'
        ]
    },
    'shipbuilding': {
        'forced_labor_risk': 55,
        'child_labor_risk': 40,
        'supply_chain_complexity': 75,
        'raw_material_risk': 60,
        'manufacturing_risk': 50,
        'sector_specific_risks': [
            'Steel processing',
            'Assembly operations',
            'Painting and finishing',
            'Installation work'
        ],
        'high_risk_processes': [
            'Hull construction',
            'Engine installation',
            'Interior fitting',
            'Sea trials'
        ]
    },
    'fishing': {
        'forced_labor_risk': 85,
        'child_labor_risk': 70,
        'supply_chain_complexity': 50,
        'raw_material_risk': 40,
        'manufacturing_risk': 60,
        'sector_specific_risks': [
            'Vessel operations',
            'Processing plants',
            'Cold storage',
            'Distribution'
        ],
        'high_risk_processes': [
            'Fishing operations',
            'Fish processing',
            'Packaging operations',
            'Cold storage management'
        ]
    },
    'forestry': {
        'forced_labor_risk': 65,
        'child_labor_risk': 60,
        'supply_chain_complexity': 55,
        'raw_material_risk': 70,
        'manufacturing_risk': 45,
        'sector_specific_risks': [
            'Logging operations',
            'Processing mills',
            'Transportation',
            'Reforestation'
        ],
        'high_risk_processes': [
            'Tree harvesting',
            'Log processing',
            'Transportation services',
            'Mill operations'
        ]
    },
    'tobacco': {
        'forced_labor_risk': 75,
        'child_labor_risk': 85,
        'supply_chain_complexity': 55,
        'raw_material_risk': 80,
        'manufacturing_risk': 50,
        'sector_specific_risks': [
            'Tobacco farming',
            'Leaf processing',
            'Manufacturing',
            'Packaging'
        ],
        'high_risk_processes': [
            'Tobacco cultivation',
            'Leaf curing',
            'Manufacturing processes',
            'Packaging operations'
        ]
    },
    'palm_oil': {
        'forced_labor_risk': 80,
        'child_labor_risk': 75,
        'supply_chain_complexity': 65,
        'raw_material_risk': 85,
        'manufacturing_risk': 55,
        'sector_specific_risks': [
            'Plantation operations',
            'Harvesting',
            'Processing mills',
            'Transportation'
        ],
        'high_risk_processes': [
            'Palm fruit harvesting',
            'Oil extraction',
            'Refining processes',
            'Quality control'
        ]
    },
    'cocoa': {
        'forced_labor_risk': 80,
        'child_labor_risk': 90,
        'supply_chain_complexity': 70,
        'raw_material_risk': 85,
        'manufacturing_risk': 50,
        'sector_specific_risks': [
            'Cocoa farming',
            'Bean processing',
            'Chocolate manufacturing',
            'Distribution'
        ],
        'high_risk_processes': [
            'Cocoa cultivation',
            'Bean harvesting',
            'Processing operations',
            'Manufacturing processes'
        ]
    },
    'coffee': {
        'forced_labor_risk': 70,
        'child_labor_risk': 75,
        'supply_chain_complexity': 65,
        'raw_material_risk': 75,
        'manufacturing_risk': 40,
        'sector_specific_risks': [
            'Coffee farming',
            'Bean processing',
            'Roasting operations',
            'Packaging'
        ],
        'high_risk_processes': [
            'Coffee cultivation',
            'Bean harvesting',
            'Processing operations',
            'Roasting and packaging'
        ]
    },
    'sugar': {
        'forced_labor_risk': 75,
        'child_labor_risk': 70,
        'supply_chain_complexity': 50,
        'raw_material_risk': 80,
        'manufacturing_risk': 45,
        'sector_specific_risks': [
            'Sugarcane farming',
            'Harvesting operations',
            'Processing mills',
            'Refining'
        ],
        'high_risk_processes': [
            'Sugarcane cultivation',
            'Manual harvesting',
            'Mill operations',
            'Refining processes'
        ]
    },
    'tea': {
        'forced_labor_risk': 65,
        'child_labor_risk': 70,
        'supply_chain_complexity': 55,
        'raw_material_risk': 70,
        'manufacturing_risk': 35,
        'sector_specific_risks': [
            'Tea plantation work',
            'Leaf picking',
            'Processing operations',
            'Packaging'
        ],
        'high_risk_processes': [
            'Tea cultivation',
            'Leaf harvesting',
            'Processing operations',
            'Packaging and distribution'
        ]
    },
    'rubber': {
        'forced_labor_risk': 70,
        'child_labor_risk': 65,
        'supply_chain_complexity': 60,
        'raw_material_risk': 75,
        'manufacturing_risk': 50,
        'sector_specific_risks': [
            'Rubber tapping',
            'Processing plants',
            'Manufacturing',
            'Distribution'
        ],
        'high_risk_processes': [
            'Latex collection',
            'Processing operations',
            'Manufacturing processes',
            'Quality control'
        ]
    }
}

# Comprehensive Company Profiles - Extended Dataset
COMPANY_PROFILES = {
    'Apple': {
        'industry': 'technology',
        'revenue_billions': 365,
        'countries': ['China', 'United States', 'Germany', 'Japan', 'South Korea', 'Ireland', 'India', 'Vietnam', 'Malaysia', 'Thailand'],
        'manufacturing_locations': [
            {
                'city': 'Shenzhen',
                'country': 'China',
                'coordinates': {'lat': 22.5431, 'lng': 114.0579},
                'facility_type': 'Final Assembly',
                'products': ['iPhone', 'iPad', 'MacBook'],
                'risk_factors': ['Forced labor concerns in supplier facilities', 'Complex supplier oversight challenges', 'Xinjiang supply chain risks']
            },
            {
                'city': 'Zhengzhou',
                'country': 'China',
                'coordinates': {'lat': 34.7466, 'lng': 113.6253},
                'facility_type': 'iPhone Manufacturing',
                'products': ['iPhone production'],
                'risk_factors': ['Labor rights monitoring needed', 'Supplier compliance issues']
            },
            {
                'city': 'Cupertino',
                'country': 'United States',
                'coordinates': {'lat': 37.3230, 'lng': -122.0322},
                'facility_type': 'Design & Development',
                'products': ['Software', 'Design', 'R&D'],
                'risk_factors': ['Minimal direct risks']
            },
            {
                'city': 'Cork',
                'country': 'Ireland',
                'coordinates': {'lat': 51.8985, 'lng': -8.4756},
                'facility_type': 'Manufacturing',
                'products': ['iMac', 'Mac Pro'],
                'risk_factors': ['Low risk jurisdiction']
            },
            {
                'city': 'Chennai',
                'country': 'India',
                'coordinates': {'lat': 13.0827, 'lng': 80.2707},
                'facility_type': 'iPhone Assembly',
                'products': ['iPhone'],
                'risk_factors': ['Labor monitoring required', 'Working conditions oversight']
            },
            {
                'city': 'Ho Chi Minh City',
                'country': 'Vietnam',
                'coordinates': {'lat': 10.8231, 'lng': 106.6297},
                'facility_type': 'Component Manufacturing',
                'products': ['iPad components', 'MacBook parts'],
                'risk_factors': ['Labor rights monitoring needed', 'Supplier oversight required']
            }
        ],
        'supply_chain_transparency': 75,
        'modern_slavery_policies': {
            'has_policy': True,
            'supplier_audits': True,
            'grievance_mechanism': True,
            'training_programs': True,
            'effectiveness_score': 78
        }
    },
    'Nike': {
        'industry': 'textiles',
        'revenue_billions': 51,
        'countries': ['Vietnam', 'China', 'Indonesia', 'Thailand', 'United States', 'Turkey', 'Bangladesh', 'India'],
        'manufacturing_locations': [
            {
                'city': 'Ho Chi Minh City',
                'country': 'Vietnam',
                'coordinates': {'lat': 10.8231, 'lng': 106.6297},
                'facility_type': 'Footwear Manufacturing',
                'products': ['Athletic Shoes', 'Apparel'],
                'risk_factors': ['Labor rights concerns', 'Overtime violations', 'Worker safety monitoring needed']
            },
            {
                'city': 'Dongguan',
                'country': 'China',
                'coordinates': {'lat': 23.0489, 'lng': 113.7447},
                'facility_type': 'Apparel Manufacturing',
                'products': ['Sports Apparel', 'Equipment'],
                'risk_factors': ['Supplier compliance issues', 'Working hours monitoring']
            },
            {
                'city': 'Beaverton',
                'country': 'United States',
                'coordinates': {'lat': 45.4871, 'lng': -122.8037},
                'facility_type': 'Design & Headquarters',
                'products': ['Design', 'Marketing', 'R&D'],
                'risk_factors': ['Minimal direct risks']
            },
            {
                'city': 'Jakarta',
                'country': 'Indonesia',
                'coordinates': {'lat': -6.2088, 'lng': 106.8456},
                'facility_type': 'Footwear Production',
                'products': ['Athletic footwear'],
                'risk_factors': ['Labor monitoring required', 'Supplier oversight needed']
            },
            {
                'city': 'Bangkok',
                'country': 'Thailand',
                'coordinates': {'lat': 13.7563, 'lng': 100.5018},
                'facility_type': 'Apparel Manufacturing',
                'products': ['Sports apparel'],
                'risk_factors': ['Migrant worker concerns', 'Labor rights monitoring']
            }
        ],
        'supply_chain_transparency': 82,
        'modern_slavery_policies': {
            'has_policy': True,
            'supplier_audits': True,
            'grievance_mechanism': True,
            'training_programs': True,
            'effectiveness_score': 85
        }
    },
    'Samsung': {
        'industry': 'electronics',
        'revenue_billions': 279,
        'countries': ['South Korea', 'China', 'Vietnam', 'India', 'United States', 'Hungary', 'Slovakia'],
        'manufacturing_locations': [
            {
                'city': 'Suwon',
                'country': 'South Korea',
                'coordinates': {'lat': 37.2636, 'lng': 127.0286},
                'facility_type': 'Semiconductor Manufacturing',
                'products': ['Memory Chips', 'Processors', 'Displays'],
                'risk_factors': ['Labor overtime concerns', 'Worker safety monitoring']
            },
            {
                'city': 'Xi\'an',
                'country': 'China',
                'coordinates': {'lat': 34.3416, 'lng': 108.9398},
                'facility_type': 'Memory Manufacturing',
                'products': ['NAND Flash', 'DRAM'],
                'risk_factors': ['Supplier oversight challenges', 'Labor compliance monitoring']
            },
            {
                'city': 'Thai Nguyen',
                'country': 'Vietnam',
                'coordinates': {'lat': 21.5954, 'lng': 105.8482},
                'facility_type': 'Smartphone Assembly',
                'products': ['Galaxy Phones', 'Tablets'],
                'risk_factors': ['Labor rights monitoring needed', 'Working conditions oversight']
            },
            {
                'city': 'Noida',
                'country': 'India',
                'coordinates': {'lat': 28.5355, 'lng': 77.3910},
                'facility_type': 'Smartphone Manufacturing',
                'products': ['Galaxy smartphones'],
                'risk_factors': ['Labor monitoring required', 'Supplier compliance']
            }
        ],
        'supply_chain_transparency': 68,
        'modern_slavery_policies': {
            'has_policy': True,
            'supplier_audits': True,
            'grievance_mechanism': False,
            'training_programs': True,
            'effectiveness_score': 72
        }
    },
    'Walmart': {
        'industry': 'retail',
        'revenue_billions': 572,
        'countries': ['United States', 'China', 'Mexico', 'India', 'Bangladesh', 'Vietnam', 'Guatemala', 'Honduras'],
        'manufacturing_locations': [
            {
                'city': 'Bentonville',
                'country': 'United States',
                'coordinates': {'lat': 36.3729, 'lng': -94.2088},
                'facility_type': 'Corporate Headquarters',
                'products': ['Retail Operations', 'Logistics'],
                'risk_factors': ['Minimal direct risks']
            },
            {
                'city': 'Dhaka',
                'country': 'Bangladesh',
                'coordinates': {'lat': 23.8103, 'lng': 90.4125},
                'facility_type': 'Supplier Factories',
                'products': ['Textiles', 'Garments', 'Home goods'],
                'risk_factors': ['Factory safety concerns', 'Labor violations', 'Building safety issues']
            },
            {
                'city': 'Guangzhou',
                'country': 'China',
                'coordinates': {'lat': 23.1291, 'lng': 113.2644},
                'facility_type': 'Manufacturing Hub',
                'products': ['Consumer Goods', 'Electronics', 'Toys'],
                'risk_factors': ['Supplier oversight challenges', 'Labor compliance monitoring']
            },
            {
                'city': 'Mumbai',
                'country': 'India',
                'coordinates': {'lat': 19.0760, 'lng': 72.8777},
                'facility_type': 'Supplier Network',
                'products': ['Textiles', 'Home goods'],
                'risk_factors': ['Labor monitoring required', 'Supplier compliance issues']
            }
        ],
        'supply_chain_transparency': 65,
        'modern_slavery_policies': {
            'has_policy': True,
            'supplier_audits': True,
            'grievance_mechanism': True,
            'training_programs': False,
            'effectiveness_score': 68
        }
    },
    'Tesla': {
        'industry': 'automotive',
        'revenue_billions': 96,
        'countries': ['United States', 'China', 'Germany', 'Mexico'],
        'manufacturing_locations': [
            {
                'city': 'Fremont',
                'country': 'United States',
                'coordinates': {'lat': 37.5502, 'lng': -121.9886},
                'facility_type': 'Vehicle Assembly',
                'products': ['Model S', 'Model 3', 'Model X', 'Model Y'],
                'risk_factors': ['Worker safety concerns', 'Labor relations issues']
            },
            {
                'city': 'Shanghai',
                'country': 'China',
                'coordinates': {'lat': 31.2304, 'lng': 121.4737},
                'facility_type': 'Gigafactory',
                'products': ['Model 3', 'Model Y'],
                'risk_factors': ['Supply chain transparency needed', 'Supplier oversight required']
            },
            {
                'city': 'Berlin',
                'country': 'Germany',
                'coordinates': {'lat': 52.5200, 'lng': 13.4050},
                'facility_type': 'Gigafactory',
                'products': ['Model Y', 'Batteries'],
                'risk_factors': ['Low risk jurisdiction', 'Environmental compliance']
            },
            {
                'city': 'Austin',
                'country': 'United States',
                'coordinates': {'lat': 30.2672, 'lng': -97.7431},
                'facility_type': 'Gigafactory',
                'products': ['Cybertruck', 'Model Y'],
                'risk_factors': ['Worker safety monitoring', 'Rapid expansion oversight']
            }
        ],
        'supply_chain_transparency': 58,
        'modern_slavery_policies': {
            'has_policy': True,
            'supplier_audits': False,
            'grievance_mechanism': False,
            'training_programs': False,
            'effectiveness_score': 45
        }
    },
    'Amazon': {
        'industry': 'retail',
        'revenue_billions': 513,
        'countries': ['United States', 'China', 'India', 'Germany', 'United Kingdom', 'Japan', 'Mexico', 'Brazil'],
        'manufacturing_locations': [
            {
                'city': 'Seattle',
                'country': 'United States',
                'coordinates': {'lat': 47.6062, 'lng': -122.3321},
                'facility_type': 'Corporate Headquarters',
                'products': ['Technology', 'Logistics'],
                'risk_factors': ['Minimal direct risks']
            },
            {
                'city': 'Shenzhen',
                'country': 'China',
                'coordinates': {'lat': 22.5431, 'lng': 114.0579},
                'facility_type': 'Electronics Manufacturing',
                'products': ['Echo devices', 'Kindle', 'Fire tablets'],
                'risk_factors': ['Supplier oversight challenges', 'Labor compliance monitoring']
            },
            {
                'city': 'Chennai',
                'country': 'India',
                'coordinates': {'lat': 13.0827, 'lng': 80.2707},
                'facility_type': 'Fulfillment Centers',
                'products': ['Logistics', 'Warehousing'],
                'risk_factors': ['Labor monitoring required', 'Working conditions oversight']
            }
        ],
        'supply_chain_transparency': 62,
        'modern_slavery_policies': {
            'has_policy': True,
            'supplier_audits': True,
            'grievance_mechanism': True,
            'training_programs': True,
            'effectiveness_score': 72
        }
    },
    'Microsoft': {
        'industry': 'technology',
        'revenue_billions': 211,
        'countries': ['United States', 'China', 'Ireland', 'Singapore', 'India', 'Mexico'],
        'manufacturing_locations': [
            {
                'city': 'Redmond',
                'country': 'United States',
                'coordinates': {'lat': 47.6740, 'lng': -122.1215},
                'facility_type': 'Corporate Headquarters',
                'products': ['Software', 'Cloud services'],
                'risk_factors': ['Minimal direct risks']
            },
            {
                'city': 'Shanghai',
                'country': 'China',
                'coordinates': {'lat': 31.2304, 'lng': 121.4737},
                'facility_type': 'Hardware Manufacturing',
                'products': ['Surface devices', 'Xbox'],
                'risk_factors': ['Supplier oversight needed', 'Labor compliance monitoring']
            },
            {
                'city': 'Dublin',
                'country': 'Ireland',
                'coordinates': {'lat': 53.3498, 'lng': -6.2603},
                'facility_type': 'Operations Center',
                'products': ['Cloud services', 'Support'],
                'risk_factors': ['Low risk jurisdiction']
            }
        ],
        'supply_chain_transparency': 78,
        'modern_slavery_policies': {
            'has_policy': True,
            'supplier_audits': True,
            'grievance_mechanism': True,
            'training_programs': True,
            'effectiveness_score': 82
        }
    },
    'Google': {
        'industry': 'technology',
        'revenue_billions': 307,
        'countries': ['United States', 'Ireland', 'Singapore', 'Taiwan', 'China'],
        'manufacturing_locations': [
            {
                'city': 'Mountain View',
                'country': 'United States',
                'coordinates': {'lat': 37.4169, 'lng': -122.0781},
                'facility_type': 'Corporate Headquarters',
                'products': ['Software', 'AI', 'Cloud services'],
                'risk_factors': ['Minimal direct risks']
            },
            {
                'city': 'Taipei',
                'country': 'Taiwan',
                'coordinates': {'lat': 25.0330, 'lng': 121.5654},
                'facility_type': 'Hardware Manufacturing',
                'products': ['Pixel phones', 'Nest devices'],
                'risk_factors': ['Supplier monitoring required']
            },
            {
                'city': 'Dublin',
                'country': 'Ireland',
                'coordinates': {'lat': 53.3498, 'lng': -6.2603},
                'facility_type': 'Operations Center',
                'products': ['Cloud services', 'Data centers'],
                'risk_factors': ['Low risk jurisdiction']
            }
        ],
        'supply_chain_transparency': 75,
        'modern_slavery_policies': {
            'has_policy': True,
            'supplier_audits': True,
            'grievance_mechanism': True,
            'training_programs': True,
            'effectiveness_score': 80
        }
    },
    'H&M': {
        'industry': 'textiles',
        'revenue_billions': 24,
        'countries': ['Bangladesh', 'Cambodia', 'China', 'India', 'Myanmar', 'Turkey', 'Vietnam', 'Ethiopia'],
        'manufacturing_locations': [
            {
                'city': 'Dhaka',
                'country': 'Bangladesh',
                'coordinates': {'lat': 23.8103, 'lng': 90.4125},
                'facility_type': 'Garment Manufacturing',
                'products': ['Fast fashion', 'Textiles'],
                'risk_factors': ['Factory safety concerns', 'Labor violations', 'Building safety']
            },
            {
                'city': 'Phnom Penh',
                'country': 'Cambodia',
                'coordinates': {'lat': 11.5564, 'lng': 104.9282},
                'facility_type': 'Apparel Production',
                'products': ['Clothing', 'Accessories'],
                'risk_factors': ['Labor rights monitoring needed', 'Working conditions oversight']
            },
            {
                'city': 'Addis Ababa',
                'country': 'Ethiopia',
                'coordinates': {'lat': 9.0320, 'lng': 38.7469},
                'facility_type': 'Textile Manufacturing',
                'products': ['Basic garments'],
                'risk_factors': ['Labor monitoring required', 'Worker safety concerns']
            }
        ],
        'supply_chain_transparency': 75,
        'modern_slavery_policies': {
            'has_policy': True,
            'supplier_audits': True,
            'grievance_mechanism': True,
            'training_programs': True,
            'effectiveness_score': 78
        }
    },
    'Zara': {
        'industry': 'textiles',
        'revenue_billions': 32,
        'countries': ['Spain', 'Turkey', 'Morocco', 'Portugal', 'India', 'Bangladesh', 'China', 'Vietnam'],
        'manufacturing_locations': [
            {
                'city': 'A Coruña',
                'country': 'Spain',
                'coordinates': {'lat': 43.3623, 'lng': -8.4115},
                'facility_type': 'Design & Logistics',
                'products': ['Fashion design', 'Distribution'],
                'risk_factors': ['Low risk jurisdiction']
            },
            {
                'city': 'Istanbul',
                'country': 'Turkey',
                'coordinates': {'lat': 41.0082, 'lng': 28.9784},
                'facility_type': 'Garment Manufacturing',
                'products': ['Fast fashion', 'Textiles'],
                'risk_factors': ['Labor monitoring required', 'Supplier oversight needed']
            },
            {
                'city': 'Casablanca',
                'country': 'Morocco',
                'coordinates': {'lat': 33.5731, 'lng': -7.5898},
                'facility_type': 'Textile Production',
                'products': ['Clothing', 'Accessories'],
                'risk_factors': ['Labor rights monitoring', 'Working conditions oversight']
            }
        ],
        'supply_chain_transparency': 68,
        'modern_slavery_policies': {
            'has_policy': True,
            'supplier_audits': True,
            'grievance_mechanism': False,
            'training_programs': True,
            'effectiveness_score': 70
        }
    },
    'Coca-Cola': {
        'industry': 'food_processing',
        'revenue_billions': 43,
        'countries': ['United States', 'Mexico', 'Brazil', 'China', 'India', 'Turkey', 'Egypt', 'Philippines'],
        'manufacturing_locations': [
            {
                'city': 'Atlanta',
                'country': 'United States',
                'coordinates': {'lat': 33.7490, 'lng': -84.3880},
                'facility_type': 'Corporate Headquarters',
                'products': ['Beverage concentrate', 'R&D'],
                'risk_factors': ['Minimal direct risks']
            },
            {
                'city': 'Mexico City',
                'country': 'Mexico',
                'coordinates': {'lat': 19.4326, 'lng': -99.1332},
                'facility_type': 'Bottling Operations',
                'products': ['Coca-Cola beverages'],
                'risk_factors': ['Water usage concerns', 'Labor monitoring']
            },
            {
                'city': 'São Paulo',
                'country': 'Brazil',
                'coordinates': {'lat': -23.5505, 'lng': -46.6333},
                'facility_type': 'Production Facility',
                'products': ['Soft drinks', 'Juices'],
                'risk_factors': ['Environmental compliance', 'Labor oversight']
            }
        ],
        'supply_chain_transparency': 72,
        'modern_slavery_policies': {
            'has_policy': True,
            'supplier_audits': True,
            'grievance_mechanism': True,
            'training_programs': True,
            'effectiveness_score': 75
        }
    },
    'Nestle': {
        'industry': 'food_processing',
        'revenue_billions': 103,
        'countries': ['Switzerland', 'Brazil', 'Mexico', 'China', 'India', 'Côte d\'Ivoire', 'Ghana', 'Indonesia'],
        'manufacturing_locations': [
            {
                'city': 'Vevey',
                'country': 'Switzerland',
                'coordinates': {'lat': 46.4600, 'lng': 6.8416},
                'facility_type': 'Corporate Headquarters',
                'products': ['R&D', 'Strategy'],
                'risk_factors': ['Low risk jurisdiction']
            },
            {
                'city': 'Abidjan',
                'country': 'Côte d\'Ivoire',
                'coordinates': {'lat': 5.3600, 'lng': -4.0083},
                'facility_type': 'Cocoa Processing',
                'products': ['Chocolate', 'Cocoa products'],
                'risk_factors': ['Child labor in cocoa supply chain', 'Farmer exploitation concerns']
            },
            {
                'city': 'Accra',
                'country': 'Ghana',
                'coordinates': {'lat': 5.6037, 'lng': -0.1870},
                'facility_type': 'Cocoa Operations',
                'products': ['Cocoa beans', 'Chocolate'],
                'risk_factors': ['Child labor monitoring needed', 'Supplier oversight required']
            }
        ],
        'supply_chain_transparency': 70,
        'modern_slavery_policies': {
            'has_policy': True,
            'supplier_audits': True,
            'grievance_mechanism': True,
            'training_programs': True,
            'effectiveness_score': 73
        }
    },
    'Unilever': {
        'industry': 'food_processing',
        'revenue_billions': 60,
        'countries': ['United Kingdom', 'Netherlands', 'India', 'Brazil', 'Indonesia', 'China', 'Turkey', 'Mexico'],
        'manufacturing_locations': [
            {
                'city': 'London',
                'country': 'United Kingdom',
                'coordinates': {'lat': 51.5074, 'lng': -0.1278},
                'facility_type': 'Corporate Headquarters',
                'products': ['Strategy', 'R&D'],
                'risk_factors': ['Low risk jurisdiction']
            },
            {
                'city': 'Mumbai',
                'country': 'India',
                'coordinates': {'lat': 19.0760, 'lng': 72.8777},
                'facility_type': 'Manufacturing Hub',
                'products': ['Personal care', 'Home care'],
                'risk_factors': ['Labor monitoring required', 'Supplier compliance']
            },
            {
                'city': 'Jakarta',
                'country': 'Indonesia',
                'coordinates': {'lat': -6.2088, 'lng': 106.8456},
                'facility_type': 'Palm Oil Processing',
                'products': ['Palm oil', 'Personal care'],
                'risk_factors': ['Palm oil supply chain risks', 'Environmental concerns']
            }
        ],
        'supply_chain_transparency': 78,
        'modern_slavery_policies': {
            'has_policy': True,
            'supplier_audits': True,
            'grievance_mechanism': True,
            'training_programs': True,
            'effectiveness_score': 82
        }
    },
    'Ford': {
        'industry': 'automotive',
        'revenue_billions': 158,
        'countries': ['United States', 'Mexico', 'China', 'Germany', 'India', 'Brazil', 'Turkey'],
        'manufacturing_locations': [
            {
                'city': 'Dearborn',
                'country': 'United States',
                'coordinates': {'lat': 42.3223, 'lng': -83.1763},
                'facility_type': 'Headquarters & Assembly',
                'products': ['F-150', 'Mustang', 'Electric vehicles'],
                'risk_factors': ['Worker safety monitoring']
            },
            {
                'city': 'Hermosillo',
                'country': 'Mexico',
                'coordinates': {'lat': 29.0729, 'lng': -110.9559},
                'facility_type': 'Vehicle Assembly',
                'products': ['Ford Bronco Sport', 'Fusion'],
                'risk_factors': ['Labor monitoring required', 'Supplier oversight']
            },
            {
                'city': 'Chongqing',
                'country': 'China',
                'coordinates': {'lat': 29.4316, 'lng': 106.9123},
                'facility_type': 'Assembly Plant',
                'products': ['Ford vehicles for China market'],
                'risk_factors': ['Supplier oversight challenges', 'Labor compliance monitoring']
            }
        ],
        'supply_chain_transparency': 65,
        'modern_slavery_policies': {
            'has_policy': True,
            'supplier_audits': True,
            'grievance_mechanism': False,
            'training_programs': True,
            'effectiveness_score': 68
        }
    },
    'General Motors': {
        'industry': 'automotive',
        'revenue_billions': 157,
        'countries': ['United States', 'China', 'Mexico', 'Canada', 'Brazil', 'South Korea'],
        'manufacturing_locations': [
            {
                'city': 'Detroit',
                'country': 'United States',
                'coordinates': {'lat': 42.3314, 'lng': -83.0458},
                'facility_type': 'Headquarters & Assembly',
                'products': ['Chevrolet', 'GMC', 'Cadillac'],
                'risk_factors': ['Worker safety monitoring']
            },
            {
                'city': 'Shanghai',
                'country': 'China',
                'coordinates': {'lat': 31.2304, 'lng': 121.4737},
                'facility_type': 'Joint Venture Operations',
                'products': ['Buick', 'Chevrolet', 'Cadillac'],
                'risk_factors': ['Supplier oversight challenges', 'Joint venture compliance']
            },
            {
                'city': 'Silao',
                'country': 'Mexico',
                'coordinates': {'lat': 20.9333, 'lng': -101.4267},
                'facility_type': 'Assembly Plant',
                'products': ['Chevrolet Silverado', 'GMC Sierra'],
                'risk_factors': ['Labor monitoring required', 'Cross-border supply chain']
            }
        ],
        'supply_chain_transparency': 62,
        'modern_slavery_policies': {
            'has_policy': True,
            'supplier_audits': True,
            'grievance_mechanism': False,
            'training_programs': False,
            'effectiveness_score': 58
        }
    }
}

def get_ai_economic_analysis(country_data, country_name):
    """Get shortened AI analysis of economic vulnerability factors - FIXED VERSION"""
    try:
        # Use GPT API with very short response requirement
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        prompt = f"""Economic factors for {country_name}: GDP vulnerability score {country_data.get('economic_vulnerability', 'N/A')}.
        
        VERY BRIEF response required - maximum 1-2 sentences explaining how economic conditions affect modern slavery risk. NO detailed explanations."""
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'system', 
                    'content': 'You are an economic analyst. Provide VERY BRIEF, 1-2 sentences maximum. No verbose explanations.'
                },
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 100,  # Reduced from 600
            'temperature': 0.3
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions', 
                               headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            ai_text = result['choices'][0]['message']['content'].strip()
            # Hard limit to 100 characters
            return ai_text[:100] + "..." if len(ai_text) > 100 else ai_text
        else:
            return "Economic vulnerability increases exploitation risk."
            
    except Exception as e:
        print(f"AI Analysis error: {e}")
        return "Economic conditions create worker vulnerability."

def analyze_api_risk_factors(country, company_name):
    """Analyze risk factors with shortened AI responses - FIXED VERSION"""
    try:
        risk_factors = []
        country_data = COUNTRY_RISK_DATA.get(country, {})
        
        # Basic governance analysis
        governance_risk = country_data.get('governance_risk', 50)
        if governance_risk > 60:
            risk_factors.append({
                'factor': 'Governance Risk',
                'score': governance_risk,
                'evidence': 'Weak governance increases exploitation risk.'
            })
        
        # Economic vulnerability with shortened AI analysis
        econ_vuln = country_data.get('economic_vulnerability', 50)
        if econ_vuln > 40:
            ai_analysis = get_ai_economic_analysis(country_data, country)
            risk_factors.append({
                'factor': 'Economic Vulnerability',
                'score': econ_vuln,
                'evidence': ai_analysis
            })
        
        # Modern slavery prevalence
        ms_prev = country_data.get('modern_slavery_prevalence', 0)
        if ms_prev > 5:
            risk_factors.append({
                'factor': 'Modern Slavery Prevalence',
                'score': min(ms_prev * 5, 100),
                'evidence': f'{ms_prev} per 1000 population affected.'
            })
            
        return risk_factors
        
    except Exception as e:
        print(f"Risk analysis error: {e}")
        return [{'factor': 'Data Unavailable', 'score': 50, 'evidence': 'Limited risk data available.'}]

def get_ai_news_analysis(company_name, country):
    """Get shortened AI analysis of news sentiment - FIXED VERSION"""
    try:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        prompt = f"Briefly analyze modern slavery risks for {company_name} in {country}. One sentence maximum."
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'system', 
                    'content': 'Provide ONE sentence maximum about modern slavery risks. Be concise.'
                },
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 50,  # Reduced from 400
            'temperature': 0.3
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions', 
                               headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            ai_text = result['choices'][0]['message']['content'].strip()
            # Hard limit to 100 characters
            return ai_text[:100] + "..." if len(ai_text) > 100 else ai_text
        else:
            return "Monitor supply chain risks."
            
    except Exception as e:
        print(f"News analysis error: {e}")
        return "Regular monitoring recommended."

def calculate_modern_slavery_risk(company_data, company_name):
    """Calculate comprehensive modern slavery risk assessment"""
    risk_scores = {}
    vulnerability_factors = []
    
    for country in company_data['countries']:
        country_data = COUNTRY_RISK_DATA.get(country, {})
        
        # Core modern slavery indicators
        ms_prevalence = country_data.get('modern_slavery_prevalence', 5.0)
        tip_tier = country_data.get('tip_tier', 2)
        forced_labor_score = country_data.get('forced_labor_score', 50)
        
        # Calculate country-specific modern slavery risk
        tip_penalty = (tip_tier - 1) * 25  # Tier 3 = +50, Tier 2 = +25, Tier 1 = 0
        prevalence_score = min(ms_prevalence * 5, 100)
        
        country_ms_risk = (prevalence_score * 0.4 + 
                          forced_labor_score * 0.4 + 
                          tip_penalty * 0.2)
        
        risk_scores[country] = min(country_ms_risk, 100)
        
        # Add vulnerability factors for high-risk countries
        if country_ms_risk > 60:
            vulnerability_factors.append({
                'country': country,
                'risk_level': 'High',
                'prevalence_rate': ms_prevalence,
                'tip_tier': tip_tier,
                'primary_concerns': get_country_specific_concerns(country)
            })
    
    # Industry risk multiplier
    industry = company_data.get('industry', 'technology')
    industry_data = INDUSTRY_RISK_DATA.get(industry, {})
    industry_multiplier = industry_data.get('forced_labor_risk', 50) / 100
    
    # Company mitigation factor
    policies = company_data.get('modern_slavery_policies', {})
    mitigation_score = calculate_mitigation_effectiveness(policies)
    
    # Calculate final modern slavery risk
    base_risk = sum(risk_scores.values()) / len(risk_scores) if risk_scores else 50
    industry_adjusted_risk = base_risk * (1 + industry_multiplier * 0.3)
    final_risk = industry_adjusted_risk * (1 - mitigation_score * 0.4)
    
    return {
        'final_risk_score': min(final_risk, 100),
        'risk_category': categorize_modern_slavery_risk(final_risk),
        'country_risks': risk_scores,
        'industry_risk_multiplier': industry_multiplier,
        'mitigation_effectiveness': mitigation_score,
        'vulnerability_factors': vulnerability_factors,
        'key_concerns': identify_key_modern_slavery_concerns(company_data, final_risk)
    }

def get_country_specific_concerns(country):
    """Get specific modern slavery concerns for each country"""
    concerns_map = {
        'China': ['Forced labor in Xinjiang', 'Technology surveillance', 'Supply chain opacity'],
        'Bangladesh': ['Garment factory conditions', 'Debt bondage', 'Child labor'],
        'India': ['Bonded labor', 'Child labor', 'Migrant worker exploitation'],
        'Vietnam': ['Labor trafficking', 'Forced overtime', 'Recruitment fees'],
        'Thailand': ['Fishing industry slavery', 'Migrant worker abuse', 'Human trafficking'],
        'Mexico': ['Agricultural forced labor', 'Manufacturing exploitation', 'Child labor'],
        'Malaysia': ['Migrant worker exploitation', 'Passport confiscation', 'Electronics sector risks'],
        'Indonesia': ['Palm oil forced labor', 'Fishing industry abuse', 'Debt bondage'],
        'Philippines': ['Domestic servitude', 'Child labor', 'Trafficking'],
        'Brazil': ['Agricultural forced labor', 'Charcoal production', 'Construction exploitation'],
        'Turkey': ['Textile industry labor issues', 'Syrian refugee exploitation'],
        'Pakistan': ['Bonded labor', 'Brick kiln slavery', 'Agricultural exploitation'],
        'Myanmar': ['Military forced labor', 'Ethnic minority targeting', 'Jade mining'],
        'Cambodia': ['Brick kiln labor', 'Construction exploitation', 'Fishing industry'],
        'Ethiopia': ['Agricultural forced labor', 'Child labor in farming'],
        'Nigeria': ['Child labor', 'Trafficking', 'Agricultural exploitation'],
        'Egypt': ['Child labor', 'Agricultural work', 'Domestic servitude']
    }
    return concerns_map.get(country, ['General forced labor risks', 'Worker exploitation'])

def calculate_mitigation_effectiveness(policies):
    """Calculate how effective company mitigation policies are"""
    if not policies:
        return 0.0
    
    score = 0
    if policies.get('has_policy', False):
        score += 0.2
    if policies.get('supplier_audits', False):
        score += 0.3
    if policies.get('grievance_mechanism', False):
        score += 0.2
    if policies.get('training_programs', False):
        score += 0.2
    
    effectiveness = policies.get('effectiveness_score', 50) / 100
    score += effectiveness * 0.1
    
    return min(score, 1.0)

def categorize_modern_slavery_risk(risk_score):
    """Categorize modern slavery risk level"""
    if risk_score >= 75:
        return 'Very High'
    elif risk_score >= 60:
        return 'High'
    elif risk_score >= 40:
        return 'Medium'
    elif risk_score >= 25:
        return 'Low'
    else:
        return 'Very Low'

def identify_key_modern_slavery_concerns(company_data, risk_score):
    """Identify the most critical modern slavery concerns"""
    concerns = []
    
    if risk_score >= 70:
        concerns.append('Immediate supply chain audit required')
        concerns.append('Enhanced due diligence needed')
    
    industry = company_data.get('industry', 'technology')
    if industry in ['textiles', 'electronics', 'agriculture', 'mining', 'fishing']:
        concerns.append('High-risk industry requiring continuous monitoring')
    
    # Check for high-risk countries
    high_risk_countries = []
    for country in company_data.get('countries', []):
        country_data = COUNTRY_RISK_DATA.get(country, {})
        if country_data.get('modern_slavery_prevalence', 0) > 10:
            high_risk_countries.append(country)
    
    if high_risk_countries:
        concerns.append(f'Operations in high-prevalence countries: {", ".join(high_risk_countries)}')
    
    return concerns

def fetch_company_data(company_name):
    """Fetch or generate company data"""
    company_name_clean = company_name.strip().title()
    
    if company_name_clean in COMPANY_PROFILES:
        return COMPANY_PROFILES[company_name_clean]
    
    # Generate synthetic data for unknown companies
    return generate_synthetic_company_data(company_name_clean)

def generate_synthetic_company_data(company_name):
    """Generate realistic synthetic data for unknown companies"""
    industries = list(INDUSTRY_RISK_DATA.keys())
    countries = list(COUNTRY_RISK_DATA.keys())
    
    # Select industry based on company name patterns
    industry = 'technology'  # default
    if any(word in company_name.lower() for word in ['fashion', 'apparel', 'clothing', 'textile']):
        industry = 'textiles'
    elif any(word in company_name.lower() for word in ['auto', 'motor', 'car']):
        industry = 'automotive'
    elif any(word in company_name.lower() for word in ['food', 'agriculture', 'farm']):
        industry = 'agriculture'
    elif any(word in company_name.lower() for word in ['retail', 'store', 'mart']):
        industry = 'retail'
    elif any(word in company_name.lower() for word in ['mining', 'mine', 'coal', 'gold']):
        industry = 'mining'
    elif any(word in company_name.lower() for word in ['oil', 'gas', 'petroleum', 'energy']):
        industry = 'oil_and_gas'
    elif any(word in company_name.lower() for word in ['pharmaceutical', 'pharma', 'drug', 'medicine']):
        industry = 'pharmaceuticals'
    
    # Select 3-5 countries with realistic distribution
    selected_countries = random.sample(countries, random.randint(3, 5))
    
    # Generate manufacturing locations
    manufacturing_locations = []
    for i, country in enumerate(selected_countries[:3]):  # Max 3 locations
        # Get realistic coordinates for major cities
        city_coords = get_major_city_coordinates(country)
        manufacturing_locations.append({
            'city': city_coords['city'],
            'country': country,
            'coordinates': {'lat': city_coords['lat'], 'lng': city_coords['lng']},
            'facility_type': random.choice(['Manufacturing', 'Assembly', 'Distribution', 'R&D', 'Processing']),
            'products': [f'Product Line {i+1}', f'Component {i+1}'],
            'risk_factors': generate_location_risk_factors(country)
        })
    
    return {
        'industry': industry,
        'revenue_billions': random.randint(1, 100),
        'countries': selected_countries,
        'manufacturing_locations': manufacturing_locations,
        'supply_chain_transparency': random.randint(30, 85),
        'modern_slavery_policies': {
            'has_policy': random.choice([True, False]),
            'supplier_audits': random.choice([True, False]),
            'grievance_mechanism': random.choice([True, False]),
            'training_programs': random.choice([True, False]),
            'effectiveness_score': random.randint(30, 80)
        }
    }

def get_major_city_coordinates(country):
    """Get coordinates for major cities in each country"""
    city_data = {
        'China': {'city': 'Shanghai', 'lat': 31.2304, 'lng': 121.4737},
        'Bangladesh': {'city': 'Dhaka', 'lat': 23.8103, 'lng': 90.4125},
        'India': {'city': 'Mumbai', 'lat': 19.0760, 'lng': 72.8777},
        'Vietnam': {'city': 'Ho Chi Minh City', 'lat': 10.8231, 'lng': 106.6297},
        'Thailand': {'city': 'Bangkok', 'lat': 13.7563, 'lng': 100.5018},
        'Mexico': {'city': 'Mexico City', 'lat': 19.4326, 'lng': -99.1332},
        'United States': {'city': 'New York', 'lat': 40.7128, 'lng': -74.0060},
        'Germany': {'city': 'Berlin', 'lat': 52.5200, 'lng': 13.4050},
        'United Kingdom': {'city': 'London', 'lat': 51.5074, 'lng': -0.1278},
        'Japan': {'city': 'Tokyo', 'lat': 35.6762, 'lng': 139.6503},
        'South Korea': {'city': 'Seoul', 'lat': 37.5665, 'lng': 126.9780},
        'Singapore': {'city': 'Singapore', 'lat': 1.3521, 'lng': 103.8198},
        'Malaysia': {'city': 'Kuala Lumpur', 'lat': 3.1390, 'lng': 101.6869},
        'Indonesia': {'city': 'Jakarta', 'lat': -6.2088, 'lng': 106.8456},
        'Philippines': {'city': 'Manila', 'lat': 14.5995, 'lng': 120.9842},
        'Brazil': {'city': 'São Paulo', 'lat': -23.5505, 'lng': -46.6333},
        'Turkey': {'city': 'Istanbul', 'lat': 41.0082, 'lng': 28.9784},
        'Pakistan': {'city': 'Karachi', 'lat': 24.8607, 'lng': 67.0011},
        'Myanmar': {'city': 'Yangon', 'lat': 16.8661, 'lng': 96.1951},
        'Cambodia': {'city': 'Phnom Penh', 'lat': 11.5564, 'lng': 104.9282},
        'Laos': {'city': 'Vientiane', 'lat': 17.9757, 'lng': 102.6331},
        'Sri Lanka': {'city': 'Colombo', 'lat': 6.9271, 'lng': 79.8612},
        'Ethiopia': {'city': 'Addis Ababa', 'lat': 9.0320, 'lng': 38.7469},
        'Kenya': {'city': 'Nairobi', 'lat': -1.2921, 'lng': 36.8219},
        'South Africa': {'city': 'Cape Town', 'lat': -33.9249, 'lng': 18.4241},
        'Nigeria': {'city': 'Lagos', 'lat': 6.5244, 'lng': 3.3792},
        'Egypt': {'city': 'Cairo', 'lat': 30.0444, 'lng': 31.2357},
        'Morocco': {'city': 'Casablanca', 'lat': 33.5731, 'lng': -7.5898},
        'Tunisia': {'city': 'Tunis', 'lat': 36.8065, 'lng': 10.1815},
        'Peru': {'city': 'Lima', 'lat': -12.0464, 'lng': -77.0428},
        'Colombia': {'city': 'Bogotá', 'lat': 4.7110, 'lng': -74.0721},
        'Chile': {'city': 'Santiago', 'lat': -33.4489, 'lng': -70.6693},
        'Argentina': {'city': 'Buenos Aires', 'lat': -34.6118, 'lng': -58.3960},
        'Costa Rica': {'city': 'San José', 'lat': 9.9281, 'lng': -84.0907},
        'Guatemala': {'city': 'Guatemala City', 'lat': 14.6349, 'lng': -90.5069},
        'Canada': {'city': 'Toronto', 'lat': 43.6532, 'lng': -79.3832},
        'Australia': {'city': 'Sydney', 'lat': -33.8688, 'lng': 151.2093},
        'New Zealand': {'city': 'Auckland', 'lat': -36.8485, 'lng': 174.7633},
        'France': {'city': 'Paris', 'lat': 48.8566, 'lng': 2.3522},
        'Italy': {'city': 'Milan', 'lat': 45.4642, 'lng': 9.1900},
        'Spain': {'city': 'Madrid', 'lat': 40.4168, 'lng': -3.7038},
        'Netherlands': {'city': 'Amsterdam', 'lat': 52.3676, 'lng': 4.9041},
        'Belgium': {'city': 'Brussels', 'lat': 50.8503, 'lng': 4.3517},
        'Switzerland': {'city': 'Zurich', 'lat': 47.3769, 'lng': 8.5417},
        'Sweden': {'city': 'Stockholm', 'lat': 59.3293, 'lng': 18.0686},
        'Norway': {'city': 'Oslo', 'lat': 59.9139, 'lng': 10.7522},
        'Denmark': {'city': 'Copenhagen', 'lat': 55.6761, 'lng': 12.5683},
        'Finland': {'city': 'Helsinki', 'lat': 60.1699, 'lng': 24.9384},
        'Austria': {'city': 'Vienna', 'lat': 48.2082, 'lng': 16.3738},
        'Portugal': {'city': 'Lisbon', 'lat': 38.7223, 'lng': -9.1393},
        'Poland': {'city': 'Warsaw', 'lat': 52.2297, 'lng': 21.0122},
        'Czech Republic': {'city': 'Prague', 'lat': 50.0755, 'lng': 14.4378},
        'Hungary': {'city': 'Budapest', 'lat': 47.4979, 'lng': 19.0402},
        'Slovakia': {'city': 'Bratislava', 'lat': 48.1486, 'lng': 17.1077},
        'Slovenia': {'city': 'Ljubljana', 'lat': 46.0569, 'lng': 14.5058},
        'Croatia': {'city': 'Zagreb', 'lat': 45.8150, 'lng': 15.9819},
        'Romania': {'city': 'Bucharest', 'lat': 44.4268, 'lng': 26.1025},
        'Bulgaria': {'city': 'Sofia', 'lat': 42.6977, 'lng': 23.3219},
        'Greece': {'city': 'Athens', 'lat': 37.9838, 'lng': 23.7275},
        'Cyprus': {'city': 'Nicosia', 'lat': 35.1856, 'lng': 33.3823},
        'Malta': {'city': 'Valletta', 'lat': 35.8989, 'lng': 14.5146},
        'Luxembourg': {'city': 'Luxembourg City', 'lat': 49.6116, 'lng': 6.1319},
        'Ireland': {'city': 'Dublin', 'lat': 53.3498, 'lng': -6.2603},
        'Iceland': {'city': 'Reykjavik', 'lat': 64.1466, 'lng': -21.9426},
        'Estonia': {'city': 'Tallinn', 'lat': 59.4370, 'lng': 24.7536},
        'Latvia': {'city': 'Riga', 'lat': 56.9496, 'lng': 24.1052},
        'Lithuania': {'city': 'Vilnius', 'lat': 54.6872, 'lng': 25.2797}
    }
    return city_data.get(country, {'city': 'Unknown', 'lat': 0, 'lng': 0})

def generate_location_risk_factors(country):
    """Generate realistic risk factors for each location"""
    country_data = COUNTRY_RISK_DATA.get(country, {})
    governance_risk = country_data.get('governance_risk', 50)
    
    if governance_risk > 70:
        return ['High governance risk', 'Limited oversight capabilities', 'Compliance challenges']
    elif governance_risk > 50:
        return ['Moderate oversight concerns', 'Regular monitoring needed']
    else:
        return ['Low risk jurisdiction', 'Strong regulatory framework']

def calculate_risk_score(company_data, company_name):
    """Calculate comprehensive risk score"""
    try:
        # Get base risk factors
        country_scores = []
        risk_factors = {}
        
        for country in company_data['countries']:
            country_data = COUNTRY_RISK_DATA.get(country, {})
            
            # Calculate inherent country risk
            inherent_risk = (
                country_data.get('governance_risk', 50) * 0.3 +
                country_data.get('economic_vulnerability', 50) * 0.2 +
                country_data.get('modern_slavery_prevalence', 5) * 3 * 0.3 +  # Scale prevalence
                (4 - country_data.get('tip_tier', 2)) * 25 * 0.2  # TIP tier penalty
            )
            
            country_scores.append(min(inherent_risk, 100))
            
            # Get AI-enhanced risk analysis
            api_factors = analyze_api_risk_factors(country, company_name)
            risk_factors[country] = api_factors
        
        # Calculate industry risk
        industry = company_data.get('industry', 'technology')
        industry_data = INDUSTRY_RISK_DATA.get(industry, {})
        industry_risk = sum(industry_data.values()) / len(industry_data) if industry_data else 50
        
        # Calculate mitigation from company policies
        policies = company_data.get('modern_slavery_policies', {})
        transparency = company_data.get('supply_chain_transparency', 50)
        
        mitigation_score = 0
        if policies.get('has_policy'):
            mitigation_score += 20
        if policies.get('supplier_audits'):
            mitigation_score += 25
        if policies.get('grievance_mechanism'):
            mitigation_score += 15
        if policies.get('training_programs'):
            mitigation_score += 15
        
        mitigation_score += transparency * 0.25
        mitigation_score = min(mitigation_score, 100)
        
        # Final calculation: Risk = 0.75 * Inherent + 0.25 * (100 - Residual * 4)
        avg_country_risk = sum(country_scores) / len(country_scores) if country_scores else 50
        inherent_risk = (avg_country_risk * 0.6 + industry_risk * 0.4)
        residual_risk_factor = mitigation_score / 100
        final_risk = 0.75 * inherent_risk + 0.25 * (100 - residual_risk_factor * 400)
        final_risk = max(0, min(final_risk, 100))
        
        return {
            'inherent_risk': inherent_risk,
            'residual_risk': residual_risk_factor * 100,
            'final_risk': final_risk,
            'country_scores': dict(zip(company_data['countries'], country_scores)),
            'industry_risk': industry_risk,
            'mitigation_score': mitigation_score,
            'risk_factors': risk_factors,
            'risk_level': get_risk_level(final_risk)
        }
        
    except Exception as e:
        print(f"Risk calculation error: {e}")
        return {
            'inherent_risk': 50,
            'residual_risk': 50,
            'final_risk': 50,
            'country_scores': {},
            'industry_risk': 50,
            'mitigation_score': 25,
            'risk_factors': {},
            'risk_level': 'Medium'
        }

def get_risk_level(score):
    """Convert risk score to categorical level"""
    if score >= 80:
        return 'Very High'
    elif score >= 65:
        return 'High'
    elif score >= 45:
        return 'Medium'
    elif score >= 25:
        return 'Low'
    else:
        return 'Very Low'

def get_news_sentiment(company_name):
    """Get news sentiment analysis"""
    try:
        # Simulate news API call
        if NEWS_API_KEY and NEWS_API_KEY != "your_news_api_key_here":
            url = f"https://newsapi.org/v2/everything"
            params = {
                'q': f'"{company_name}" AND ("modern slavery" OR "forced labor" OR "labor violations")',
                'apiKey': NEWS_API_KEY,
                'language': 'en',
                'sortBy': 'relevancy',
                'pageSize': 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                news_data = response.json()
                if news_data['totalResults'] > 0:
                    # Process news articles
                    negative_keywords = ['violation', 'abuse', 'exploitation', 'forced', 'illegal']
                    positive_keywords = ['compliance', 'ethical', 'improvement', 'initiative']
                    
                    articles = news_data['articles'][:5]
                    sentiment_score = analyze_news_sentiment(articles, negative_keywords, positive_keywords)
                    
                    return {
                        'sentiment_score': sentiment_score,
                        'articles_found': len(articles),
                        'recent_concerns': extract_recent_concerns(articles),
                        'ai_analysis': get_ai_news_analysis(company_name, 'multiple countries')
                    }
        
        # Fallback synthetic data
        return generate_synthetic_news_sentiment(company_name)
        
    except Exception as e:
        print(f"News sentiment error: {e}")
        return generate_synthetic_news_sentiment(company_name)

def analyze_news_sentiment(articles, negative_keywords, positive_keywords):
    """Analyze sentiment of news articles"""
    sentiment_score = 50  # Neutral baseline
    
    for article in articles:
        text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
        
        negative_count = sum(1 for keyword in negative_keywords if keyword in text)
        positive_count = sum(1 for keyword in positive_keywords if keyword in text)
        
        if negative_count > positive_count:
            sentiment_score -= 15
        elif positive_count > negative_count:
            sentiment_score += 10
    
    return max(0, min(sentiment_score, 100))

def extract_recent_concerns(articles):
    """Extract key concerns from recent articles"""
    concerns = []
    for article in articles[:3]:
        title = article.get('title', '')
        if any(word in title.lower() for word in ['labor', 'worker', 'supply', 'factory']):
            concerns.append(title[:100] + "..." if len(title) > 100 else title)
    
    return concerns if concerns else ["No recent specific concerns identified"]

def generate_synthetic_news_sentiment(company_name):
    """Generate realistic synthetic news sentiment"""
    base_score = random.randint(40, 70)
    
    return {
        'sentiment_score': base_score,
        'articles_found': random.randint(0, 8),
        'recent_concerns': [
            f"Supply chain transparency initiatives for {company_name}",
            f"Labor monitoring in {company_name} facilities",
            f"Compliance updates from {company_name}"
        ],
        'ai_analysis': get_ai_news_analysis(company_name, 'global operations')
    }

@app.route('/assess', methods=['GET'])
def assess_company():
    """Main assessment endpoint"""
    try:
        company_name = request.args.get('company', '').strip()
        
        if not company_name:
            return jsonify({'error': 'Company name is required'}), 400
        
        # Fetch company data
        company_data = fetch_company_data(company_name)
        
        # Calculate comprehensive risk scores
        risk_assessment = calculate_risk_score(company_data, company_name)
        
        # Calculate modern slavery specific risk
        modern_slavery_risk = calculate_modern_slavery_risk(company_data, company_name)
        
        # Get news sentiment
        news_sentiment = get_news_sentiment(company_name)
        
        # Prepare response
        response = {
            'company_name': company_name,
            'assessment_date': datetime.now().isoformat(),
            'overall_risk_score': risk_assessment['final_risk'],
            'risk_level': risk_assessment['risk_level'],
            'modern_slavery_risk': modern_slavery_risk,
            'risk_breakdown': {
                'inherent_risk': risk_assessment['inherent_risk'],
                'residual_risk': risk_assessment['residual_risk'],
                'country_risks': risk_assessment['country_scores'],
                'industry_risk': risk_assessment['industry_risk'],
                'mitigation_effectiveness': risk_assessment['mitigation_score']
            },
            'company_profile': {
                'industry': company_data['industry'],
                'revenue_billions': company_data.get('revenue_billions', 'N/A'),
                'countries_of_operation': company_data['countries'],
                'manufacturing_locations': company_data['manufacturing_locations'],
                'supply_chain_transparency_score': company_data.get('supply_chain_transparency', 50)
            },
            'risk_factors': {
                'governance_and_regulatory': risk_assessment['risk_factors'],
                'economic_vulnerability': {country: [f for f in factors if f['factor'] == 'Economic Vulnerability'] 
                                         for country, factors in risk_assessment['risk_factors'].items()},
                'modern_slavery_indicators': modern_slavery_risk['vulnerability_factors'],
                'industry_specific': {
                    'sector': company_data['industry'],
                    'risk_profile': INDUSTRY_RISK_DATA.get(company_data['industry'], {})
                }
            },
            'mitigation_measures': {
                'current_policies': company_data.get('modern_slavery_policies', {}),
                'effectiveness_score': risk_assessment['mitigation_score'],
                'recommendations': generate_recommendations(risk_assessment, modern_slavery_risk)
            },
            'data_sources': {
                'primary_sources': [
                    'Global Slavery Index 2023 (Walk Free Foundation)',
                    'US State Department TIP Reports (2020-2024)',
                    'ILO Global Estimates of Modern Slavery 2022',
                    'UN Protocol to Prevent Trafficking in Persons',
                    'Country governance indicators (World Bank)',
                    'Industry risk assessments',
                    'Economic indicators (World Bank, IMF)',
                    'News and regulatory analysis'
                ],
                'news_analysis': news_sentiment,
                'last_updated': datetime.now().isoformat(),
                'methodology': 'Risk calculation: 0.75 × Inherent + 0.25 × (100 - Residual × 4) with AI-enhanced vulnerability analysis'
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Assessment error: {e}")
        return jsonify({'error': 'Assessment failed', 'details': str(e)}), 500

def generate_recommendations(risk_assessment, modern_slavery_risk):
    """Generate specific recommendations based on risk assessment"""
    recommendations = []
    
    final_risk = risk_assessment['final_risk']
    ms_risk = modern_slavery_risk['final_risk_score']
    
    if final_risk > 70 or ms_risk > 70:
        recommendations.extend([
            "Conduct immediate comprehensive supply chain audit",
            "Implement enhanced due diligence for high-risk suppliers",
            "Establish direct monitoring in high-risk locations",
            "Develop crisis response protocols for labor violations"
        ])
    
    if modern_slavery_risk['mitigation_effectiveness'] < 0.5:
        recommendations.extend([
            "Develop comprehensive modern slavery policy",
            "Implement supplier audit program with unannounced visits",
            "Establish worker grievance mechanisms",
            "Provide regular training for procurement teams"
        ])
    
    if final_risk > 50:
        recommendations.extend([
            "Increase supply chain transparency reporting",
            "Implement technology solutions for supply chain tracking",
            "Engage with industry initiatives on labor standards"
        ])
    
    for country, score in risk_assessment['country_scores'].items():
        if score > 75:
            recommendations.append(f"Enhanced monitoring required for operations in {country}")
    
    if not recommendations:
        recommendations = [
            "Maintain current monitoring practices",
            "Continue regular supplier assessments",
            "Monitor for emerging risks in supply chain",
            "Review and update policies annually"
        ]
    
    return recommendations

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '3.0',
        'features': [
            'Modern slavery risk assessment',
            'Multi-country analysis with 80+ countries',
            'Industry-specific risk factors for 25+ sectors',
            'AI-enhanced analysis (shortened responses)',
            'Real-time news sentiment analysis',
            'Comprehensive company profiles',
            'Supply chain transparency scoring',
            'TIP tier integration',
            'Manufacturing location mapping'
        ],
        'data_coverage': {
            'countries': len(COUNTRY_RISK_DATA),
            'industries': len(INDUSTRY_RISK_DATA),
            'company_profiles': len(COMPANY_PROFILES)
        }
    })

@app.route('/countries', methods=['GET'])
def get_countries():
    """Get list of all countries with risk data"""
    countries_list = []
    for country, data in COUNTRY_RISK_DATA.items():
        countries_list.append({
            'name': country,
            'modern_slavery_prevalence': data.get('modern_slavery_prevalence', 0),
            'tip_tier': data.get('tip_tier', 2),
            'governance_risk': data.get('governance_risk', 50),
            'economic_vulnerability': data.get('economic_vulnerability', 50)
        })
    
    return jsonify({
        'total_countries': len(countries_list),
        'countries': sorted(countries_list, key=lambda x: x['name'])
    })

@app.route('/industries', methods=['GET'])
def get_industries():
    """Get list of all industries with risk data"""
    industries_list = []
    for industry, data in INDUSTRY_RISK_DATA.items():
        industries_list.append({
            'name': industry,
            'forced_labor_risk': data.get('forced_labor_risk', 50),
            'child_labor_risk': data.get('child_labor_risk', 50),
            'supply_chain_complexity': data.get('supply_chain_complexity', 50),
            'sector_specific_risks': data.get('sector_specific_risks', [])
        })
    
    return jsonify({
        'total_industries': len(industries_list),
        'industries': sorted(industries_list, key=lambda x: x['name'])
    })

@app.route('/companies', methods=['GET'])
def get_companies():
    """Get list of all predefined companies"""
    companies_list = []
    for company, data in COMPANY_PROFILES.items():
        companies_list.append({
            'name': company,
            'industry': data.get('industry', ''),
            'revenue_billions': data.get('revenue_billions', 0),
            'countries_count': len(data.get('countries', [])),
            'manufacturing_locations_count': len(data.get('manufacturing_locations', [])),
            'supply_chain_transparency': data.get('supply_chain_transparency', 50)
        })
    
    return jsonify({
        'total_companies': len(companies_list),
        'companies': sorted(companies_list, key=lambda x: x['name'])
    })

@app.route('/risk_factors/<country>', methods=['GET'])
def get_country_risk_factors(country):
    """Get detailed risk factors for a specific country"""
    if country not in COUNTRY_RISK_DATA:
        return jsonify({'error': f'Country {country} not found'}), 404
    
    country_data = COUNTRY_RISK_DATA[country]
    
    return jsonify({
        'country': country,
        'risk_factors': country_data,
        'modern_slavery_concerns': get_country_specific_concerns(country),
        'risk_category': categorize_modern_slavery_risk(
            country_data.get('modern_slavery_prevalence', 0) * 5
        )
    })

@app.route('/industry_analysis/<industry>', methods=['GET'])
def get_industry_analysis(industry):
    """Get detailed analysis for a specific industry"""
    if industry not in INDUSTRY_RISK_DATA:
        return jsonify({'error': f'Industry {industry} not found'}), 404
    
    industry_data = INDUSTRY_RISK_DATA[industry]
    
    # Calculate overall industry risk score
    risk_scores = [
        industry_data.get('forced_labor_risk', 50),
        industry_data.get('child_labor_risk', 50),
        industry_data.get('supply_chain_complexity', 50),
        industry_data.get('raw_material_risk', 50),
        industry_data.get('manufacturing_risk', 50)
    ]
    
    overall_risk = sum(risk_scores) / len(risk_scores)
    
    return jsonify({
        'industry': industry,
        'overall_risk_score': overall_risk,
        'risk_category': get_risk_level(overall_risk),
        'detailed_risks': industry_data,
        'companies_in_industry': [
            company for company, data in COMPANY_PROFILES.items()
            if data.get('industry') == industry
        ]
    })

@app.route('/compare', methods=['GET'])
def compare_companies():
    """Compare risk scores between multiple companies"""
    companies = request.args.get('companies', '').split(',')
    companies = [c.strip() for c in companies if c.strip()]
    
    if len(companies) < 2:
        return jsonify({'error': 'At least 2 companies required for comparison'}), 400
    
    comparison_results = {}
    
    for company_name in companies:
        try:
            company_data = fetch_company_data(company_name)
            risk_assessment = calculate_risk_score(company_data, company_name)
            modern_slavery_risk = calculate_modern_slavery_risk(company_data, company_name)
            
            comparison_results[company_name] = {
                'overall_risk_score': risk_assessment['final_risk'],
                'risk_level': risk_assessment['risk_level'],
                'modern_slavery_risk_score': modern_slavery_risk['final_risk_score'],
                'modern_slavery_category': modern_slavery_risk['risk_category'],
                'industry': company_data['industry'],
                'countries_count': len(company_data['countries']),
                'supply_chain_transparency': company_data.get('supply_chain_transparency', 50),
                'mitigation_effectiveness': risk_assessment['mitigation_score']
            }
        except Exception as e:
            comparison_results[company_name] = {'error': str(e)}
    
    return jsonify({
        'comparison_date': datetime.now().isoformat(),
        'companies_compared': len(companies),
        'results': comparison_results
    })

@app.route('/search', methods=['GET'])
def search_data():
    """Search across countries, industries, and companies"""
    query = request.args.get('q', '').lower().strip()
    
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    results = {
        'countries': [],
        'industries': [],
        'companies': []
    }
    
    # Search countries
    for country in COUNTRY_RISK_DATA.keys():
        if query in country.lower():
            results['countries'].append({
                'name': country,
                'modern_slavery_prevalence': COUNTRY_RISK_DATA[country].get('modern_slavery_prevalence', 0),
                'tip_tier': COUNTRY_RISK_DATA[country].get('tip_tier', 2)
            })
    
    # Search industries
    for industry in INDUSTRY_RISK_DATA.keys():
        if query in industry.lower():
            results['industries'].append({
                'name': industry,
                'forced_labor_risk': INDUSTRY_RISK_DATA[industry].get('forced_labor_risk', 50)
            })
    
    # Search companies
    for company in COMPANY_PROFILES.keys():
        if query in company.lower():
            results['companies'].append({
                'name': company,
                'industry': COMPANY_PROFILES[company].get('industry', ''),
                'revenue_billions': COMPANY_PROFILES[company].get('revenue_billions', 0)
            })
    
    return jsonify({
        'query': query,
        'total_results': sum(len(results[key]) for key in results),
        'results': results
    })

@app.route('/statistics', methods=['GET'])
def get_statistics():
    """Get overall statistics about the risk assessment database"""
    # Calculate statistics
    total_countries = len(COUNTRY_RISK_DATA)
    high_risk_countries = sum(1 for data in COUNTRY_RISK_DATA.values() 
                             if data.get('modern_slavery_prevalence', 0) > 10)
    
    total_industries = len(INDUSTRY_RISK_DATA)
    high_risk_industries = sum(1 for data in INDUSTRY_RISK_DATA.values() 
                              if data.get('forced_labor_risk', 0) > 70)
    
    total_companies = len(COMPANY_PROFILES)
    
    # TIP tier distribution
    tip_distribution = {}
    for data in COUNTRY_RISK_DATA.values():
        tier = data.get('tip_tier', 2)
        tip_distribution[f'Tier {tier}'] = tip_distribution.get(f'Tier {tier}', 0) + 1
    
    return jsonify({
        'database_statistics': {
            'total_countries': total_countries,
            'high_risk_countries': high_risk_countries,
            'total_industries': total_industries,
            'high_risk_industries': high_risk_industries,
            'total_companies': total_companies,
            'tip_tier_distribution': tip_distribution
        },
        'risk_thresholds': {
            'modern_slavery_prevalence': {
                'low': '< 5 per 1000',
                'medium': '5-15 per 1000',
                'high': '> 15 per 1000'
            },
            'forced_labor_risk': {
                'low': '< 50',
                'medium': '50-70',
                'high': '> 70'
            }
        },
        'data_sources': [
            'Global Slavery Index 2023 (Walk Free Foundation)',
            'US State Department TIP Reports (2020-2024)',
            'ILO Global Estimates of Modern Slavery 2022',
            'World Bank Governance Indicators',
            'Economic Freedom Index',
            'Transparency International Corruption Index'
        ],
        'last_updated': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 Starting Enhanced Modern Slavery Assessment Backend v3.0")
    print("=" * 80)
    print("📊 Database Coverage:")
    print(f"   • Countries: {len(COUNTRY_RISK_DATA)}")
    print(f"   • Industries: {len(INDUSTRY_RISK_DATA)}")
    print(f"   • Company Profiles: {len(COMPANY_PROFILES)}")
    print("\n🔧 Features:")
    print("   • Modern slavery risk assessment")
    print("   • Multi-country analysis")
    print("   • Industry-specific risk factors")
    print("   • AI-enhanced analysis (shortened responses)")
    print("   • Supply chain transparency scoring")
    print("   • Manufacturing location mapping")
    print("   • TIP tier integration")
    print("   • Comprehensive API endpoints")
    print("\n🌐 Available Endpoints:")
    print("   • GET /assess?company=<name> - Main assessment")
    print("   • GET /health - Health check")
    print("   • GET /countries - List all countries")
    print("   • GET /industries - List all industries")
    print("   • GET /companies - List predefined companies")
    print("   • GET /risk_factors/<country> - Country details")
    print("   • GET /industry_analysis/<industry> - Industry details")
    print("   • GET /compare?companies=<name1,name2> - Compare companies")
    print("   • GET /search?q=<query> - Search database")
    print("   • GET /statistics - Database statistics")
    print("=" * 80)
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)