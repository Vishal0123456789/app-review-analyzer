import React, { useState, useEffect } from 'react';
import './App.css';

// Get API URL from environment - for Vercel, it's injected into HTML meta tag
const getApiUrl = (): string => {
  // Try to get from meta tag (set in index.html)
  const metaTag = document.querySelector('meta[name="api-url"]');
  if (metaTag?.getAttribute('content')) {
    return metaTag.getAttribute('content') || '';
  }
  // Fallback to localStorage if available
  if (typeof localStorage !== 'undefined') {
    return localStorage.getItem('VITE_API_URL') || 'http://localhost:8000';
  }
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiUrl();

interface PulseData {
  start_date: string;
  end_date: string;
  top_themes: Array<{
    theme: string;
    summary_bullets?: string[];
  }>;
  quotes: string[];
  action_ideas: string[];
  note_markdown: string;
}

interface AnalyzeResponse {
  status: 'success' | 'error';
  message: string;
  window_days?: number;
  pulse_file_name?: string;
  pulse_data?: PulseData;
  detail?: {
    message: string;
  };
}

function App() {
  const [windowDays, setWindowDays] = useState(28);
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<PulseData | null>(null);
  const [pulseFileName, setPulseFileName] = useState('');

  const validateForm = (): boolean => {
    if (windowDays < 7 || windowDays > 56) {
      setError('Window must be between 7 and 56 days.');
      return false;
    }
    return true;
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setResult(null);

    if (!validateForm()) return;

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          window_days: windowDays,
          email: email || '',
        }),
      });

      const data: AnalyzeResponse = await response.json();

      if (!response.ok) {
        const errorMsg = data.detail?.message || data.message || 'Analysis failed';
        setError(errorMsg);
        setLoading(false);
        return;
      }

      if (data.status === 'success' && data.pulse_data) {
        setResult(data.pulse_data);
        setPulseFileName(data.pulse_file_name || '');
        setError('');
      } else {
        setError(data.message || 'Unknown error');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Network error');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!pulseFileName) {
      setError('No file to download');
      return;
    }

    const url = `${API_BASE_URL}/api/download-pulse?file=${encodeURIComponent(pulseFileName)}`;
    const a = document.createElement('a');
    a.href = url;
    a.download = pulseFileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const statusMessage = loading
    ? 'Running analysis… this may take a moment.'
    : result
      ? 'Analysis completed. Emails sent.'
      : error
        ? `Error: ${error}`
        : 'Select a window and click Analyze.';

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-blue-50/40 text-slate-900 font-body py-6 px-4 md:px-6">
      {/* Mobile Sticky Header */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-b border-gray-200 shadow-sm">
        <div className="px-4 py-4 flex flex-col items-center justify-center text-center">
          <h2 className="text-xl font-bold text-gray-900">🚀 Groww App Review Insights Analyzer</h2>
          <p className="text-sm text-gray-600 mt-2 leading-relaxed">Your shortcut to understanding Groww users — fast, clear, and actionable.</p>
        </div>
      </div>
      
      {/* Hero Section with top padding for mobile (hidden on mobile, shown on desktop) */}
      <div className="hidden md:block max-w-3xl mx-auto mb-12 md:mb-16">
        <div className="text-center">
          <h1 className="text-3xl md:text-5xl font-extrabold text-gray-900 mb-3 md:mb-4">
            🚀 Groww App Review Insights Analyzer
          </h1>
          <p className="text-base md:text-xl text-gray-600 leading-relaxed">
            Your shortcut to understanding Groww users — fast, clear, and actionable.
          </p>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="max-w-6xl mx-auto pt-32 md:pt-0">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-10 items-start md:h-screen md:overflow-hidden">
          {/* Form Card - Left Column */}
          <div className="md:col-span-1 flex justify-center md:justify-start">
            <div className="w-full md:w-[480px] bg-white rounded-3xl shadow-2xl shadow-gray-300/50 border border-gray-200 p-8 md:p-10 sticky top-6">
              <form onSubmit={handleAnalyze} className="space-y-5">
                {/* Window Days Input */}
                <div>
                  <label htmlFor="windowDays" className="block text-sm font-medium text-gray-700 mb-2">
                    Analysis Window
                    <span className="text-gray-400 font-normal ml-1 text-sm">(Pick how far back we should fetch Groww reviews)</span>
                  </label>
                  <input
                    id="windowDays"
                    type="number"
                    min="7"
                    max="56"
                    value={windowDays}
                    onChange={(e) => {
                      setWindowDays(parseInt(e.target.value) || 28);
                      setError('');
                    }}
                    className="w-full h-12 px-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-gray-900 placeholder-gray-500"
                  />
                  <p className="text-xs text-gray-500 mt-2">7–56 days</p>
                </div>

                {/* Email Input */}
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Your Email
                  </label>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      setError('');
                    }}
                    placeholder="you@example.com"
                    className="w-full h-12 px-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-gray-900 placeholder-gray-500"
                  />
                  <p className="text-xs text-gray-500 mt-2">Optional</p>
                </div>

                {/* Analyze Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full h-12 rounded-xl font-semibold transition-all ${
                    loading
                      ? 'bg-gray-400 text-white cursor-not-allowed'
                      : 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:scale-[1.02] hover:shadow-xl active:scale-95'
                  }`}
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <span className="inline-block h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                      Analyzing…
                    </span>
                  ) : (
                    'Analyze'
                  )}
                </button>
              </form>

              {/* Status Message */}
              {error || loading || result ? (
                <div
                  className={`mt-4 p-3 rounded-lg text-sm font-medium ${
                    loading
                      ? 'bg-blue-50 border border-blue-200 text-blue-700'
                      : result
                        ? 'bg-green-50 border border-green-200 text-green-700'
                        : 'bg-red-50 border border-red-200 text-red-700'
                  }`}
                >
                  {loading
                    ? '⚡ It may take a few minutes — good insights need a moment.'
                    : result
                      ? '✨ Analysis completed. Emails sent.'
                      : `Error: ${error}`}
                </div>
              ) : (
                <div className="mt-4 p-3 rounded-lg text-sm font-medium bg-gray-50 border border-gray-200 text-gray-600">
                  🔎 Select a window and click Analyze.
                </div>
              )}
            </div>
          </div>

          {/* Results Card - Right Column */}
          {result && (
            <div className="md:col-span-1 md:overflow-y-auto md:h-screen md:pr-2">
              <div className="bg-white rounded-3xl shadow-2xl shadow-gray-300/50 border border-gray-200 p-8 md:p-10 space-y-6">
                {/* Download Button */}
                {pulseFileName && (
                  <button
                    onClick={handleDownload}
                    className="w-full h-11 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-semibold hover:scale-[1.02] hover:shadow-xl active:scale-95 transition-all"
                  >
                    📥 Download Weekly Pulse (JSON)
                  </button>
                )}

                {/* Analysis Window */}
                <div className="border-l-4 border-blue-500 pl-4 py-2">
                  <p className="text-sm text-gray-600">
                    <span className="font-semibold text-gray-900">📅 Analysis Window</span>
                  </p>
                  <p className="text-base text-gray-700 mt-1">
                    {result.start_date} → {result.end_date}
                  </p>
                </div>

                {/* Top Themes */}
                {result.top_themes && result.top_themes.length > 0 && (
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-4">🎯 Top Themes</h3>
                    <ul className="space-y-3">
                      {result.top_themes.map((item, idx) => (
                        <li key={idx} className="text-gray-700">
                          <div className="font-semibold text-gray-900 mb-1">
                            {typeof item === 'string' ? item : item.theme}
                          </div>
                          {item.summary_bullets && item.summary_bullets.length > 0 && (
                            <ul className="ml-4 space-y-1">
                              {item.summary_bullets.slice(0, 2).map((bullet, bidx) => (
                                <li key={bidx} className="text-sm text-gray-600 leading-relaxed">
                                  • {bullet}
                                </li>
                              ))}
                            </ul>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Quotes */}
                {result.quotes && result.quotes.length > 0 && (
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-4">💬 Real User Quotes</h3>
                    <ul className="space-y-3">
                      {result.quotes.slice(0, 3).map((quote, idx) => (
                        <li key={idx} className="text-gray-700 italic border-l-2 border-gray-300 pl-4">
                          "{quote}"
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Action Ideas */}
                {result.action_ideas && result.action_ideas.length > 0 && (
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-4">🛠️ Action Ideas</h3>
                    <ul className="space-y-3">
                      {result.action_ideas.slice(0, 3).map((idea, idx) => (
                        <li key={idx} className="text-gray-700 flex gap-3">
                          <span className="text-blue-500 font-bold flex-shrink-0 mt-0.5">✓</span>
                          <span>{idea}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Detailed Notes */}
                {result.note_markdown && (
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-4">📋 Detailed Report</h3>
                    <div className="bg-gray-50 p-5 rounded-xl border border-gray-200 space-y-4">
                      {result.note_markdown.split('\n\n').map((paragraph, idx) => {
                        const lines = paragraph.split('\n');
                        const firstLine = lines[0];
                        
                        // Handle markdown headings (##)
                        if (firstLine.startsWith('##')) {
                          return (
                            <h4 key={idx} className="font-bold text-gray-900 mb-3 mt-4 text-base">
                              {firstLine.replace(/^#+\s*/, '')}
                            </h4>
                          );
                        }
                        
                        // Handle theme sections (bold title followed by bullets)
                        const isBoldedTheme = firstLine && !firstLine.startsWith('*') && !firstLine.startsWith('#');
                        if (isBoldedTheme && lines.length > 1 && lines[1]?.trim().startsWith('*')) {
                          return (
                            <div key={idx} className="mt-4">
                              <h5 className="font-semibold text-gray-900 mb-3 text-sm">
                                {firstLine.replace(/\*\*/g, '').trim()}
                              </h5>
                              <ul className="space-y-2 ml-4">
                                {lines.map((line, i) => (
                                  line.trim().startsWith('*') && (
                                    <li key={i} className="list-disc text-sm text-gray-700">
                                      {line.replace(/^[*\-]\s*/, '').replace(/\*\*/g, '').trim()}
                                    </li>
                                  )
                                ))}
                              </ul>
                            </div>
                          );
                        }
                        
                        // Handle bullet lists
                        if (firstLine.startsWith('*')) {
                          return (
                            <ul key={idx} className="space-y-2 ml-4">
                              {lines.map((line, i) => (
                                line.trim() && (
                                  <li key={i} className="list-disc text-sm text-gray-700">
                                    {line.replace(/^[*\-]\s*/, '').replace(/\*\*/g, '').trim()}
                                  </li>
                                )
                              ))}
                            </ul>
                          );
                        }
                        
                        // Handle regular paragraphs
                        return (
                          <p key={idx} className="text-sm text-gray-800 leading-relaxed">
                            {paragraph.replace(/\*\*/g, '').trim()}
                          </p>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
