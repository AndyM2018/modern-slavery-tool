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

// Helper function to capitalize first letter
const capitalizeFirst = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
};

// Export functionality
const exportToExcel = (results, companyName) => {
  // Create workbook data
  const workbookData = [];

  // Overview Sheet
  const overviewData = [
    ['Modern Slavery Risk Assessment - Overview'],
    ['Company:', companyName],
    ['Assessment Date:', results.assessment_date || new Date().toLocaleDateString()],
    ['Overall Risk Level:', results.overall_risk_level || results.risk_level || 'Unknown'],
    ['Risk Score:', `${results.overall_risk_score || results.risk_score || 'N/A'}/100`],
    ['Manufacturing Sites:', results.manufacturing_locations ? results.manufacturing_locations.length : 0],
    ['Data Sources:', results.data_sources ? (results.data_sources.total_sources || Object.values(results.data_sources).filter(v => typeof v === 'number').reduce((a, b) => a + b, 0)) : 0],
    [''],
    ['Key Findings:'],
  ];

  if (results.key_findings && results.key_findings.length > 0) {
    results.key_findings.forEach((finding, index) => {
      const findingText = typeof finding === 'string' ? finding : finding.description;
      const severity = finding.severity || '';
      overviewData.push([`${index + 1}.`, findingText, severity]);
    });
  }

  overviewData.push([''], ['Risk Factors:']);
  if (results.risk_factors && results.risk_factors.length > 0) {
    results.risk_factors.forEach((factor, index) => {
      overviewData.push([`${index + 1}.`, factor.factor, factor.impact || '', factor.evidence || '']);
    });
  }

  overviewData.push([''], ['Recommendations:']);
  if (results.recommendations && results.recommendations.length > 0) {
    results.recommendations.forEach((rec, index) => {
      const recText = typeof rec === 'string' ? rec : rec.description || rec.title;
      const priority = rec.priority || '';
      overviewData.push([`${index + 1}.`, recText, priority]);
    });
  }

  workbookData.push({ name: 'Overview', data: overviewData });

  // Industry Benchmarking Sheet
  if (results.industry_benchmarking) {
    const benchData = [
      ['Industry Benchmarking'],
      ['Industry:', results.industry_benchmarking.matched_industry || ''],
      ['Company Score:', results.industry_benchmarking.company_score || ''],
      ['Industry Average:', results.industry_benchmarking.industry_average_score || ''],
      ['Performance vs Peers:', results.industry_benchmarking.performance_vs_peers || ''],
      [''],
      ['Peer Companies:'],
    ];

    if (results.industry_benchmarking.peer_companies) {
      results.industry_benchmarking.peer_companies.forEach((company, index) => {
        benchData.push([`${index + 1}.`, company]);
      });
    }

    benchData.push([''], ['Common Industry Risks:']);
    if (results.industry_benchmarking.industry_common_risks) {
      results.industry_benchmarking.industry_common_risks.forEach((risk, index) => {
        benchData.push([`${index + 1}.`, risk]);
      });
    }

    workbookData.push({ name: 'Industry Benchmarking', data: benchData });
  }

  // Manufacturing Locations Sheet
  if (results.manufacturing_locations && results.manufacturing_locations.length > 0) {
    const locationData = [
      ['Manufacturing Locations'],
      ['City', 'Country', 'Facility Type', 'Products', 'Risk Level', 'Risk Score', 'Latitude', 'Longitude'],
    ];

    results.manufacturing_locations.forEach(location => {
      locationData.push([
        location.city || '',
        location.country || '',
        location.facility_type || '',
        location.products || '',
        location.country_risk_level || '',
        location.country_risk_score || '',
        location.coordinates?.lat || '',
        location.coordinates?.lng || '',
      ]);
    });

    workbookData.push({ name: 'Manufacturing Locations', data: locationData });
  }

  // Enhanced Data Sheet
  if (results.enhanced_data) {
    const enhancedData = [
      ['Enhanced Data Analysis'],
      [''],
      ['Economic Indicators:'],
    ];

    if (results.enhanced_data.economic_indicators) {
      Object.entries(results.enhanced_data.economic_indicators).forEach(([country, data]) => {
        enhancedData.push([
          country,
          `GDP per capita: $${data.gdp_per_capita?.toLocaleString() || 'N/A'}`,
          `Economic risk: ${data.economic_risk_factor || 'N/A'}`
        ]);
      });
    }

    enhancedData.push([''], ['Data Sources Used:']);
    if (results.enhanced_data.data_sources_used) {
      results.enhanced_data.data_sources_used.forEach((source, index) => {
        enhancedData.push([`${index + 1}.`, source]);
      });
    }

    workbookData.push({ name: 'Enhanced Data', data: enhancedData });
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

// UPDATED: Risk Factors Grouped Component
const RiskFactorsGrouped = ({ riskFactors }) => {
  if (!riskFactors || riskFactors.length === 0) return null;

  // Group risk factors by category
  const groupRiskFactors = (factors) => {
    const groups = {
      operational: [],
      geographic: [],
      governance: [],
      business_model: []
    };

    factors.forEach(factor => {
      const factorText = factor.factor || factor;
      const lowerText = factorText.toLowerCase();

      // Categorize based on keywords
      if (lowerText.includes('supply chain') || 
          lowerText.includes('manufacturing') || 
          lowerText.includes('labor') || 
          lowerText.includes('worker') || 
          lowerText.includes('operational') ||
          lowerText.includes('production')) {
        groups.operational.push(factor);
      } else if (lowerText.includes('country') || 
                 lowerText.includes('geographic') || 
                 lowerText.includes('gdp') || 
                 lowerText.includes('economic') ||
                 lowerText.includes('region')) {
        groups.geographic.push(factor);
      } else if (lowerText.includes('policy') || 
                 lowerText.includes('governance') || 
                 lowerText.includes('compliance') || 
                 lowerText.includes('transparency') ||
                 lowerText.includes('audit') ||
                 lowerText.includes('reporting')) {
        groups.governance.push(factor);
      } else {
        // Default to business model risks
        groups.business_model.push(factor);
      }
    });

    return groups;
  };

  const groupedFactors = groupRiskFactors(riskFactors);

  const renderRiskGroup = (title, icon, factors, groupKey) => {
    if (factors.length === 0) return null;

    return (
      <div key={groupKey} className="risk-group">
        <h5 className="risk-group-title">
          {icon} {title}
        </h5>
        <div className="risk-group-items">
          {factors.map((riskFactor, index) => (
            <div key={index} className="finding-item">
              <div className="finding-text">
                <strong>{riskFactor.factor}</strong>
                <div style={{fontSize: '0.9rem', color: '#666', marginTop: '8px'}}>
                  <strong>Impact:</strong> <span className={`severity-badge ${riskFactor.impact}`}>
                    {riskFactor.impact?.toUpperCase()}
                  </span>
                </div>
                <div style={{fontSize: '0.9rem', color: '#555', marginTop: '5px'}}>
                  <strong>Evidence:</strong> {riskFactor.evidence}
                </div>
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
        {renderRiskGroup("Operational Risks", "🏭", groupedFactors.operational, "operational")}
        {renderRiskGroup("Geographic Risks", "🌍", groupedFactors.geographic, "geographic")}
        {renderRiskGroup("Governance Risks", "📋", groupedFactors.governance, "governance")}
        {renderRiskGroup("Business Model Risks", "💼", groupedFactors.business_model, "business_model")}
      </div>
    </div>
  );
};

// IMPROVED: Industry Benchmarking Component
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

  const getScoreBackgroundColor = (score) => {
    if (score <= 35) return '#d4edda';
    if (score <= 65) return '#fff3cd';
    return '#f8d7da';
  };

  return (
    <div className="section industry-benchmarking">
      <h3>📊 Industry Benchmarking</h3>
      
      <div className="benchmark-overview">
        {/* IMPROVED: Better Industry Header */}
        <div className="industry-header-card">
          <div className="industry-title">
            <h4>Industry: {benchmarkData.matched_industry}</h4>
            <span className="data-quality-badge">
              Data Quality: {benchmarkData.data_quality || 'High'}
            </span>
          </div>
        </div>

        {/* IMPROVED: Better Score Comparison Layout */}
        <div className="score-comparison-improved">
          <div className="score-card company-score-card">
            <div className="score-header">
              <span className="score-label">Company Score</span>
              <span className="score-trend">
                {benchmarkData.performance_vs_peers === 'above average' ? '📈' : '📉'}
              </span>
            </div>
            <div 
              className="score-display"
              style={{ 
                color: getScoreColor(benchmarkData.company_score),
                backgroundColor: getScoreBackgroundColor(benchmarkData.company_score)
              }}
            >
              {benchmarkData.company_score}
              <span className="score-suffix">/100</span>
            </div>
            <div className="score-description">Company Risk Score</div>
          </div>

          <div className="vs-divider">
            <span>VS</span>
          </div>

          <div className="score-card industry-score-card">
            <div className="score-header">
              <span className="score-label">Industry Average</span>
              <span className="score-trend">📊</span>
            </div>
            <div 
              className="score-display"
              style={{ 
                color: getScoreColor(benchmarkData.industry_average_score),
                backgroundColor: getScoreBackgroundColor(benchmarkData.industry_average_score)
              }}
            >
              {benchmarkData.industry_average_score}
              <span className="score-suffix">/100</span>
            </div>
            <div className="score-description">Industry Benchmark</div>
          </div>
        </div>

        {/* IMPROVED: Performance Summary Card */}
        <div className="performance-summary-card">
          <div className="performance-result">
            <span className="performance-label">Performance vs Peers:</span>
            <span 
              className="performance-value"
              style={{ color: getPerformanceColor(benchmarkData.performance_vs_peers) }}
            >
              {benchmarkData.performance_vs_peers.toUpperCase()}
            </span>
          </div>
          <div className="score-difference">
            <span className="difference-label">Score Difference:</span>
            <span className="difference-value">
              {Math.abs(benchmarkData.company_score - benchmarkData.industry_average_score)} points
            </span>
          </div>
          <div className="percentile-ranking">
            <span className="percentile-label">Industry Ranking:</span>
            <span className="percentile-value">
              {benchmarkData.percentile_ranking || 'Calculating...'}
            </span>
          </div>
        </div>

        {/* IMPROVED: Key Insights Card */}
        {benchmarkData.benchmark_insights && benchmarkData.benchmark_insights.length > 0 && (
          <div className="insights-card">
            <h5>🔍 Key Insights</h5>
            <ul className="insights-list">
              {benchmarkData.benchmark_insights.map((insight, index) => (
                <li key={index} className="insight-item">{insight}</li>
              ))}
            </ul>
          </div>
        )}

        {/* IMPROVED: Industry Details Grid */}
        <div className="industry-details-grid">
          <div className="detail-card peer-companies-card">
            <h5>🏢 Industry Peer Companies</h5>
            <div className="peer-companies-improved">
              {benchmarkData.peer_companies?.slice(0, 8).map((company, index) => (
                <span key={index} className="peer-company-tag">{company}</span>
              ))}
            </div>
          </div>

          <div className="detail-card risks-card">
            <h5>⚠️ Common Industry Risks</h5>
            <ul className="industry-risks-improved">
              {benchmarkData.industry_common_risks?.slice(0, 5).map((risk, index) => (
                <li key={index} className="risk-item">
                  <span className="risk-bullet">•</span>
                  {capitalizeFirst(risk)}
                </li>
              ))}
            </ul>
          </div>

          <div className="detail-card practices-card">
            <h5>✅ Industry Best Practices</h5>
            <ul className="best-practices-improved">
              {benchmarkData.industry_best_practices?.slice(0, 5).map((practice, index) => (
                <li key={index} className="practice-item">
                  <span className="practice-bullet">✓</span>
                  {capitalizeFirst(practice)}
                </li>
              ))}
            </ul>
          </div>

          <div className="detail-card regulatory-card">
            <h5>📋 Regulatory Focus Areas</h5>
            <div className="regulatory-tags">
              {benchmarkData.regulatory_focus?.slice(0, 4).map((regulation, index) => (
                <span key={index} className="regulatory-tag">{regulation}</span>
              ))}
            </div>
          </div>
        </div>

        {/* IMPROVED: Metadata Footer */}
        <div className="benchmark-metadata-improved">
          <div className="metadata-item">
            <span className="metadata-label">Last Updated:</span>
            <span className="metadata-value">{benchmarkData.last_updated}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Peer Companies Analyzed:</span>
            <span className="metadata-value">{benchmarkData.peer_companies?.length || 0}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Data Sources:</span>
            <span className="metadata-value">{benchmarkData.data_sources?.length || 3}</span>
          </div>
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
              <Popup 
                offset={[0, 10]}
                className="custom-popup"
                maxWidth={250}
                minWidth={200}
                autoPan={true}
                autoPanPadding={[10, 10]}
                closeButton={true}
                autoClose={false}
                closeOnEscapeKey={true}
              >
                <div className="location-popup">
                  <h4>{location.city}, {location.country}</h4>
                  <p><strong>Type:</strong> {capitalizeFirst(location.facility_type)}</p>
                  <p><strong>Products:</strong> {capitalizeFirst(location.products)}</p>
                  <p><strong>Risk Level:</strong> 
                    <span 
                      className="risk-badge"
                      style={{ backgroundColor: getRiskColor(location.country_risk_score || 50) }}
                    >
                      {capitalizeFirst(location.country_risk_level) || 'Unknown'}
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
        <div className="selected-location-details-fixed">
          <div className="location-details-header">
            <h5>Selected Location Details</h5>
            <button 
              className="close-details-btn"
              onClick={() => setSelectedLocation(null)}
              aria-label="Close details"
            >
              ×
            </button>
          </div>
          <div className="location-details-grid">
            <div><strong>Location:</strong> {selectedLocation.city}, {selectedLocation.country}</div>
            <div><strong>Facility Type:</strong> {capitalizeFirst(selectedLocation.facility_type)}</div>
            <div><strong>Risk Score:</strong> {selectedLocation.country_risk_score}/100</div>
            <div><strong>Products/Services:</strong> {capitalizeFirst(selectedLocation.products)}</div>
          </div>
        </div>
      )}
    </div>
  );
};

// UPDATED: Enhanced Data Sources Component
const EnhancedDataSources = ({ enhancedData }) => {
  // Debug logging to see what we're getting
  console.log("🔍 Enhanced Data Analysis:");
  console.log("  - Raw data:", enhancedData);
  console.log("  - Type:", typeof enhancedData);
  console.log("  - Keys:", enhancedData ? Object.keys(enhancedData) : "No data");

  if (!enhancedData) {
    return (
      <div className="section enhanced-data">
        <h3>🔍 Enhanced Data Analysis</h3>
        <div className="no-data">
          <p>⚠️ No enhanced data received from backend</p>
          <small>This could be due to API rate limits or data availability</small>
        </div>
      </div>
    );
  }

  // Safe data extraction with fallbacks
  const economicData = enhancedData.economic_indicators || {};
  const newsData = enhancedData.enhanced_news || [];
  const dataSources = enhancedData.data_sources_used || [];
  const apiRiskFactors = enhancedData.api_risk_factors || [];

  // Data availability checks
  const hasEconomicData = Object.keys(economicData).length > 0;
  const hasNewsData = Array.isArray(newsData) && newsData.length > 0;
  const hasDataSources = Array.isArray(dataSources) && dataSources.length > 0;
  const hasApiRiskFactors = Array.isArray(apiRiskFactors) && apiRiskFactors.length > 0;

  console.log("🔍 Data availability:", {
    hasEconomicData,
    hasNewsData, 
    hasDataSources,
    hasApiRiskFactors,
    economicDataCount: Object.keys(economicData).length,
    newsDataCount: newsData.length
  });

  return (
    <div className="section enhanced-data">
      <h3>🔍 Enhanced Data Analysis</h3>
      
      <div className="data-sources-grid">
        {/* UPDATED: Economic Indicators with improved formatting */}
        <div className="data-source-item">
          <h5>📊 Economic Indicators</h5>
          {hasEconomicData ? (
            <div className="economic-data">
              {Object.entries(economicData).map(([country, data]) => (
                <div key={country} className="country-economic-data">
                  <strong>{country}:</strong> GDP per capita ${data.gdp_per_capita?.toLocaleString() || 'N/A'}
                  <br />
                  <span className={`risk-indicator ${data.economic_risk_factor || 'unknown'}`}>
                    Economic Risk: {capitalizeFirst(data.economic_risk_factor || 'Unknown')}
                  </span>
                  {data.year && (
                    <>
                      <br />
                      <small style={{color: '#666'}}>Year: {data.year}</small>
                    </>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="no-data">
              <p>No economic data available</p>
              <small style={{color: '#999', fontSize: '0.8em'}}>
                Debug: economic_indicators type = {typeof enhancedData.economic_indicators}, 
                keys = {enhancedData.economic_indicators ? Object.keys(enhancedData.economic_indicators).length : 0}
              </small>
            </div>
          )}
        </div>

        {/* UPDATED: Enhanced News with "coming soon" message */}
        <div className="data-source-item">
          <h5>📰 Enhanced News Analysis</h5>
          <div className="news-coming-soon">
            <p style={{
              color: '#666', 
              fontStyle: 'italic',
              textAlign: 'center',
              padding: '20px',
              backgroundColor: '#f8f9fa',
              borderRadius: '4px',
              border: '1px dashed #ddd'
            }}>
              📰 Enhanced news analysis coming soon
            </p>
            <small style={{color: '#999', fontSize: '0.8em', textAlign: 'center', display: 'block', marginTop: '8px'}}>
              We're working on integrating premium news sources for more comprehensive labor rights coverage
            </small>
          </div>
        </div>

        {/* Data Sources */}
        <div className="data-source-item">
          <h5>🔗 Data Sources Used</h5>
          {hasDataSources ? (
            <ul className="data-sources-list">
              {dataSources.map((source, index) => (
                <li key={index}>{source}</li>
              ))}
            </ul>
          ) : (
            <div className="no-data">
              <p>No data sources information available</p>
              <small style={{color: '#999', fontSize: '0.8em'}}>
                Debug: data_sources_used type = {typeof enhancedData.data_sources_used}, 
                isArray = {Array.isArray(enhancedData.data_sources_used)}, 
                length = {enhancedData.data_sources_used?.length || 0}
              </small>
            </div>
          )}
        </div>
      </div>

      {/* API Risk Factors */}
      {hasApiRiskFactors && (
        <div className="api-risk-factors">
          <h5>⚠️ Additional Risk Factors from External Data</h5>
          <div className="api-factors-grid">
            {apiRiskFactors.map((factor, index) => (
              <div key={index} className="api-risk-factor">
                <div className="factor-header">
                  <strong>{factor.factor}</strong>
                  <span className={`impact-badge ${factor.impact || 'unknown'}`}>
                    {(factor.impact || 'unknown').toUpperCase()} IMPACT
                  </span>
                </div>
                <div className="factor-evidence">{factor.evidence}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Debug Section - Only show in development */}
      {process.env.NODE_ENV === 'development' && (
        <details style={{marginTop: '20px', fontSize: '12px', color: '#666'}}>
          <summary style={{cursor: 'pointer'}}>🔧 Debug: Raw Data Structure</summary>
          <pre style={{background: '#f8f9fa', padding: '10px', borderRadius: '4px', overflow: 'auto', maxHeight: '200px'}}>
            {JSON.stringify(enhancedData, null, 2)}
          </pre>
        </details>
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
                    style={{ backgroundColor: getRiskColor(results.overall_risk_level || results.risk_level) }}
                  >
                    {(results.overall_risk_level || results.risk_level || 'Unknown').toUpperCase()}
                  </div>
                </div>
                
                <div className="risk-card">
                  <h3>Control Effectiveness</h3>
                  <div className="risk-score">
                    {results.control_effectiveness ? 
                      `${results.control_effectiveness.risk_reduction_percentage}%` : 
                      'N/A'
                    }
                  </div>
                </div>
                
                <div className="risk-card">
                  <h3>Risk Reduction</h3>
                  <div className="risk-score">
                    {results.control_effectiveness ? 
                      `-${results.control_effectiveness.risk_reduction_points}pts` : 
                      'N/A'
                    }
                  </div>
                </div>

                <div className="risk-card">
                  <h3>Data Sources</h3>
                  <div className="risk-score">
                    {results.data_sources ? 
                      (results.data_sources.total_sources || 
                       Object.values(results.data_sources).filter(v => typeof v === 'number').reduce((a, b) => a + b, 0)) : 
                      0
                    }
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
                    {/* Control Effectiveness Section - UNCHANGED POSITION */}
                    {results.control_effectiveness && (
                      <div className="section">
                        <h3 className="risk-level-headline">🛡️ Risk Assessment Overview</h3>
                        
                        <div className="control-effectiveness-display">
                          <div className="inherent-risk-card">
                            <h4>Inherent Risk</h4>
                            <div className="risk-score-large">
                              {results.control_effectiveness.inherent_risk_score}
                            </div>
                            <p>{results.control_effectiveness.inherent_risk_level ? results.control_effectiveness.inherent_risk_level.toUpperCase() : 'HIGH'}</p>
                          </div>
                          
                          <div className="arrow-section">
                            <div className="arrow">→</div>
                            <div className="after-controls">
                              <span>After Controls</span>
                              <div className="risk-reduction-display">
                                -{results.control_effectiveness.risk_reduction_points}pts
                              </div>
                            </div>
                          </div>
                          
                          <div className="residual-risk-card">
                            <h4>Residual Risk</h4>
                            <div className="risk-score-large">
                              {results.control_effectiveness.final_risk_score}
                            </div>
                            <p>{results.overall_risk_level ? results.overall_risk_level.toUpperCase() : 'MEDIUM'}</p>
                          </div>
                        </div>
                        
                        <div className="control-effectiveness-bar">
                          <div className="control-label">🔧 Control Effectiveness</div>
                          <div className="effectiveness-percentage">
                            {results.control_effectiveness.risk_reduction_percentage}%
                          </div>
                          <div className="progress-bar-container">
                            <div 
                              className="progress-bar-fill"
                              style={{ 
                                width: `${results.control_effectiveness.risk_reduction_percentage}%`,
                                backgroundColor: '#007bff'
                              }}
                            ></div>
                          </div>
                          <div className="control-summary">
                            Controls have reduced risk by {results.control_effectiveness.risk_reduction_points} points ({results.control_effectiveness.risk_reduction_percentage}%)
                          </div>
                        </div>
                        
                        <div className="risk-factors-and-controls-container">
                          <div className="inherent-risk-factors">
                            <h5>Inherent Risk Factors:</h5>
                            <ul>
                              <li>Industry and operational risks</li>
                              <li>Geographic and supply chain exposure</li>
                              <li>Natural business model vulnerabilities</li>
                            </ul>
                          </div>
                          
                          <div className="risk-controls">
                            <h5>Risk Controls:</h5>
                            <ul>
                              <li>Policies and procedures</li>
                              <li>Due diligence and monitoring</li>
                              <li>Training and awareness programs</li>
                            </ul>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* NEW: Company Profile Section */}
                    {results.company_profile && (
                      <div className="section">
                        <h3>🏢 Company Profile</h3>
                        <div className="company-profile-grid">
                          <div className="profile-item">
                            <strong>Company Name:</strong>
                            <span>{results.company_profile.name || results.company_name}</span>
                          </div>
                          <div className="profile-item">
                            <strong>Industry:</strong>
                            <span>{results.company_profile.primary_industry || 'Unknown'}</span>
                          </div>
                          <div className="profile-item">
                            <strong>Headquarters:</strong>
                            <span>{results.company_profile.headquarters || 'Unknown'}</span>
                          </div>
                          <div className="profile-item">
                            <strong>Revenue:</strong>
                            <span>{results.company_profile.revenue || 'Unknown'}</span>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* NEW: Modern Slavery Summary */}
                    {results.modern_slavery_summary && (
                      <div className="section">
                        <h3>📋 Modern Slavery Risk Profile</h3>
                        <div className="slavery-summary-content">
                          <p>{results.modern_slavery_summary}</p>
                        </div>
                      </div>
                    )}

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

                    {/* UPDATED: Use the new grouped risk factors component */}
                    {results.risk_factors && results.risk_factors.length > 0 && (
                      <RiskFactorsGrouped riskFactors={results.risk_factors} />
                    )}
                    
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
                  </>
                )}

                {activeTab === 'benchmarking' && (
                  <>
                    <IndustryBenchmarking benchmarkData={results.industry_benchmarking} />
                    
                    <div className="section">
                      <h3>📊 Assessment Details</h3>
                      <div className="details-grid">
                        <div className="detail-item">
                          <strong>Benchmarking Source:</strong> Industry Database
                        </div>
                        <div className="detail-item">
                          <strong>Peer Companies:</strong> {results.industry_benchmarking?.peer_companies?.length || 0} analyzed
                        </div>
                        <div className="detail-item">
                          <strong>Data Quality:</strong> {results.industry_benchmarking?.data_quality || 'High'}
                        </div>
                        <div className="detail-item">
                          <strong>Last Updated:</strong> {results.industry_benchmarking?.last_updated || new Date().toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </>
                )}

                {activeTab === 'mapping' && (
                  <>
                    <ManufacturingMap 
                      mapData={results.supply_chain_map} 
                      locations={results.manufacturing_locations} 
                    />
                    
                    <div className="section">
                      <h3>📊 Assessment Details</h3>
                      <div className="details-grid">
                        <div className="detail-item">
                          <strong>Locations Mapped:</strong> {results.manufacturing_locations?.length || 0}
                        </div>
                        <div className="detail-item">
                          <strong>Coverage:</strong> Global Supply Chain
                        </div>
                        <div className="detail-item">
                          <strong>Risk Assessment:</strong> Country-level analysis
                        </div>
                        <div className="detail-item">
                          <strong>Map Data:</strong> OpenStreetMap
                        </div>
                      </div>
                    </div>
                  </>
                )}

                {activeTab === 'enhanced' && (
                  <>
                    <EnhancedDataSources enhancedData={results.enhanced_data} />
                    
                    <div className="section">
                      <h3>📊 Assessment Details</h3>
                      <div className="details-grid">
                        <div className="detail-item">
                          <strong>Data Sources:</strong> {results.enhanced_data?.data_sources_used?.length || 0} external APIs
                        </div>
                        <div className="detail-item">
                          <strong>News Articles:</strong> Enhanced analysis coming soon
                        </div>
                        <div className="detail-item">
                          <strong>Economic Indicators:</strong> {Object.keys(results.enhanced_data?.economic_indicators || {}).length} countries
                        </div>
                        <div className="detail-item">
                          <strong>Analysis Depth:</strong> Enhanced AI Processing
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