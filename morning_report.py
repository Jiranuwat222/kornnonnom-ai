import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sheets_client import get_sheet

# โหลดค่าต่างๆ จากไฟล์ .env
load_dotenv()

def send_telegram(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def generate_report():
    try:
        sheet = get_sheet()
        # ดึงข้อมูลทั้งหมดมาเป็น Dictionary
        records = sheet.get_all_records() 
        
        # ดึงยอดของ "วันนี้"
        target_date = datetime.now().strftime("%d/%m/%Y") 
        
        total_sales = 0
        menu_counts = {}
        
        # กรองและคำนวณยอด
        for row in records:
            if str(row.get('วันที่')) == target_date:
                menu = row.get('เมนู', 'ไม่ระบุ')
                qty = int(row.get('จำนวน', 0))
                price = float(row.get('ยอดรวม', 0))
                
                total_sales += price
                if menu in menu_counts:
                    menu_counts[menu] += qty
                else:
                    menu_counts[menu] = qty
        
        # สรุปข้อความส่งเข้า Telegram ฉบับ LaserPay
        if total_sales == 0:
            msg = f"⚡️ รายงานระบบ LaserPay \nประจำวันที่ ({target_date}) 📝\n\nวันนี้ยังไม่มีออเดอร์เข้ามาครับ ระบบสแตนด์บายรอให้บริการต่อไป! 🎮✨"
        else:
            best_seller = max(menu_counts, key=menu_counts.get)
            msg = f"⚡️ สรุปยอดระบบ LaserPay \nรายงานยอดเติมเกมประจำวันที่ ({target_date}) 📊\n\n"
            msg += f"💰 ยอดเติมเงินรวม: *{total_sales}* บาท\n"
            msg += f"🔥 แพ็กเกจยอดฮิต: *{best_seller}* ({menu_counts[best_seller]} แพ็ก)\n\n"
            msg += "ระบบสแตนด์บายปกติ พร้อมลุยรับออเดอร์ตลอด 24 ชม. ครับบอส! 🚀🎮"
            
        send_telegram(msg)
        print("✅ ส่งรายงานเข้า Telegram เรียบร้อยแล้ว! ลองเปิดแอปดูได้เลยครับ")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    generate_report()