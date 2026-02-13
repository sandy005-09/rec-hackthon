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
    text = data.get("text")
    context = data.get("context", user_context)
    
    response = chain.invoke({
        "input": text,
        **context 
    })
    return {"reply": response}

@app.post("/get-insight")
async def get_insight(data: dict = Body(...)):
    context = data.get("context", user_context)
    transactions = data.get("transactions", [])
    
    # Format transactions for the LLM
    t_summary = "\n".join([f"- {t['date']}: {t['desc']} ({t['cat']}) ₹{t['amount']}" for t in transactions])
    
    insight_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert Financial Companion. 
        Analyze the user's income, total expenses, and specific transaction history.
        Identify patterns (e.g., high spending on food, subscription leaks, or rent burden).
        Provide a smart, professional, actionable suggestion in 1-2 powerful sentences.
        Address the user as Alex."""),
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
