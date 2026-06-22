skills_db = [
    "python",
    "java",
    "c++",
    "react",
    "node.js",
    "mongodb",
    "express",
    "sql",
    "aws",
    "docker",
    "machine learning",
    "git",
    "rest api"
]

def extract_skills(text):

    text = text.lower()

    found = []

    for skill in skills_db:
        if skill in text:
            found.append(skill)

    return found