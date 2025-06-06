import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import './App.css';

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Industry Benchmarking Component
const IndustryBenchmarking = ({ benchmarkData }) => {
  if (!benchmarkData) return null;

  const getPerformanceColor = (performance) => {
    return performance === 'above average' ? '#28a745' : '#dc3545';
  };

  const getScoreColor = (score) => {
    if (score <= 35) return '#28a745';
    if (score <= 65) return '#ffc107';
    return '#dc3545';
  };

  return (
    <div className="section industry-benchmarking">
      <h3>📊 Industry Benchmarking</h3>
      
      <div className="benchmark-overview">
        <div className="benchmark-header">
          <h4>Industry: {benchmarkData.matched_industry}</h4>
          <div className="score-comparison">
            <div className="score-item">
              <span className="label">Your Score:</span>
              <span 
                className="score company-score"
                style={{ color: getScoreColor(benchmarkData.company_score) }}
              >
                {benchmarkData.company_score}
              </span>
            </div>
            <div className="score-item">
              <span className="label">Industry Average:</span>
              <span 
                className="score industry-score"
                style={{ color: getScoreColor(benchmarkData.industry_average_score) }}
              >
                {benchmarkData.industry_average_score}
              </span>
            </div>
            <div className="score-item">
              <span className="label">Performance:</span>
              <span 
                className="performance-badge"
                style={{ color: getPerformanceColor(benchmarkData.performance_vs_peers) }}
              >
                {benchmarkData.performance_vs_peers.toUpperCase()}
              </span>
            </div>
          </div>
          
          <div className="benchmark-insights">
            <h5>Key Insights:</h5>
            <ul>
              {benchmarkData.benchmark_insights?.map((insight, index) => (
                <li key={index}>{insight}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="benchmark-grid">
          <div className="benchmark-section">
            <h5>🏢 Industry Peer Companies</h5>
            <div className="peer-companies">
              {benchmarkData.peer_companies?.slice(0, 6).map((company, index) => (
                <span key={index} className="peer-company">{company}</span>
              ))}
            </div>
          </div>

          <div className="benchmark-section">
            <h5>⚠️ Common Industry Risks</h5>
            <ul className="industry-risks">
              {benchmarkData.industry_common_risks?.slice(0, 4).map((risk, index) => (
                <li key={index}>{risk}</li>
              ))}
            </ul>
          </div>

          <div className="benchmark-section">
            <h5>✅ Industry Best Practices</h5>
            <ul className="best-practices">
              {benchmarkData.industry_best_practices?.slice(0, 4).map((practice, index) => (
                <li key={index}>{practice}</li>
              ))}
            </ul>
          </div>

          <div className="benchmark-section">
            <h5>📋 Regulatory Focus Areas</h5>
            <div className="regulatory-items">
              {benchmarkData.regulatory_focus?.slice(0, 3).map((regulation, index) => (
                <span key={index} className="regulatory-item">{regulation}</span>
              ))}
            </div>
          </div>
        </div>

        <div className="benchmark-metadata">
          <small>
            Data Quality: <strong>{benchmarkData.data_quality}</strong> | 
            Last Updated: <strong>{benchmarkData.last_updated}</strong> | 
            Percentile: <strong>{benchmarkData.percentile_ranking}</strong>
          </small>
        </div>
      </div>
    </div>
  );
};

// Manufacturing Map Component
const ManufacturingMap = ({ mapData, locations }) => {
  const [selectedLocation, setSelectedLocation] = useState(null);

  if (!locations || locations.length === 0) {
    return (
      <div className="section">
        <h3>🗺️ Global Manufacturing Locations</h3>
        <div className="no-data">No manufacturing location data available</div>
      </div>
    );
  }

  const getRiskColor = (riskScore) => {
    if (riskScore > 75) return '#dc3545';
    if (riskScore > 50) return '#ffc107';
    return '#28a745';
  };

  const createCustomIcon = (riskScore, facilityType) => {
    const color = getRiskColor(riskScore);
    const size = facilityType === 'manufacturing' ? 25 : 20;
    
    return L.divIcon({
      className: 'custom-marker',
      html: `<div style="background-color: ${color}; width: ${size}px; height: ${size}px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
      iconSize: [size, size],
      iconAnchor: [size/2, size/2]
    });
  };

  // Calculate map center based on locations
  const validLocations = locations.filter(loc => 
    loc.coordinates && 
    typeof loc.coordinates.lat === 'number' && 
    typeof loc.coordinates.lng === 'number'
  );

  if (validLocations.length === 0) {
    return (
      <div className="section">
        <h3>🗺️ Global Manufacturing Locations</h3>
        <div className="no-data">Location coordinates not available</div>
      </div>
    );
  }

  const centerLat = validLocations.reduce((sum, loc) => sum + loc.coordinates.lat, 0) / validLocations.length;
  const centerLng = validLocations.reduce((sum, loc) => sum + loc.coordinates.lng, 0) / validLocations.length;

  return (
    <div className="section manufacturing-map">
      <h3>🗺️ Global Manufacturing Locations</h3>
      
      {mapData && (
        <div className="map-summary">
          <div className="summary-stats">
            <div className="stat-item">
              <span className="stat-number">{mapData.total_locations}</span>
              <span className="stat-label">Total Sites</span>
            </div>
            <div className="stat-item high-risk">
              <span className="stat-number">{mapData.risk_summary?.high_risk_sites || 0}</span>
              <span className="stat-label">High Risk</span>
            </div>
            <div className="stat-item medium-risk">
              <span className="stat-number">{mapData.risk_summary?.medium_risk_sites || 0}</span>
              <span className="stat-label">Medium Risk</span>
            </div>
            <div className="stat-item low-risk">
              <span className="stat-number">{mapData.risk_summary?.low_risk_sites || 0}</span>
              <span className="stat-label">Low Risk</span>
            </div>
          </div>
        </div>
      )}

      <div className="map-container">
        <MapContainer
          center={[centerLat, centerLng]}
          zoom={2}
          style={{ height: '500px', width: '100%', borderRadius: '8px' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          
          {validLocations.map((location, index) => (
            <Marker
              key={index}
              position={[location.coordinates.lat, location.coordinates.lng]}
              icon={createCustomIcon(location.country_risk_score || 50, location.facility_type)}
              eventHandlers={{
                click: () => setSelectedLocation(location)
              }}
            >
              <Popup>
                <div className="location-popup">
                  <h4>{location.city}, {location.country}</h4>
                  <p><strong>Type:</strong> {location.facility_type}</p>
                  <p><strong>Products:</strong> {location.products}</p>
                  <p><strong>Risk Level:</strong> 
                    <span 
                      className="risk-badge"
                      style={{ backgroundColor: getRiskColor(location.country_risk_score || 50) }}
                    >
                      {location.country_risk_level || 'Unknown'}
                    </span>
                  </p>
                  {location.workforce_size && (
                    <p><strong>Workforce:</strong> {location.workforce_size}</p>
                  )}
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      <div className="map-legend">
        <h5>Legend:</h5>
        <div className="legend-items">
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#dc3545' }}></div>
            <span>High Risk (75+)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#ffc107' }}></div>
            <span>Medium Risk (50-75)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#28a745' }}></div>
            <span>Low Risk (&lt;50)</span>
          </div>
        </div>
      </div>

      {selectedLocation && (
        <div className="selected-location-details">
          <h5>Selected Location Details:</h5>
          <div className="location-details-grid">
            <div><strong>Location:</strong> {selectedLocation.city}, {selectedLocation.country}</div>
            <div><strong>Facility Type:</strong> {selectedLocation.facility_type}</div>
            <div><strong>Risk Score:</strong> {selectedLocation.country_risk_score}/100</div>
            <div><strong>Products/Services:</strong> {selectedLocation.products}</div>
          </div>
        </div>
      )}
    </div>
  );
};

// Enhanced Data Sources Component
const EnhancedDataSources = ({ enhancedData }) => {
  if (!enhancedData) return null;

  return (
    <div className="section enhanced-data">
      <h3>🔍 Enhanced Data Analysis</h3>
      
      <div className="data-sources-grid">
        <div className="data-source-item">
          <h5>📊 Economic Indicators</h5>
          {enhancedData.economic_indicators && Object.keys(enhancedData.economic_indicators).length > 0 ? (
            <div className="economic-data">
              {Object.entries(enhancedData.economic_indicators).map(([country, data]) => (
                <div key={country} className="country-economic-data">
                  <strong>{country}:</strong> GDP per capita ${data.gdp_per_capita?.toLocaleString()} 
                  <span className={`risk-indicator ${data.economic_risk_factor}`}>
                    ({data.economic_risk_factor} economic risk)
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="no-data">No economic data available</div>
          )}
        </div>

        <div className="data-source-item">
          <h5>📰 Enhanced News Analysis</h5>
          {enhancedData.enhanced_news && enhancedData.enhanced_news.length > 0 ? (
            <div className="news-analysis">
              <p>Found {enhancedData.enhanced_news.length} relevant news articles</p>
              <div className="news-items">
                {enhancedData.enhanced_news.slice(0, 3).map((article, index) => (
                  <div key={index} className="news-item">
                    <a href={article.url} target="_blank" rel="noopener noreferrer">
                      {article.title}
                    </a>
                    <small>Source: {article.domain} | Tone: {article.tone}</small>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="no-data">No enhanced news data available</div>
          )}
        </div>

        <div className="data-source-item">
          <h5>🔗 Data Sources Used</h5>
          <ul className="data-sources-list">
            {enhancedData.data_sources_used?.map((source, index) => (
              <li key={index}>{source}</li>
            ))}
          </ul>
        </div>
      </div>

      {enhancedData.api_risk_factors && enhancedData.api_risk_factors.length > 0 && (
        <div className="api-risk-factors">
          <h5>⚠️ Additional Risk Factors from External Data</h5>
          <div className="api-factors-grid">
            {enhancedData.api_risk_factors.map((factor, index) => (
              <div key={index} className="api-risk-factor">
                <div className="factor-header">
                  <strong>{factor.factor}</strong>
                  <span className={`impact-badge ${factor.impact}`}>
                    {factor.impact.toUpperCase()} IMPACT
                  </span>
                </div>
                <div className="factor-evidence">{factor.evidence}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

function App() {
  const [companyName, setCompanyName] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!companyName.trim()) {
      setError('Please enter a company name');
      return;
    }
    
    setLoading(true);
    setError('');
    setResults(null);
    
    try {
      const response = await fetch('https://modern-slavery-tool-production.up.railway.app/assess', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company_name: companyName.trim(),
          assessment_type: 'comprehensive',
          options: {
            include_supply_chain: true,
            include_news: true,
            include_legal: true,
            include_financial: true,
            geographic_scope: 'global',
            timeframe_months: 12,
            risk_threshold: 'medium',
            include_benchmarking: true,
            include_mapping: true
          }
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      
      const data = await response.json();
      console.log("Full results:", data);
      setResults(data);
    } catch (err) {
      console.error('Assessment error:', err);
      setError('Failed to assess company. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    if (!riskLevel) return '#6c757d';
    switch (riskLevel.toLowerCase()) {
      case 'low':
      case 'very-low':
        return '#28a745';
      case 'medium':
        return '#ffc107';
      case 'high':
      case 'very-high':
        return '#dc3545';
      default:
        return '#6c757d';
    }
  };

  const clearResults = () => {
    setResults(null);
    setCompanyName('');
    setError('');
    setActiveTab('overview');
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <div className="brand-section">
            <img src="/rosetta-logo.png" alt="Rosetta Solutions Logo" className="company-logo" />
            <div className="brand-text">
              <h1>🛡️ Rosetta Solutions - Modern Slavery Risk Assessment</h1>
              <p>AI-Powered Analysis | Industry Benchmarking | Global Supply Chain Mapping</p>
            </div>
          </div>
        </header>
        
        <div className="assessment-section">
          <form onSubmit={handleSubmit} className="assessment-form">
            <div className="input-group">
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="Enter company name (e.g., Apple, Nike, Walmart, Tesla)"
                className="company-input"
                disabled={loading}
              />
              <button 
                type="submit" 
                disabled={loading || !companyName.trim()}
                className="assess-button"
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Analyzing...
                  </>
                ) : (
                  'Assess Company'
                )}
              </button>
            </div>
          </form>

          {error && (
            <div className="alert error">
              <strong>Error:</strong> {error}
            </div>
          )}
          
          {results && (
            <div className="results-container">
              <div className="results-header">
                <h2>Assessment Results for: {companyName}</h2>
                <button onClick={clearResults} className="clear-button">
                  New Assessment
                </button>
              </div>
              
              <div className="risk-overview">
                <div className="risk-card">
                  <h3>Overall Risk Level</h3>
                  <div 
                    className="risk-badge"
                    style={{ backgroundColor: getRiskColor(results.overall_risk_level || results.risk_level) }}
                  >
                    {(results.overall_risk_level || results.risk_level || 'Unknown').toUpperCase()}
                  </div>
                </div>
                
                <div className="risk-card">
                  <h3>Risk Score</h3>
                  <div className="risk-score">
                    {results.overall_risk_score || results.risk_score || 'N/A'}
                    <span className="score-max">/100</span>
                  </div>
                </div>
                
                <div className="risk-card">
                  <h3>Manufacturing Sites</h3>
                  <div className="risk-score">
                    {results.manufacturing_locations ? results.manufacturing_locations.length : 0}
                  </div>
                </div>

                <div className="risk-card">
                  <h3>Data Sources</h3>
                  <div className="risk-score">
                    {results.data_sources ? Object.values(results.data_sources).reduce((a, b) => a + b, 0) : 0}
                  </div>
                </div>
              </div>

              {/* Tab Navigation */}
              <div className="tab-navigation">
                <button 
                  className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
                  onClick={() => setActiveTab('overview')}
                >
                  Overview
                </button>
                <button 
                  className={`tab-button ${activeTab === 'benchmarking' ? 'active' : ''}`}
                  onClick={() => setActiveTab('benchmarking')}
                >
                  Industry Benchmarking
                </button>
                <button 
                  className={`tab-button ${activeTab === 'mapping' ? 'active' : ''}`}
                  onClick={() => setActiveTab('mapping')}
                >
                  Global Mapping
                </button>
                <button 
                  className={`tab-button ${activeTab === 'enhanced' ? 'active' : ''}`}
                  onClick={() => setActiveTab('enhanced')}
                >
                  Enhanced Data
                </button>
              </div>

              {/* Tab Content */}
              <div className="tab-content">
                {activeTab === 'overview' && (
                  <>
                    {results.key_findings && results.key_findings.length > 0 && (
                      <div className="section">
                        <h3>🔍 Key Findings</h3>
                        <ul className="findings-list">
                          {results.key_findings.map((finding, index) => (
                            <li key={index} className="finding-item">
                              <span className="finding-text">
                                {typeof finding === 'string' ? finding : finding.description}
                              </span>
                              {finding.severity && (
                                <span className={`severity-badge ${finding.severity}`}>
                                  {finding.severity.toUpperCase()}
                                </span>
                              )}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {results.recommendations && results.recommendations.length > 0 && (
                      <div className="section">
                        <h3>💡 Recommendations</h3>
                        <ul className="recommendations-list">
                          {results.recommendations.map((rec, index) => (
                            <li key={index} className="recommendation-item">
                              <span className="rec-text">
                                {typeof rec === 'string' ? rec : rec.description || rec.title}
                              </span>
                              {rec.priority && (
                                <span className={`priority-badge ${rec.priority}`}>
                                  {rec.priority.toUpperCase()} PRIORITY
                                </span>
                              )}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {results.risk_factors && results.risk_factors.length > 0 && (
                      <div className="section">
                        <h3>⚠️ Risk Factors</h3>
                        <div className="space-y-4">
                          {results.risk_factors.map((riskFactor, index) => (
                            <div key={index} className="finding-item">
                              <div className="finding-text">
                                <strong>{riskFactor.factor}</strong>
                                <div style={{fontSize: '0.9rem', color: '#666', marginTop: '8px'}}>
                                  <strong>Impact:</strong> <span className={`severity-badge ${riskFactor.impact}`}>{riskFactor.impact?.toUpperCase()}</span>
                                </div>
                                <div style={{fontSize: '0.9rem', color: '#555', marginTop: '5px'}}>
                                  <strong>Evidence:</strong> {riskFactor.evidence}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}

                {activeTab === 'benchmarking' && (
                  <IndustryBenchmarking benchmarkData={results.industry_benchmarking} />
                )}

                {activeTab === 'mapping' && (
                  <ManufacturingMap 
                    mapData={results.supply_chain_map} 
                    locations={results.manufacturing_locations} 
                  />
                )}

                {activeTab === 'enhanced' && (
                  <EnhancedDataSources enhancedData={results.enhanced_data} />
                )}
              </div>

              <div className="section">
                <h3>📊 Assessment Details</h3>
                <div className="details-grid">
                  <div className="detail-item">
                    <strong>Assessment Type:</strong> Comprehensive with Benchmarking & Mapping
                  </div>
                  <div className="detail-item">
                    <strong>Date:</strong> {results.assessment_date || new Date().toLocaleDateString()}
                  </div>
                  <div className="detail-item">
                    <strong>Confidence Level:</strong> {results.confidence_level || 'High'}
                  </div>
                  {results.assessment_id && (
                    <div className="detail-item">
                      <strong>Assessment ID:</strong> {results.assessment_id}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
        
        <footer className="footer">
          <p>© 2025 Rosetta Solutions. This tool provides risk assessment guidance using AI analysis, industry benchmarking, and global mapping. Professional legal advice should be sought for specific situations.</p>
        </footer>
      </div>
    </div>
  );
}

export default App;