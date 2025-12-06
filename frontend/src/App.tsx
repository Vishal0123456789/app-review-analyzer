import React, { useState } from 'react';
import './App.css';

// Get API URL from environment
const getApiUrl = (): string => {
  const metaTag = document.querySelector('meta[name="api-url"]');
  let url = '';
  
  if (metaTag?.getAttribute('content')) {
    url = metaTag.getAttribute('content') || '';
  } else if (typeof localStorage !== 'undefined') {
    url = localStorage.getItem('VITE_API_URL') || 'http://localhost:8000';
  } else {
    url = 'http://localhost:8000';
  }
  
  return url.endsWith('/') ? url.slice(0, -1) : url;
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

type AnalysisStep = 'idle' | 'fetching' | 'classifying' | 'generating' | 'delivery' | 'complete';

function App() {
  const [windowDays, setWindowDays] = useState(7);
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<PulseData | null>(null);
  const [pulseFileName, setPulseFileName] = useState('');
  const [currentStep, setCurrentStep] = useState<AnalysisStep>('idle');
  const [expandedTheme, setExpandedTheme] = useState<number | null>(null);

  const weeklyOptions = [
    { label: 'Last 1 week', days: 7 },
    { label: 'Last 2 weeks', days: 14 },
    { label: 'Last 3 weeks', days: 21 },
    { label: 'Last 4 weeks', days: 28 },
    { label: 'Last 5 weeks', days: 35 },
  ];

  const analysisSteps = [
    { id: 'fetching', label: 'Fetching Data', description: 'Collecting reviews from the Play Store...' },
    { id: 'classifying', label: 'Classifying Sentiment', description: 'Applying NLP to sort reviews into 5 core categories...' },
    { id: 'generating', label: 'Generating Pulse Report', description: 'Structuring key insights and actionable ideas...' },
    { id: 'delivery', label: 'Delivery & Finalizing', description: 'Formatting email and sending...' },
  ];

  const validateForm = (): boolean => {
    if (windowDays < 7 || windowDays > 35) {
      setError('Window must be between 7 and 35 days.');
      return false;
    }
    return true;
  };

  const getStepStatus = (stepId: string) => {
    const steps = ['fetching', 'classifying', 'generating', 'delivery'];
    const currentIndex = steps.indexOf(currentStep as any);
    const stepIndex = steps.indexOf(stepId as any);
    
    if (currentIndex > stepIndex) return 'complete';
    if (currentIndex === stepIndex) return 'active';
    return 'pending';
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setResult(null);
    setCurrentStep('fetching');

    if (!validateForm()) {
      setCurrentStep('idle');
      return;
    }

    setLoading(true);
    
    // ... existing code ...
    
    // Step progression with longer intervals and smarter timing
    const stepProgression = ['fetching', 'classifying', 'generating', 'delivery'];
    let stepIndex = 0;
    
    // Longer, more realistic step durations
    const stepDurations = [60000, 60000, 60000, 15000]; // milliseconds for each step (60s, 60s, 60s, 15s)
    let currentStepStartTime = Date.now();
    
    const stepInterval = setInterval(() => {
      if (stepIndex < stepProgression.length - 1) {
        const elapsedInStep = Date.now() - currentStepStartTime;
        if (elapsedInStep >= stepDurations[stepIndex]) {
          stepIndex++;
          setCurrentStep(stepProgression[stepIndex] as AnalysisStep);
          currentStepStartTime = Date.now();
        }
      }
    }, 1000); // Check every second instead of every 3 seconds

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1200000);
      
      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          window_days: windowDays,
          email: email || '',
        }),
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      clearInterval(stepInterval);

      const data: AnalyzeResponse = await response.json();

      if (!response.ok) {
        const errorMsg = data.detail?.message || data.message || 'Analysis failed';
        setError(errorMsg);
        setCurrentStep('idle');
        setLoading(false);
        return;
      }

      if (data.status === 'success' && data.pulse_data) {
        setResult(data.pulse_data);
        setPulseFileName(data.pulse_file_name || '');
        setCurrentStep('complete');
        setError('');
      } else {
        setError(data.message || 'Unknown error');
        setCurrentStep('idle');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Network error');
      setCurrentStep('idle');
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white py-6 px-4 md:px-6 relative overflow-hidden">
      {/* Geometric Background Pattern */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-10 w-72 h-72 bg-teal-500/10 rounded-full mix-blend-screen filter blur-3xl"></div>
        <div className="absolute -bottom-40 -right-40 w-80 h-80 bg-purple-500/10 rounded-full mix-blend-screen filter blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-blue-500/5 rounded-full mix-blend-screen filter blur-3xl"></div>
      </div>

      {/* Mobile Sticky Header */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-40 bg-slate-900/95 backdrop-blur-md border-b border-teal-500/30 shadow-lg">
        <div className="px-4 py-4 flex flex-col items-center justify-center text-center">
          <h2 className="text-xl font-bold text-white">Groww App Review Insights Analyzer</h2>
          <p className="text-xs text-teal-300 mt-1">The Real-Time Voice of Your Users</p>
        </div>
      </div>
      
      {/* Hero Section */}
      <div className="hidden md:block max-w-4xl mx-auto mb-16 relative z-10 pt-8">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-extrabold bg-gradient-to-r from-teal-400 via-cyan-300 to-blue-400 bg-clip-text text-transparent mb-4">
            Groww App Review Insights Analyzer
          </h1>
          <p className="text-lg md:text-xl text-slate-300 leading-relaxed">
            The Real-Time Voice of Your Users. Fast, Classified, and Actionable.
          </p>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="max-w-7xl mx-auto pt-24 md:pt-0 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-10 items-start md:h-screen md:overflow-hidden">
          {/* Form Card - Left Column */}
          <div className="md:col-span-1 flex justify-center md:justify-start">
            <div className="w-full md:w-[500px] bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl border border-teal-500/30 p-8 md:p-10 sticky top-6">
              <form onSubmit={handleAnalyze} className="space-y-6">
                {/* Window Days Dropdown */}
                <div>
                  <label htmlFor="windowDays" className="block text-sm font-semibold text-white mb-2">
                    Analysis Window
                  </label>
                  <select
                    id="windowDays"
                    value={windowDays}
                    onChange={(e) => {
                      setWindowDays(parseInt(e.target.value));
                      setError('');
                    }}
                    className="w-full h-12 px-4 border border-teal-500/50 bg-slate-800/50 rounded-xl focus:ring-2 focus:ring-teal-400 focus:border-transparent transition text-white placeholder-slate-400 font-medium"
                  >
                    {weeklyOptions.map((option) => (
                      <option key={option.days} value={option.days} className="bg-slate-900">
                        {option.label} ({option.days} days)
                      </option>
                    ))}
                  </select>
                </div>

                {/* Email Input */}
                <div>
                  <label htmlFor="email" className="block text-sm font-semibold text-white mb-2">
                    Your Email <span className="text-slate-400 font-normal">(Optional)</span>
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
                    className="w-full h-12 px-4 border border-teal-500/50 bg-slate-800/50 rounded-xl focus:ring-2 focus:ring-teal-400 focus:border-transparent transition text-white placeholder-slate-400"
                  />
                </div>

                {/* Analyze Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full h-12 rounded-xl font-bold text-white transition-all duration-300 ${
                    loading
                      ? 'bg-gradient-to-r from-slate-600 to-slate-700 cursor-not-allowed'
                      : 'bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-400 hover:to-cyan-400 hover:scale-[1.02] hover:shadow-lg hover:shadow-teal-500/50 active:scale-95'
                  }`}
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <span className="inline-block h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                      Analyzing
                    </span>
                  ) : (
                    'Analyze Reviews'
                  )}
                </button>
              </form>

              {/* Multi-Step Tracker */}
              {loading && (
                <div className="mt-8 space-y-4">
                  <div className="text-xs font-semibold text-teal-300 uppercase tracking-wider">Analysis Progress</div>
                  {analysisSteps.map((step, idx) => {
                    const status = getStepStatus(step.id);
                    return (
                      <div key={step.id} className="flex items-start gap-3">
                        <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs transition-all ${
                          status === 'complete' ? 'bg-teal-500 text-white' :
                          status === 'active' ? 'bg-cyan-400 text-slate-900 animate-pulse' :
                          'bg-slate-700 text-slate-400'
                        }`}>
                          {status === 'complete' ? '✓' : status === 'active' ? '⚙' : idx + 1}
                        </div>
                        <div className="flex-1">
                          <p className={`text-sm font-semibold ${
                            status === 'complete' || status === 'active' ? 'text-white' : 'text-slate-400'
                          }`}>
                            {step.label}
                          </p>
                          <p className={`text-xs mt-0.5 ${
                            status === 'active' ? 'text-cyan-300' : 'text-slate-500'
                          }`}>
                            {step.description}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Status Message */}
              {error || result || loading ? (
                <div
                  className={`mt-6 p-4 rounded-lg text-sm font-medium ${
                    loading
                      ? 'bg-cyan-500/20 border border-cyan-500/50 text-cyan-200'
                      : result
                      ? 'bg-teal-500/20 border border-teal-500/50 text-teal-200'
                      : 'bg-red-500/20 border border-red-500/50 text-red-200'
                  }`}
                >
                  {loading
                    ? '⚡ It may take a few minutes — good insights need a moment.'
                    : result
                    ? '✅ Analysis completed successfully.'
                    : `Error: ${error}`}
                </div>
              ) : (
                <div className="mt-6 p-4 rounded-lg text-sm font-medium bg-slate-700/50 border border-slate-600/50 text-slate-300">
                  🔎 Select a window and click Analyze.
                </div>
              )}
            </div>
          </div>

          {/* Results Card - Right Column */}
          {result && (
            <div className="md:col-span-1 md:overflow-y-auto md:h-screen md:pr-2">
              <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl border border-teal-500/30 p-8 md:p-10 space-y-8">
                {/* Download Button */}
                {pulseFileName && (
                  <button
                    onClick={handleDownload}
                    className="w-full h-11 bg-gradient-to-r from-cyan-500 to-teal-500 text-white rounded-xl font-semibold hover:scale-[1.02] hover:shadow-lg hover:shadow-cyan-500/50 active:scale-95 transition-all"
                  >
                    Download Pulse Report (JSON)
                  </button>
                )}

                {/* Analysis Window */}
                <div className="border-l-4 border-teal-400 pl-4 py-2">
                  <p className="text-xs text-teal-300 font-semibold uppercase tracking-wide">Analysis Window</p>
                  <p className="text-lg text-white font-bold mt-1">
                    {result.start_date} → {result.end_date}
                  </p>
                </div>

                {/* Executive Scorecard */}
                <div>
                  <p className="text-xs text-teal-300 font-semibold uppercase tracking-wide mb-4">Executive Scorecard</p>
                  <div className="grid grid-cols-3 gap-3">
                    <div className="bg-gradient-to-br from-purple-500/30 to-purple-600/20 border border-purple-500/50 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-purple-300">{result.top_themes?.length || 0}</p>
                      <p className="text-xs text-purple-200 mt-1">Key Themes</p>
                    </div>
                    <div className="bg-gradient-to-br from-cyan-500/30 to-cyan-600/20 border border-cyan-500/50 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-cyan-300">{result.quotes?.length || 0}</p>
                      <p className="text-xs text-cyan-200 mt-1">User Quotes</p>
                    </div>
                    <div className="bg-gradient-to-br from-teal-500/30 to-teal-600/20 border border-teal-500/50 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-teal-300">{result.action_ideas?.length || 0}</p>
                      <p className="text-xs text-teal-200 mt-1">Action Ideas</p>
                    </div>
                  </div>
                </div>

                {/* Top Themes - Collapsible Accordion */}
                {result.top_themes && result.top_themes.length > 0 && (
                  <div>
                    <p className="text-xs text-teal-300 font-semibold uppercase tracking-wide mb-3">Product Themes</p>
                    <div className="space-y-2">
                      {result.top_themes.map((item, idx) => (
                        <div key={idx} className="border border-teal-500/30 rounded-lg overflow-hidden">
                          <button
                            onClick={() => setExpandedTheme(expandedTheme === idx ? null : idx)}
                            className="w-full px-4 py-3 bg-slate-800/50 hover:bg-slate-800/70 transition text-left flex items-center justify-between group"
                          >
                            <span className="font-semibold text-white group-hover:text-teal-300 transition">
                              {typeof item === 'string' ? item : item.theme}
                            </span>
                            <span className={`text-teal-400 transition-transform ${
                              expandedTheme === idx ? 'rotate-180' : ''
                            }`}>
                              ▼
                            </span>
                          </button>
                          {expandedTheme === idx && item.summary_bullets && item.summary_bullets.length > 0 && (
                            <div className="px-4 py-3 bg-slate-900/30 border-t border-teal-500/20 space-y-2">
                              {item.summary_bullets.map((bullet, bidx) => (
                                <p key={bidx} className="text-sm text-slate-300 leading-relaxed flex gap-2">
                                  <span className="text-teal-400 flex-shrink-0">•</span>
                                  <span>{bullet}</span>
                                </p>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* User Quotes */}
                {result.quotes && result.quotes.length > 0 && (
                  <div>
                    <p className="text-xs text-teal-300 font-semibold uppercase tracking-wide mb-3">User Voice</p>
                    <div className="space-y-3">
                      {result.quotes.slice(0, 3).map((quote, idx) => (
                        <div key={idx} className="pl-4 border-l-2 border-cyan-400 text-slate-300 italic text-sm">
                          "{quote}"
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Action Ideas */}
                {result.action_ideas && result.action_ideas.length > 0 && (
                  <div>
                    <p className="text-xs text-teal-300 font-semibold uppercase tracking-wide mb-3">Recommended Actions</p>
                    <ul className="space-y-2">
                      {result.action_ideas.slice(0, 3).map((idea, idx) => (
                        <li key={idx} className="text-slate-300 flex gap-3 text-sm">
                          <span className="text-teal-400 flex-shrink-0 font-bold">✓</span>
                          <span>{idea}</span>
                        </li>
                      ))}
                    </ul>
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
