import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import './App.css';

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Helper function to capitalize first letter
const capitalizeFirst = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
};

// Export functionality - Enhanced version
const exportToExcel = (results, companyName) => {
  // Create workbook data
  const workbookData = [];

  // Overview Sheet
  const overviewData = [
    ['Modern Slavery Risk Assessment - Overview'],
    ['Company:', companyName],
    ['Assessment Date:', results.assessment_date || new Date().toLocaleDateString()],
    ['Overall Risk Level:', results.risk_level || 'Unknown'],
    ['Risk Score:', `${results.overall_risk_score || 'N/A'}/100`],
    ['Manufacturing Sites:', results.company_profile?.manufacturing_locations?.length || 0],
    ['Countries of Operation:', results.company_profile?.countries_of_operation?.length || 0],
    [''],
    ['Modern Slavery Risk Details:'],
  ];

  if (results.modern_slavery_risk) {
    overviewData.push(['Modern Slavery Score:', `${results.modern_slavery_risk.final_risk_score}/100`]);
    overviewData.push(['Risk Category:', results.modern_slavery_risk.risk_category]);
    overviewData.push(['Industry Risk Multiplier:', `${(results.modern_slavery_risk.industry_risk_multiplier * 100).toFixed(1)}%`]);
    overviewData.push(['Mitigation Effectiveness:', `${(results.modern_slavery_risk.mitigation_effectiveness * 100).toFixed(1)}%`]);
  }

  overviewData.push([''], ['Risk Breakdown:']);
  if (results.risk_breakdown) {
    overviewData.push(['Inherent Risk:', `${results.risk_breakdown.inherent_risk}/100`]);
    overviewData.push(['Industry Risk:', `${results.risk_breakdown.industry_risk}/100`]);
    overviewData.push(['Mitigation Score:', `${results.risk_breakdown.mitigation_score}/100`]);
  }

  overviewData.push([''], ['Recommendations:']);
  if (results.mitigation_measures?.recommendations) {
    results.mitigation_measures.recommendations.forEach((rec, index) => {
      overviewData.push([`${index + 1}.`, rec]);
    });
  }

  workbookData.push({ name: 'Overview', data: overviewData });

  // Modern Slavery Risk Sheet
  if (results.modern_slavery_risk) {
    const modernSlaveryData = [
      ['Modern Slavery Risk Analysis'],
      ['Final Risk Score:', `${results.modern_slavery_risk.final_risk_score}/100`],
      ['Risk Category:', results.modern_slavery_risk.risk_category],
      [''],
      ['Country Risk Breakdown:'],
    ];

    if (results.modern_slavery_risk.country_risks) {
      Object.entries(results.modern_slavery_risk.country_risks).forEach(([country, score]) => {
        modernSlaveryData.push([country + ':', `${score}/100`]);
      });
    }

    modernSlaveryData.push([''], ['Vulnerability Factors:']);
    if (results.modern_slavery_risk.vulnerability_factors) {
      results.modern_slavery_risk.vulnerability_factors.forEach((factor, index) => {
        modernSlaveryData.push([`${index + 1}.`, factor.country, `Prevalence: ${factor.prevalence_rate}`, `TIP Tier: ${factor.tip_tier}`]);
      });
    }

    modernSlaveryData.push([''], ['Key Concerns:']);
    if (results.modern_slavery_risk.key_concerns) {
      results.modern_slavery_risk.key_concerns.forEach((concern, index) => {
        modernSlaveryData.push([`${index + 1}.`, concern]);
      });
    }

    workbookData.push({ name: 'Modern Slavery Risk', data: modernSlaveryData });
  }

  // Company Profile Sheet
  if (results.company_profile) {
    const companyData = [
      ['Company Profile'],
      ['Industry:', results.company_profile.industry || ''],
      ['Revenue (Billions):', results.company_profile.revenue_billions || ''],
      ['Supply Chain Transparency:', `${results.company_profile.supply_chain_transparency_score || 'N/A'}/100`],
      [''],
      ['Countries of Operation:'],
    ];

    if (results.company_profile.countries_of_operation) {
      results.company_profile.countries_of_operation.forEach((country, index) => {
        const riskScore = results.risk_breakdown?.country_risks?.[country] || 'N/A';
        companyData.push([`${index + 1}.`, country, `Risk Score: ${riskScore}`]);
      });
    }

    companyData.push([''], ['Current Policies:']);
    if (results.mitigation_measures?.current_policies) {
      Object.entries(results.mitigation_measures.current_policies).forEach(([policy, value]) => {
        companyData.push([capitalizeFirst(policy.replace('_', ' ')) + ':', typeof value === 'boolean' ? (value ? 'Yes' : 'No') : value]);
      });
    }

    workbookData.push({ name: 'Company Profile', data: companyData });
  }

  // Manufacturing Locations Sheet
  if (results.company_profile?.manufacturing_locations && results.company_profile.manufacturing_locations.length > 0) {
    const locationData = [
      ['Manufacturing Locations'],
      ['City', 'Country', 'Facility Type', 'Products', 'Risk Score', 'Latitude', 'Longitude'],
    ];

    results.company_profile.manufacturing_locations.forEach(location => {
      const countryRisk = results.risk_breakdown?.country_risks?.[location.country] || 'N/A';
      locationData.push([
        location.city || '',
        location.country || '',
        location.facility_type || '',
        location.products?.join(', ') || '',
        countryRisk,
        location.coordinates?.lat || '',
        location.coordinates?.lng || '',
      ]);
    });

    workbookData.push({ name: 'Manufacturing Locations', data: locationData });
  }

  // Risk Factors Sheet
  if (results.risk_factors) {
    const riskData = [
      ['Risk Factors Analysis'],
      [''],
      ['Governance and Regulatory Risks:'],
    ];

    if (results.risk_factors.governance_and_regulatory) {
      Object.entries(results.risk_factors.governance_and_regulatory).forEach(([country, factors]) => {
        riskData.push([`Country: ${country}`]);
        factors.forEach((factor, index) => {
          riskData.push([`${index + 1}.`, factor.factor, `Score: ${factor.score}`, factor.evidence]);
        });
      });
    }

    riskData.push([''], ['Economic Vulnerability:']);
    if (results.risk_factors.economic_vulnerability) {
      Object.entries(results.risk_factors.economic_vulnerability).forEach(([country, factors]) => {
        riskData.push([`Country: ${country}`]);
        factors.forEach((factor, index) => {
          riskData.push([`${index + 1}.`, factor.factor, `Score: ${factor.score}`, factor.evidence]);
        });
      });
    }

    workbookData.push({ name: 'Risk Factors', data: riskData });
  }

  // Data Sources Sheet
  if (results.data_sources) {
    const dataSourcesData = [
      ['Data Sources & Methodology'],
      ['Methodology:', results.data_sources.methodology || 'Comprehensive modern slavery risk analysis'],
      [''],
      ['Primary Sources:'],
    ];

    if (results.data_sources.primary_sources) {
      results.data_sources.primary_sources.forEach((source, index) => {
        dataSourcesData.push([`${index + 1}.`, source]);
      });
    }

    dataSourcesData.push([''], ['News Analysis:']);
    if (results.data_sources.news_analysis) {
      dataSourcesData.push(['Articles Found:', results.data_sources.news_analysis.articles_found || 0]);
      dataSourcesData.push(['Sentiment Score:', `${results.data_sources.news_analysis.sentiment_score || 'N/A'}/100`]);
      dataSourcesData.push(['AI Analysis:', results.data_sources.news_analysis.ai_analysis || 'N/A']);
    }

    workbookData.push({ name: 'Data Sources', data: dataSourcesData });
  }

  // Convert to CSV format and download
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
  link.setAttribute('download', `${companyName}_Modern_Slavery_Assessment.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// Risk level color mapping
const getRiskColor = (score) => {
  if (score >= 75) return '#dc2626'; // Red
  if (score >= 60) return '#ea580c'; // Orange-red
  if (score >= 40) return '#d97706'; // Orange
  if (score >= 25) return '#ca8a04'; // Yellow
  return '#16a34a'; // Green
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

// Modern Slavery Risk Component - Enhanced for new backend
const ModernSlaveryRisk = ({ modernSlaveryData }) => {
  if (!modernSlaveryData) return (
    <div className="section">
      <div className="no-data">
        <p>🎯 Modern slavery risk data not available</p>
      </div>
    </div>
  );

  const {
    final_risk_score,
    risk_category,
    country_risks,
    industry_risk_multiplier,
    mitigation_effectiveness,
    vulnerability_factors,
    key_concerns
  } = modernSlaveryData;

  return (
    <div className="section">
      <h3>🎯 Modern Slavery Risk Assessment</h3>
      
      {/* Risk Score Overview */}
      <div className="risk-overview">
        <div className="risk-card">
          <h3>Final Risk Score</h3>
          <div className="risk-score" style={{ color: getRiskColor(final_risk_score) }}>
            {Math.round(final_risk_score)}
            <span className="score-max">/100</span>
          </div>
        </div>
        
        <div className="risk-card">
          <h3>Risk Category</h3>
          <div 
            className="risk-badge"
            style={{ backgroundColor: getRiskColor(final_risk_score) }}
          >
            {risk_category}
          </div>
        </div>
        
        <div className="risk-card">
          <h3>Industry Multiplier</h3>
          <div className="risk-score">
            {(industry_risk_multiplier * 100).toFixed(0)}
            <span className="score-max">%</span>
          </div>
        </div>

        <div className="risk-card">
          <h3>Mitigation Effect</h3>
          <div className="risk-score" style={{ color: '#16a34a' }}>
            {(mitigation_effectiveness * 100).toFixed(0)}
            <span className="score-max">%</span>
          </div>
        </div>
      </div>

      {/* Country Risk Breakdown */}
      {country_risks && Object.keys(country_risks).length > 0 && (
        <div className="section">
          <h4>Country Risk Breakdown</h4>
          <div className="details-grid">
            {Object.entries(country_risks).map(([country, score]) => (
              <div key={country} className="detail-item">
                <strong>{country}:</strong> 
                <span style={{ color: getRiskColor(score), marginLeft: '8px' }}>
                  {Math.round(score)}/100
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Vulnerability Factors */}
      {vulnerability_factors && vulnerability_factors.length > 0 && (
        <div className="section">
          <h4>High-Risk Locations</h4>
          <div className="risk-groups-container">
            {vulnerability_factors.map((factor, index) => (
              <div key={index} className="risk-group">
                <h5 className="risk-group-title">
                  🌍 {factor.country} - {factor.risk_level} Risk
                </h5>
                <div className="risk-group-items">
                  <div className="finding-item">
                    <div className="finding-text">
                      <div style={{ marginBottom: '8px' }}>
                        <strong>Prevalence Rate:</strong> {factor.prevalence_rate} per 1,000 population
                      </div>
                      <div style={{ marginBottom: '8px' }}>
                        <strong>TIP Tier:</strong> {factor.tip_tier}
                      </div>
                      {factor.primary_concerns && factor.primary_concerns.length > 0 && (
                        <div>
                          <strong>Primary Concerns:</strong>
                          <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                            {factor.primary_concerns.map((concern, i) => (
                              <li key={i}>{concern}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Key Concerns */}
      {key_concerns && key_concerns.length > 0 && (
        <div className="section">
          <h4>Key Concerns</h4>
          <ul className="findings-list">
            {key_concerns.map((concern, index) => (
              <li key={index} className="finding-item">
                <span className="finding-text">⚠️ {concern}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Assessment Method */}
      <div className="details-grid">
        <div className="detail-item">
          <strong>Assessment Method:</strong> Comprehensive modern slavery risk analysis combining country and industry level risks with company mitigation efforts
        </div>
      </div>
    </div>
  );
};

// Enhanced Risk Factors Component for new backend structure
const RiskFactorsGrouped = ({ riskFactors }) => {
  if (!riskFactors) return null;

  const renderRiskSection = (title, icon, factors, sectionKey) => {
    if (!factors || Object.keys(factors).length === 0) return null;

    return (
      <div key={sectionKey} className="risk-group">
        <h5 className="risk-group-title">
          {icon} {title}
        </h5>
        <div className="risk-group-items">
          {Object.entries(factors).map(([country, countryFactors]) => (
            <div key={country} className="finding-item">
              <div className="finding-text">
                <h6 style={{ margin: '0 0 10px 0', color: '#333' }}>{country}</h6>
                {Array.isArray(countryFactors) && countryFactors.map((factor, index) => (
                  <div key={index} style={{ marginBottom: '12px', padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                    <div style={{ fontWeight: '600', marginBottom: '4px' }}>{factor.factor}</div>
                    <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '4px' }}>
                      <strong>Score:</strong> <span style={{ color: getRiskColor(factor.score) }}>{factor.score}</span>
                    </div>
                    <div style={{ fontSize: '0.9rem', color: '#555' }}>
                      <strong>Evidence:</strong> {factor.evidence}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="section">
      <h3>⚠️ Risk Factors</h3>
      <div className="risk-groups-container">
        {renderRiskSection("🏛️ Governance & Regulatory", "🏛️", riskFactors.governance_and_regulatory, "governance")}
        {renderRiskSection("💰 Economic Vulnerability", "💰", riskFactors.economic_vulnerability, "economic")}
        {renderRiskSection("🎯 Modern Slavery Indicators", "🎯", riskFactors.modern_slavery_indicators, "modern_slavery")}
        {renderRiskSection("🏭 Industry Specific", "🏭", riskFactors.industry_specific, "industry")}
      </div>
    </div>
  );
};

// Manufacturing Map Component with react-leaflet
const ManufacturingMap = ({ locations }) => {
  const [selectedLocation, setSelectedLocation] = useState(null);

  if (!locations || locations.length === 0) {
    return (
      <div className="section">
        <h3>🗺️ Global Manufacturing Locations</h3>
        <div className="no-data">No manufacturing location data available</div>
      </div>
    );
  }

  // Calculate center point for map
  const centerLat = locations.reduce((sum, loc) => sum + loc.coordinates.lat, 0) / locations.length;
  const centerLng = locations.reduce((sum, loc) => sum + loc.coordinates.lng, 0) / locations.length;

  return (
    <div className="section manufacturing-map">
      <h3>🗺️ Global Manufacturing Locations</h3>
      
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
          {locations.map((location, index) => {
            const riskScore = location.risk_score || 50;
            return (
              <Marker
                key={index}
                position={[location.coordinates.lat, location.coordinates.lng]}
                icon={createCustomIcon(riskScore)}
              >
                <Popup>
                  <div style={{ minWidth: '200px' }}>
                    <h4 style={{ margin: '0 0 8px 0' }}>{location.city}, {location.country}</h4>
                    <p><strong>Facility:</strong> {location.facility_type}</p>
                    <p><strong>Products:</strong> {location.products?.join(', ')}</p>
                    <p><strong>Risk Score:</strong> <span style={{color: getRiskColor(riskScore)}}>{Math.round(riskScore)}</span></p>
                    {location.risk_factors && location.risk_factors.length > 0 && (
                      <div>
                        <strong>Risk Factors:</strong>
                        <ul style={{ margin: '4px 0', paddingLeft: '16px' }}>
                          {location.risk_factors.map((factor, i) => (
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

      {/* Map Legend */}
      <div className="details-grid" style={{ marginBottom: '20px' }}>
        <div className="detail-item" style={{ borderLeft: '4px solid #dc2626' }}>
          <strong>High Risk (75+)</strong> - Significant concerns requiring immediate attention
        </div>
        <div className="detail-item" style={{ borderLeft: '4px solid #d97706' }}>
          <strong>Medium Risk (40-75)</strong> - Moderate risk factors present
        </div>
        <div className="detail-item" style={{ borderLeft: '4px solid #16a34a' }}>
          <strong>Low Risk (&lt;40)</strong> - Lower risk environment
        </div>
      </div>

      {/* Location Cards Grid */}
      <div className="risk-groups-container">
        {locations.map((location, index) => {
          const riskScore = location.risk_score || 50;
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
                      <div><strong>Facility Type:</strong> {capitalizeFirst(location.facility_type || 'Operations')}</div>
                      <div><strong>Risk Score:</strong> {Math.round(riskScore)}/100</div>
                    </div>
                    <div style={{ marginBottom: '10px' }}>
                      <strong>Products/Services:</strong> {location.products?.join(', ') || 'Various'}
                    </div>
                    
                    {location.coordinates && (
                      <div style={{ marginBottom: '10px', fontSize: '0.9em', color: '#666' }}>
                        <strong>Coordinates:</strong> {location.coordinates.lat.toFixed(4)}, {location.coordinates.lng.toFixed(4)}
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
                        <strong style={{ color: '#856404' }}>⚠️ Risk Factors:</strong>
                        <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                          {location.risk_factors.map((factor, i) => (
                            <li key={i} style={{ fontSize: '0.9em', color: '#856404' }}>{factor}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <button 
                      className="tab-button"
                      style={{ 
                        marginTop: '10px',
                        padding: '8px 16px',
                        fontSize: '0.9em'
                      }}
                      onClick={() => setSelectedLocation(selectedLocation === index ? null : index)}
                    >
                      {selectedLocation === index ? 'Hide Details' : 'Show Details'}
                    </button>

                    {selectedLocation === index && (
                      <div style={{ 
                        marginTop: '15px', 
                        padding: '15px', 
                        backgroundColor: '#f8f9fa', 
                        borderRadius: '8px',
                        border: '1px solid #e9ecef'
                      }}>
                        <h6 style={{ margin: '0 0 10px 0', color: '#333' }}>📍 Detailed Location Information</h6>
                        <div className="details-grid">
                          <div className="detail-item">
                            <strong>Full Address:</strong> {location.city}, {location.country}
                          </div>
                          <div className="detail-item">
                            <strong>Facility Type:</strong> {location.facility_type}
                          </div>
                          {location.coordinates && (
                            <>
                              <div className="detail-item">
                                <strong>Latitude:</strong> {location.coordinates.lat.toFixed(6)}
                              </div>
                              <div className="detail-item">
                                <strong>Longitude:</strong> {location.coordinates.lng.toFixed(6)}
                              </div>
                            </>
                          )}
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

// Enhanced Data Sources Component for new backend
const EnhancedDataSources = ({ dataSources }) => {
  if (!dataSources) {
    return (
      <div className="section enhanced-data">
        <h3>🔍 Data Sources & Methodology</h3>
        <div className="no-data">
          <p>⚠️ No data sources information available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="section enhanced-data">
      <h3>🔍 Data Sources & Methodology</h3>
      
      {/* Methodology */}
      <div className="section">
        <h4>📋 Assessment Methodology</h4>
        <div className="details-grid">
          <div className="detail-item">
            <strong>Method:</strong> {dataSources.methodology || 'Comprehensive modern slavery risk analysis combining country and industry level risks with company mitigation efforts'}
          </div>
        </div>
      </div>

      {/* Primary Sources */}
      <div className="data-sources-grid">
        <div className="data-source-item">
          <h5>🌍 Primary Data Sources</h5>
          <div className="source-list">
            {dataSources.primary_sources?.map((source, index) => (
              <div key={index} className="source-item">
                <div className="data-quality-indicators">
                  <span className="quality-indicator high">✓ Verified</span>
                  <span className="quality-indicator medium">📊 Quantitative</span>
                </div>
                <span className="source-name">{source}</span>
              </div>
            ))}
          </div>
        </div>

        {/* News Analysis */}
        {dataSources.news_analysis && (
          <div className="data-source-item">
            <h5>📰 News Sentiment Analysis</h5>
            <div className="news-stats">
              <div className="stat-item">
                <span className="stat-label">Articles Analyzed:</span>
                <span className="stat-value">{dataSources.news_analysis.articles_found}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Sentiment Score:</span>
                <span 
                  className="stat-value"
                  style={{color: getRiskColor(100 - dataSources.news_analysis.sentiment_score)}}
                >
                  {dataSources.news_analysis.sentiment_score}/100
                </span>
              </div>
            </div>
            {dataSources.news_analysis.recent_concerns && (
              <div className="recent-concerns">
                <h6>Recent Concerns Identified:</h6>
                <ul>
                  {dataSources.news_analysis.recent_concerns.map((concern, index) => (
                    <li key={index}>{concern}</li>
                  ))}
                </ul>
              </div>
            )}
            {dataSources.news_analysis.ai_analysis && (
              <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#e7f3ff', borderRadius: '4px' }}>
                <strong style={{ color: '#0056b3' }}>🤖 AI Analysis:</strong> {dataSources.news_analysis.ai_analysis}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Metadata */}
      <div className="assessment-metadata">
        <div className="metadata-item">
          <span className="metadata-label">Last Updated:</span>
          <span className="metadata-value">
            {new Date(dataSources.last_updated || new Date()).toLocaleString()}
          </span>
        </div>
      </div>
    </div>
  );
};

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
    }, 400);
    
    try {
      // Use the comprehensive backend endpoint
      const response = await fetch(`http://localhost:5000/assess?company=${encodeURIComponent(companyName.trim())}`);
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      
      const data = await response.json();
      console.log("Full results:", data);

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
      console.error('Assessment error:', err);
      clearInterval(progressInterval);
      setError('Failed to assess company. Please try again later.');
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
    <div className="App">
      <div className="container">
        <header className="header">
          <div className="brand-section">
            <div className="logo-line">
              <a 
                href="https://www.rosettasolutions.com.au" 
                target="_blank" 
                rel="noopener noreferrer"
                className="company-logo-link"
                style={{display: 'flex', alignItems: 'center', gap: '15px', textDecoration: 'none', color: 'inherit'}}
              >
                <img src="/rosetta-logo.png" alt="Rosetta Solutions Logo" className="company-logo" />
                <h2 className="company-name">Rosetta Solutions</h2>
              </a>
            </div>
            <div className="title-line">
              <h1 className="main-title">Modern Slavery Risk Assessment</h1>
            </div>
            <p className="subtitle">AI-Powered Analysis | Industry Benchmarking | Global Supply Chain Mapping</p>
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
                    <div className="circular-progress-container">
                      <svg className="circular-progress" width="32" height="32">
                        <circle 
                          cx="16" 
                          cy="16" 
                          r="14" 
                          stroke="rgba(255,255,255,0.3)" 
                          strokeWidth="2" 
                          fill="none"
                        />
                        <circle 
                          cx="16" 
                          cy="16" 
                          r="14" 
                          stroke="#ffffff" 
                          strokeWidth="2" 
                          fill="none"
                          strokeDasharray="87.96"
                          strokeDashoffset={87.96 - (87.96 * progress) / 100}
                          className="progress-circle"
                        />
                      </svg>
                      <div className="progress-percentage">{Math.round(progress)}%</div>
                    </div>
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
                <div className="header-buttons">
                  <button onClick={handleExport} className="export-button">
                    📊 Export Data
                  </button>
                  <button onClick={clearResults} className="clear-button">
                    New Assessment
                  </button>
                </div>
              </div>
              
              <div className="risk-overview">
                <div className="risk-card">
                  <h3>Overall Risk Level</h3>
                  <div 
                    className="risk-badge"
                    style={{ backgroundColor: getRiskColor(results.overall_risk_score) }}
                  >
                    {results.risk_level || 'Unknown'}
                  </div>
                </div>
                
                <div className="risk-card">
                  <h3>Risk Score</h3>
                  <div className="risk-score">
                    {Math.round(results.overall_risk_score) || 'N/A'}
                    <span className="score-max">/100</span>
                  </div>
                </div>
                
                <div className="risk-card">
                  <h3>Manufacturing Sites</h3>
                  <div className="risk-score">
                    {results.company_profile?.manufacturing_locations?.length || 0}
                  </div>
                </div>

                <div className="risk-card">
                  <h3>Countries</h3>
                  <div className="risk-score">
                    {results.company_profile?.countries_of_operation?.length || 0}
                  </div>
                </div>
              </div>

              {/* Tab Navigation */}
              <div className="tab-navigation">
                <button 
                  className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
                  onClick={() => setActiveTab('overview')}
                >
                  📊 Overview
                </button>
                <button 
                  className={`tab-button ${activeTab === 'modern-slavery' ? 'active' : ''}`}
                  onClick={() => setActiveTab('modern-slavery')}
                >
                  🎯 Modern Slavery
                </button>
                <button 
                  className={`tab-button ${activeTab === 'risk-factors' ? 'active' : ''}`}
                  onClick={() => setActiveTab('risk-factors')}
                >
                  ⚠️ Risk Factors
                </button>
                <button 
                  className={`tab-button ${activeTab === 'mapping' ? 'active' : ''}`}
                  onClick={() => setActiveTab('mapping')}
                >
                  🗺️ Global Map
                </button>
                <button 
                  className={`tab-button ${activeTab === 'data-sources' ? 'active' : ''}`}
                  onClick={() => setActiveTab('data-sources')}
                >
                  📋 Data Sources
                </button>
                <button 
                  className={`tab-button ${activeTab === 'mitigation' ? 'active' : ''}`}
                  onClick={() => setActiveTab('mitigation')}
                >
                  🛡️ Mitigation
                </button>
              </div>

              {/* Tab Content */}
              <div className="tab-content">
                {activeTab === 'overview' && (
                  <>
                    {/* Company Profile Overview */}
                    <div className="section">
                      <h3>🏢 Company Profile</h3>
                      <div className="details-grid">
                        <div className="detail-item">
                          <strong>Industry:</strong> {capitalizeFirst(results.company_profile?.industry || 'N/A')}
                        </div>
                        <div className="detail-item">
                          <strong>Revenue:</strong> ${results.company_profile?.revenue_billions || 'N/A'}B
                        </div>
                        <div className="detail-item">
                          <strong>Countries:</strong> {results.company_profile?.countries_of_operation?.length || 0}
                        </div>
                        <div className="detail-item">
                          <strong>Transparency Score:</strong> {results.company_profile?.supply_chain_transparency_score || 'N/A'}/100
                        </div>
                      </div>
                    </div>

                    {/* Risk Breakdown */}
                    <div className="section">
                      <h3>📊 Risk Breakdown</h3>
                      <div className="details-grid">
                        <div className="detail-item">
                          <strong>Inherent Risk:</strong> {Math.round(results.risk_breakdown?.inherent_risk || 0)}/100
                        </div>
                        <div className="detail-item">
                          <strong>Industry Risk:</strong> {Math.round(results.risk_breakdown?.industry_risk || 0)}/100
                        </div>
                        <div className="detail-item">
                          <strong>Mitigation Score:</strong> {Math.round(results.risk_breakdown?.mitigation_score || 0)}/100
                        </div>
                        <div className="detail-item">
                          <strong>Final Risk:</strong> {Math.round(results.overall_risk_score || 0)}/100
                        </div>
                      </div>
                    </div>

                    {/* Countries of Operation */}
                    {results.company_profile?.countries_of_operation && (
                      <div className="section">
                        <h3>🌍 Countries of Operation</h3>
                        <div className="risk-groups-container">
                          {results.company_profile.countries_of_operation.map((country, index) => {
                            const countryRisk = results.risk_breakdown?.country_risks?.[country] || 50;
                            return (
                              <div key={index} className="risk-group" style={{ border: `3px solid ${getRiskColor(countryRisk)}` }}>
                                <h5 className="risk-group-title" style={{ backgroundColor: getRiskColor(countryRisk), color: 'white' }}>
                                  🌍 {country}
                                  <span style={{ float: 'right', fontSize: '0.8em' }}>Score: {Math.round(countryRisk)}</span>
                                </h5>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Recommendations */}
                    {results.mitigation_measures?.recommendations && (
                      <div className="section">
                        <h3>💡 Recommendations</h3>
                        <ul className="recommendations-list">
                          {results.mitigation_measures.recommendations.map((rec, index) => (
                            <li key={index} className="recommendation-item">
                              <span className="rec-text">{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    <div className="section">
                      <h3>📊 Assessment Details</h3>
                      <div className="details-grid">
                        <div className="detail-item">
                          <strong>Assessment Type:</strong> Comprehensive Modern Slavery Risk Analysis
                        </div>
                        <div className="detail-item">
                          <strong>Date:</strong> {new Date(results.assessment_date).toLocaleDateString()}
                        </div>
                        <div className="detail-item">
                          <strong>Confidence Level:</strong> High
                        </div>
                        <div className="detail-item">
                          <strong>Backend Version:</strong> 3.0 Enhanced
                        </div>
                      </div>
                    </div>
                  </>
                )}

                {/* Modern Slavery Tab */}
                {activeTab === 'modern-slavery' && (
                  <>
                    <ModernSlaveryRisk modernSlaveryData={results.modern_slavery_risk} />
                    
                    <div className="section">
                      <h3>📊 Assessment Details</h3>
                      <div className="details-grid">
                        <div className="detail-item">
                          <strong>Assessment Source:</strong> Comprehensive Risk Model v3.0
                        </div>
                        <div className="detail-item">
                          <strong>Data Quality:</strong> AI Enhanced with 80+ Countries
                        </div>
                        <div className="detail-item">
                          <strong>Calculation Method:</strong> Country + Industry + Mitigation Analysis
                        </div>
                        <div className="detail-item">
                          <strong>Last Updated:</strong> {new Date(results.assessment_date).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </>
                )}

                {/* Risk Factors Tab */}
                {activeTab === 'risk-factors' && (
                  <>
                    <RiskFactorsGrouped riskFactors={results.risk_factors} />
                    
                    <div className="section">
                      <h3>📊 Assessment Details</h3>
                      <div className="details-grid">
                        <div className="detail-item">
                          <strong>Risk Analysis:</strong> Multi-dimensional Assessment
                        </div>
                        <div className="detail-item">
                          <strong>Data Sources:</strong> {results.data_sources?.primary_sources?.length || 0} Primary Sources
                        </div>
                        <div className="detail-item">
                          <strong>AI Analysis:</strong> Shortened responses (1-2 sentences)
                        </div>
                        <div className="detail-item">
                          <strong>Coverage:</strong> Global and Industry-specific
                        </div>
                      </div>
                    </div>
                  </>
                )}

                {/* Global Mapping Tab */}
                {activeTab === 'mapping' && (
                  <>
                    <ManufacturingMap locations={results.company_profile?.manufacturing_locations} />
                    
                    <div className="section">
                      <h3>📊 Assessment Details</h3>
                      <div className="details-grid">
                        <div className="detail-item">
                          <strong>Locations Mapped:</strong> {results.company_profile?.manufacturing_locations?.length || 0}
                        </div>
                        <div className="detail-item">
                          <strong>Coverage:</strong> Global Supply Chain Analysis
                        </div>
                        <div className="detail-item">
                          <strong>Risk Assessment:</strong> Country-level Modern Slavery Risk
                        </div>
                        <div className="detail-item">
                          <strong>Map Technology:</strong> React-Leaflet with OpenStreetMap
                        </div>
                      </div>
                    </div>
                  </>
                )}

                {/* Data Sources Tab */}
                {activeTab === 'data-sources' && (
                  <>
                    <EnhancedDataSources dataSources={results.data_sources} />
                    
                    <div className="section">
                      <h3>📊 Assessment Details</h3>
                      <div className="details-grid">
                        <div className="detail-item">
                          <strong>Primary Sources:</strong> {results.data_sources?.primary_sources?.length || 0} Verified Sources
                        </div>
                        <div className="detail-item">
                          <strong>News Analysis:</strong> {results.data_sources?.news_analysis?.articles_found || 0} Articles Analyzed
                        </div>
                        <div className="detail-item">
                          <strong>AI Enhancement:</strong> GPT-powered Risk Analysis
                        </div>
                        <div className="detail-item">
                          <strong>Data Quality:</strong> High Confidence Level
                        </div>
                      </div>
                    </div>
                  </>
                )}

                {/* Mitigation Tab */}
                {activeTab === 'mitigation' && (
                  <>
                    <div className="section">
                      <h3>🛡️ Current Policies</h3>
                      {results.mitigation_measures?.current_policies ? (
                        <div className="details-grid">
                          {Object.entries(results.mitigation_measures.current_policies).map(([policy, value]) => (
                            <div key={policy} className="detail-item">
                              <strong>{capitalizeFirst(policy.replace('_', ' '))}:</strong> 
                              <span className={`policy-status ${value ? 'active' : 'inactive'}`} style={{ marginLeft: '8px' }}>
                                {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : value}
                              </span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="no-data">No policy information available</div>
                      )}
                    </div>

                    <div className="section">
                      <h3>📈 Effectiveness Score</h3>
                      <div className="details-grid">
                        <div className="detail-item">
                          <strong>Overall Effectiveness:</strong> {results.mitigation_measures?.effectiveness_score || 'N/A'}/100
                        </div>
                      </div>
                    </div>

                    {results.mitigation_measures?.recommendations && (
                      <div className="section">
                        <h3>💡 Recommendations</h3>
                        <ul className="recommendations-list">
                          {results.mitigation_measures.recommendations.map((rec, index) => (
                            <li key={index} className="recommendation-item">
                              <span className="rec-text">{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    <div className="section">
                      <h3>📊 Assessment Details</h3>
                      <div className="details-grid">
                        <div className="detail-item">
                          <strong>Policy Analysis:</strong> Comprehensive Review
                        </div>
                        <div className="detail-item">
                          <strong>Effectiveness Calculation:</strong> Multi-factor Assessment
                        </div>
                        <div className="detail-item">
                          <strong>Recommendations:</strong> Tailored to Risk Profile
                        </div>
                        <div className="detail-item">
                          <strong>Implementation:</strong> Prioritized by Impact
                        </div>
                      </div>
                    </div>
                  </>
                )}
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