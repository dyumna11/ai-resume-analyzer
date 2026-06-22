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
    <div style={{ padding: "30px" }}>

      <h1>AI Resume Analyzer</h1>

      <br />

      <input
        type="file"
        accept=".pdf"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <br />
      <br />

      <textarea
        rows="8"
        cols="80"
        placeholder="Paste Job Description"
        value={jd}
        onChange={(e) => setJd(e.target.value)}
      />

      <br />
      <br />

      <button onClick={handleAnalyze}>
        {loading ? "Analyzing..." : "Analyze Resume"}
      </button>

      <br />
      <br />

      {result && (

<div>

  <div
    style={{
      border: "1px solid #ddd",
      padding: "20px",
      borderRadius: "10px",
      marginBottom: "20px",
      backgroundColor: "#f5f5f5"
    }}
  >
    <h2>ATS Score</h2>
    <h1>{result.ats_score}%</h1>

    <p>
      Semantic Score: {result.semantic_score}
    </p>

    <p>
      Skill Match Score: {result.skill_match_score}
    </p>
  </div>

  <div
    style={{
      border: "1px solid #ddd",
      padding: "20px",
      borderRadius: "10px",
      marginBottom: "20px"
    }}
  >
    <h3>Resume Skills</h3>

    <ul>
      {result.resume_skills?.map((skill, index) => (
        <li
          key={index}
          style={{
            color: "green",
            fontWeight: "bold"
          }}
        >
          {skill}
        </li>
      ))}
    </ul>
  </div>

  <div
    style={{
      border: "1px solid #ddd",
      padding: "20px",
      borderRadius: "10px",
      marginBottom: "20px"
    }}
  >
    <h3>Missing Skills</h3>

    <ul>
      {result.missing_skills?.map((skill, index) => (
        <li
          key={index}
          style={{
            color: "red",
            fontWeight: "bold"
          }}
        >
          {skill}
        </li>
      ))}
    </ul>
  </div>

  <div
    style={{
      border: "1px solid #ddd",
      padding: "20px",
      borderRadius: "10px"
    }}
  >
    <h3>Resume Preview</h3>

    <p>
      {result.resume_preview}
    </p>
  </div>

</div>

      )}

    </div>
  );
}

export default App;
