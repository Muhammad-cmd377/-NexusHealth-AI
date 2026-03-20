from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a professional, empathetic AI Health Assistant named NexusHealth AI.

Your role:
- Analyze patient vitals clearly and concisely
- Give diet & exercise recommendations when asked
- Interpret BMI and suggest healthy lifestyle habits
- Review medicine lists for general guidance

Guidelines:
- Be warm, professional, and supportive
- Use plain text with simple labels: Assessment:, Recommendation:, Diet Tips:, Exercise Tips:
- Never use excessive markdown (**, ##, ***)
- Always remind patient to consult a licensed physician
- Never diagnose — offer observations and guidance only
- Keep responses focused and practical
"""

def build_vitals_context(bp_systolic, bp_diastolic, heart_rate, glucose, bmi=None):
    ctx = (
        f"Current Patient Vitals:\n"
        f"  Blood Pressure: {bp_systolic}/{bp_diastolic} mmHg\n"
        f"  Heart Rate: {heart_rate} bpm\n"
        f"  Blood Glucose: {glucose} mg/dL\n"
    )
    if bmi:
        ctx += f"  BMI: {bmi:.1f}\n"
    return ctx

def get_ai_response(chat_history, vitals_context, user_message):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({"role": "system", "content": f"Patient's current vitals:\n{vitals_context}"})
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.6,
            max_tokens=1024,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def get_diet_plan(bp_systolic, bp_diastolic, glucose, bmi):
    prompt = f"""
Patient vitals: BP {bp_systolic}/{bp_diastolic} mmHg, Glucose {glucose} mg/dL, BMI {bmi:.1f}

Create a practical 1-day diet plan with:
1. Breakfast, Lunch, Dinner, Snacks
2. Foods to AVOID based on their vitals
3. Hydration tips
4. 3 key nutrition recommendations

Keep it simple, practical, and specific. Plain text only.
"""
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def get_exercise_plan(bp_systolic, heart_rate, bmi):
    prompt = f"""
Patient: BP {bp_systolic} mmHg systolic, Heart Rate {heart_rate} bpm, BMI {bmi:.1f}

Create a safe weekly exercise plan with:
1. Recommended exercise types
2. Duration and frequency
3. Exercises to AVOID
4. Warm-up and cool-down tips
5. Safety precautions based on vitals

Keep it simple and safe. Plain text only.
"""
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"