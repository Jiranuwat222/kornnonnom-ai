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

# คำสั่งบังคับให้ AI ทำตัวเป็น Agent และตอบเป็น JSON เท่านั้น
SYSTEM_INSTRUCTION = """
คุณคือ Kornnonnom ผู้ช่วย AI ของร้าน Kornnonnom Cafe
หน้าที่ของนักศึกษาคือแปลงคำสั่งภาษาไทยเป็น JSON action
ตอบกลับเป็น JSON เท่านั้น ในรูปแบบ:
{"action": "log_sale", "args": {"menu": "...", "quantity": N, "price": N}}
ถ้าคำสั่งไม่ใช่การบันทึกยอดขาย ตอบ: {"action": "unknown", "args": {}}
"""

TRACE_FILE = "agent_trace.log"

def write_trace(event: str, data: dict) -> None:
    """ฟังก์ชันสำหรับแอบจดบันทึกว่า AI คิดและทำอะไรบ้าง"""
    with open(TRACE_FILE, "a", encoding="utf-8") as f:
        record = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            **data,
        }
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def run_agent(user_input: str) -> str:
    write_trace("user_input", {"message": user_input})

    # ส่งข้อความไปให้ Gemini คิด
    response = client.models.generate_content(
        model=MODEL,
        contents=f"{SYSTEM_INSTRUCTION}\n\nคำสั่ง: {user_input}",
    )
    raw = response.text.strip()
    write_trace("llm_response", {"raw": raw})

    # --- เพิ่ม 4 บรรทัดนี้เพื่อล้าง Markdown ที่ AI แถมมา ---
    raw = raw.removeprefix("```json")
    raw = raw.removeprefix("```")
    raw = raw.removesuffix("```")
    raw = raw.strip()
    # ----------------------------------------

    # พยายามถอดรหัส JSON ที่ AI ตอบกลับมา
    try:
        action_data = json.loads(raw)
    except json.JSONDecodeError:
        return "❌ AI ตอบกลับในรูปแบบที่ไม่ถูกต้อง"

    action = action_data.get("action")
    args = action_data.get("args", {})

    # เช็กว่าคำสั่งที่ AI บอกมา มีอยู่ในกล่องเครื่องมือเราไหม
    if action not in TOOLS:
        return f"⚠️ ไม่รู้จัก action: {action}"

    # สั่งให้เครื่องมือทำงาน
    try:
        result = TOOLS[action](**args)
        write_trace("tool_result", {"action": action, "result": result})
        return (
            f"✅ บันทึกสำเร็จ: {result['menu']} "
            f"x{result['quantity']} = {result['total']} บาท"
        )
    except (ValueError, TypeError) as e:
        write_trace("tool_error", {"action": action, "error": str(e)})
        return f"❌ ข้อมูลไม่ถูกต้อง: {e}"

if __name__ == "__main__":
    print("Kornnonnom Agent พร้อมรับคำสั่ง (พิมพ์ 'exit' เพื่อออก)\n")
    while True:
        user_input = input("คุณ: ").strip()
        if user_input.lower() == "exit":
            break
        print(f"Kornnonnom: {run_agent(user_input)}\n")