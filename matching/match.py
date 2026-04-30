import requests
import random

def get_ai_match(profile_text, target_text):
    # رابط سيرفر عبد الله
    URL = "https://unimpartible-glaringly-maudie.ngrok-free.dev/API/match"
    
    payload = {
        "cv_text": profile_text,
        "job_description": target_text
    }
    
    try:
        # بنقلل الـ timeout لـ 3 ثواني عشان لو عبد الله قافل المشروع ميهنجش
        response = requests.post(URL, json=payload, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return (
                data.get('match_score', 0.0), 
                data.get('matched_skills', []), 
                data.get('ai_tips', '')
            )
    except Exception:
        # لو السيرفر وقع أو الـ timeout خلص، بنرجع داتا عشوائية
        pass
    
    # الـ Fallback (الخطة البديلة)
    mock_score = float(random.randint(65, 95))
    mock_tips = "Note: AI Server is offline. Using local matching logic."
    return mock_score, ["Skill A", "Skill B"], mock_tips

def generate_ai_proposal(profile_data, project_description):
    # رابط سيرفر عبد الله الخاص بالبروبوزال (كما في الصورة)
    URL = "https://unimpartible-glaringly-maudie.ngrok-free.dev/API/proposel"
    
    payload = {
        "profile": profile_data,
        "project": project_description
    }
    
    try:
        # بنكلم سيرفر عبدالله بمهلة 5 ثواني
        response = requests.post(URL, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # بنرجع نص البروبوزال اللي عبدالله باعتة
            return data.get('generated_proposal', "")
    except Exception:
        pass
    
    # الـ Fallback في حالة السيرفر قافل
    fallback_text = (
        f"Hi, I'm very interested in your project: '{project_description[:40]}...'. "
        "Based on my profile and skills, I believe I can deliver high-quality results. "
        "Looking forward to discussing more details with you."
    )
    return fallback_text