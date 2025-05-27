import React, { useState } from 'react';
import './App.css';

function App() {
  const [companyName, setCompanyName] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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
      const response = await fetch('http://localhost:5000/assess', {
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
            risk_threshold: 'medium'
          }
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      
      const data = await response.json();
      console.log("Full results:", data); // Debug line to see all data
      console.log("Risk factors:", data.risk_factors); // Debug line for risk factors
      setResults(data);
    } catch (err) {
      console.error('Assessment error:', err);
      setError('Failed to assess company. Make sure your backend is running on port 5000.');
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
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>🛡️ Modern Slavery Risk Assessment</h1>
          <p>AI-powered assessment tool for identifying modern slavery risks in your supply chain</p>
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
                    Assessing...
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
                  <h3>Risk Indicators</h3>
                  <div className="risk-score">
                    {results.risk_factors ? results.risk_factors.length : 0}
                  </div>
                </div>
              </div>
              
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

              <div className="section">
                <h3>📊 Assessment Details</h3>
                <div className="details-grid">
                  <div className="detail-item">
                    <strong>Assessment Type:</strong> Comprehensive
                  </div>
                  <div className="detail-item">
                    <strong>Date:</strong> {new Date().toLocaleDateString()}
                  </div>
                  <div className="detail-item">
                    <strong>Data Sources:</strong> News, Legal, Financial, Supply Chain
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
          <p>This tool provides risk assessment guidance. Professional legal advice should be sought for specific situations.</p>
        </footer>
      </div>
    </div>
  );
}

export default App;