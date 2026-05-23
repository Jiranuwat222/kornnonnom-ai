import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv
from sheets_client import get_sheet

# 1. โหลด env variables จาก .env
load_dotenv()

# --- 🟢 ฟังก์ชันส่งแจ้งเตือนเข้า Telegram ทันทีที่มีออเดอร์ ---
def send_order_alert(menu, quantity, total):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        return
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    msg = f"🔔 **ออเดอร์ LaserPay เข้าแล้วครับบอส!** ⚡\n\n🎮 แพ็กเกจ: *{menu}*\n📦 จำนวน: *{quantity}* ชุด\n💰 ยอดรวม: *{total}* บาท\n\nรีบเข้าไปดำเนินการให้ลูกค้าด่วนเลยครับ! 🚀"
    
    payload = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram Alert Error: {e}")

# --- 🟢 ฟังก์ชันให้ AI บันทึกชีต + เรียกแจ้งเตือน ---
def log_sale_to_sheet(menu: str, quantity: int, price: float, total: float):
    date_today = datetime.now().strftime("%d/%m/%Y")
    sheet = get_sheet()
    row_data = [date_today, menu, quantity, price, total]
    sheet.append_row(row_data)
    
    # พอจดออเดอร์ลงชีตเสร็จ ให้ส่งแจ้งเตือนเข้า Telegram ทันที
    send_order_alert(menu, quantity, total)

# --- ฟังก์ชันเดิม: สำหรับให้รับค่าจาก Terminal ---
def log_sales():
    if len(sys.argv) < 2:
        print("กรุณาใส่ข้อมูลในรูปแบบ 'เมนู:จำนวน:ราคา'")
        return

    data = sys.argv[1]
    
    try:
        menu, quantity, price = data.split(':')
        quantity = int(quantity)
        price = float(price)
        total = quantity * price
        
        log_sale_to_sheet(menu, quantity, price, total)
        print(f"✅ บันทึกออเดอร์สำเร็จ: {menu} ยอดรวม {total} บาท")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    log_sales()