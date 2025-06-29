import React, { useState } from 'react';
import './App.css';

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
    ['Data Sources:', results.data_sources ? Object.values(results.data_sources).reduce((a, b) => a + b, 0) : 0],
    [''],
    ['Modern Slavery Risk Details:'],
  ];

  if (results.modern_slavery_risk) {
    overviewData.push(['Modern Slavery Score:', `${results.modern_slavery_risk.final_risk_score}/100`]);
    overviewData.push(['Risk Category:', results.modern_slavery_risk.risk_category]);
    overviewData.push(['Inherent Risk:', `${results.modern_slavery_risk.inherent_risk?.inherent_score || 'N/A'}/100`]);
    overviewData.push(['Residual Risk:', `${results.modern_slavery_risk.residual_risk?.residual_score || 'N/A'}/100`]);
    overviewData.push(['Data Source:', results.modern_slavery_risk.residual_risk?.data_source || 'Unknown']);
  }

  overviewData.push([''], ['Key Findings:']);
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

  // Modern Slavery Risk Sheet
  if (results.modern_slavery_risk) {
    const modernSlaveryData = [
      ['Modern Slavery Risk Analysis'],
      ['Final Risk Score:', `${results.modern_slavery_risk.final_risk_score}/100`],
      ['Risk Category:', results.modern_slavery_risk.risk_category],
      ['Calculation Method:', results.modern_slavery_risk.calculation_method || 'N/A'],
      [''],
      ['Inherent Risk Breakdown:'],
      ['Total Inherent Score:', `${results.modern_slavery_risk.inherent_risk?.inherent_score || 'N/A'}/100`],
    ];

    if (results.modern_slavery_risk.inherent_risk?.components) {
      Object.entries(results.modern_slavery_risk.inherent_risk.components).forEach(([component, value]) => {
        modernSlaveryData.push([capitalizeFirst(component.replace(/_/g, ' ')) + ':', value]);
      });
    }

    modernSlaveryData.push([''], ['Residual Risk (Mitigation):']);
    modernSlaveryData.push(['Statement Quality Score:', `${results.modern_slavery_risk.residual_risk?.residual_score || 'N/A'}/100`]);
    modernSlaveryData.push(['Has Statement:', results.modern_slavery_risk.residual_risk?.has_statement ? 'Yes' : 'No']);
    modernSlaveryData.push(['Data Source:', results.modern_slavery_risk.residual_risk?.data_source || 'Unknown']);

    workbookData.push({ name: 'Modern Slavery Risk', data: modernSlaveryData });
  }

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

// NEW: Modern Slavery Risk Component (using your existing CSS classes)
const ModernSlaveryRisk = ({ modernSlaveryData }) => {
  if (!modernSlaveryData) return (
    <div className="section">
      <div className="no-data">
        <p>🎯 Modern slavery risk data not available</p>
      </div>
    </div>
  );


  const getRiskColor = (score) => {
    if (score >= 75) return '#dc3545';
    if (score >= 60) return '#fd7e14';
    if (score >= 40) return '#ffc107';
    if (score >= 25) return '#28a745';
    return '#20c997';
  };

  return (
    <div className="section">
      <h3>🎯 Modern Slavery Risk Assessment</h3>
      
      {/* Risk Score Overview using your existing CSS grid structure */}
      <div className="risk-overview">
        <div className="risk-card">
          <h3>Final Risk Score</h3>
          <div className="risk-score" style={{ color: getRiskColor(final_risk_score) }}>
            {final_risk_score}
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
          <h3>Inherent Risk</h3>
          <div className="risk-score">
            {inherent_risk?.inherent_score || 'N/A'}
            <span className="score-max">/100</span>
          </div>
        </div>

        <div className="risk-card">
          <h3>Residual Risk</h3>
          <div className="risk-score">
            {residual_risk?.residual_score || 'N/A'}
            <span className="score-max">/100</span>
          </div>
        </div>
      </div>

      {/* Risk Breakdown Details */}
      <div className="details-grid">
        <div className="detail-item">
          <strong>Assessment Method:</strong> Comprehensive modern slavery risk analysis combining country and industry level risks with company mitigation efforts
        </div>
        <div className="detail-item">
          <strong>Statement Found:</strong> {residual_risk?.has_statement ? 'Yes' : 'No'}
        </div>
        <div className="detail-item">
          <strong>Data Source:</strong> {residual_risk?.data_source || 'Unknown'}
        </div>
        {data_coverage?.ai_enhanced && (
          <div className="detail-item">
            <strong>AI Enhanced:</strong> Yes
          </div>
        )}
      </div>

      {/* Inherent Risk Components */}
      {inherent_risk?.components && (
        <div className="section">
          <h4>Inherent Risk Components</h4>
          <div className="details-grid">
            {Object.entries(inherent_risk.components).map(([component, value]) => (
              <div key={component} className="detail-item">
                <strong>{capitalizeFirst(component.replace(/_/g, ' '))}:</strong> {value}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// ENHANCED: Risk Factors Grouped Component with Modern Slavery grouping (keeping your CSS)
const RiskFactorsGrouped = ({ riskFactors }) => {
  if (!riskFactors || riskFactors.length === 0) return null;

  // Enhanced grouping with Modern Slavery category
  const groupRiskFactors = (factors) => {
    const groups = {
      modern_slavery: [],
      economic: [],
      operational: [],
      geographic: [],
      governance: [],
      business_model: []
    };

    factors.forEach(factor => {
      const factorText = factor.factor || factor;
      const lowerText = factorText.toLowerCase();

      // Modern slavery specific factors
      if (lowerText.includes('modern slavery') || 
          lowerText.includes('forced labor') || 
          lowerText.includes('inherent risk') || 
          lowerText.includes('residual risk') ||
          lowerText.includes('tip tier') ||
          lowerText.includes('gsi prevalence')) {
        groups.modern_slavery.push(factor);
      }
      // Economic factors  
      else if (lowerText.includes('economic') || 
               lowerText.includes('gdp') || 
               lowerText.includes('vulnerability') ||
               lowerText.includes('financial')) {
        groups.economic.push(factor);
      }
      // Operational factors
      else if (lowerText.includes('supply chain') || 
               lowerText.includes('manufacturing') || 
               lowerText.includes('labor') || 
               lowerText.includes('worker') || 
               lowerText.includes('operational') ||
               lowerText.includes('production')) {
        groups.operational.push(factor);
      }
      // Geographic factors
      else if (lowerText.includes('country') || 
               lowerText.includes('geographic') || 
               lowerText.includes('region')) {
        groups.geographic.push(factor);
      }
      // Governance factors
      else if (lowerText.includes('policy') || 
               lowerText.includes('governance') || 
               lowerText.includes('compliance') || 
               lowerText.includes('transparency') ||
               lowerText.includes('audit') ||
               lowerText.includes('reporting')) {
        groups.governance.push(factor);
      } else {
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
                
                {/* Enhanced AI analysis fields */}
                {riskFactor.vulnerability_analysis && (
                  <div style={{fontSize: '0.9rem', color: '#555', marginTop: '8px'}}>
                    <strong>🤖 AI Vulnerability Analysis:</strong> {riskFactor.vulnerability_analysis}
                  </div>
                )}

                {riskFactor.business_implications && (
                  <div style={{fontSize: '0.9rem', color: '#555', marginTop: '8px'}}>
                    <strong>💼 Business Implications:</strong> {riskFactor.business_implications}
                  </div>
                )}

                {riskFactor.specific_risks && riskFactor.specific_risks.length > 0 && (
                  <div style={{fontSize: '0.9rem', color: '#555', marginTop: '8px'}}>
                    <strong>⚠️ Specific Risks:</strong>
                    <ul style={{margin: '4px 0', paddingLeft: '20px'}}>
                      {riskFactor.specific_risks.map((risk, i) => (
                        <li key={i}>{risk}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {riskFactor.recommended_actions && riskFactor.recommended_actions.length > 0 && (
                  <div style={{fontSize: '0.9rem', color: '#555', marginTop: '8px'}}>
                    <strong>✅ Recommended Actions:</strong>
                    <ul style={{margin: '4px 0', paddingLeft: '20px'}}>
                      {riskFactor.recommended_actions.map((action, i) => (
                        <li key={i}>{action}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {riskFactor.data_source && (
                  <div style={{fontSize: '0.8rem', color: '#888', marginTop: '8px', fontStyle: 'italic'}}>
                    Source: {riskFactor.data_source}
                  </div>
                )}
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
        {renderRiskGroup("🎯 Modern Slavery Factors", "🎯", groupedFactors.modern_slavery, "modern_slavery")}
        {renderRiskGroup("💰 Economic Risks", "💰", groupedFactors.economic, "economic")}
        {renderRiskGroup("Operational Risks", "🏭", groupedFactors.operational, "operational")}
        {renderRiskGroup("Geographic Risks", "🌍", groupedFactors.geographic, "geographic")}
        {renderRiskGroup("Governance Risks", "📋", groupedFactors.governance, "governance")}
        {renderRiskGroup("Business Model Risks", "💼", groupedFactors.business_model, "business_model")}
      </div>
    </div>
  );
};

// IMPROVED: Industry Benchmarking Component (keeping your existing CSS classes)
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
        {/* Industry Header using your existing CSS */}
        <div className="industry-header-card">
          <div className="industry-title">
            <h4>Industry: {benchmarkData.matched_industry}</h4>
            <span className="data-quality-badge">
              Data Quality: {benchmarkData.data_quality || 'High'}
            </span>
          </div>
        </div>

        {/* Score Comparison using your existing CSS */}
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

        {/* Performance Summary using your existing CSS */}
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

        {/* Key Insights using your existing CSS */}
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

        {/* Industry Details Grid using your existing CSS */}
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

        {/* Metadata Footer using your existing CSS */}
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

// Manufacturing Locations Component (Card-based view using your existing CSS)
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

  const getRiskLevel = (riskScore) => {
    if (riskScore > 75) return 'High';
    if (riskScore > 50) return 'Medium';
    return 'Low';
  };

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

      {/* Location Cards Grid using your existing CSS structure */}
      <div className="risk-groups-container">
        {locations.map((location, index) => {
          const riskScore = location.country_risk_score || 50;
          const riskColor = getRiskColor(riskScore);
          const riskLevel = getRiskLevel(riskScore);

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
                      <div><strong>Risk Score:</strong> {riskScore}/100</div>
                    </div>
                    <div style={{ marginBottom: '10px' }}>
                      <strong>Products/Services:</strong> {capitalizeFirst(location.products || 'Various')}
                    </div>
                    
                    {location.workforce_size && (
                      <div style={{ marginBottom: '10px' }}>
                        <strong>Workforce Size:</strong> {location.workforce_size}
                      </div>
                    )}

                    {location.coordinates && (
                      <div style={{ marginBottom: '10px', fontSize: '0.9em', color: '#666' }}>
                        <strong>Coordinates:</strong> {location.coordinates.lat.toFixed(4)}, {location.coordinates.lng.toFixed(4)}
                      </div>
                    )}

                    {/* Modern slavery indicators if available */}
                    {location.modern_slavery_indicators && location.modern_slavery_indicators.length > 0 && (
                      <div style={{ 
                        marginTop: '10px', 
                        padding: '10px', 
                        backgroundColor: '#fff3cd', 
                        borderRadius: '4px',
                        border: '1px solid #ffeaa7'
                      }}>
                        <strong style={{ color: '#856404' }}>⚠️ Modern Slavery Risk Indicators:</strong>
                        <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                          {location.modern_slavery_indicators.map((indicator, i) => (
                            <li key={i} style={{ fontSize: '0.9em', color: '#856404' }}>{indicator}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {location.labor_risk_level && (
                      <div style={{ marginTop: '10px' }}>
                        <strong>Labor Risk Level:</strong> 
                        <span className="severity-badge" style={{ 
                          backgroundColor: location.labor_risk_level === 'high' ? '#dc3545' : 
                                          location.labor_risk_level === 'medium' ? '#ffc107' : '#28a745',
                          color: 'white',
                          marginLeft: '8px'
                        }}>
                          {capitalizeFirst(location.labor_risk_level)}
                        </span>
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
                            <strong>Country Risk Level:</strong> {capitalizeFirst(location.country_risk_level) || 'Unknown'}
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

      {/* Risk Level Legend using your existing CSS */}
      <div className="section">
        <h5>🗺️ Risk Level Legend:</h5>
        <div className="details-grid">
          <div className="detail-item" style={{ borderLeft: '4px solid #dc3545' }}>
            <strong>High Risk (75+)</strong> - Significant modern slavery concerns
          </div>
          <div className="detail-item" style={{ borderLeft: '4px solid #ffc107' }}>
            <strong>Medium Risk (50-75)</strong> - Moderate risk factors present
          </div>
          <div className="detail-item" style={{ borderLeft: '4px solid #28a745' }}>
            <strong>Low Risk (&lt;50)</strong> - Lower risk environment
          </div>
        </div>
      </div>
    </div>
  );
};

// ENHANCED: Enhanced Data Sources Component with better AI analysis display (keeping your CSS)
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
        {/* Economic Indicators with AI analysis */}
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
            </div>
          )}
        </div>

        {/* Enhanced News Analysis */}
        <div className="data-source-item">
          <h5>📰 Enhanced News Analysis</h5>
          {hasNewsData ? (
            <div>
              <div style={{
                marginBottom: '15px',
                padding: '10px',
                backgroundColor: '#e7f3ff',
                borderRadius: '4px',
                border: '1px solid #b3d9ff'
              }}>
                <div style={{fontSize: '0.9em', color: '#0056b3', fontWeight: '600'}}>
                  📈 Found {newsData.length} news articles
                </div>
                <div style={{fontSize: '0.8em', color: '#0056b3', marginTop: '4px'}}>
                  Analyzing labor practices and supply chain coverage
                </div>
              </div>
              
              {newsData.slice(0, 3).map((article, index) => (
                <div key={index} style={{
                  marginBottom: '12px',
                  padding: '12px',
                  backgroundColor: '#f8f9fa',
                  borderRadius: '6px',
                  border: '1px solid #e9ecef'
                }}>
                  <div style={{fontSize: '0.9em', fontWeight: '600', color: '#333', marginBottom: '4px'}}>
                    {article.title || 'News Article'}
                  </div>
                  <div style={{fontSize: '0.8em', color: '#666'}}>
                    {article.domain || 'News Source'}
                    {article.tone !== undefined && (
                      <span style={{
                        marginLeft: '8px',
                        padding: '2px 6px',
                        borderRadius: '3px',
                        backgroundColor: article.tone > 0 ? '#d4edda' : article.tone < 0 ? '#f8d7da' : '#e2e3e5',
                        color: article.tone > 0 ? '#155724' : article.tone < 0 ? '#721c24' : '#383d41',
                        fontSize: '0.7em'
                      }}>
                        {article.tone > 0 ? 'Positive' : article.tone < 0 ? 'Negative' : 'Neutral'}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
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
                📰 Enhanced news analysis ready
              </p>
              <small style={{color: '#999', fontSize: '0.8em', textAlign: 'center', display: 'block', marginTop: '8px'}}>
                Premium news sources integration for comprehensive labor rights coverage
              </small>
            </div>
          )}
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
            </div>
          )}
        </div>
      </div>

      {/* API Risk Factors with AI Analysis */}
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
                
                {/* Enhanced AI analysis fields */}
                {factor.vulnerability_analysis && (
                  <div style={{marginTop: '8px', padding: '8px', backgroundColor: '#e7f3ff', borderRadius: '4px'}}>
                    <strong style={{color: '#0056b3'}}>🤖 AI Analysis:</strong> {factor.vulnerability_analysis}
                  </div>
                )}

                {factor.business_implications && (
                  <div style={{marginTop: '8px', padding: '8px', backgroundColor: '#fff3cd', borderRadius: '4px'}}>
                    <strong style={{color: '#856404'}}>💼 Business Impact:</strong> {factor.business_implications}
                  </div>
                )}

                {factor.specific_risks && factor.specific_risks.length > 0 && (
                  <div style={{marginTop: '8px'}}>
                    <strong>⚠️ Specific Risks:</strong>
                    <ul style={{margin: '4px 0', paddingLeft: '20px'}}>
                      {factor.specific_risks.map((risk, i) => (
                        <li key={i} style={{fontSize: '0.9em'}}>{risk}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {factor.recommended_actions && factor.recommended_actions.length > 0 && (
                  <div style={{marginTop: '8px'}}>
                    <strong>✅ Recommended Actions:</strong>
                    <ul style={{margin: '4px 0', paddingLeft: '20px'}}>
                      {factor.recommended_actions.map((action, i) => (
                        <li key={i} style={{fontSize: '0.9em'}}>{action}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {factor.data_source && (
                  <div style={{fontSize: '0.8em', color: '#888', marginTop: '8px', fontStyle: 'italic'}}>
                    Source: {factor.data_source}
                  </div>
                )}
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

              {/* Tab Navigation - keeping your exact original */}
              <div className="tab-navigation">
                <button 
                  className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
                  onClick={() => setActiveTab('overview')}
                >
                  Overview
                </button>
                <button 
                  className={`tab-button ${activeTab === 'modern-slavery' ? 'active' : ''}`}
                  onClick={() => setActiveTab('modern-slavery')}
                >
                  🎯 Modern Slavery
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

              {/* Tab Content - keeping your exact original structure */}
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

                    {/* ENHANCED: Use the new grouped risk factors component */}
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

                {/* NEW: Modern Slavery Tab */}
                {activeTab === 'modern-slavery' && (
                  <>
                    <ModernSlaveryRisk modernSlaveryData={results.modern_slavery_risk} />
                    
                    <div className="section">
                      <h3>📊 Assessment Details</h3>
                      <div className="details-grid">
                        <div className="detail-item">
                          <strong>Assessment Source:</strong> Sophisticated Risk Model
                        </div>
                        <div className="detail-item">
                          <strong>Data Quality:</strong> {results.modern_slavery_risk?.data_coverage?.ai_enhanced ? 'AI Enhanced' : 'High'}
                        </div>
                        <div className="detail-item">
                          <strong>Calculation Method:</strong> Inherent + Residual Risk
                        </div>
                        <div className="detail-item">
                          <strong>Last Updated:</strong> {results.assessment_date || new Date().toLocaleDateString()}
                        </div>
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
                          <strong>News Articles:</strong> {results.enhanced_data?.enhanced_news?.length || 0} analyzed
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