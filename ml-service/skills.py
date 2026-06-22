skills_db = [
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

def extract_skills(text):

    text = text.lower()

    found = []

    for skill in skills_db:
        if skill in text:
            found.append(skill)

    return found