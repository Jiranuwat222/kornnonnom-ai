# Caption generator for Kornnonnom cafe Instagram posts
# - Load GOOGLE_API_KEY from .env file
# - Use Gemini 2.5 Flash to generate 3 caption variants
# - Take menu name and price as input
# - Output: 3 caption styles (cute, minimal, gen-z)
import os
from dotenv import load_dotenv
from google import genai  # <-- เปลี่ยนมาใช้แพ็กเกจตัวใหม่

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# สร้าง Client แบบใหม่
client = genai.Client(api_key=api_key)

def generate_captions(menu_name, price):
    prompt = f"""สร้างแคปชั่นอินสตาแกรม 3 แบบสำหรับเมนูคาเฟ่ Kornnonnom
เมนู: {menu_name}
ราคา: {price}

สร้างแคปชั่น 3 แบบในภาษาไทย โดยใช้ภาษาที่เป็นกันเองและน่ารัก:
1. Cute: แบบน่ารักน่าเอ็นดู มีอีโมจิและคำพูดที่อบอุ่น
2. Minimal: แบบสะอาด เรียบง่าย สะบายตา สั้นกระชับ
3. Gen-Z: แบบเทรนด์ มีสแลง เป็นกันเอง มีแฮชแท็ก

จัดรูปแบบการตอบเป็น:
Cute: [แคปชั่น]
Minimal: [แคปชั่น]
Gen-Z: [แคปชั่น]
"""
    
    # เรียกใช้โมเดล Gemini 2.5 Flash
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text

if __name__ == "__main__":
    menu_name = input("ใส่ชื่อเมนู: ")
    price = input("ใส่ราคา: ")
    captions = generate_captions(menu_name, price)
    print("\n--- ผลลัพธ์ ---")
    print(captions)