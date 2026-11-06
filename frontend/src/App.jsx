import { useState, useEffect } from "react";
import axios from "axios";

// Enable credentials so HttpOnly cookies are automatically sent with CORS requests
axios.defaults.withCredentials = true;

const API_BASE = "http://127.0.0.1:8000";

function App() {
  // Auth state
  const [currentUser, setCurrentUser] = useState(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState("login"); // 'login' | 'register'
  const [authForm, setAuthForm] = useState({ name: "", email: "", password: "" });
  const [authError, setAuthError] = useState("");
  const [authLoading, setAuthLoading] = useState(false);

  // Tab state
  const [activeTab, setActiveTab] = useState("analyzer"); // 'analyzer' | 'history'

  // Analysis state (Preserved from existing UI)
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [bullet, setBullet] = useState("");
  const [enhancedBullet, setEnhancedBullet] = useState("");

  // Resume Management state
  const [resumes, setResumes] = useState([]);
  const [selectedResumeId, setSelectedResumeId] = useState(null);
  const [expandedResumeId, setExpandedResumeId] = useState(null);
  const [resumeAnalyses, setResumeAnalyses] = useState({});
  const [analysesLoading, setAnalysesLoading] = useState(false);

  // Check auth status on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await axios.get(`${API_BASE}/auth/me`);
      setCurrentUser(response.data);
      fetchResumes();
    } catch {
      setCurrentUser(null);
    }
  };

  const fetchResumes = async () => {
    try {
      const response = await axios.get(`${API_BASE}/resumes`);
      setResumes(response.data);
    } catch (err) {
      console.error("Failed to load resumes", err);
    }
  };

  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    setAuthError("");
    setAuthLoading(true);

    try {
      if (authMode === "register") {
        const response = await axios.post(`${API_BASE}/auth/register`, {
          name: authForm.name,
          email: authForm.email,
          password: authForm.password
        });
        setCurrentUser(response.data.user);
      } else {
        const response = await axios.post(`${API_BASE}/auth/login`, {
          email: authForm.email,
          password: authForm.password
        });
        setCurrentUser(response.data.user);
      }

      setAuthModalOpen(false);
      setAuthForm({ name: "", email: "", password: "" });
      fetchResumes();
    } catch (err) {
      const msg = err.response?.data?.detail || "Authentication failed. Please check your credentials.";
      setAuthError(typeof msg === "string" ? msg : JSON.stringify(msg));
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API_BASE}/auth/logout`);
    } catch (err) {
      console.error(err);
    } finally {
      setCurrentUser(null);
      setResumes([]);
      setSelectedResumeId(null);
      setActiveTab("analyzer");
    }
  };

  const handleAnalyze = async () => {
    if (!jd.trim()) {
      alert("Please enter a Job Description");
      return;
    }

    if (selectedResumeId) {
      // Re-analyzing existing saved resume
      try {
        setLoading(true);
        const response = await axios.post(
          `${API_BASE}/resumes/${selectedResumeId}/analyze`,
          { jd }
        );
        // Normalize response shape to match existing UI
        const data = response.data;
        setResult({
          analysis_id: data.id,
          resume_id: data.resume_id,
          ats_score: data.final_ats_score,
          semantic_score: data.semantic_score,
          skill_match_score: data.skill_match_score,
          resume_skills: data.matched_skills || [],
          matched_skills: data.matched_skills || [],
          missing_skills: data.missing_skills || [],
          suggestions: data.suggestions || [],
          section_scores: data.section_scores || {},
          interview_questions: data.interview_questions || [],
          resume_preview: "Loaded from saved resume"
        });
        fetchResumes();
      } catch (error) {
        console.error(error);
        alert("Analysis failed. " + (error.response?.data?.detail || ""));
      } finally {
        setLoading(false);
      }
    } else {
      // Uploading file
      if (!file) {
        alert("Upload a resume PDF or select an existing resume");
        return;
      }

      const formData = new FormData();
      formData.append("file", file);
      formData.append("jd", jd);

      try {
        setLoading(true);
        const response = await axios.post(`${API_BASE}/analyze`, formData);
        setResult(response.data);
        if (currentUser) {
          fetchResumes();
        }
      } catch (error) {
        console.error(error);
        alert("Analysis failed. " + (error.response?.data?.detail || ""));
      } finally {
        setLoading(false);
      }
    }
  };

  const handleEnhance = async () => {
    if (!bullet.trim()) return;
    try {
      const response = await axios.post(`${API_BASE}/enhance-bullet`, { bullet });
      setEnhancedBullet(response.data.enhanced_bullet);
    } catch (error) {
      console.error(error);
      alert("Failed to enhance bullet point.");
    }
  };

  const handleDeleteResume = async (resumeId) => {
    if (!window.confirm("Are you sure you want to delete this resume and its analysis history?")) {
      return;
    }
    try {
      await axios.delete(`${API_BASE}/resumes/${resumeId}`);
      if (selectedResumeId === resumeId) {
        setSelectedResumeId(null);
      }
      fetchResumes();
    } catch (err) {
      console.error(err);
      alert("Failed to delete resume.");
    }
  };

  const handleToggleHistory = async (resumeId) => {
    if (expandedResumeId === resumeId) {
      setExpandedResumeId(null);
      return;
    }
    setExpandedResumeId(resumeId);
    setAnalysesLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/resumes/${resumeId}/analyses`);
      setResumeAnalyses((prev) => ({ ...prev, [resumeId]: res.data }));
    } catch (err) {
      console.error("Failed to load analyses", err);
    } finally {
      setAnalysesLoading(false);
    }
  };

  const handleLoadPastAnalysis = (past) => {
    setResult({
      analysis_id: past.id,
      resume_id: past.resume_id,
      ats_score: past.final_ats_score,
      semantic_score: past.semantic_score,
      skill_match_score: past.skill_match_score,
      resume_skills: past.matched_skills || [],
      matched_skills: past.matched_skills || [],
      missing_skills: past.missing_skills || [],
      suggestions: past.suggestions || [],
      section_scores: past.section_scores || {},
      interview_questions: past.interview_questions || [],
      resume_preview: "Loaded from past analysis report"
    });
    setJd(past.job_description || "");
    setActiveTab("analyzer");
    window.scrollTo({ top: 400, behavior: "smooth" });
  };

  const handleSelectResumeForAnalysis = (resume) => {
    setSelectedResumeId(resume.id);
    setFile(null);
    setActiveTab("analyzer");
    window.scrollTo({ top: 100, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-slate-100 p-4 md:p-8">
      <div className="max-w-5xl mx-auto">
        {/* Navigation & Header */}
        <header className="flex flex-col md:flex-row items-center justify-between gap-4 mb-8 bg-white p-6 rounded-2xl shadow-sm">
          <div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-slate-800 tracking-tight">
              AI Resume Analyzer
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              ATS Compatibility • Semantic Analysis • Gemini AI Enhancement
            </p>
          </div>

          <div className="flex items-center gap-3">
            {currentUser ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 bg-slate-100 py-1.5 px-3 rounded-full border border-slate-200">
                  <span className="w-7 h-7 rounded-full bg-blue-600 text-white font-bold flex items-center justify-center text-xs">
                    {currentUser.name.charAt(0).toUpperCase()}
                  </span>
                  <span className="text-sm font-medium text-slate-700">
                    {currentUser.name}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="text-sm text-red-600 hover:text-red-800 font-medium py-1 px-3 rounded-lg border border-red-200 hover:bg-red-50 transition"
                >
                  Logout
                </button>
              </div>
            ) : (
              <button
                onClick={() => {
                  setAuthMode("login");
                  setAuthError("");
                  setAuthModalOpen(true);
                }}
                className="bg-blue-600 text-white px-5 py-2.5 rounded-xl font-medium hover:bg-blue-700 shadow-sm transition"
              >
                Sign In / Register
              </button>
            )}
          </div>
        </header>

        {/* Navigation Tabs (when logged in) */}
        {currentUser && (
          <div className="flex gap-2 mb-6 border-b border-gray-200 pb-2">
            <button
              onClick={() => setActiveTab("analyzer")}
              className={`px-5 py-2.5 rounded-lg font-medium text-sm transition ${
                activeTab === "analyzer"
                  ? "bg-blue-600 text-white shadow-sm"
                  : "bg-white text-gray-600 hover:bg-gray-50"
              }`}
            >
              Analyze Resume
            </button>
            <button
              onClick={() => setActiveTab("history")}
              className={`px-5 py-2.5 rounded-lg font-medium text-sm transition flex items-center gap-2 ${
                activeTab === "history"
                  ? "bg-blue-600 text-white shadow-sm"
                  : "bg-white text-gray-600 hover:bg-gray-50"
              }`}
            >
              <span>Saved Resumes & History</span>
              {resumes.length > 0 && (
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  activeTab === "history" ? "bg-blue-800 text-white" : "bg-gray-200 text-gray-700"
                }`}>
                  {resumes.length}
                </span>
              )}
            </button>
          </div>
        )}

        {/* TAB 1: ANALYZER (Original UI + Enhanced Capabilities) */}
        {activeTab === "analyzer" && (
          <>
            <div className="bg-white p-6 rounded-xl shadow-md mb-8">
              {/* If user has saved resumes, allow choosing between Upload or Existing */}
              {currentUser && resumes.length > 0 && (
                <div className="mb-6 pb-4 border-b border-gray-100">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-semibold text-gray-700">
                      Choose Resume Source:
                    </span>
                    {selectedResumeId && (
                      <button
                        onClick={() => setSelectedResumeId(null)}
                        className="text-xs text-blue-600 hover:underline"
                      >
                        Switch to Upload New PDF
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <button
                      type="button"
                      onClick={() => setSelectedResumeId(null)}
                      className={`p-3 rounded-lg border text-left flex items-center gap-3 transition ${
                        !selectedResumeId
                          ? "border-blue-600 bg-blue-50 text-blue-900"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <span className="text-xl">📄</span>
                      <div>
                        <p className="font-medium text-sm">Upload New Resume</p>
                        <p className="text-xs text-gray-500">PDF file up to 10MB</p>
                      </div>
                    </button>

                    <div className="relative">
                      <select
                        value={selectedResumeId || ""}
                        onChange={(e) => {
                          const val = e.target.value ? Number(e.target.value) : null;
                          setSelectedResumeId(val);
                          if (val) setFile(null);
                        }}
                        className={`w-full p-3 rounded-lg border text-sm transition appearance-none pr-8 ${
                          selectedResumeId
                            ? "border-blue-600 bg-blue-50 text-blue-900 font-medium"
                            : "border-gray-200 text-gray-700"
                        }`}
                      >
                        <option value="">Or select previously uploaded resume...</option>
                        {resumes.map((r) => (
                          <option key={r.id} value={r.id}>
                            {r.filename} ({new Date(r.uploaded_at).toLocaleDateString()})
                          </option>
                        ))}
                      </select>
                      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-500">
                        ▼
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Upload Dropzone (shown if no existing resume selected) */}
              {!selectedResumeId && (
                <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center mb-6">
                  <h2 className="text-xl font-bold mb-3">Upload Resume</h2>
                  <p className="text-gray-500 mb-4">Select your resume in PDF format</p>
                  <input
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={(e) => setFile(e.target.files[0])}
                    className="block mx-auto cursor-pointer"
                  />
                  {file && (
                    <div className="mt-4">
                      <span className="bg-green-100 text-green-700 px-4 py-2 rounded-full inline-block font-medium">
                        ✓ {file.name}
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* Selected Resume Banner */}
              {selectedResumeId && (
                <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-xl flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">📑</span>
                    <div>
                      <p className="font-semibold text-blue-950 text-sm">
                        Selected: {resumes.find((r) => r.id === selectedResumeId)?.filename}
                      </p>
                      <p className="text-xs text-blue-700">
                        Will be analyzed against the Job Description below.
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedResumeId(null)}
                    className="text-xs text-blue-700 hover:text-blue-950 font-medium underline"
                  >
                    Change
                  </button>
                </div>
              )}

              <label className="block text-lg font-semibold mb-2">
                Job Description
              </label>

              <textarea
                rows="8"
                placeholder="Paste Job Description here..."
                value={jd}
                onChange={(e) => setJd(e.target.value)}
                className="w-full border rounded-lg p-3 focus:outline-blue-500 focus:ring-1 focus:ring-blue-500"
              />

              <button
                onClick={handleAnalyze}
                disabled={loading}
                className={`mt-4 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium transition ${
                  loading ? "opacity-60 cursor-not-allowed" : ""
                }`}
              >
                {loading ? "Analyzing..." : "Analyze Resume"}
              </button>
            </div>

            {/* RESULTS SECTION (Exact original layout & components preserved) */}
            {result && (
              <div className="grid md:grid-cols-2 gap-6 mt-8">
                {/* ATS Score Card */}
                <div className="bg-white p-6 rounded-xl shadow">
                  <h2 className="text-xl font-bold mb-2">ATS Score</h2>

                  <p
                    className={`text-5xl font-bold ${
                      result.ats_score >= 75
                        ? "text-green-600"
                        : result.ats_score >= 50
                        ? "text-yellow-600"
                        : "text-red-600"
                    }`}
                  >
                    {result.ats_score}%
                  </p>

                  <div className="w-full bg-gray-200 rounded-full h-4 mt-4">
                    <div
                      className={`h-4 rounded-full transition-all duration-500 ${
                        result.ats_score >= 75
                          ? "bg-green-500"
                          : result.ats_score >= 50
                          ? "bg-yellow-500"
                          : "bg-red-500"
                      }`}
                      style={{
                        width: `${Math.min(100, Math.max(0, result.ats_score))}%`
                      }}
                    />
                  </div>

                  {/* Section-wise breakdown */}
                  <div className="bg-white p-4 rounded-xl shadow-inner border border-gray-100 mt-6">
                    <h3 className="text-lg font-bold mb-4">Section-wise Score</h3>

                    {Object.entries(result.section_scores || {}).map(([section, score]) => (
                      <div key={section} className="mb-3">
                        <div className="flex justify-between text-sm">
                          <span className="font-medium text-gray-700">{section}</span>
                          <span className="font-semibold">{score}%</span>
                        </div>

                        <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                          <div
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="mt-4 text-sm text-gray-600 space-y-1">
                    <p>
                      <strong>Semantic Score:</strong> {result.semantic_score}%
                    </p>
                    <p>
                      <strong>Skill Match:</strong> {result.skill_match_score}%
                    </p>
                  </div>

                  {/* Download Report Button */}
                  <div className="mt-5">
                    <a
                      href={
                        result.analysis_id
                          ? `${API_BASE}/analyses/${result.analysis_id}/report`
                          : `${API_BASE}/download-report`
                      }
                      target="_blank"
                      rel="noreferrer"
                    >
                      <button className="bg-purple-600 text-white px-5 py-2.5 rounded-lg hover:bg-purple-700 font-medium transition shadow-sm">
                        Download PDF Report
                      </button>
                    </a>
                  </div>
                </div>

                {/* Resume Skills */}
                <div className="bg-white p-6 rounded-xl shadow">
                  <h2 className="text-xl font-bold mb-4">Resume Skills</h2>
                  <div className="flex flex-wrap gap-2">
                    {result.resume_skills && result.resume_skills.length > 0 ? (
                      result.resume_skills.map((skill, index) => (
                        <span
                          key={index}
                          className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium"
                        >
                          {skill}
                        </span>
                      ))
                    ) : (
                      <p className="text-gray-400 text-sm">No predefined skills detected.</p>
                    )}
                  </div>
                </div>

                {/* Missing Skills */}
                <div className="bg-white p-6 rounded-xl shadow">
                  <h2 className="text-xl font-bold mb-4">Missing Skills</h2>
                  <div className="flex flex-wrap gap-2">
                    {result.missing_skills && result.missing_skills.length > 0 ? (
                      result.missing_skills.map((skill, index) => (
                        <span
                          key={index}
                          className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm font-medium"
                        >
                          {skill}
                        </span>
                      ))
                    ) : (
                      <p className="text-green-600 text-sm font-medium">
                        ✓ No missing skills from job description!
                      </p>
                    )}
                  </div>
                </div>

                {/* Suggestions */}
                <div className="bg-white p-6 rounded-xl shadow">
                  <h2 className="text-xl font-bold mb-4">Suggestions</h2>
                  <ul className="space-y-2">
                    {result.suggestions && result.suggestions.length > 0 ? (
                      result.suggestions.map((item, index) => (
                        <li key={index} className="bg-blue-50 p-3 rounded-lg text-sm text-blue-900">
                          {item}
                        </li>
                      ))
                    ) : (
                      <p className="text-gray-500 text-sm">No suggestions.</p>
                    )}
                  </ul>
                </div>

                {/* Interview Questions */}
                <div className="bg-white p-6 rounded-xl shadow">
                  <h2 className="text-xl font-bold mb-4">Interview Questions</h2>
                  <ul className="space-y-2">
                    {result.interview_questions && result.interview_questions.length > 0 ? (
                      result.interview_questions.map((q, index) => (
                        <li key={index} className="bg-purple-50 p-3 rounded-lg text-sm text-purple-900">
                          {q}
                        </li>
                      ))
                    ) : (
                      <p className="text-gray-500 text-sm">No questions generated.</p>
                    )}
                  </ul>
                </div>

                {/* Resume Preview */}
                <div className="bg-white p-6 rounded-xl shadow">
                  <h2 className="text-xl font-bold mb-4">Resume Preview</h2>
                  <p className="text-gray-700 whitespace-pre-wrap text-sm max-h-64 overflow-y-auto bg-gray-50 p-3 rounded-lg border border-gray-100">
                    {result.resume_preview}
                  </p>
                </div>
              </div>
            )}

            {/* Resume Bullet Enhancer (Exact original component preserved) */}
            <div className="bg-white p-6 rounded-xl shadow mt-8">
              <h2 className="text-xl font-bold mb-4">Resume Bullet Enhancer</h2>
              <textarea
                rows="4"
                value={bullet}
                onChange={(e) => setBullet(e.target.value)}
                placeholder="Paste a resume bullet..."
                className="w-full border rounded-lg p-3 focus:outline-green-500 focus:ring-1 focus:ring-green-500"
              />
              <button
                onClick={handleEnhance}
                className="mt-4 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-medium transition"
              >
                Enhance Bullet
              </button>

              {enhancedBullet && (
                <div className="mt-4 bg-green-50 p-4 rounded-lg border border-green-200">
                  <h3 className="font-bold mb-2 text-green-900">Enhanced Version</h3>
                  <p className="text-green-800">{enhancedBullet}</p>
                </div>
              )}
            </div>
          </>
        )}

        {/* TAB 2: RESUME MANAGEMENT & HISTORY */}
        {activeTab === "history" && currentUser && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-slate-800">Your Uploaded Resumes</h2>
              <button
                onClick={() => {
                  setSelectedResumeId(null);
                  setActiveTab("analyzer");
                }}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition"
              >
                + Upload New Resume
              </button>
            </div>

            {resumes.length === 0 ? (
              <div className="bg-white p-12 text-center rounded-xl shadow-sm border border-gray-200">
                <span className="text-4xl">📁</span>
                <h3 className="text-lg font-semibold text-gray-700 mt-3">No resumes uploaded yet</h3>
                <p className="text-sm text-gray-500 mt-1 mb-4">
                  Upload your first resume PDF to begin tracking ATS analyses.
                </p>
                <button
                  onClick={() => setActiveTab("analyzer")}
                  className="bg-blue-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700"
                >
                  Upload Resume
                </button>
              </div>
            ) : (
              resumes.map((resume) => (
                <div
                  key={resume.id}
                  className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 transition hover:border-gray-300"
                >
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex items-start gap-4">
                      <span className="text-3xl p-2 bg-blue-50 rounded-xl text-blue-600">
                        📄
                      </span>
                      <div>
                        <h3 className="text-lg font-bold text-slate-800">
                          {resume.filename}
                        </h3>
                        <p className="text-xs text-gray-400 mt-0.5">
                          Uploaded on {new Date(resume.uploaded_at).toLocaleDateString()} at{" "}
                          {new Date(resume.uploaded_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                        </p>
                        {resume.extracted_text_preview && (
                          <p className="text-xs text-gray-600 mt-2 italic line-clamp-2 max-w-2xl">
                            "{resume.extracted_text_preview}"
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 flex-wrap">
                      <button
                        onClick={() => handleSelectResumeForAnalysis(resume)}
                        className="bg-blue-50 text-blue-700 hover:bg-blue-100 px-3 py-1.5 rounded-lg text-xs font-semibold transition"
                      >
                        ⚡ Re-analyze vs new JD
                      </button>

                      <button
                        onClick={() => handleToggleHistory(resume.id)}
                        className="bg-gray-100 text-gray-700 hover:bg-gray-200 px-3 py-1.5 rounded-lg text-xs font-semibold transition"
                      >
                        {expandedResumeId === resume.id ? "Hide History ▲" : "View History ▼"}
                      </button>

                      <button
                        onClick={() => handleDeleteResume(resume.id)}
                        className="text-red-500 hover:text-red-700 hover:bg-red-50 p-2 rounded-lg text-xs font-medium transition"
                        title="Delete Resume"
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </div>

                  {/* Expanded Analysis History for this resume */}
                  {expandedResumeId === resume.id && (
                    <div className="mt-6 pt-6 border-t border-gray-100">
                      <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">
                        Analysis History
                      </h4>

                      {analysesLoading && (
                        <p className="text-xs text-gray-400">Loading analysis history...</p>
                      )}

                      {!analysesLoading &&
                        resumeAnalyses[resume.id] &&
                        resumeAnalyses[resume.id].length === 0 && (
                          <p className="text-xs text-gray-500 italic">
                            No analyses performed yet for this resume.
                          </p>
                        )}

                      {!analysesLoading &&
                        resumeAnalyses[resume.id] &&
                        resumeAnalyses[resume.id].map((past) => (
                          <div
                            key={past.id}
                            className="bg-slate-50 p-4 rounded-lg mb-3 border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-3"
                          >
                            <div>
                              <div className="flex items-center gap-3">
                                <span
                                  className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                                    past.final_ats_score >= 75
                                      ? "bg-green-100 text-green-700"
                                      : past.final_ats_score >= 50
                                      ? "bg-yellow-100 text-yellow-700"
                                      : "bg-red-100 text-red-700"
                                  }`}
                                >
                                  ATS Score: {past.final_ats_score}%
                                </span>
                                <span className="text-xs text-gray-400">
                                  {new Date(past.created_at).toLocaleDateString()}
                                </span>
                              </div>

                              <p className="text-xs text-gray-600 mt-2 line-clamp-1">
                                <strong>JD:</strong> {past.job_description}
                              </p>
                            </div>

                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => handleLoadPastAnalysis(past)}
                                className="text-xs bg-white border border-gray-300 hover:bg-gray-100 px-3 py-1.5 rounded-md font-medium text-gray-700 transition"
                              >
                                View in Dashboard
                              </button>
                              <a
                                href={`${API_BASE}/analyses/${past.id}/report`}
                                target="_blank"
                                rel="noreferrer"
                              >
                                <button className="text-xs bg-purple-600 text-white hover:bg-purple-700 px-3 py-1.5 rounded-md font-medium transition">
                                  Download PDF
                                </button>
                              </a>
                            </div>
                          </div>
                        ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {/* AUTH MODAL (Login / Register) */}
        {authModalOpen && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl p-6 md:p-8 max-w-md w-full shadow-2xl relative">
              <button
                onClick={() => setAuthModalOpen(false)}
                className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-xl font-bold"
              >
                ✕
              </button>

              <div className="flex gap-4 border-b border-gray-100 pb-3 mb-6">
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode("login");
                    setAuthError("");
                  }}
                  className={`font-semibold pb-2 text-sm transition ${
                    authMode === "login"
                      ? "text-blue-600 border-b-2 border-blue-600"
                      : "text-gray-400 hover:text-gray-600"
                  }`}
                >
                  Sign In
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode("register");
                    setAuthError("");
                  }}
                  className={`font-semibold pb-2 text-sm transition ${
                    authMode === "register"
                      ? "text-blue-600 border-b-2 border-blue-600"
                      : "text-gray-400 hover:text-gray-600"
                  }`}
                >
                  Create Account
                </button>
              </div>

              {authError && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg">
                  {authError}
                </div>
              )}

              <form onSubmit={handleAuthSubmit} className="space-y-4">
                {authMode === "register" && (
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">
                      Full Name
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="Jane Doe"
                      value={authForm.name}
                      onChange={(e) => setAuthForm({ ...authForm, name: e.target.value })}
                      className="w-full border rounded-lg p-2.5 text-sm focus:outline-blue-500 focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                )}

                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    required
                    placeholder="name@example.com"
                    value={authForm.email}
                    onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })}
                    className="w-full border rounded-lg p-2.5 text-sm focus:outline-blue-500 focus:ring-1 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Password
                  </label>
                  <input
                    type="password"
                    required
                    minLength={6}
                    placeholder="••••••••"
                    value={authForm.password}
                    onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })}
                    className="w-full border rounded-lg p-2.5 text-sm focus:outline-blue-500 focus:ring-1 focus:ring-blue-500"
                  />
                </div>

                <button
                  type="submit"
                  disabled={authLoading}
                  className={`w-full bg-blue-600 text-white py-2.5 rounded-lg text-sm font-semibold hover:bg-blue-700 transition shadow-sm ${
                    authLoading ? "opacity-60 cursor-not-allowed" : ""
                  }`}
                >
                  {authLoading
                    ? "Processing..."
                    : authMode === "login"
                    ? "Sign In"
                    : "Create Account"}
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
