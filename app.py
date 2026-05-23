import os
import streamlit as st
from dotenv import load_dotenv
from rag_engine import RAGEngine
from agent_harness import AgentHarness

load_dotenv()

@st.cache_resource
def load_rag():
    return RAGEngine("knowledge/laserpay_kb.txt") 

@st.cache_resource
def load_agent():
    return AgentHarness()

rag = load_rag()
agent = load_agent()

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="LaserPay AI", page_icon="⚡", layout="centered", initial_sidebar_state="expanded")

# --- 🟢 ระบบใหม่: จัดการปุ่มกดเมนูลัด ---
if "preset_prompt" not in st.session_state:
    st.session_state.preset_prompt = None

def set_prompt(text):
    st.session_state.preset_prompt = text

# 2. Sidebar แถบด้านข้าง
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚡ LaserPay Top-up</h2>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=800&q=80", use_container_width=True)
    
    st.success("🟢 บอทสแตนด์บาย 24 ชั่วโมง")
    st.markdown("---")
    st.markdown("### 🎮 กดเลือกเกมเพื่อดูราคา")
    
    # เปลี่ยนจากเมนู Dropdown เป็นปุ่มกด (Button)
    if st.button("🟦 Roblox", use_container_width=True):
        set_prompt("ขอดูแพ็กเกจและราคาของเกม Roblox ทั้งหมดหน่อยครับ")
        
    if st.button("🔫 Valorant", use_container_width=True):
        set_prompt("ขอดูแพ็กเกจและราคาของเกม Valorant ทั้งหมดหน่อยครับ")
        
    if st.button("⚔️ RoV: Arena of Valor", use_container_width=True):
        set_prompt("ขอดูแพ็กเกจและราคาของเกม RoV ทั้งหมดหน่อยครับ")

    if st.button("🎭 Identity V", use_container_width=True):
        set_prompt("ขอดูแพ็กเกจและราคาของเกม Identity V ทั้งหมดหน่อยครับ")

    if st.button("👊 One Punch Man", use_container_width=True):
        set_prompt("ขอดูแพ็กเกจและราคาของเกม One Punch Man ทั้งหมดหน่อยครับ")

# 3. Header ตกแต่งตัวหนังสือเรืองแสง
st.markdown("""
<div style="text-align: center; padding: 10px;">
    <h1 style="color: #ffffff; text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #00e676, 0 0 40px #00e676; font-size: 42px;">
        ⚡ LaserPay Bot
    </h1>
    <p style="color: #A0AEC0; font-size: 16px;">เติมเกมไว ดั่งใจนึก สไตล์ LaserPay! พิมพ์ชื่อเกมและแพ็กเกจได้เลย 🎮</p>
</div>
<hr>
""", unsafe_allow_html=True)

# 4. ระบบแชท
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    avatar_icon = "⚡" if msg["role"] == "assistant" else "🎮"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.write(msg["content"])

# --- 🟢 ระบบประมวลผลแชท (รองรับทั้งการพิมพ์เอง และการกดปุ่ม) ---
user_input = st.chat_input("ตัวอย่าง: เติมแพ็ก 800 โรบัก 1 แพ็ก")

# ถ้ามีการกดปุ่มมาจาก Sidebar ให้ใช้ข้อความจากปุ่มแทน
if st.session_state.preset_prompt:
    user_input = st.session_state.preset_prompt
    st.session_state.preset_prompt = None # เคลียร์ค่าทิ้งหลังจากดึงมาใช้แล้ว

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🎮"):
        st.write(user_input)

    with st.spinner("บอทกำลังค้นหาแพ็กเกจสุดคุ้ม..."):
        context_chunks = rag.search(user_input, top_k=3)
        context = "\n---\n".join(context_chunks)
        
        # 🟢 ส่งประวัติแชททั้งหมด (ยกเว้นข้อความล่าสุด) ไปให้บอทด้วย เพื่อให้มันจำบริบทได้
        past_history = st.session_state.messages[:-1] 
        answer = agent.run(user_input, context, past_history)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant", avatar="⚡"):
        st.write(answer)