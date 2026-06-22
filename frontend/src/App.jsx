import { useState } from "react";
import axios from "axios";

function App() {

  const [file, setFile] = useState(null);
  const [jd, setJd] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

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

  return (
    <div className="min-h-screen bg-slate-100 p-8">
  <div className="max-w-5xl mx-auto">

    <h1 className="text-4xl font-bold text-center mb-8">
      AI Resume Analyzer
    </h1>

    <div className="bg-white p-6 rounded-xl shadow-md">

      <input
        type="file"
        accept=".pdf"
        className="mb-4 block w-full"
        onChange={(e) => setFile(e.target.files[0])}
      />

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

  </div>
</div>
  );
}

export default App;