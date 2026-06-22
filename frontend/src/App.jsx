import { useState } from "react";
import axios from "axios";

function App() {

  const [file, setFile] = useState(null);
  const [jd, setJd] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [bullet, setBullet] = useState("");
  const [enhancedBullet, setEnhancedBullet] = useState("");
  const handleAnalyze = async () => {

    if (!file || !jd) {
      alert("Upload resume and enter JD");
      return;
    }

    const formData = new FormData();

    formData.append("file", file);
    formData.append("jd", jd);

    try {

      setLoading(true);

      const response = await axios.post(
        "http://127.0.0.1:8000/analyze",
        formData
      );

      setResult(response.data);

    } catch (error) {

      console.error(error);
      alert("Analysis failed");

    } finally {

      setLoading(false);

    }
  };
  const handleEnhance = async () => {

    try {
  
      const response = await axios.post(
        "http://127.0.0.1:8000/enhance-bullet",
        {
          bullet: bullet
        }
      );
  
      setEnhancedBullet(
        response.data.enhanced_bullet
      );
  
    } catch (error) {
  
      console.error(error);
  
    }
  };
  return (
    <div className="min-h-screen bg-slate-100 p-8">
  <div className="max-w-5xl mx-auto">

    <h1 className="text-4xl font-bold text-center mb-8">
      AI Resume Analyzer
    </h1>

    <div className="bg-white p-6 rounded-xl shadow-md">

<div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center mb-6">

  <h2 className="text-xl font-bold mb-3">
    Upload Resume
  </h2>

  <p className="text-gray-500 mb-4">
    Select your resume in PDF format
  </p>

  <input
    type="file"
    accept=".pdf"
    onChange={(e) => setFile(e.target.files[0])}
    className="block mx-auto"
  />

  {file && (
    <div className="mt-4">
      <span className="bg-green-100 text-green-700 px-4 py-2 rounded-full">
        ✓ {file.name}
      </span>
    </div>
  )}

</div>

<label className="block text-lg font-semibold mb-2">
  Job Description
</label>

<textarea
  rows="8"
  placeholder="Paste Job Description"
  value={jd}
  onChange={(e) => setJd(e.target.value)}
  className="w-full border rounded-lg p-3"
/>

<button
  onClick={handleAnalyze}
  className="mt-4 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
>
  {loading ? "Analyzing..." : "Analyze Resume"}
</button>
</div>

    {result && (

      <div className="grid md:grid-cols-2 gap-6 mt-8">

        <div className="bg-white p-6 rounded-xl shadow">
          <h2 className="text-xl font-bold mb-2">
            ATS Score
          </h2>

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
    className={`h-4 rounded-full ${
      result.ats_score >= 75
        ? "bg-green-500"
        : result.ats_score >= 50
        ? "bg-yellow-500"
        : "bg-red-500"
    }`}
    style={{
      width: `${result.ats_score}%`
    }}
  />

</div>

          <div className="mt-4">
            <p>
              Semantic Score: {result.semantic_score}
            </p>

            <p>
              Skill Match: {result.skill_match_score}
            </p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow">
          <h2 className="text-xl font-bold mb-4">
            Resume Skills
          </h2>

          <div className="flex flex-wrap gap-2">
            {result.resume_skills?.map((skill, index) => (
              <span
                key={index}
                className="bg-green-100 text-green-700 px-3 py-1 rounded-full"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow">
          <h2 className="text-xl font-bold mb-4">
            Missing Skills
          </h2>

          <div className="flex flex-wrap gap-2">
            {result.missing_skills?.map((skill, index) => (
              <span
                key={index}
                className="bg-red-100 text-red-700 px-3 py-1 rounded-full"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow">
  <h2 className="text-xl font-bold mb-4">
    Suggestions
  </h2>

  <ul className="space-y-2">
    {result.suggestions?.map((item, index) => (
      <li
        key={index}
        className="bg-blue-50 p-3 rounded-lg"
      >
        {item}
      </li>
    ))}
  </ul>
</div>

        <div className="bg-white p-6 rounded-xl shadow">
          <h2 className="text-xl font-bold mb-4">
            Resume Preview
          </h2>

          <p className="text-gray-700 whitespace-pre-wrap">
            {result.resume_preview}
          </p>
        </div>

      </div>

  )}


<div className="bg-white p-6 rounded-xl shadow mt-8">

  <h2 className="text-xl font-bold mb-4">
    Resume Bullet Enhancer
  </h2>

  <textarea
    rows="4"
    value={bullet}
    onChange={(e) => setBullet(e.target.value)}
    placeholder="Paste a resume bullet..."
    className="w-full border rounded-lg p-3"
  />

  <button
    onClick={handleEnhance}
    className="mt-4 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700"
  >
    Enhance Bullet
  </button>

  {enhancedBullet && (
    <div className="mt-4 bg-green-50 p-4 rounded-lg">
      <h3 className="font-bold mb-2">
        Enhanced Version
      </h3>

      <p>{enhancedBullet}</p>
    </div>
  
  )}
</div>

</div>
</div>
  );
}

export default App;