# app.py
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from rag_engine import RAGEngine

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = "gemini-2.5-flash"

@st.cache_resource
def load_rag():
    # ดึงข้อมูลจากคู่มือร้านเวอร์ชันนอนดึก
    return RAGEngine("knowledge/kornnonnom_kb.txt")

rag = load_rag()

# ตั้งค่าหน้าเว็บให้ดูทันสมัย
st.set_page_config(page_title="Kornnonnom AI", page_icon="🥛", layout="centered")

st.title("🥛 Kornnonnom Bot v2.0")
st.subheader("เพื่อนซี้คนนอนดึก แห่ง Kornnonnom Cafe ✨")
st.caption("ง่วงนอน อ่านหนังสือสอบ หรือหิวดึก? ถามเรื่องเมนูและเวลาเปิดปิดกับเราได้เลย!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("คุยกับบอทก่อนนอนนมตรงนี้เลย..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # RAG: ค้นหาข้อมูลจากคู่มือรอบดึก
    context_chunks = rag.search(prompt, top_k=3)
    context = "\n---\n".join(context_chunks)

    # Generate: ปรับ System Prompt ให้ทันสมัย วัยรุ่นชอบ มีความยืดหยุ่นและเป็นกันเอง
    full_prompt = f"""คุณคือ Kornnonnom (ก่อนนอนนม) บอทผู้ช่วยสุดเท่และทันสมัยของร้าน Kornnonnom Cafe 
ตอบคำถามลูกค้าด้วยความเป็นกันเอง ใช้หางเสียง "ครับ" หรือ "ครับผม" มีความสปอร์ตและเข้าใจคนนอนดึก (เช่น นักศึกษาอ่านหนังสือสอบ, คนเล่นเกม, คนทำงานดึก)

กฎเหล็ก:
1. ตอบคำถามโดยใช้ข้อมูลที่ให้ไว้ด้านล่างนี้เท่านั้น
2. ถ้าในข้อมูลไม่มีสิ่งที่ลูกค้าถาม ให้ตอบสุภาพและเป็นกันเองว่าไม่ทราบ หรือแนะนำให้ทัก DM ไปหาพี่กวาง (Thanet) เจ้าของร้านโดยตรง อย่าเมคข้อมูลเองเด็ดขาด

ข้อมูลร้าน:
{context}

คำถามจากลูกค้า: {prompt}
"""
    response = client.models.generate_content(model=MODEL, contents=full_prompt)
    answer = response.text

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)