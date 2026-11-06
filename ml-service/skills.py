from typing import List, Tuple, Set, Optional

# Default predefined skills list preserved from existing architecture
DEFAULT_SKILLS = [
    "python",
    "java",
    "c++",
    "react",
    "reactjs",
    "node.js",
    "nodejs",
    "mongodb",
    "sql",
    "mysql",
    "postgresql",
    "docker",
    "aws",
    "git",
    "github",
    "machine learning",
    "tensorflow",
    "pytorch",
    "express",
    "rest api"
]

# Backward compatibility alias
skills_db = DEFAULT_SKILLS


class SkillExtractor:
    """
    Modular skill extractor that handles skill discovery and matching.
    Designed to allow pluggable skill taxonomies, regex/token-based matching,
    or external knowledge graphs in the future while preserving exact
    current behavior.
    """

    def __init__(self, predefined_skills: Optional[List[str]] = None):
        self.skills = list(predefined_skills) if predefined_skills is not None else list(DEFAULT_SKILLS)

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract matching skills from the provided text string.
        Preserves original substring-in-lowercased-text logic.
        """
        if not text:
            return []

        text_lower = text.lower()
        found: List[str] = []

        for skill in self.skills:
            if skill.lower() in text_lower:
                found.append(skill)

        return found

    def match_skills(
        self,
        resume_skills: List[str],
        jd_skills: List[str]
    ) -> Tuple[List[str], List[str], float]:
        """
        Compare resume skills with JD skills.
        Safely handles empty JD skill lists without ZeroDivisionError.

        Returns:
            Tuple of (matched_skills, missing_skills, skill_match_score)
        """
        resume_set: Set[str] = set(resume_skills)
        jd_set: Set[str] = set(jd_skills)

        missing_skills = [skill for skill in jd_skills if skill not in resume_set]
        matched_skills = [skill for skill in jd_skills if skill in resume_set]

        if len(jd_skills) > 0:
            skill_match_score = (len(matched_skills) / len(jd_skills)) * 100.0
        else:
            # Safe handling for empty JD skill list:
            # If no skills are specified in the JD, skill match is neutral 100% or 0%?
            # Per existing code: len(jd_skills) == 0 led to skill_match_score = 0
            skill_match_score = 0.0

        return matched_skills, missing_skills, round(skill_match_score, 2)


# Default singleton extractor
default_extractor = SkillExtractor()


def extract_skills(text: str) -> List[str]:
    """Backward-compatible top-level function for skill extraction."""
    return default_extractor.extract_skills(text)
