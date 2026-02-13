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
    "income": 65000,
    "savings": 12000,
    "debt": 5000,
    "goals": ["buy a house", "pay off student loans"]
}

# --- 2. UPDATED PROMPT ---
system_template = """
You are a Financial Assistant. Use this data to answer:
User: {name} | Income: ${income} | Savings: ${savings} | Debt: {debt} | Goals: {goals}
Keep answers concise and helpful.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("user", "{input}")
])
chain = prompt | llm | StrOutputParser()

@app.post("/chat")
async def chat(text: str = Body(..., embed=True)):
    # Inject context into every message
    response = chain.invoke({
        "input": text,
        **user_context 
    })
    return {"reply": response}

@app.post("/generate-alert")
async def generate_alert(data: dict = Body(...)):
    alert_type = data.get("type")

    # Define Scenarios based on User Context
    scenarios = {
        "overspending": f"User spent $500 on dinner. Monthly budget is exceeded. Income: {user_context['income']}",
        "bill": f"Student Loan payment of $200 is due tomorrow. Savings: {user_context['savings']}",
        "summary": f"End of month report. Saved $500, Debt reduced by $100. Goals: {user_context['goals']}"
    }

    scenario_text = scenarios.get(alert_type, "General update")

    # Ask Gemini to write a notification
    notify_prompt = ChatPromptTemplate.from_messages([
        ("system", "Write a single, urgent, 10-15 word push notification for a finance app based on the scenario."),
        ("user", f"Scenario: {scenario_text}")
    ])

    notify_chain = notify_prompt | llm | StrOutputParser()
    notification_text = notify_chain.invoke({})

    return {"message": notification_text}
