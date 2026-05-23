import os
import re # 🟢 นำเข้า library regex สำหรับจัดการข้อความพิมพ์ติดกัน
import streamlit as st
from dotenv import load_dotenv
from rag_engine import RAGEngine
from agent_harness import AgentHarness
from agent_tools import TOOLS 

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
    
    # 🟢 1. ดึงรูปโลโก้ laserpay.png มาใช้
    st.image("laserpay.png", use_container_width=True)
    
    # 🟢 2. เปลี่ยนป้ายสถานะบอทให้ดูมินิมอล มีไฟกระพริบแบบล้ำๆ
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; background-color: rgba(0, 230, 118, 0.1); padding: 8px; border-radius: 8px; border: 1px solid rgba(0, 230, 118, 0.3); margin-top: 10px; margin-bottom: 15px;">
        <div style="width: 10px; height: 10px; background-color: #00e676; border-radius: 50%; box-shadow: 0 0 10px #00e676; margin-right: 10px; animation: pulse 2s infinite;"></div>
        <span style="color: #00e676; font-weight: 600; font-size: 14px;">AI แอดมินพร้อมให้บริการ 24 ชม.</span>
    </div>
    <style>
        @keyframes pulse {
            0% { opacity: 1; box-shadow: 0 0 10px #00e676; }
            50% { opacity: 0.4; box-shadow: 0 0 2px #00e676; }
            100% { opacity: 1; box-shadow: 0 0 10px #00e676; }
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎮 กดเลือกเกมเพื่อดูราคา")
    
    # 🟢 เลย์เอาต์ปุ่มเป็นแบบ 2 คอลัมน์ ประหยัดพื้นที่
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🟦 Roblox", use_container_width=True):
            set_prompt("ขอดูแพ็กเกจและราคาของเกม Roblox ทั้งหมดหน่อยครับ")
        if st.button("⚔️ RoV", use_container_width=True):
            set_prompt("ขอดูแพ็กเกจและราคาของเกม RoV ทั้งหมดหน่อยครับ")
        if st.button("👊 OPM", use_container_width=True):
            set_prompt("ขอดูแพ็กเกจและราคาของเกม One Punch Man ทั้งหมดหน่อยครับ")
            
    with col2:
        if st.button("🔫 Valorant", use_container_width=True):
            set_prompt("ขอดูแพ็กเกจและราคาของเกม Valorant ทั้งหมดหน่อยครับ")
        if st.button("🎭 Identity V", use_container_width=True):
            set_prompt("ขอดูแพ็กเกจและราคาของเกม Identity V ทั้งหมดหน่อยครับ")

# 3. Header ตกแต่งตัวหนังสือเรืองแสง และ CSS กันหน้าจอกระตุก
st.markdown("""
<style>
    html { scroll-behavior: smooth; }
    .stChatMessage { animation: fadeIn 0.3s ease-in-out; }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
</style>
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

# --- 🟢 ฟังก์ชันสร้างหน้าต่าง Popup (Dialog) กลางจอ ---
@st.dialog("🛒 ยืนยันคำสั่งซื้อ LaserPay")
def order_popup(menu, quantity, price):
    total = quantity * price
    
    st.write(f"🎮 **เกม/แพ็กเกจ:** {menu}")
    st.write(f"📦 **จำนวน:** {quantity} ชุด")
    st.write(f"💰 **ยอดชำระรวม:** {total:,.2f} บาท")
    st.markdown("---")
    
    # 🟢 เพิ่ม Mockup QR Code อัจฉริยะ (รูป QR เปลี่ยนตามออเดอร์อัตโนมัติ)
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown("📲 **สแกน QR Code เพื่อชำระเงิน**")
    
    # สร้างข้อมูลที่จะฝังใน QR (เช่น ชื่อเมนู และยอดเงิน)
    qr_data = f"LaserPay Order: {menu} | Total: {total} THB"
    # เรียกใช้ API ฟรีเพื่อแปลงข้อความเป็นรูป QR Code
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_data}"
    
    st.image(qr_url, width=150)
    st.caption("*(ระบบจำลอง: สแกนเพื่อดูข้อมูลสรุปออเดอร์ ไม่มีการตัดเงินจริง)*")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ช่องให้ลูกค้ากรอก ID
    game_id = st.text_input("🔑 รบกวนระบุ ID เกม / UID / Riot ID:", placeholder="เช่น id: 1234567")
    
    # เปลี่ยนชื่อปุ่มให้เข้ากับโฟลว์การสแกนจ่าย
    if st.button("✅ ยืนยันและโอนเงินเรียบร้อย!", use_container_width=True):
        if game_id:
            with st.spinner("กำลังจดออเดอร์ลงระบบ..."):
                full_menu_name = f"{menu} (UID: {game_id})"
                
                result = TOOLS["log_sale"](full_menu_name, quantity, price)
                
                if result.get("status") == "success":
                    success_msg = f"🎉 เติมแพ็กเกจ **{menu}** ให้ไอดี `{game_id}` เรียบร้อยคร้าบ! รอกดรับของในเกมได้เลย 🚀\n\n*(✅ ระบบหลังบ้าน: บันทึกออเดอร์ลงชีตเรียบร้อย)*"
                    st.session_state.messages.append({"role": "assistant", "content": success_msg})
                    st.rerun() 
        else:
            st.error("⚠️ รบกวนกรอก ID เกมก่อนกดรับออเดอร์นะคร้าบ")

# --- 🟢 ระบบประมวลผลแชท (รองรับทั้งการพิมพ์เอง และการกดปุ่ม) ---
user_input = st.chat_input("พิมพ์ตรงนี้..")

if st.session_state.preset_prompt:
    user_input = st.session_state.preset_prompt
    st.session_state.preset_prompt = None 

if user_input:
    # 🟢 เพิ่มการจัดฟอร์แมตข้อความ (Regex) แยกไทย-อังกฤษ
    clean_input = re.sub(r'([ก-๙])([a-zA-Z])', r'\1 \2', user_input)
    clean_input = re.sub(r'([a-zA-Z])([ก-๙])', r'\1 \2', clean_input)

    st.session_state.messages.append({"role": "user", "content": user_input}) # โชว์ข้อความเดิมที่ลูกค้าพิมพ์
    with st.chat_message("user", avatar="🎮"):
        st.write(user_input)

    with st.spinner("บอทกำลังค้นหาแพ็กเกจสุดคุ้ม..."):
        # 🟢 ใช้ clean_input ที่เว้นวรรคแล้วส่งไปให้ RAG และ AI
        context_chunks = rag.search(clean_input, top_k=3)
        context = "\n---\n".join(context_chunks)
        
        past_history = st.session_state.messages[:-1] 
        response_data = agent.run(clean_input, context, past_history)
        
        if isinstance(response_data, dict):
            reply_text = response_data.get("reply", "ระบบกำลังประมวลผล...")
            action = response_data.get("action", "none")
            args = response_data.get("args", {})
        else:
            reply_text = str(response_data)
            action = "none"
            args = {}

    st.session_state.messages.append({"role": "assistant", "content": reply_text})
    with st.chat_message("assistant", avatar="⚡"):
        st.write(reply_text)
        
    if action == "request_id":
        order_popup(args.get("menu", "แพ็กเกจไม่ระบุ"), args.get("quantity", 1), args.get("price", 0))