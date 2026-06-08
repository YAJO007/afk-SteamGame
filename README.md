# Steam Playtime Idler GUI

เครื่องมือ GUI ภาษาไทยสำหรับรัน Steam Playtime Idler ด้วยเลข AppID โดยใช้ Steamworks API ผ่านไฟล์ `steam_api64.dll`

โปรแกรมนี้เหมาะสำหรับการทดสอบ Steamworks, ตรวจสอบ AppID, หรือใช้งานในสภาพแวดล้อมที่ต้องการให้ Steam เห็นว่าแอปกำลังรันอยู่ โดยไม่ต้องเปิดตัวเกมจริง

> ใช้งานกับบัญชี Steam และเกมที่คุณมีสิทธิ์ใช้งานเท่านั้น

## คุณสมบัติ

- หน้า GUI ใช้งานง่าย
- รองรับ AppID เดียวหรือหลาย AppID พร้อมกัน
- เพิ่ม ลบ และล้างรายการ AppID ได้จากหน้าโปรแกรม
- ปุ่มเลือก `steam_api64.dll` แล้วคัดลอกเข้าโฟลเดอร์โปรแกรมให้อัตโนมัติ
- ปุ่มหยุด idler ทั้งหมด
- ยังรองรับการใช้งานแบบ command line เหมือนเดิม

## ภาพรวมการทำงาน

โปรแกรมจะสร้าง process แยกสำหรับแต่ละ AppID แล้วเขียนไฟล์ `steam_appid.txt` ใน session ของ AppID นั้น จากนั้นเรียก `SteamAPI_Init()` เพื่อให้ Steamworks API เริ่มทำงาน

เมื่อกดหยุดหรือปิดหน้าต่าง โปรแกรมจะปิด process ที่รันอยู่ทั้งหมด

## สิ่งที่ต้องมี

- Windows 64-bit
- Python 64-bit
- Steam client เปิดอยู่และ login แล้ว
- บัญชี Steam ต้องมีสิทธิ์ใช้งานเกมหรือ AppID นั้น
- ไฟล์ `steam_api64.dll`

## การติดตั้ง

โคลนโปรเจกต์:

```powershell
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
```

หรือดาวน์โหลดเป็น ZIP แล้วแตกไฟล์

จากนั้นตรวจสอบว่า Python ใช้งานได้:

```powershell
python --version
```

## การเตรียม steam_api64.dll

โปรแกรมต้องใช้ไฟล์:

```text
steam_api64.dll
```

ไฟล์นี้มักอยู่ใน Steamworks SDK ที่:

```text
redistributable_bin\win64\steam_api64.dll
```

นำไฟล์ไปไว้ในโฟลเดอร์เดียวกับ `idle.py`

ตัวอย่าง:

```text
AFKgameSteam
├── idle.py
├── README.md
└── steam_api64.dll
```

หรือเปิดโปรแกรมแล้วกดปุ่ม `เลือก DLL` เพื่อเลือกไฟล์ `steam_api64.dll` จากเครื่อง โปรแกรมจะคัดลอกมาไว้ให้เอง

## วิธีใช้งานแบบ GUI

เปิดโปรแกรม:

```powershell
python idle.py
```

จากนั้น:

1. ใส่ AppID เช่น `730`
2. ถ้าต้องการหลายเกม ให้ใส่แบบนี้: `730 440 570`
3. กด `เพิ่ม`
4. กด `เริ่ม Idle`
5. เมื่อต้องการหยุด ให้กด `หยุดทั้งหมด`

การปิดหน้าต่างโปรแกรมจะหยุด idler ทั้งหมดโดยอัตโนมัติ

## วิธีใช้งานแบบ Command Line

รัน AppID เดียว:

```powershell
python idle.py 730
```

รันหลาย AppID:

```powershell
python idle.py 730 440 570
```

หยุดด้วย:

```text
Ctrl+C
```

## AppID คืออะไร

AppID คือเลขประจำเกมหรือแอปบน Steam แต่ละเกมจะมีเลขไม่ซ้ำกัน

ตัวอย่าง:

| เกม | AppID |
|---|---:|
| Counter-Strike 2 | `730` |
| Dota 2 | `570` |
| Team Fortress 2 | `440` |
| PUBG | `578080` |

วิธีหา AppID:

1. เปิดหน้าเกมใน Steam Store
2. ดู URL ของหน้าเกม

ตัวอย่าง:

```text
https://store.steampowered.com/app/730/CounterStrike_2/
```

เลขหลัง `/app/` คือ AppID ดังนั้นตัวอย่างนี้คือ:

```text
730
```

## โครงสร้างไฟล์

```text
AFKgameSteam
├── idle.py              # โปรแกรมหลักและ GUI
├── README.md            # เอกสารโปรเจกต์
├── steam_api64.dll      # DLL ที่ต้องเตรียมเอง
└── .sessions            # สร้างอัตโนมัติเมื่อรันหลาย AppID
```

## ปัญหาที่พบบ่อย

| ปัญหา | สาเหตุ / วิธีแก้ |
|---|---|
| ไม่พบ `steam_api64.dll` | ยังไม่มี DLL ในโฟลเดอร์โปรแกรม ให้กด `เลือก DLL` หรือคัดลอกไฟล์มาไว้ข้าง `idle.py` |
| `SteamAPI_Init failed` | Steam client ยังไม่เปิด, ยังไม่ได้ login, หรือบัญชีไม่มีสิทธิ์ใช้ AppID นั้น |
| `OSError: [WinError 126]` | มักเกิดจาก Python/DLL คนละสถาปัตยกรรม เช่น Python 32-bit แต่ DLL เป็น 64-bit ให้ติดตั้ง Python 64-bit |
| กดเริ่มแล้วหยุดเอง | AppID อาจไม่ถูกต้อง, Steam ไม่พร้อม, หรือบัญชีไม่มีสิทธิ์ใช้งาน AppID นั้น |

## หมายเหตุสำหรับ GitHub

ไม่แนะนำให้อัปโหลด `steam_api64.dll` ขึ้น GitHub หากคุณไม่มีสิทธิ์แจกจ่ายไฟล์นั้น ให้ผู้ใช้เตรียมไฟล์จาก Steamworks SDK ด้วยตัวเอง

ควรเพิ่มไฟล์ `.gitignore` เพื่อกันไฟล์ runtime เช่น:

```gitignore
__pycache__/
.sessions/
steam_appid.txt
```

ถ้าไม่ต้องการอัปโหลด DLL ให้เพิ่ม:

```gitignore
steam_api64.dll
```

## ข้อจำกัดความรับผิดชอบ

โปรเจกต์นี้จัดทำเพื่อการศึกษาและการทดสอบเท่านั้น ผู้ใช้ต้องรับผิดชอบการใช้งานเอง และควรใช้งานให้สอดคล้องกับข้อกำหนดของ Steam และสิทธิ์การใช้งานที่เกี่ยวข้อง
