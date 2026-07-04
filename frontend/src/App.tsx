import React, { useState } from 'react';
import './App.css';
import ResumeUploader from './components/ResumeUploader';
//import ResultsDisplay from './components/ResultsDisplay';
import Dashboard from './components/Dashboard';
import Navigation from './components/Navigation';

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

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'upload' | 'dashboard'>('upload');
  const [results, setResults] = useState<ScreeningResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedResult, setSelectedResult] = useState<ScreeningResult | null>(null);

  const handleScreeningComplete = (newResult: ScreeningResult) => {
    setResults([newResult, ...results]);
    setSelectedResult(newResult);
    setActiveTab('dashboard');
  };

  const handleDeleteResult = (id: string) => {
    setResults(results.filter(r => r.id !== id));
    if (selectedResult?.id === id) {
      setSelectedResult(null);
    }
  };

  return (
    <div className="app">
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="main-content">
        <div className="container">
          {activeTab === 'upload' ? (
            <ResumeUploader
              onScreeningComplete={handleScreeningComplete}
              isLoading={isLoading}
              setIsLoading={setIsLoading}
            />
          ) : (
            <Dashboard
              results={results}
              selectedResult={selectedResult}
              setSelectedResult={setSelectedResult}
              onDeleteResult={handleDeleteResult}
            />
          )}
        </div>
      </main>
      <footer className="footer">
        <p>Jetski SmartHire AI © 2024 | Intelligent Resume Screening Platform</p>
      </footer>
    </div>
  );
};

export default App;
