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

# Basic Chat Chain
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful financial assistant."),
    ("user", "{input}")
])
chain = prompt | llm | StrOutputParser()

@app.post("/chat")
async def chat(text: str = Body(..., embed=True)):
    response = chain.invoke({"input": text})
    return {"reply": response}
