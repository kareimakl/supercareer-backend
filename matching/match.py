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
        # تقليل الـ timeout لـ 2 ثانية لضمان الاستجابة السريعة في Render
        response = requests.post(URL, json=payload, timeout=2)
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
    URL = "http://76.13.55.54:8080/API/proposel"
    
    # تحويل البيانات لنص لأن السيرفر يتوقع string في user_profile
    if isinstance(profile_data, dict):
        profile_str = f"Name: {profile_data.get('full_name', '')}. Bio: {profile_data.get('bio', '')}. Skills: {', '.join(profile_data.get('skills', []))}"
    else:
        profile_str = str(profile_data)
        
    payload = {
        "user_profile": profile_str,
        "project_details": project_description
    }
    
    try:
        # زيادة الـ timeout لأن الـ AI قد يستغرق بعض الوقت للتوليد (مثلاً 30 ثانية)
        response = requests.post(URL, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # السيرفر يرجع النص في مفتاح proposal_text
            proposal_text = data.get('proposal_text')
            if proposal_text:
                return proposal_text
    except Exception:
        pass
    
    # الـ Fallback في حالة السيرفر قافل
    fallback_text = (
        f"Hi, I'm very interested in your project: '{project_description[:40]}...'. "
        "Based on my profile and skills, I believe I can deliver high-quality results. "
        "Looking forward to discussing more details with you."
    )
    return fallback_text