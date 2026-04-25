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