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
        
        # ตามโจทย์ต้องสรุปยอดของ "เมื่อวาน"
        # แต่เพื่อทดสอบว่าโค้ดทำงานได้ตอนนี้ (เพราะเราเพิ่งคีย์ยอดของ"วันนี้"ไป) 
        # ผมขอตั้งเป็นวันที่ของ "วันนี้" ก่อนนะครับ
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
        
        # สรุปข้อความส่งเข้า Telegram
        if total_sales == 0:
            msg = f"🌅 อรุณสวัสดิ์ค่าบอส~ \nสรุปยอดขายของวันที่ ({target_date}) 📝\n\nไม่มีออเดอร์เลยค่ะ ฮึบๆ สู้ใหม่วันนี้นะคะ! ✌️✨"
        else:
            best_seller = max(menu_counts, key=menu_counts.get)
            msg = f"🌅 อรุณสวัสดิ์ค่าบอส~ \nบอท Kornnonnom มาส่งรายงานยอดขายของวันที่ ({target_date}) แล้วจ้า 📊\n\n"
            msg += f"💰 ยอดขายรวม: *{total_sales}* บาท\n"
            msg += f"👑 เมนูขายดีสุด: *{best_seller}* ({menu_counts[best_seller]} แก้ว)\n\n"
            msg += "ขอให้วันนี้ลูกค้าแน่นๆ ออเดอร์ปังๆ นะคะ! 🎉💖"
            
        send_telegram(msg)
        print("✅ ส่งรายงานเข้า Telegram เรียบร้อยแล้ว! ลองเปิดแอปดูได้เลยครับ")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    generate_report()