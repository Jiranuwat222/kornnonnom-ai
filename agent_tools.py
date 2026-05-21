from datetime import datetime
from sales_logger import log_sale_to_sheet  # นำเข้าฟังก์ชันบันทึกลงชีต

def validate_sale(menu: str, quantity: int, price: float) -> None:
    """Guardrails: ป้อมยามดักจับความผิดปกติ raise ValueError ถ้าข้อมูลไม่ถูกต้อง"""
    if not menu or not menu.strip():
        raise ValueError("ชื่อเมนูห้ามว่าง")
    if quantity <= 0:
        raise ValueError("จำนวนต้องมากกว่า 0")
    if price <= 0:
        raise ValueError("ราคาต้องมากกว่า 0")

def log_sale(menu: str, quantity: int, price: float) -> dict:
    """เครื่องมือบันทึกยอดขาย (เชื่อมต่อกับ Google Sheets)"""
    validate_sale(menu, quantity, price)
    total = quantity * price
    
    # 🔴 เรียกใช้ฟังก์ชันบันทึกลงชีตของจริง
    log_sale_to_sheet(menu, quantity, price, total)
    
    return {
        "status": "success",
        "menu": menu,
        "quantity": quantity,
        "price": price,
        "total": total,
        "timestamp": datetime.now().isoformat(),
    }

# ลงทะเบียนเครื่องมือให้ AI รู้จัก
TOOLS = {
    "log_sale": log_sale,
}