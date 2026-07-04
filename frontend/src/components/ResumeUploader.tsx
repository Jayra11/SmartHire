import React, { useState, useRef } from 'react';

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

interface ResumeUploaderProps {
  onScreeningComplete: (result: ScreeningResult) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ResumeUploader: React.FC<ResumeUploaderProps> = ({
  onScreeningComplete,
  isLoading,
  setIsLoading,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  ];

  const handleFileSelect = (selected: File | undefined | null) => {
    setError(null);
    if (!selected) return;
    if (!allowedTypes.includes(selected.type)) {
      setError('Please upload a PDF or Word document.');
      return;
    }
    setFile(selected);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files?.[0]);
  };

  const handleSubmit = async () => {
    setError(null);

    if (!file) {
      setError('Please select a resume file first.');
      return;
    }
    if (!jobDescription.trim()) {
      setError('Please paste a job description.');
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('job_description', jobDescription);

      const response = await fetch(`${API_URL}/api/screen`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const detail = await response.json().catch(() => null);
        throw new Error(detail?.detail || 'Failed to screen resume.');
      }

      const result: ScreeningResult = await response.json();
      onScreeningComplete(result);

      setFile(null);
      setJobDescription('');
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="card">
        <div className="loading">
          <div className="spinner" />
          <p className="loading-text">Analyzing resume with Gemini…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="card-title">Screen a Resume</h2>

      {error && <div className="alert alert-error">{error}</div>}

      <div
        className={`upload-area${isDragging ? ' dragover' : ''}`}
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        <div className="upload-icon">📄</div>
        <p className="upload-text">
          {file ? file.name : 'Drag & drop a resume here, or click to browse'}
        </p>
        <p className="upload-subtext">PDF or Word (.doc, .docx) — max 10MB</p>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.doc,.docx"
          style={{ display: 'none' }}
          onChange={(e) => handleFileSelect(e.target.files?.[0])}
        />
      </div>

      <div className="form-group" style={{ marginTop: '1.5rem' }}>
        <label htmlFor="job-description">Job Description</label>
        <textarea
          id="job-description"
          rows={8}
          placeholder="Paste the job description here..."
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
        />
      </div>

      <button className="btn btn-primary btn-block" onClick={handleSubmit}>
        Screen Resume
      </button>
    </div>
  );
};

export default ResumeUploader;
