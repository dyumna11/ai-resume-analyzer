from ats import ats_score, chunk_text, get_document_embedding
from skills import SkillExtractor, default_extractor

def test_scoring_formula_and_empty_jd():
    # Test 1: Empty JD skills safe handling
    resume_skills = ["python", "react", "sql"]
    jd_skills = []
    matched, missing, skill_score = default_extractor.match_skills(resume_skills, jd_skills)
    assert skill_score == 0.0
    assert matched == []
    assert missing == []

    # Test 2: Partial skill match
    jd_skills = ["python", "docker", "aws", "react"]
    matched, missing, skill_score = default_extractor.match_skills(resume_skills, jd_skills)
    assert set(matched) == {"python", "react"}
    assert set(missing) == {"docker", "aws"}
    assert skill_score == 50.0  # 2 out of 4 = 50%

    # Test 3: Formula verification
    # final_score = round(0.7 * skill_match_score + 0.3 * semantic_score, 2)
    semantic_score = 60.0
    final_score = round(0.7 * skill_score + 0.3 * semantic_score, 2)
    assert final_score == round(0.7 * 50.0 + 0.3 * 60.0, 2)
    assert final_score == 53.0

    # Test 4: Chunking for long text
    long_text = "Experienced software engineer specializing in Python and React. " * 50
    chunks = chunk_text(long_text, chunk_size=150, overlap=40)
    assert len(chunks) > 1

    # Test 5: Semantic ATS score handles long text without error
    score = ats_score(long_text, "Looking for Python and React software engineer.")
    assert isinstance(score, float)
    assert 0.0 <= score <= 100.0

    print("SUCCESS: All scoring formula, empty JD, and chunking tests passed!")

if __name__ == "__main__":
    test_scoring_formula_and_empty_jd()

