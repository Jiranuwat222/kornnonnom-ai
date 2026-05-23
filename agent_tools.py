import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from sheets_client import get_sheet

load_dotenv()

# --- 🟢 ฟังก์ชันส่งแจ้งเตือน Telegram (เพิ่มสรุปยอดวันนี้) ---
def send_order_alert(menu, quantity, current_total, today_orders_count, today_total_revenue):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        return
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # จัดข้อความให้ดูสวยงามและอ่านง่าย
    msg = f"🔔 **ออเดอร์ใหม่ LaserPay เข้าแล้วครับ!** ⚡\n\n"
    msg += f"🎮 แพ็กเกจ: *{menu}*\n"
    msg += f"📦 จำนวน: *{quantity}* ชุด\n"
    msg += f"💰 ยอดบิลนี้: *{current_total:,.2f}* บาท\n"
    msg += f"------------------------\n"
    msg += f"📊 **อัปเดตยอดรวมวันนี้**\n"
    msg += f"📝 จำนวนออเดอร์: *{today_orders_count}* รายการ\n"
    msg += f"💵 รายได้รวม: *{today_total_revenue:,.2f}* บาท\n\n"
    msg += f"รีบเข้าไปดำเนินการให้ลูกค้าด่วนเลยครับบอส! 🚀"
    
    payload = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram Alert Error: {e}")

# --- 🟢 เครื่องมือจดชีตของ AI ---
def log_sale(menu: str, quantity: int, price: float) -> dict:
    total = quantity * price
    date_today = datetime.now().strftime("%d/%m/%Y")
    
    try:
        sheet = get_sheet()
        
        # 1. บันทึกออเดอร์ใหม่ลง Google Sheets ก่อน
        sheet.append_row([date_today, menu, quantity, price, total])
        
        # 2. ดึงข้อมูลทั้งหมดในชีตมาคำนวณยอดของวันนี้
        records = sheet.get_all_records()
        today_orders_count = 0
        today_total_revenue = 0
        
        for row in records:
            if str(row.get('วันที่')) == date_today:
                today_orders_count += 1
                today_total_revenue += float(row.get('ยอดรวม', 0))
        
        # 3. ส่งแจ้งเตือน Telegram พร้อมแนบยอดสรุป
        send_order_alert(menu, quantity, total, today_orders_count, today_total_revenue)
        
        return {
            "status": "success",
            "menu": menu,
            "quantity": quantity,
            "total": total
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# รวมเครื่องมือให้ AI หยิบไปใช้
TOOLS = {
    "log_sale": log_sale
}