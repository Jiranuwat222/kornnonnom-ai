# agent_harness.py
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

    def run(self, user_input: str, context: str = "") -> str:
        self.write_trace("user_input", {"message": user_input})

        # อัปเกรดสมองกล: สั่งให้ตอบกลับทั้งแชทและ JSON Action
        system_prompt = f"""
        คุณคือ Kornnonnom ผู้ช่วย AI สุดเท่ของร้าน Kornnonnom Cafe รอบดึก
        
        กฎการทำงานของคุณ:
        คุณต้องตอบกลับเป็นรูปแบบ JSON เสมอ โดยมีโครงสร้างดังนี้:
        {{
            "reply": "ข้อความที่คุณต้องการตอบลูกค้า (ตอบคำถาม, ชวนคุย, หรือยืนยันออเดอร์ สไตล์วัยรุ่นนอนดึก)",
            "action": "ชื่อเครื่องมือ (ถ้ามีการสั่งเครื่องดื่มให้ใช้ 'log_sale', ถ้าไม่มีให้ใส่ 'none')",
            "args": {{"menu": "ชื่อเมนู", "quantity": จำนวน, "price": ราคาต่อ 1 แก้ว}}
        }}
        
        ตัวอย่างที่ 1 (ลูกค้าถามด้วย และสั่งด้วย): "มิลค์ทีหมดรึยัง เอา 4 แก้ว"
        {{
            "reply": "มิลค์ทียังไม่หมดครับผม! จัดไป 4 แก้วแบบตาค้างกันไปเลย 🦉✨",
            "action": "log_sale",
            "args": {{"menu": "มิลค์ทีสายนอนน้อย", "quantity": 4, "price": 55}}
        }}

        ตัวอย่างที่ 2 (ลูกค้าแค่ชวนคุย หรือถามข้อมูลเฉยๆ): "ร้านเปิดกี่โมงครับ"
        {{
            "reply": "ร้านเปิด 18:00 - 02:00 น. ครับผม แวะมานั่งชิลๆ โต้รุ่งด้วยกันได้เลย! 🌙",
            "action": "none",
            "args": {{}}
        }}

        ข้อมูลร้านสำหรับตอบคำถาม หรือดูราคาเครื่องดื่ม:
        {context}
        """

        response = self.client.models.generate_content(
            model=MODEL,
            contents=f"{system_prompt}\n\nคำสั่งจากลูกค้า: {user_input}",
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
                
                # เอากลับมาผูกรวมกัน: คำตอบจาก AI + ข้อความยืนยันจากระบบ
                return f"{reply_text}\n\n*(✅ ระบบหลังบ้าน: บันทึก {result['menu']} จำนวน {result['quantity']} แก้ว ยอดรวม {result['total']} บาท ลงชีตเรียบร้อย)*"
            else:
                return reply_text
                
        except json.JSONDecodeError:
            return raw # เผื่อ AI หลุดกรอบ ตอบมาเป็นข้อความธรรมดา
        except Exception as e:
            return f"❌ ข้อมูลไม่ถูกต้อง หรือไม่มีเมนูนี้ครับ: {e}"