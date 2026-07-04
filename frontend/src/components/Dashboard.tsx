import React, { useState } from 'react';
import ResultsDisplay from './ResultsDisplay';

interface ScreeningResult {
  id: string;
  filename: string;
  score: number;
  status: string;
  feedback: string;
  strengths: string[];
  improvements: string[];
  timestamp: string;
  match_percentage: number;
}

interface DashboardProps {
  results: ScreeningResult[];
  selectedResult: ScreeningResult | null;
  setSelectedResult: (result: ScreeningResult | null) => void;
  onDeleteResult: (id: string) => void;
}

interface SearchMatch {
  id: string;
  filename: string;
  score: number;
  status: string;
  feedback: string;
  similarity: number;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const Dashboard: React.FC<DashboardProps> = ({
  results,
  selectedResult,
  setSelectedResult,
  onDeleteResult,
}) => {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchMatch[] | null>(null);
  const [searching, setSearching] = useState(false);

  const total = results.length;
  const passed = results.filter((r) => r.status === 'passed').length;
  const failed = results.filter((r) => r.status === 'failed').length;
  const avgScore = total ? Math.round(results.reduce((sum, r) => sum + r.score, 0) / total) : 0;

  const runSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    try {
      const response = await fetch(`${API_URL}/api/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 5 }),
      });
      if (!response.ok) throw new Error('Search failed');
      const data = await response.json();
      setSearchResults(data.results);
    } catch (err) {
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  if (total === 0) {
    return (
      <div className="card">
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h3 className="empty-title">No resumes screened yet</h3>
          <p className="empty-description">
            Head to the "Screen Resume" tab to analyze your first candidate.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="stats-section">
        <div className="stat-box">
          <div className="stat-value">{total}</div>
          <div className="stat-label">Total Screened</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{passed}</div>
          <div className="stat-label">Passed</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{failed}</div>
          <div className="stat-label">Failed</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{avgScore}</div>
          <div className="stat-label">Avg Score</div>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">🔎 Search Candidates (RAG)</h2>
        <div className="form-group" style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="text"
            placeholder="e.g. backend engineer with Kubernetes and AWS experience"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && runSearch()}
          />
          <button className="btn btn-primary" disabled={searching} onClick={runSearch}>
            {searching ? 'Searching…' : 'Search'}
          </button>
        </div>
        {searchResults && (
          <div className="results-container" style={{ marginTop: '1rem' }}>
            {searchResults.length === 0 && <p>No matches found.</p>}
            {searchResults.map((m) => (
              <div className="result-card" key={m.id}>
                <div className="result-score">{Math.round(m.similarity * 100)}%</div>
                <div className="result-filename">{m.filename}</div>
                <span className={`result-status status-${m.status}`}>{m.status}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <h2 className="card-title">Results</h2>
          <div className="results-container">
            {results.map((r) => (
              <div
                className="result-card"
                key={r.id}
                onClick={() => setSelectedResult(r)}
              >
                <div className="result-score">{r.score}</div>
                <div className="result-filename">{r.filename}</div>
                <span className={`result-status status-${r.status}`}>{r.status}</span>
                <button
                  className="btn btn-danger btn-sm btn-block"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteResult(r.id);
                  }}
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        </div>

        <div>
          {selectedResult ? (
            <ResultsDisplay result={selectedResult} />
          ) : (
            <div className="card">
              <div className="empty-state">
                <div className="empty-icon">👈</div>
                <h3 className="empty-title">Select a candidate</h3>
                <p className="empty-description">Click a result to see the full breakdown.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
