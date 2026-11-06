import io
from fastapi.testclient import TestClient
from main import app

def test_health():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Resume Analyzer API Running"

def test_auth_and_ownership_flow():
    client1 = TestClient(app)
    client2 = TestClient(app)

    # 1. Register User 1
    u1_email = "alice@example.com"
    u1_pass = "Password123!"
    reg1_resp = client1.post(
        "/auth/register",
        json={"name": "Alice User", "email": u1_email, "password": u1_pass}
    )
    if reg1_resp.status_code == 400:
        login1_resp = client1.post(
            "/auth/login",
            json={"email": u1_email, "password": u1_pass}
        )
        assert login1_resp.status_code == 200
        u1_token = login1_resp.json()["access_token"]
        u1_id = login1_resp.json()["user"]["id"]
    else:
        assert reg1_resp.status_code == 201
        u1_token = reg1_resp.json()["access_token"]
        u1_id = reg1_resp.json()["user"]["id"]

    # Register User 2 on client2
    u2_email = "bob@example.com"
    u2_pass = "Password456!"
    reg2_resp = client2.post(
        "/auth/register",
        json={"name": "Bob User", "email": u2_email, "password": u2_pass}
    )
    if reg2_resp.status_code == 400:
        login2_resp = client2.post(
            "/auth/login",
            json={"email": u2_email, "password": u2_pass}
        )
        assert login2_resp.status_code == 200
        u2_token = login2_resp.json()["access_token"]
        u2_id = login2_resp.json()["user"]["id"]
    else:
        assert reg2_resp.status_code == 201
        u2_token = reg2_resp.json()["access_token"]
        u2_id = reg2_resp.json()["user"]["id"]

    # 2. Check /auth/me for User 1 using cookie on client1
    me_resp = client1.get("/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == u1_email
    assert me_resp.json()["id"] == u1_id

    # Check /auth/me for User 2 using cookie on client2
    me2_resp = client2.get("/auth/me")
    assert me2_resp.status_code == 200
    assert me2_resp.json()["email"] == u2_email
    assert me2_resp.json()["id"] == u2_id

    # 3. Check /auth/me without auth on a fresh client -> 401
    anon_client = TestClient(app)
    unauth_resp = anon_client.get("/auth/me")
    assert unauth_resp.status_code == 401

    # 4. Login with bad password -> 401
    bad_login = anon_client.post(
        "/auth/login",
        json={"email": u1_email, "password": "WrongPassword"}
    )
    assert bad_login.status_code == 401

    # 5. User 1 uploads a resume
    pdf_bytes = (
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\n"
        b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF"
    )

    upload_resp = client1.post(
        "/resumes/upload",
        files={"file": ("alice_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    )
    assert upload_resp.status_code == 201
    u1_resume_id = upload_resp.json()["id"]

    # 6. User 1 lists resumes -> contains u1_resume_id
    u1_resumes = client1.get("/resumes")
    assert u1_resumes.status_code == 200
    assert any(r["id"] == u1_resume_id for r in u1_resumes.json())

    # User 2 lists resumes -> does NOT contain u1_resume_id
    u2_resumes = client2.get("/resumes")
    assert u2_resumes.status_code == 200
    assert not any(r["id"] == u1_resume_id for r in u2_resumes.json())

    # 7. User 2 tries to access User 1's resume -> 403 Forbidden!
    u2_access_u1 = client2.get(f"/resumes/{u1_resume_id}")
    assert u2_access_u1.status_code == 403
    assert "forbidden" in u2_access_u1.json()["detail"].lower()

    # 8. User 2 tries to delete User 1's resume -> 403 Forbidden!
    u2_del_u1 = client2.delete(f"/resumes/{u1_resume_id}")
    assert u2_del_u1.status_code == 403

    # 9. User 1 re-analyzes resume against JD
    reanalyze_resp = client1.post(
        f"/resumes/{u1_resume_id}/analyze",
        json={"jd": "Looking for python, react, docker, and postgresql experience"}
    )
    assert reanalyze_resp.status_code == 200
    analysis_data = reanalyze_resp.json()
    analysis_id = analysis_data["id"]
    assert "final_ats_score" in analysis_data
    assert "semantic_score" in analysis_data
    assert "skill_match_score" in analysis_data
    assert "matched_skills" in analysis_data
    assert "missing_skills" in analysis_data

    # 10. User 2 tries to get analysis result -> 403 Forbidden!
    u2_analysis_access = client2.get(f"/analyses/{analysis_id}")
    assert u2_analysis_access.status_code == 403

    # 11. User 2 tries to download User 1's analysis report -> 403 Forbidden!
    u2_report_download = client2.get(f"/analyses/{analysis_id}/report")
    assert u2_report_download.status_code == 403

    # 12. User 1 downloads their report -> 200 OK application/pdf
    u1_report_download = client1.get(f"/analyses/{analysis_id}/report")
    assert u1_report_download.status_code == 200
    assert u1_report_download.headers["content-type"] == "application/pdf"

    # 13. File validation: Non-PDF rejected
    bad_file_resp = client1.post(
        "/resumes/upload",
        files={"file": ("malicious.exe", io.BytesIO(b"MZ\x90\x00"), "application/octet-stream")}
    )
    assert bad_file_resp.status_code == 400

    # 14. User 1 logs out
    logout_resp = client1.post("/auth/logout")
    assert logout_resp.status_code == 200
    # After logout, accessing protected endpoint returns 401
    post_logout_me = client1.get("/auth/me")
    assert post_logout_me.status_code == 401

    print("SUCCESS: All backend security, auth, and ownership tests passed!")

if __name__ == "__main__":
    test_health()
    test_auth_and_ownership_flow()
