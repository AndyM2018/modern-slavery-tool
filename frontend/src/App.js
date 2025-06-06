// ✅ FINAL FIXED VERSION OF APP.JS
// All tab content is now consistently wrapped in a `.container`
// This ensures consistent width and padding across all pages

import React, { useState } from 'react';
import IndustryBenchmarking from './IndustryBenchmarking';
import ManufacturingMap from './ManufacturingMap';
import EnhancedDataSources from './EnhancedDataSources';
import './App.css';

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
        headers: { 'Content-Type': 'application/json' },
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
        })
      });
      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError('Failed to assess company. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    if (!level) return '#6c757d';
    switch (level.toLowerCase()) {
      case 'low': return '#28a745';
      case 'medium': return '#ffc107';
      case 'high': return '#dc3545';
      default: return '#6c757d';
    }
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>Modern Slavery Risk Assessment</h1>
          <p>Powered by Rosetta Solutions</p>
        </header>

        <form onSubmit={handleSubmit} className="assessment-form">
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="Enter company name"
            disabled={loading}
          />
          <button type="submit" disabled={loading || !companyName.trim()}>
            {loading ? 'Analyzing...' : 'Assess Company'}
          </button>
        </form>

        {error && <div className="alert error">{error}</div>}

        {results && (
          <div className="results">
            <div className="tabs">
              <button onClick={() => setActiveTab('overview')} className={activeTab === 'overview' ? 'active' : ''}>Overview</button>
              <button onClick={() => setActiveTab('benchmarking')} className={activeTab === 'benchmarking' ? 'active' : ''}>Benchmarking</button>
              <button onClick={() => setActiveTab('mapping')} className={activeTab === 'mapping' ? 'active' : ''}>Mapping</button>
              <button onClick={() => setActiveTab('enhanced')} className={activeTab === 'enhanced' ? 'active' : ''}>Enhanced</button>
            </div>

            <div className="tab-content">
              <div className="container">
                {activeTab === 'overview' && (
                  <>
                    <h2>Risk Level</h2>
                    <div className="badge" style={{ backgroundColor: getRiskColor(results.overall_risk_level) }}>
                      {results.overall_risk_level?.toUpperCase() || 'UNKNOWN'}
                    </div>
                    {/* Add additional overview content here */}
                  </>
                )}

                {activeTab === 'benchmarking' && <IndustryBenchmarking benchmarkData={results.industry_benchmarking} />}

                {activeTab === 'mapping' && (
                  <ManufacturingMap
                    mapData={results.supply_chain_map}
                    locations={results.manufacturing_locations}
                  />
                )}

                {activeTab === 'enhanced' && <EnhancedDataSources enhancedData={results.enhanced_data} />}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
