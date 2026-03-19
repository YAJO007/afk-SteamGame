# Steam Game Simulator

โปรแกรมสำหรับจำลองการเปิดเกมบน Steam โดยไม่ต้องรันเกมจริง

## คุณสมบัติ

- ✅ จำลองการออนไลน์ในเกมอย่างปลอดภัย
- ✅ ไม่ใช้ process spoofing ที่เสี่ยงโดนตรวจจับ
- ✅ สร้าง background process ที่ดูเป็นธรรมชาติ
- ✅ มี heartbeat และ status updates
- ✅ รองรับการหยุดด้วย Ctrl+C

## การติดตั้ง

```bash
pip install -r requirements.txt
```

## การใช้งาน

```bash
python afkGAME.py
```

## วิธีการทำงาน

1. ตรวจสอบว่า Steam กำลังทำงานอยู่
2. สร้าง script จำลอง process ชั่วคราว
3. ส่ง status updates ประจำ
4. ใช้ Steam URL scheme เพื่อลงทะเบียน (อาจไม่ทำงานจริง)

## ข้อควรระวัง

- โปรแกรมนี้ใช้เพื่อการศึกษาเท่านั้น
- ไม่รับประกันว่าจะไม่โดนตรวจจับ
- ควรเปิด Steam ก่อนรันโปรแกรม

## ปรับแต่ง

แก้ไข game_id และ game_name ในบรรทัดที่ 147:

```python
simulator = SteamGameSimulator("GAME_ID", "Game Name")
```
