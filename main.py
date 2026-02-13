import os
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Gemini
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)

# --- 1. SIMULATED DB ---
user_context = {
    "name": "User",
    "income": 45000,
    "savings": 9000,
    "expenses": 36000,
    "previous_expenses": 32500,
    "goals": ["buy a bikefund"]
}

# --- 2. PROMPTS ---
system_template = """
You are a Financial Companion. Use this data to provide expert advice:
User: {name} | Income: ₹{income} | Expenses: ₹{expenses} | Savings: ₹{savings} | Goals: {goals}
Transactions: {transactions}

Analyze the user's spending patterns and provide professional, actionable advice based on both their balance and their specific transaction history.
Keep answers concise and addressed to the user.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("user", "{input}")
])
chain = prompt | llm | StrOutputParser()

@app.post("/chat")
async def chat(data: dict = Body(...)):
    text = data.get("text", "").lower()
    context = data.get("context", user_context)
    transactions = context.get("transactions", [])
    
    # Check if Gemini is configured
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or "your_key_here" in api_key:
        # Fallback Logic: Rules-based bot
        if "spending" in text or "expense" in text:
            total_exp = context.get('expenses', 0)
            return {"reply": f"Your total spending is currently ₹{total_exp:,}. You have {len(transactions)} logged transactions."}
        if "income" in text:
            return {"reply": f"Your monthly income is set to ₹{context.get('income', 0):,}."}
        if "save" in text or "goal" in text:
            savings = context.get('income', 0) - context.get('expenses', 0)
            return {"reply": f"You are currently saving ₹{savings:,} this month. Keep it up!"}
        return {"reply": "I'm SpendWise AI! Please add your Google API Key to the .env file for advanced AI analysis. I can still give basic info if you ask about 'spending' or 'income'."}

    try:
        response = chain.invoke({
            "input": text,
            **context 
        })
        return {"reply": response}
    except Exception as e:
        return {"reply": "Connection error. Using local rules: Your current expenses are ₹" + str(context.get('expenses'))}

@app.post("/get-insight")
async def get_insight(data: dict = Body(...)):
    context = data.get("context", user_context)
    transactions = data.get("transactions", [])
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or "your_key_here" in api_key:
        # Smart Fallback Suggestion
        income = context.get('income', 1)
        expenses = context.get('expenses', 0)
        ratio = (expenses / income) * 100
        
        if ratio > 80:
            msg = "Alert: You are spending over 80% of your income. Consider reviewing your 'Others' category."
        elif ratio < 50:
            msg = "Great job! You're saving over half your income. Invest your surplus to grow your net worth."
        else:
            msg = "Your spending is balanced. To reach your goals faster, try to reduce 'Food' costs by 10%."
        return {"insight": msg}

    # Format transactions for the LLM
    t_summary = "\n".join([f"- {t['date']}: {t['desc']} ({t['cat']}) ₹{t['amount']}" for t in transactions])
    
    try:
        insight_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are SpendWise AI, an expert Financial Companion. 
            Analyze the user's income, total expenses, and specific transaction history.
            Identify patterns (e.g., high spending on food, subscription leaks, or rent burden).
            Provide a smart, professional, actionable suggestion in 1-2 powerful sentences.
            Address the user as User."""),
            ("user", f"""
            Income: ₹{context.get('income')}
            Total Expenses: ₹{context.get('expenses')}
            Transaction History:
            {t_summary if t_summary else "No transactions logged yet."}
            """)
        ])
        
        insight_chain = insight_prompt | llm | StrOutputParser()
        insight = insight_chain.invoke({})
        return {"insight": insight}
    except:
        return {"insight": "Spending is stable. Keep tracking to see long-term trends."}

@app.post("/generate-alert")
async def generate_alert(data: dict = Body(...)):
    alert_type = data.get("type")
    context = data.get("context", user_context)

    scenarios = {
        "overspending": f"User spent more than usual. Current expenses: {context.get('expenses')}, Income: {context.get('income')}",
        "bill": f"Utilities bill is due. Savings: {context.get('savings')}",
        "summary": f"End of month report. Income: {context.get('income')}, Savings: {context.get('savings')}"
    }

    scenario_text = scenarios.get(alert_type, "General update")

    notify_prompt = ChatPromptTemplate.from_messages([
        ("system", "Write a single, urgent, 10-15 word push notification for a finance app based on the scenario."),
        ("user", f"Scenario: {scenario_text}")
    ])

    notify_chain = notify_prompt | llm | StrOutputParser()
    notification_text = notify_chain.invoke({})

    return {"message": notification_text}
