import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from sheets_client import get_sheet

load_dotenv()

# --- 🟢 ฟังก์ชันส่งแจ้งเตือน Telegram (เพิ่มสรุปยอดแยกตามเกมวันนี้) ---
def send_order_alert(menu, quantity, current_total, today_orders_count, today_total_revenue, daily_summary):
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
    msg += f"📊 **สรุปยอดขายวันนี้ (รวม {today_orders_count} บิล)**\n"
    
    # วนลูปดึงข้อมูลสรุปแต่ละเกมมาแสดงผล
    for game_name, data in daily_summary.items():
        msg += f"🔸 {game_name}: {data['qty']} ชุด ({data['revenue']:,.0f} ฿)\n"
        
    msg += f"------------------------\n"
    msg += f"💵 **รายได้รวมวันนี้: {today_total_revenue:,.2f} บาท**\n\n"
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
        
        # สร้าง Dictionary สำหรับจัดกลุ่มยอดขายรายแพ็กเกจ
        daily_summary = {}
        
        for row in records:
            # ใช้การดึงข้อมูลแบบเผื่อว่าหัวคอลัมน์สะกดต่างไปเล็กน้อย
            row_date = str(row.get('วันที่', list(row.values())[0]))
            
            if row_date == date_today:
                today_orders_count += 1
                
                # ดึงยอดรวมและจำนวนของแต่ละแถวมาบวกเพิ่ม
                try:
                    row_total = float(str(row.get('ยอดรวม', list(row.values())[4])).replace(',', ''))
                    row_qty = int(str(row.get('จำนวน', list(row.values())[2])).replace(',', ''))
                except:
                    row_total = 0
                    row_qty = 1
                    
                today_total_revenue += row_total
                
                # ดึงชื่อแพ็กเกจ และตัดข้อความ (UID: xxxx) ออก เพื่อให้รวมยอดเกมเดียวกันได้
                raw_menu_name = str(row.get('แพ็กเกจ', list(row.values())[1]))
                clean_menu = raw_menu_name.split(' (UID:')[0].strip()
                
                if clean_menu not in daily_summary:
                    daily_summary[clean_menu] = {'qty': 0, 'revenue': 0}
                
                daily_summary[clean_menu]['qty'] += row_qty
                daily_summary[clean_menu]['revenue'] += row_total
        
        # 3. ส่งแจ้งเตือน Telegram พร้อมแนบยอดสรุป
        send_order_alert(menu, quantity, total, today_orders_count, today_total_revenue, daily_summary)
        
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