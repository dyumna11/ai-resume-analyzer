# AI Resume Analyzer

An AI-powered Resume Analyzer that evaluates resume–job description alignment, generates ATS compatibility scores, identifies missing skills, and provides personalized improvement recommendations using NLP and Large Language Models.

## Features

* Upload and analyze PDF resumes
* Compare resumes against job descriptions
* Generate ATS compatibility scores
* Perform semantic resume–JD matching using Sentence Transformers
* Identify missing skills and keywords
* Generate section-wise resume analysis
* AI-powered resume bullet enhancement
* Generate role-specific interview questions
* Export detailed PDF feedback reports

---

## Tech Stack

### Frontend

* React.js
* Tailwind CSS
* Axios

### Backend

* FastAPI
* Python

### AI & NLP

* Gemini API
* Sentence Transformers
* Scikit-learn (Cosine Similarity)

### Document Processing

* PDFPlumber
* ReportLab

---

## System Architecture

```text
Resume PDF
      │
      ▼
PDF Extraction
      │
      ▼
Resume Parsing
      │
      ▼
Semantic Matching
(Sentence Transformers)
      │
      ▼
ATS Score Calculation
      │
      ▼
Gemini Analysis
      │
      ├── Skill Gap Analysis
      ├── Resume Suggestions
      ├── Bullet Enhancement
      └── Interview Questions
      │
      ▼
PDF Report Generation
```

---

## Key Features

### ATS Scoring

The system evaluates resumes across multiple sections including:

* Skills
* Projects
* Experience
* Education
* Achievements

and generates an overall ATS compatibility score.

---

### Semantic Resume Matching

Unlike traditional keyword matching, the application uses Sentence Transformers to compute semantic similarity between the resume and job description.

Benefits:

* Understands contextual relevance
* Detects related technologies and skills
* Reduces dependence on exact keyword matches

---

### Skill Gap Analysis

The analyzer:

* Extracts technical and soft skills
* Identifies missing job requirements
* Highlights improvement opportunities
* Generates personalized recommendations

---

### AI-Powered Resume Enhancement

Using Gemini API, the platform can:

* Improve resume bullet points
* Suggest stronger action verbs
* Quantify impact statements
* Increase ATS friendliness

---

### Interview Preparation

Automatically generates:

* Technical interview questions
* Behavioral interview questions
* Role-specific questions based on the target job description

---

## Example Output

### ATS Analysis

```text
ATS Score: 84%

Matching Skills:
✓ React
✓ Node.js
✓ MongoDB
✓ REST APIs

Missing Skills:
✗ Docker
✗ Kubernetes
✗ CI/CD
```

### Generated Recommendation

```text
Add experience with containerization tools such as Docker
and highlight deployment workflows to improve alignment
with backend engineering roles.
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/dyumna11/ai-resume-analyzer.git
cd ai-resume-analyzer
```

### Backend Setup

```bash
cd backend

python -m venv venv

source venv/bin/activate
# Windows
# venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

## Environment Variables

Create a `.env` file inside the backend directory.

```env
GEMINI_API_KEY=your_api_key
```

---

## Future Enhancements

* Resume version tracking
* Multi-job comparison
* Recruiter mode
* LinkedIn profile analysis
* Cover letter generation
* Resume benchmarking against top candidates

---

## Project Highlights

* Semantic Resume–JD Matching using Sentence Transformers
* ATS Score Generation across 5+ resume sections
* Skill Gap Detection across 20+ skill categories
* AI-Powered Resume Optimization
* Automated Interview Question Generation
* PDF Feedback Report Export

---

## Author

**Dyumna Negi**

GitHub: https://github.com/dyumna11
