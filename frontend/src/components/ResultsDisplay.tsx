import React, { useState } from 'react';

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

interface ResultsDisplayProps {
  result: ScreeningResult;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ result }) => {
  const [coverLetter, setCoverLetter] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string | null>(null);
  const [question, setQuestion] = useState('');
  const [chatLog, setChatLog] = useState<{ role: string; content: string }[]>([]);
  const [busy, setBusy] = useState<'cover' | 'improve' | 'chat' | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runAction = async (
    kind: 'cover' | 'improve',
    endpoint: string,
    onDone: (text: string) => void
  ) => {
    setBusy(kind);
    setError(null);
    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ result_id: result.id }),
      });
      if (!response.ok) throw new Error('Request failed');
      const data = await response.json();
      onDone(data.cover_letter || data.suggestions);
    } catch (err) {
      setError('Something went wrong generating that. Please try again.');
    } finally {
      setBusy(null);
    }
  };

  const askQuestion = async () => {
    if (!question.trim()) return;
    const newLog = [...chatLog, { role: 'user', content: question }];
    setChatLog(newLog);
    setQuestion('');
    setBusy('chat');
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          result_id: result.id,
          question,
          history: newLog,
        }),
      });
      if (!response.ok) throw new Error('Request failed');
      const data = await response.json();
      setChatLog([...newLog, { role: 'assistant', content: data.answer }]);
    } catch (err) {
      setError('Something went wrong answering that. Please try again.');
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="detailed-results">
      <div className="score-section">
        <div className="score-circle">{result.score}</div>
        <p className="score-percentage">{result.match_percentage}% match</p>
        <span className={`result-status status-${result.status}`}>{result.status}</span>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${result.match_percentage}%` }} />
        </div>
      </div>

      <div className="section">
        <h3 className="section-title">Feedback</h3>
        <p>{result.feedback}</p>
      </div>

      {result.strengths.length > 0 && (
        <div className="section strengths">
          <h3 className="section-title">Strengths</h3>
          {result.strengths.map((s, i) => (
            <div className="list-item" key={i}>
              <span className="list-item-icon">✅</span>
              <span>{s}</span>
            </div>
          ))}
        </div>
      )}

      {result.improvements.length > 0 && (
        <div className="section improvements">
          <h3 className="section-title">Areas to Improve</h3>
          {result.improvements.map((s, i) => (
            <div className="list-item" key={i}>
              <span className="list-item-icon">⚠️</span>
              <span>{s}</span>
            </div>
          ))}
        </div>
      )}

      {error && <div className="alert alert-error">{error}</div>}

      <div className="section">
        <h3 className="section-title">AI Tools</h3>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
          <button
            className="btn btn-secondary btn-sm"
            disabled={busy !== null}
            onClick={() => runAction('cover', '/api/cover-letter', setCoverLetter)}
          >
            {busy === 'cover' ? 'Writing…' : '✉️ Generate Cover Letter'}
          </button>
          <button
            className="btn btn-secondary btn-sm"
            disabled={busy !== null}
            onClick={() => runAction('improve', '/api/improve-resume', setSuggestions)}
          >
            {busy === 'improve' ? 'Thinking…' : '💡 Resume Suggestions'}
          </button>
        </div>

        {coverLetter && (
          <div className="alert alert-info" style={{ whiteSpace: 'pre-wrap' }}>{coverLetter}</div>
        )}
        {suggestions && (
          <div className="alert alert-info" style={{ whiteSpace: 'pre-wrap' }}>{suggestions}</div>
        )}

        <h4 className="section-title" style={{ marginTop: '1.5rem' }}>Ask about this candidate</h4>
        {chatLog.map((m, i) => (
          <div className="list-item" key={i}>
            <span className="list-item-icon">{m.role === 'user' ? '🙋' : '🤖'}</span>
            <span>{m.content}</span>
          </div>
        ))}
        <div className="form-group" style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="text"
            placeholder="e.g. Does this candidate have Kubernetes experience?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && askQuestion()}
          />
          <button className="btn btn-primary btn-sm" disabled={busy !== null} onClick={askQuestion}>
            {busy === 'chat' ? '…' : 'Ask'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultsDisplay;
