import json
import os
from datetime import datetime

from dotenv import load_dotenv
from google import genai

from agent_tools import TOOLS

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = "gemini-2.5-flash"
TRACE_FILE = "agent_trace.log"

class AgentHarness:
    def __init__(self):
        self.client = client

    def write_trace(self, event: str, data: dict) -> None:
        with open(TRACE_FILE, "a", encoding="utf-8") as f:
            record = {
                "timestamp": datetime.now().isoformat(),
                "event": event,
                **data,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # 🟢 เพิ่มประวัติแชท (history) เข้ามาเป็นตัวแปร
    def run(self, user_input: str, context: str = "", history: list = None) -> str:
        self.write_trace("user_input", {"message": user_input})

        # 🟢 จัดรูปแบบประวัติการคุย (ดึงมา 4 ข้อความล่าสุด เพื่อให้บอทจำได้ว่ากำลังคุยเกมอะไรอยู่)
        history_text = "ไม่มีประวัติการคุยก่อนหน้า"
        if history and len(history) > 0:
            history_text = ""
            for msg in history[-4:]:
                role = "ลูกค้า" if msg["role"] == "user" else "แอดมิน"
                history_text += f"{role}: {msg['content']}\n"

        system_prompt = f"""
        คุณคือ AI แอดมินสุดล้ำของร้าน "LaserPay" บริการรับเติมเกมออนไลน์
        
        กฎการทำงานของคุณ:
        คุณต้องตอบกลับเป็นรูปแบบ JSON เสมอ โดยมีโครงสร้างดังนี้:
        {{
            "reply": "ข้อความตอบลูกค้า (สไตล์เกมเมอร์ เป็นกันเอง กระตือรือร้น รวดเร็ว)",
            "action": "ชื่อเครื่องมือ (ถ้ามีการสั่งเติมเกมให้ใช้ 'log_sale', ถ้าไม่มีให้ใส่ 'none')",
            "args": {{"menu": "ชื่อแพ็กเกจ+ชื่อเกม", "quantity": จำนวนแพ็กเกจ, "price": ราคาต่อ 1 แพ็กเกจ}}
        }}
        
        ประวัติการสนทนาล่าสุด (สำคัญมาก!):
        {history_text}
        *คำแนะนำ: หากลูกค้าสั่งแพ็กเกจแบบย่อๆ (เช่น "300 2แพ็ค") ให้คุณดูจาก 'ประวัติการสนทนาล่าสุด' ว่าก่อนหน้านี้ลูกค้ากำลังคุยเรื่องเกมอะไรอยู่ แล้วสรุปออเดอร์ให้ตรงกับเกมนั้น*

        ข้อมูลแพ็กเกจเกมของร้าน:
        {context}
        """

        response = self.client.models.generate_content(
            model=MODEL,
            contents=f"{system_prompt}\n\nคำสั่งล่าสุดจากลูกค้า: {user_input}",
        )
        raw = response.text.strip()
        self.write_trace("llm_response", {"raw": raw})

        clean_raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        try:
            action_data = json.loads(clean_raw)
            reply_text = action_data.get("reply", "รับทราบครับผม!")
            action = action_data.get("action", "none")
            args = action_data.get("args", {})

            if action == "log_sale" and action in TOOLS:
                result = TOOLS[action](**args)
                self.write_trace("tool_result", {"action": action, "result": result})
                
                if result.get("status") == "success":
                    return f"{reply_text}\n\n*(✅ ระบบหลังบ้าน: บันทึกออเดอร์ {result['menu']} จำนวน {result['quantity']} แพ็ก ยอดรวม {result['total']} บาท ลงชีตเรียบร้อย)*"
                else:
                    return f"❌ เกิดข้อผิดพลาด: {result.get('message')}"
            else:
                return reply_text
                
        except json.JSONDecodeError:
            return raw 
        except Exception as e:
            return f"❌ ข้อมูลแพ็กเกจไม่ถูกต้อง หรือไม่มีในระบบครับ: {e}"