# ⚡ LaserPay AI - Game Top-up Assistant

**LaserPay** คือระบบ AI แชทบอทผู้ช่วยสำหรับร้านรับเติมเกมออนไลน์ ที่ถูกพัฒนาขึ้นเพื่อช่วยตอบคำถามลูกค้าเกี่ยวกับแพ็กเกจเกมต่างๆ (เช่น Roblox, Identity V, One Punch Man) และช่วยจดบันทึกออเดอร์ยอดเติมเงินลงใน Google Sheets โดยอัตโนมัติ เพื่อลดความผิดพลาดและเพิ่มความรวดเร็วในการให้บริการตลอด 24 ชั่วโมง

โปรเจกต์นี้เป็นการต่อยอด (Pivot) จากเทมเพลตร้าน MilkLab° โดยสามารถดูรายละเอียดแนวคิดการ Pivot ได้ที่ 👉 [PIVOT.md](PIVOT.md)

---

## 🚀 Live Demo
ทดลองใช้งานระบบแชทบอท LaserPay ได้ที่นี่:
🔗 **https://huggingface.co/spaces/Jiranuwat222/laserpay-ai**

---

## ✨ Features (ความสามารถของระบบ)
* 💬 **Smart Chatbot:** AI สวมบทบาทแอดมินร้านเติมเกม ตอบคำถามได้อย่างเป็นกันเองด้วยโมเดล Gemini 2.5 Flash
* 📚 **RAG Knowledge Base:** ดึงข้อมูลแพ็กเกจเกมและราคาล่าสุดมาตอบลูกค้าได้อย่างแม่นยำ
* 📊 **Automated Sales Logger:** เมื่อลูกค้าสั่งเติมเกม ระบบจะดักจับข้อมูลและบันทึก (เมนู, จำนวน, ยอดรวม) ลงใน Google Sheets อัตโนมัติ
* 📱 **Morning Report:** มีสคริปต์ส่งสรุปยอดขายประจำวันเข้า Telegram แจ้งเตือนแอดมินทันที

---

## 🛠️ Local Setup (วิธีรันโปรเจกต์ในเครื่อง)

หากต้องการนำโปรเจกต์นี้ไปรันบนคอมพิวเตอร์ของคุณเอง สามารถทำตามขั้นตอนได้ดังนี้:

1. **Clone repository**
   ```bash
   git clone [https://github.com/Jiranuwat222/laserpay-ai.git](https://github.com/Jiranuwat222/laserpay-ai.git)
   cd laserpay-ai

2. **Install dependencies**
   pip install -r requirements.txt

3.   **Setup Environment Variables**
   สร้างไฟล์ .env และตั้งค่า API Keys ที่เกี่ยวข้อง (Google API, Telegram Token, Google Sheets Credentials)

4. **Run Application**
   streamlit run app.py