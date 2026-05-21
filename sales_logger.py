import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sheets_client import get_sheet

# 1. โหลด env variables จาก .env
load_dotenv()

def log_sales():
    if len(sys.argv) < 2:
        print("กรุณาใส่ข้อมูลในรูปแบบ 'เมนู:จำนวน:ราคา'")
        return

    data = sys.argv[1]
    
    try:
        # 3. รับยอดขายจาก command line
        menu, quantity, price = data.split(':')
        quantity = int(quantity)
        price = float(price)

        # 4. คำนวณยอดรวม
        total = quantity * price
        date_today = datetime.now().strftime("%d/%m/%Y")

        # 5. เพิ่มแถวใหม่ลงใน Google Sheets
        sheet = get_sheet()
        row_data = [date_today, menu, quantity, price, total]
        sheet.append_row(row_data)

        print(f"✅ บันทึกยอดขายสำเร็จ: {menu} จำนวน {quantity} แก้ว ยอดรวม {total} บาท")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    log_sales()