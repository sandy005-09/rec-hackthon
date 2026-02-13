# GenAI Financial Assistant

## Features
1. **Contextual Advice:** Uses Gemini to analyze simulated user data (Income, Debt, Goals).
2. **Smart Notifications:** Generates real-time alerts for:
   - ⚠️ Overspending
   - 📅 Bill Reminders
   - 📊 Monthly Summaries

## Setup
1. `pip install -r requirements.txt`
2. Add `.env` with `GOOGLE_API_KEY`
3. Run: `uvicorn main:app --reload`
