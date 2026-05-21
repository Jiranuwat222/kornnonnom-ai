import os
import streamlit as st
from dotenv import load_dotenv
from rag_engine import RAGEngine
from agent_harness import AgentHarness

load_dotenv()

@st.cache_resource
def load_rag():
    return RAGEngine("knowledge/kornnonnom_kb.txt")

@st.cache_resource
def load_agent():
    return AgentHarness()

rag = load_rag()
agent = load_agent()

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Kornnonnom AI", page_icon="🌙", layout="centered", initial_sidebar_state="expanded")

# 2. Sidebar แถบด้านข้าง (เพิ่มปุ่ม Telegram)
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🌙 Kornnonnom Cafe</h2>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1541167760496-1628856ab772?auto=format&fit=crop&w=800&q=80", use_container_width=True)
    
    st.success("🟢 เปิดบริการ 18:00 - 02:00 น.")
    
    with st.expander("ดูเมนูฮิตคนนอนดึก 🦉"):
        st.write("🍯 ลาเต้น้ำผึ้งโต้รุ่ง (65.-)")
        st.write("🧋 มิลค์ทีสายนอนน้อย (55.-)")
        st.write("🍓 สตรอว์เบอร์รี่มิลค์ (60.-)")
        
    st.markdown("---")
    st.markdown("**เครื่องมือแอดมิน 🛠️**")
    # ปุ่มส่งยอดเข้า Telegram
    if st.button("📲 ส่งสรุปยอดเข้า Telegram", use_container_width=True):
        with st.spinner("กำลังส่งข้อมูล..."):
            os.system("python morning_report.py")
        st.success("ส่งแจ้งเตือนเรียบร้อย!")

# 3. Header ตกแต่งตัวหนังสือเรืองแสง (Neon Style)
st.markdown("""
<div style="text-align: center; padding: 10px;">
    <h1 style="color: #ffffff; text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #00e6e6, 0 0 40px #00e6e6; font-size: 42px;">
        🥛 Kornnonnom Bot v2.0
    </h1>
    <p style="color: #A0AEC0; font-size: 16px;">เพื่อนซี้คนนอนดึก ✨ หิวดึกหรืออยากสั่งน้ำ พิมพ์ออเดอร์มาได้เลย!</p>
</div>
<hr>
""", unsafe_allow_html=True)

# 4. ระบบแชท
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    avatar_icon = "🥛" if msg["role"] == "assistant" else "🦉"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.write(msg["content"])

if prompt := st.chat_input("ตัวอย่าง: สั่งลาเต้น้ำผึ้งโต้รุ่ง 1 แก้ว"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🦉"):
        st.write(prompt)

    with st.spinner("บอทกำลังคิด..."):
        context_chunks = rag.search(prompt, top_k=3)
        context = "\n---\n".join(context_chunks)
        
        # ส่งให้ Agent ตัดสินใจว่าจะตอบคำถาม หรือจดลง Google Sheets
        answer = agent.run(prompt, context)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant", avatar="🥛"):
        st.write(answer)
        