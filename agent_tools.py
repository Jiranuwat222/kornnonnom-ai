from datetime import datetime

def validate_sale(menu: str, quantity: int, price: float) -> None:
    """Guardrails: ป้อมยามดักจับความผิดปกติ raise ValueError ถ้าข้อมูลไม่ถูกต้อง"""
    if not menu or not menu.strip():
        raise ValueError("ชื่อเมนูห้ามว่าง")
    if quantity <= 0:
        raise ValueError("จำนวนต้องมากกว่า 0")
    if price <= 0:
        raise ValueError("ราคาต้องมากกว่า 0")

def log_sale(menu: str, quantity: int, price: float) -> dict:
    """เครื่องมือบันทึกยอดขาย (เวอร์ชันทดสอบ ส่งค่ากลับเป็น dict)"""
    validate_sale(menu, quantity, price)
    total = quantity * price
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