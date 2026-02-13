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
    "name": "Alex",
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
Analyze the balance and provide professional, actionable advice.
Keep answers concise.
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
    
    insight_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a financial advisor. Look at the income vs expense ratio and provide a one-sentence high-impact insight."),
        ("user", f"Income: {context.get('income')}, Expenses: {context.get('expenses')}")
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
