import json
import os
from datetime import datetime
from dotenv import load_dotenv

# หากคุณใช้ google-generativeai แบบเก่า ให้แก้บรรทัด import ตามเดิมที่คุณมีนะครับ
from google import genai 

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = "gemini-2.5-flash"
TRACE_FILE = "agent_trace.log"

class AgentHarness:
    def __init__(self):
        self.client = client

    def write_trace(self, event: str, data: dict) -> None:
        try:
            with open(TRACE_FILE, "a", encoding="utf-8") as f:
                record = {"timestamp": datetime.now().isoformat(), "event": event, **data}
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except:
            pass

    def run(self, user_input: str, context: str = "", history: list = None) -> dict: # 🟢 บังคับ Return เป็น dict
        self.write_trace("user_input", {"message": user_input})

        history_text = "ไม่มีประวัติการคุยก่อนหน้า"
        if history and len(history) > 0:
            history_text = ""
            for msg in history[-4:]:
                role = "ลูกค้า" if msg["role"] == "user" else "แอดมิน"
                history_text += f"{role}: {msg['content']}\n"

        system_prompt = f"""
        คุณคือ AI แอดมินสุดล้ำของร้าน "LaserPay" บริการรับเติมเกมออนไลน์
        
        กฎเหล็กของคุณ:
        1. คุณต้องตอบกลับเป็นรูปแบบ JSON เสมอ ห้ามพิมพ์ข้อความธรรมดาเด็ดขาด
        2. หากลูกค้าแค่ "ถามราคา/ทักทาย" ให้ใช้ action: "none"
        3. หากลูกค้า "สั่งซื้อแพ็กเกจ" (เช่น เอา 2 ชุด, เติมอันนี้) ให้ใช้ action: "request_id" เพื่อส่งให้ระบบเปิด Popup ทันที ห้ามคิดเองว่าจดลงชีตแล้ว
        
        โครงสร้าง JSON ที่ต้องตอบกลับ:
        {{
            "reply": "ข้อความตอบลูกค้า (ถ้าสั่งซื้อให้บอกลูกค้าว่า 'รบกวนระบุ ID ในหน้าต่างที่เด้งขึ้นมาเพื่อยืนยันออเดอร์เลยคร้าบ 🚀')",
            "action": "request_id หรือ none",
            "args": {{"menu": "ชื่อแพ็กเกจ+ชื่อเกม", "quantity": จำนวนแพ็กเกจ (ตัวเลข), "price": ราคาต่อ 1 แพ็กเกจ (ตัวเลข)}}
        }}
        
        ประวัติการสนทนาล่าสุด:
        {history_text}

        ข้อมูลแพ็กเกจเกมของร้าน:
        {context}
        """

        try:
            response = self.client.models.generate_content(
                model=MODEL,
                contents=f"{system_prompt}\n\nคำสั่งล่าสุดจากลูกค้า: {user_input}",
            )
            raw = response.text.strip()
            self.write_trace("llm_response", {"raw": raw})

            # ล้างพวก Markdown tags เผื่อ AI ใส่มา
            clean_raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            
            # 🟢 แปลงข้อความเป็น Dictionary เพื่อส่งให้ app.py เอาไปเปิด Popup
            action_data = json.loads(clean_raw)
            
            return {
                "reply": action_data.get("reply", "รับทราบครับ!"),
                "action": action_data.get("action", "none"),
                "args": action_data.get("args", {})
            }
        except Exception as e:
            # กรณี AI ไม่ส่งเป็น JSON หรือพัง
            self.write_trace("error", {"message": str(e)})
            return {
                "reply": "กำลังประมวลผลคำสั่งซื้อครับ รบกวนรอสักครู่...",
                "action": "none",
                "args": {}
            }