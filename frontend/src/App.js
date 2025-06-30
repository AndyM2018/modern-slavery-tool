import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Helper function to capitalize first letter
const capitalizeFirst = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
};

// Enhanced export functionality for AI-powered data
const exportToExcel = (results, companyName) => {
  const workbookData = [];

  // Overview Sheet
  const overviewData = [
    ['AI-Powered Modern Slavery Risk Assessment - Overview'],
    ['Company:', companyName],
    ['Assessment Date:', results.assessment_date || new Date().toLocaleDateString()],
    ['Assessment Type:', results.methodology || 'AI-powered dynamic risk assessment'],
    ['Overall Risk Score:', `${results.overall_risk_assessment?.overall_risk_score || 'N/A'}/100`],
    ['Risk Category:', results.overall_risk_assessment?.risk_category || 'Unknown'],
    ['Confidence Level:', results.assessment_quality?.confidence_level || 'High'],
    [''],
    ['Company Profile:'],
    ['Industry:', results.company_profile?.industry || 'N/A'],
    ['Revenue:', results.company_profile?.revenue_billions ? `$${results.company_profile.revenue_billions}B` : 'N/A'],
    ['Countries:', results.company_profile?.countries_of_operation?.length || 0],
    ['Manufacturing Sites:', results.manufacturing_locations?.length || 0],
    [''],
    ['Risk Assessment Details:'],
  ];

  if (results.overall_risk_assessment) {
    overviewData.push(['Country Risk:', `${results.overall_risk_assessment.country_risk_average || 'N/A'}/100`]);
    overviewData.push(['Industry Risk:', `${results.overall_risk_assessment.industry_risk || 'N/A'}/100`]);
    overviewData.push(['Company Risk:', `${results.overall_risk_assessment.company_specific_risk || 'N/A'}/100`]);
    overviewData.push(['News Impact:', `${results.overall_risk_assessment.news_sentiment_impact || 'N/A'}/100`]);
  }

  workbookData.push({ name: 'Overview', data: overviewData });

  // AI Analysis Sheet
  const aiAnalysisData = [
    ['AI-Generated Analysis & Insights'],
    [''],
    ['Supply Chain Analysis:'],
  ];

  if (results.supply_chain_analysis) {
    Object.entries(results.supply_chain_analysis).forEach(([key, value]) => {
      if (typeof value === 'string' || typeof value === 'number') {
        aiAnalysisData.push([capitalizeFirst(key.replace(/_/g, ' ')) + ':', value]);
      }
    });
  }

  aiAnalysisData.push([''], ['Country Analysis:']);
  if (results.country_analysis) {
    Object.entries(results.country_analysis).forEach(([country, analysis]) => {
      aiAnalysisData.push([`${country}:`]);
      if (analysis.risk_score) aiAnalysisData.push(['Risk Score:', `${analysis.risk_score}/100`]);
      if (analysis.key_risks) {
        aiAnalysisData.push(['Key Risks:']);
        analysis.key_risks.forEach((risk, index) => {
          aiAnalysisData.push([`${index + 1}.`, risk]);
        });
      }
    });
  }

  workbookData.push({ name: 'AI Analysis', data: aiAnalysisData });

  // Recommendations Sheet
  const recommendationsData = [
    ['AI-Generated Recommendations'],
    [''],
  ];

  if (results.recommendations && Array.isArray(results.recommendations)) {
    results.recommendations.forEach((rec, index) => {
      if (typeof rec === 'string') {
        recommendationsData.push([`${index + 1}.`, rec]);
      } else if (typeof rec === 'object') {
        recommendationsData.push([`${index + 1}.`, rec.action || rec.description || JSON.stringify(rec)]);
        if (rec.timeline) recommendationsData.push(['Timeline:', rec.timeline]);
        if (rec.priority) recommendationsData.push(['Priority:', rec.priority]);
        recommendationsData.push(['']);
      }
    });
  }

  workbookData.push({ name: 'Recommendations', data: recommendationsData });

  // Convert to CSV and download
  const csvContent = workbookData.map(sheet => {
    const csvData = sheet.data.map(row => 
      row.map(cell => `"${cell}"`).join(',')
    ).join('\n');
    return `Sheet: ${sheet.name}\n${csvData}\n\n`;
  }).join('');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', `${companyName}_AI_Modern_Slavery_Assessment.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// Risk level color mapping
const getRiskColor = (score) => {
  if (score >= 80) return '#dc2626'; // Critical - Red
  if (score >= 65) return '#ea580c'; // High - Orange-red  
  if (score >= 45) return '#d97706'; // Medium - Orange
  if (score >= 25) return '#ca8a04'; // Low - Yellow
  return '#16a34a'; // Very Low - Green
};

// Custom marker icons based on risk level
const createCustomIcon = (riskScore) => {
  const color = getRiskColor(riskScore);
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color}; width: 25px; height: 25px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
    iconSize: [25, 25],
    iconAnchor: [12, 12]
  });
};

// Enhanced AI-Powered Risk Assessment Component
const AIRiskAssessment = ({ riskAssessment }) => {
  if (!riskAssessment) return (
    <div className="section">
      <div className="no-data">
        <p>🤖 AI risk assessment data not available</p>
      </div>
    </div>
  );

  return (
    <div className="section">
      <h3>🤖 AI-Powered Risk Assessment</h3>
      
      <div className="risk-overview">
        <div className="risk-card">
          <h3>Overall Risk Score</h3>
          <div className="risk-score" style={{ color: getRiskColor(riskAssessment.overall_risk_score) }}>
            {Math.round(riskAssessment.overall_risk_score || 0)}
            <span className="score-max">/100</span>
          </div>
        </div>
        
        <div className="risk-card">
          <h3>Risk Category</h3>
          <div 
            className="risk-badge"
            style={{ backgroundColor: getRiskColor(riskAssessment.overall_risk_score) }}
          >
            {riskAssessment.risk_category || 'Unknown'}
          </div>
        </div>
        
        <div className="risk-card">
          <h3>Country Risk</h3>
          <div className="risk-score">
            {Math.round(riskAssessment.country_risk_average || 0)}
            <span className="score-max">/100</span>
          </div>
        </div>

        <div className="risk-card">
          <h3>Industry Risk</h3>
          <div className="risk-score">
            {Math.round(riskAssessment.industry_risk || 0)}
            <span className="score-max">/100</span>
          </div>
        </div>
      </div>

      {riskAssessment.breakdown && (
        <div className="section">
          <h4>Risk Breakdown</h4>
          <div className="details-grid">
            <div className="detail-item">
              <strong>Country Risk Component:</strong> {Math.round(riskAssessment.breakdown.country_risk_component || 0)}/100
            </div>
            <div className="detail-item">
              <strong>Industry Risk Component:</strong> {Math.round(riskAssessment.breakdown.industry_risk_component || 0)}/100
            </div>
            <div className="detail-item">
              <strong>Transparency Component:</strong> {Math.round(riskAssessment.breakdown.transparency_component || 0)}/100
            </div>
            <div className="detail-item">
              <strong>Mitigation Impact:</strong> {Math.round(riskAssessment.breakdown.final_mitigation_impact || 0)}%
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// AI-Generated Country Analysis Component
const AICountryAnalysis = ({ countryAnalysis }) => {
  if (!countryAnalysis || Object.keys(countryAnalysis).length === 0) {
    return (
      <div className="section">
        <div className="no-data">
          <p>🌍 AI country analysis not available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="section">
      <h3>🌍 AI Country Risk Analysis</h3>
      <div className="risk-groups-container">
        {Object.entries(countryAnalysis).map(([country, analysis]) => {
          const riskScore = analysis.risk_score || analysis.overall_risk_score || 50;
          const riskColor = getRiskColor(riskScore);
          
          return (
            <div key={country} className="risk-group" style={{ border: `3px solid ${riskColor}` }}>
              <h5 className="risk-group-title" style={{ backgroundColor: riskColor, color: 'white' }}>
                🌍 {country}
                <span style={{ float: 'right', fontSize: '0.8em' }}>Score: {Math.round(riskScore)}</span>
              </h5>
              <div className="risk-group-items">
                <div className="finding-item">
                  <div className="finding-text">
                    {analysis.key_risks && (
                      <div style={{ marginBottom: '10px' }}>
                        <strong>Key Risks:</strong>
                        <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                          {analysis.key_risks.map((risk, i) => (
                            <li key={i}>{risk}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {analysis.economic_indicators && (
                      <div style={{ marginBottom: '10px' }}>
                        <strong>Economic Indicators:</strong>
                        <div className="details-grid" style={{ marginTop: '5px' }}>
                          {Object.entries(analysis.economic_indicators).map(([key, value]) => (
                            <div key={key} className="detail-item">
                              <strong>{capitalizeFirst(key.replace(/_/g, ' '))}:</strong> {value?.value || value}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {analysis.world_bank_data && Object.keys(analysis.world_bank_data).length > 0 && (
                      <div>
                        <strong>World Bank Data:</strong>
                        <div className="details-grid" style={{ marginTop: '5px' }}>
                          {Object.entries(analysis.world_bank_data).map(([indicator, data]) => (
                            <div key={indicator} className="detail-item">
                              <strong>{indicator}:</strong> {data?.value || 'N/A'}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// AI Industry Analysis Component
const AIIndustryAnalysis = ({ industryAnalysis }) => {
  if (!industryAnalysis || Object.keys(industryAnalysis).length === 0) {
    return (
      <div className="section">
        <div className="no-data">
          <p>🏭 AI industry analysis not available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="section">
      <h3>🏭 AI Industry Risk Analysis</h3>
      
      <div className="risk-overview">
        {industryAnalysis.overall_risk_score && (
          <div className="risk-card">
            <h3>Industry Risk</h3>
            <div className="risk-score" style={{ color: getRiskColor(industryAnalysis.overall_risk_score) }}>
              {Math.round(industryAnalysis.overall_risk_score)}
              <span className="score-max">/100</span>
            </div>
          </div>
        )}
        
        {industryAnalysis.risk_level && (
          <div className="risk-card">
            <h3>Risk Level</h3>
            <div className="risk-badge" style={{ backgroundColor: getRiskColor(industryAnalysis.overall_risk_score || 50) }}>
              {industryAnalysis.risk_level}
            </div>
          </div>
        )}
      </div>

      {industryAnalysis.risk_factors && (
        <div className="section">
          <h4>Industry Risk Factors</h4>
          <ul className="findings-list">
            {industryAnalysis.risk_factors.map((factor, index) => (
              <li key={index} className="finding-item">
                <span className="finding-text">🏭 {factor}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {industryAnalysis.vulnerabilities && (
        <div className="section">
          <h4>Industry Vulnerabilities</h4>
          <div className="details-grid">
            {Object.entries(industryAnalysis.vulnerabilities).map(([key, value]) => (
              <div key={key} className="detail-item">
                <strong>{capitalizeFirst(key.replace(/_/g, ' '))}:</strong> {value}
              </div>
            ))}
          </div>
        </div>
      )}

      {industryAnalysis.best_practices && (
        <div className="section">
          <h4>AI-Recommended Best Practices</h4>
          <ul className="findings-list">
            {industryAnalysis.best_practices.map((practice, index) => (
              <li key={index} className="finding-item">
                <span className="finding-text">✅ {practice}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

// Enhanced News & Sentiment Analysis Component
const AINewsAnalysis = ({ newsAndSentiment }) => {
  if (!newsAndSentiment) return null;

  const { sentiment_analysis, recent_articles, monitoring_alerts } = newsAndSentiment;

  return (
    <div className="section">
      <h3>📰 AI News & Sentiment Analysis</h3>
      
      {sentiment_analysis && (
        <div className="risk-overview">
          <div className="risk-card">
            <h3>Sentiment Score</h3>
            <div className="risk-score" style={{ color: getRiskColor(100 - sentiment_analysis.sentiment_score) }}>
              {Math.round(sentiment_analysis.sentiment_score || 50)}
              <span className="score-max">/100</span>
            </div>
          </div>
          
          <div className="risk-card">
            <h3>Articles Analyzed</h3>
            <div className="risk-score">
              {recent_articles?.length || 0}
            </div>
          </div>
        </div>
      )}

      {sentiment_analysis?.key_themes && (
        <div className="section">
          <h4>Key Themes Identified</h4>
          <ul className="findings-list">
            {sentiment_analysis.key_themes.map((theme, index) => (
              <li key={index} className="finding-item">
                <span className="finding-text">🔍 {theme}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {monitoring_alerts && monitoring_alerts.length > 0 && (
        <div className="section">
          <h4>Monitoring Alerts</h4>
          <div className="risk-groups-container">
            {monitoring_alerts.map((alert, index) => (
              <div key={index} className="risk-group" style={{ border: `3px solid ${alert.level === 'High' ? '#dc2626' : '#d97706'}` }}>
                <h5 className="risk-group-title" style={{ backgroundColor: alert.level === 'High' ? '#dc2626' : '#d97706', color: 'white' }}>
                  ⚠️ {alert.level} Priority Alert
                </h5>
                <div className="risk-group-items">
                  <div className="finding-item">
                    <div className="finding-text">
                      <div style={{ marginBottom: '8px' }}><strong>Message:</strong> {alert.message}</div>
                      <div><strong>Recommended Action:</strong> {alert.action}</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {recent_articles && recent_articles.length > 0 && (
        <div className="section">
          <h4>Recent Articles Analyzed</h4>
          <div className="details-grid">
            {recent_articles.slice(0, 3).map((article, index) => (
              <div key={index} className="detail-item">
                <strong>Article {index + 1}:</strong> {article.title || 'No title available'}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Enhanced Manufacturing Map Component
const AIManufacturingMap = ({ locations, companyProfile }) => {
  const [selectedLocation, setSelectedLocation] = useState(null);

  // Try to get locations from different possible sources
  const manufacturingLocations = locations || 
    companyProfile?.manufacturing_locations || 
    companyProfile?.operational_locations || 
    [];

  if (!manufacturingLocations || manufacturingLocations.length === 0) {
    return (
      <div className="section">
        <h3>🗺️ Global Operations Map</h3>
        <div className="no-data">
          <p>🔍 AI is analyzing operational locations...</p>
          <p>Manufacturing location data will be available once AI processing completes.</p>
        </div>
      </div>
    );
  }

  // Calculate center point for map
  const validLocations = manufacturingLocations.filter(loc => 
    loc.coordinates && loc.coordinates.lat && loc.coordinates.lng
  );

  if (validLocations.length === 0) {
    return (
      <div className="section">
        <h3>🗺️ Global Operations Map</h3>
        <div className="no-data">No valid coordinate data available for mapping</div>
      </div>
    );
  }

  const centerLat = validLocations.reduce((sum, loc) => sum + loc.coordinates.lat, 0) / validLocations.length;
  const centerLng = validLocations.reduce((sum, loc) => sum + loc.coordinates.lng, 0) / validLocations.length;

  return (
    <div className="section manufacturing-map">
      <h3>🗺️ AI-Mapped Global Operations</h3>
      
      {/* Interactive Map */}
      <div style={{ height: '500px', width: '100%', marginBottom: '20px', borderRadius: '8px', overflow: 'hidden' }}>
        <MapContainer 
          center={[centerLat, centerLng]} 
          zoom={2} 
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          {validLocations.map((location, index) => {
            const riskScore = location.risk_score || location.country_risk || 50;
            return (
              <Marker
                key={index}
                position={[location.coordinates.lat, location.coordinates.lng]}
                icon={createCustomIcon(riskScore)}
              >
                <Popup>
                  <div style={{ minWidth: '200px' }}>
                    <h4 style={{ margin: '0 0 8px 0' }}>{location.city}, {location.country}</h4>
                    <p><strong>Facility:</strong> {location.facility_type || 'Operations'}</p>
                    <p><strong>Products:</strong> {location.products?.join(', ') || 'Various'}</p>
                    <p><strong>Risk Score:</strong> <span style={{color: getRiskColor(riskScore)}}>{Math.round(riskScore)}</span></p>
                    {location.risk_factors && location.risk_factors.length > 0 && (
                      <div>
                        <strong>AI-Identified Risk Factors:</strong>
                        <ul style={{ margin: '4px 0', paddingLeft: '16px' }}>
                          {location.risk_factors.slice(0, 3).map((factor, i) => (
                            <li key={i} style={{ fontSize: '0.9em' }}>{factor}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>

      {/* Location Cards */}
      <div className="risk-groups-container">
        {validLocations.map((location, index) => {
          const riskScore = location.risk_score || location.country_risk || 50;
          const riskColor = getRiskColor(riskScore);
          const riskLevel = riskScore >= 75 ? 'High' : riskScore >= 40 ? 'Medium' : 'Low';

          return (
            <div key={index} className="risk-group" style={{ border: `3px solid ${riskColor}` }}>
              <h5 className="risk-group-title" style={{ backgroundColor: riskColor, color: 'white' }}>
                📍 {location.city}, {location.country}
                <span style={{ float: 'right', fontSize: '0.8em' }}>{riskLevel} Risk</span>
              </h5>
              <div className="risk-group-items">
                <div className="finding-item">
                  <div className="finding-text">
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '10px' }}>
                      <div><strong>Facility:</strong> {location.facility_type || 'Operations'}</div>
                      <div><strong>AI Risk Score:</strong> {Math.round(riskScore)}/100</div>
                    </div>
                    <div style={{ marginBottom: '10px' }}>
                      <strong>Products/Services:</strong> {location.products?.join(', ') || location.description || 'Various operations'}
                    </div>
                    
                    {location.ai_analysis && (
                      <div style={{ 
                        marginTop: '10px', 
                        padding: '10px', 
                        backgroundColor: '#e7f3ff', 
                        borderRadius: '4px',
                        border: '1px solid #b3d9ff'
                      }}>
                        <strong style={{ color: '#0056b3' }}>🤖 AI Analysis:</strong>
                        <p style={{ margin: '5px 0', fontSize: '0.9em', color: '#0056b3' }}>{location.ai_analysis}</p>
                      </div>
                    )}

                    {location.risk_factors && location.risk_factors.length > 0 && (
                      <div style={{ 
                        marginTop: '10px', 
                        padding: '10px', 
                        backgroundColor: '#fff3cd', 
                        borderRadius: '4px',
                        border: '1px solid #ffeaa7'
                      }}>
                        <strong style={{ color: '#856404' }}>⚠️ AI-Identified Risks:</strong>
                        <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                          {location.risk_factors.map((factor, i) => (
                            <li key={i} style={{ fontSize: '0.9em', color: '#856404' }}>{factor}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Enhanced AI Recommendations Component
const AIRecommendations = ({ recommendations }) => {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="section">
        <h3>💡 AI-Generated Recommendations</h3>
        <div className="no-data">No recommendations available</div>
      </div>
    );
  }

  return (
    <div className="section">
      <h3>💡 AI-Generated Recommendations</h3>
      <div className="risk-groups-container">
        {recommendations.map((rec, index) => {
          // Handle both string and object recommendations
          const recText = typeof rec === 'string' ? rec : rec.action || rec.description || rec.recommendation;
          const priority = rec.priority || 'Medium';
          const timeline = rec.timeline || rec.implementation_timeline;
          const impact = rec.expected_impact || rec.impact;
          
          const priorityColor = priority === 'Critical' ? '#dc2626' : 
                               priority === 'High' ? '#ea580c' : 
                               priority === 'Medium' ? '#d97706' : '#16a34a';

          return (
            <div key={index} className="risk-group" style={{ border: `3px solid ${priorityColor}` }}>
              <h5 className="risk-group-title" style={{ backgroundColor: priorityColor, color: 'white' }}>
                💡 Recommendation #{index + 1}
                {priority && <span style={{ float: 'right', fontSize: '0.8em' }}>{priority} Priority</span>}
              </h5>
              <div className="risk-group-items">
                <div className="finding-item">
                  <div className="finding-text">
                    <div style={{ marginBottom: '10px', fontSize: '1rem', fontWeight: '500' }}>
                      {recText}
                    </div>
                    
                    {(timeline || impact) && (
                      <div className="details-grid" style={{ marginTop: '10px' }}>
                        {timeline && (
                          <div className="detail-item">
                            <strong>Timeline:</strong> {timeline}
                          </div>
                        )}
                        {impact && (
                          <div className="detail-item">
                            <strong>Expected Impact:</strong> {impact}
                          </div>
                        )}
                      </div>
                    )}

                    {rec.success_metrics && (
                      <div style={{ 
                        marginTop: '10px', 
                        padding: '10px', 
                        backgroundColor: '#f0f9ff', 
                        borderRadius: '4px',
                        border: '1px solid #bae6fd'
                      }}>
                        <strong style={{ color: '#0c4a6e' }}>📊 Success Metrics:</strong>
                        <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                          {rec.success_metrics.map((metric, i) => (
                            <li key={i} style={{ fontSize: '0.9em', color: '#0c4a6e' }}>{metric}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [companyName, setCompanyName] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [progress, setProgress] = useState(0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!companyName.trim()) {
      setError('Please enter a company name');
      return;
    }
    
    setLoading(true);
    setError('');
    setResults(null);
    setProgress(0);

    // Simulate progress updates
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 95) return prev;
        return prev + Math.random() * 10 + 5;
      });
    }, 800);
    
    try {
      // Use the AI-powered backend endpoint
      const response = await fetch(`http://localhost:5000/assess?company=${encodeURIComponent(companyName.trim())}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.details || `Server error: ${response.status}`);
      }
      
      const data = await response.json();
      console.log("AI-powered results:", data);

      // Check for errors in response
      if (data.error) {
        throw new Error(data.details || data.error);
      }

      // Complete progress
      clearInterval(progressInterval);
      setProgress(100);

      // Brief delay to show 100% before hiding
      setTimeout(() => {
        setResults(data);
        setLoading(false);
        setProgress(0);
      }, 500);

    } catch (err) {
      console.error('AI Assessment error:', err);
      clearInterval(progressInterval);
      setError(`AI assessment failed: ${err.message}. Please ensure the AI backend is running.`);
      setLoading(false);
      setProgress(0);
    }
  };

  const clearResults = () => {
    setResults(null);
    setCompanyName('');
    setError('');
    setActiveTab('overview');
  };

  const handleExport = () => {
    if (results) {
      exportToExcel(results, companyName);
    }
  };

  return (
    <div style={{ 
      fontFamily: 'system-ui, -apple-system, sans-serif',
      margin: 0,
      padding: '20px',
      backgroundColor: '#f8fafc',
      minHeight: '100vh'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <header style={{ 
          textAlign: 'center', 
          marginBottom: '40px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          padding: '40px',
          borderRadius: '12px',
          boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px', justifyContent: 'center', marginBottom: '20px' }}>
            <h2 style={{ margin: 0 }}>🤖 AI-Powered Rosetta Solutions</h2>
          </div>
          <h1 style={{ fontSize: '2.5rem', margin: '0 0 15px 0', fontWeight: '700' }}>
            Modern Slavery Risk Assessment
          </h1>
          <p style={{ fontSize: '1.2rem', margin: 0, opacity: 0.9 }}>
            Real-Time AI Analysis | Dynamic Risk Assessment | Global Intelligence
          </p>
        </header>
          
        <div style={{ marginBottom: '30px' }}>
          <form onSubmit={handleSubmit} style={{ 
            display: 'flex', 
            gap: '15px', 
            maxWidth: '600px', 
            margin: '0 auto',
            padding: '20px',
            backgroundColor: 'white',
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}>
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="Enter any company name for AI analysis..."
              style={{
                flex: 1,
                padding: '15px',
                border: '2px solid #e2e8f0',
                borderRadius: '8px',
                fontSize: '16px',
                outline: 'none',
                transition: 'border-color 0.2s'
              }}
              disabled={loading}
            />
            <button 
              type="submit" 
              disabled={loading || !companyName.trim()}
              style={{
                padding: '15px 30px',
                background: loading ? '#94a3b8' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                minWidth: '120px',
                justifyContent: 'center'
              }}
            >
              {loading ? (
                <>
                  <div style={{
                    width: '20px',
                    height: '20px',
                    border: '2px solid rgba(255,255,255,0.3)',
                    borderTop: '2px solid white',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                  }}></div>
                  {Math.round(progress)}%
                </>
              ) : (
                '🤖 AI Analyze'
              )}
            </button>
          </form>

          {error && (
            <div style={{
              margin: '20px auto',
              maxWidth: '600px',
              padding: '15px',
              background: '#fee2e2',
              border: '1px solid #fecaca',
              borderRadius: '8px',
              color: '#dc2626'
            }}>
              <strong>Error:</strong> {error}
            </div>
          )}
          
          {results && (
            <div style={{ marginTop: '30px' }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                marginBottom: '20px',
                padding: '20px',
                backgroundColor: 'white',
                borderRadius: '12px',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}>
                <h2 style={{ margin: 0 }}>🤖 AI Assessment: {companyName}</h2>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button 
                    onClick={handleExport}
                    style={{
                      padding: '10px 20px',
                      background: '#10b981',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer'
                    }}
                  >
                    📊 Export AI Data
                  </button>
                  <button 
                    onClick={clearResults}
                    style={{
                      padding: '10px 20px',
                      background: '#6b7280',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer'
                    }}
                  >
                    New Analysis
                  </button>
                </div>
              </div>
              
              {/* AI Risk Overview */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '20px',
                marginBottom: '30px'
              }}>
                <div style={{
                  padding: '20px',
                  backgroundColor: 'white',
                  borderRadius: '12px',
                  boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                  textAlign: 'center'
                }}>
                  <h3 style={{ margin: '0 0 10px 0' }}>Overall Risk</h3>
                  <div style={{
                    fontSize: '2rem',
                    fontWeight: 'bold',
                    color: getRiskColor(results.overall_risk_assessment?.overall_risk_score || 50)
                  }}>
                    {Math.round(results.overall_risk_assessment?.overall_risk_score || 0)}
                    <span style={{ fontSize: '1rem', opacity: 0.7 }}>/100</span>
                  </div>
                  <div style={{
                    marginTop: '10px',
                    padding: '8px 16px',
                    borderRadius: '20px',
                    backgroundColor: getRiskColor(results.overall_risk_assessment?.overall_risk_score || 50),
                    color: 'white',
                    fontSize: '0.9rem',
                    fontWeight: '600'
                  }}>
                    {results.overall_risk_assessment?.risk_category || 'Unknown'}
                  </div>
                </div>
                
                <div style={{
                  padding: '20px',
                  backgroundColor: 'white',
                  borderRadius: '12px',
                  boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                  textAlign: 'center'
                }}>
                  <h3 style={{ margin: '0 0 10px 0' }}>Data Quality</h3>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#10b981' }}>
                    {Math.round(results.assessment_quality?.data_completeness || 85)}%
                  </div>
                  <div style={{ marginTop: '5px', fontSize: '0.9rem', color: '#6b7280' }}>
                    {results.assessment_quality?.confidence_level || 'High'} Confidence
                  </div>
                </div>

                <div style={{
                  padding: '20px',
                  backgroundColor: 'white',
                  borderRadius: '12px',
                  boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                  textAlign: 'center'
                }}>
                  <h3 style={{ margin: '0 0 10px 0' }}>AI Analysis</h3>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#667eea' }}>
                    ✓ Complete
                  </div>
                  <div style={{ marginTop: '5px', fontSize: '0.9rem', color: '#6b7280' }}>
                    Dynamic Assessment
                  </div>
                </div>

                <div style={{
                  padding: '20px',
                  backgroundColor: 'white',
                  borderRadius: '12px',
                  boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                  textAlign: 'center'
                }}>
                  <h3 style={{ margin: '0 0 10px 0' }}>Recommendations</h3>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#f59e0b' }}>
                    {results.recommendations?.length || 0}
                  </div>
                  <div style={{ marginTop: '5px', fontSize: '0.9rem', color: '#6b7280' }}>
                    AI-Generated Actions
                  </div>
                </div>
              </div>

              {/* Tab Navigation */}
              <div style={{
                display: 'flex',
                gap: '10px',
                marginBottom: '20px',
                padding: '10px',
                backgroundColor: 'white',
                borderRadius: '12px',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                overflow: 'auto'
              }}>
                {[
                  { key: 'overview', label: '📊 AI Overview', icon: '🤖' },
                  { key: 'risk-assessment', label: '🎯 Risk Analysis', icon: '📊' },
                  { key: 'country-analysis', label: '🌍 Country Intel', icon: '🌍' },
                  { key: 'industry-analysis', label: '🏭 Industry Risks', icon: '🏭' },
                  { key: 'mapping', label: '🗺️ AI Mapping', icon: '🗺️' },
                  { key: 'news-sentiment', label: '📰 News AI', icon: '📰' },
                  { key: 'recommendations', label: '💡 AI Actions', icon: '💡' }
                ].map(tab => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key)}
                    style={{
                      padding: '12px 20px',
                      border: 'none',
                      borderRadius: '8px',
                      background: activeTab === tab.key ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#f1f5f9',
                      color: activeTab === tab.key ? 'white' : '#475569',
                      cursor: 'pointer',
                      fontWeight: '600',
                      fontSize: '0.9rem',
                      whiteSpace: 'nowrap',
                      transition: 'all 0.2s'
                    }}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div style={{
                backgroundColor: 'white',
                borderRadius: '12px',
                padding: '30px',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}>
                {activeTab === 'overview' && (
                  <div>
                    <h3 style={{ marginTop: 0 }}>🤖 AI Company Analysis</h3>
                    {results.company_profile && (
                      <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                        gap: '15px',
                        marginBottom: '30px'
                      }}>
                        <div><strong>Industry:</strong> {results.company_profile.industry || 'AI Analyzing...'}</div>
                        <div><strong>Revenue:</strong> ${results.company_profile.revenue_billions || 'N/A'}B</div>
                        <div><strong>Countries:</strong> {results.company_profile.countries_of_operation?.length || 0}</div>
                        <div><strong>Assessment Method:</strong> {results.methodology || 'AI-powered dynamic assessment'}</div>
                      </div>
                    )}

                    {results.overall_risk_assessment && (
                      <AIRiskAssessment riskAssessment={results.overall_risk_assessment} />
                    )}
                  </div>
                )}

                {activeTab === 'risk-assessment' && (
                  <AIRiskAssessment riskAssessment={results.overall_risk_assessment} />
                )}

                {activeTab === 'country-analysis' && (
                  <AICountryAnalysis countryAnalysis={results.country_analysis} />
                )}

                {activeTab === 'industry-analysis' && (
                  <AIIndustryAnalysis industryAnalysis={results.industry_analysis} />
                )}

                {activeTab === 'mapping' && (
                  <AIManufacturingMap 
                    locations={results.manufacturing_locations} 
                    companyProfile={results.company_profile}
                  />
                )}

                {activeTab === 'news-sentiment' && (
                  <AINewsAnalysis newsAndSentiment={results.news_and_sentiment} />
                )}

                {activeTab === 'recommendations' && (
                  <AIRecommendations recommendations={results.recommendations} />
                )}
              </div>
            </div>
          )}
        </div>
        
        <footer style={{
          textAlign: 'center',
          padding: '20px',
          backgroundColor: '#374151',
          color: 'white',
          borderRadius: '12px',
          marginTop: '40px'
        }}>
          <p style={{ margin: 0 }}>
            © 2025 Rosetta Solutions - AI-Powered Modern Slavery Risk Assessment. 
            This tool provides AI-generated risk insights using real-time data analysis.
          </p>
        </footer>
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .risk-groups-container {
          display: grid;
          gap: 20px;
          margin-top: 20px;
        }
        
        .risk-group {
          border-radius: 8px;
          overflow: hidden;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .risk-group-title {
          margin: 0;
          padding: 15px;
          font-size: 1.1rem;
          font-weight: 600;
        }
        
        .risk-group-items {
          padding: 0;
        }
        
        .finding-item {
          padding: 15px;
          background: white;
        }
        
        .finding-text {
          line-height: 1.5;
        }
        
        .findings-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        
        .findings-list .finding-item {
          margin-bottom: 10px;
          padding: 15px;
          background: #f8fafc;
          border-radius: 8px;
          border-left: 4px solid #667eea;
        }
        
        .details-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 15px;
          margin-top: 15px;
        }
        
        .detail-item {
          padding: 10px;
          background: #f8fafc;
          border-radius: 6px;
          border-left: 3px solid #e2e8f0;
        }
        
        .no-data {
          text-align: center;
          padding: 40px;
          background: #f8fafc;
          border-radius: 8px;
          color: #6b7280;
        }
      `}</style>
    </div>
  );
}

export default App;