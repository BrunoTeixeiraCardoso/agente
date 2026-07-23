import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

pasta_do_projeto = Path(__file__).parent
load_dotenv(dotenv_path=pasta_do_projeto / ".env")

# Validamos se ambas as chaves estão presentes
if not os.environ.get("GOOGLE_API_KEY") or not os.environ.get("GROQ_API_KEY"):
    raise ValueError("Erro Crítico: Certifique-se de ter as chaves GOOGLE_API_KEY e GROQ_API_KEY no seu .env!")

# CÉREBRO 1: Gemini (Excelente para ler contextos imensos e buscas)
llm_gemini = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0)

# CÉREBRO 2: Groq/Llama 3.3 (Ultra rápido, excelente para lógica e código)
llm_groq = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

