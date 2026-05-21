import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sheets_client import get_sheet

# 1. โหลด env variables จาก .env
load_dotenv()

# --- 🟢 ฟังก์ชันใหม่: สำหรับให้ AI (agent_tools) ส่งข้อมูลเข้ามาบันทึก ---
def log_sale_to_sheet(menu: str, quantity: int, price: float, total: float):
    date_today = datetime.now().strftime("%d/%m/%Y")
    sheet = get_sheet()
    row_data = [date_today, menu, quantity, price, total]
    sheet.append_row(row_data)

# --- ฟังก์ชันเดิม: สำหรับให้รับค่าจาก Terminal (แก้ให้มาเรียกใช้ฟังก์ชันด้านบนแทน) ---
def log_sales():
    if len(sys.argv) < 2:
        print("กรุณาใส่ข้อมูลในรูปแบบ 'เมนู:จำนวน:ราคา'")
        return

    data = sys.argv[1]
    
    try:
        # รับยอดขายจาก command line
        menu, quantity, price = data.split(':')
        quantity = int(quantity)
        price = float(price)

        # คำนวณยอดรวม
        total = quantity * price
        
        # เรียกใช้ฟังก์ชันด้านบนเพื่อบันทึกชีต
        log_sale_to_sheet(menu, quantity, price, total)

        print(f"✅ บันทึกยอดขายสำเร็จ: {menu} จำนวน {quantity} แก้ว ยอดรวม {total} บาท")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    log_sales()