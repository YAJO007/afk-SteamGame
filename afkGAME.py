import subprocess
import time
import psutil
import requests
import json
import os
from datetime import datetime
import threading
import random

class SteamGameSimulator:
    def __init__(self, game_id="730", game_name="Counter-Strike 2"):
        self.game_id = game_id
        self.game_name = game_name
        self.start_time = None
        self.is_running = False
        self.heartbeat_thread = None
        
    def get_steam_process_info(self):
        """ดูข้อมูล Steam process"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'steam.exe' in proc.info['name'].lower():
                return proc.info
        return None
    
    def simulate_game_presence(self):
        """จำลองการออนไลน์ในเกมผ่าน Steam API"""
        try:
            # สร้าง fake process name ที่ดูเป็นธรรมชาติ
            fake_processes = [
                f"{self.game_name}.exe",
                f"{self.game_name.replace(' ', '')}.exe",
                f"game_{self.game_id}.exe"
            ]
            
            # สุ่มเปลี่ยนชื่อ process เล็กน้อย
            process_name = random.choice(fake_processes)
            
            # สร้าง script จำลอง process
            script_content = f"""
import time
import random
import sys
from datetime import datetime

# จำลอง process เกม
print(f"Starting {process_name}...")
print(f"Game ID: {self.game_id}")
print(f"Started at: {{datetime.now()}}")

# ทำงานเล็กน้อยเพื่อดูเป็นธรรมชาติ
counter = 0
while True:
    time.sleep(random.uniform(30, 120))  # สุ่มรอ 30-120 วินาที
    counter += 1
    print(f"Heartbeat {{counter}} - {{datetime.now()}}")
    
    # จำลอง activity ในเกม
    activities = ["rendering", "network_update", "input_processing", "physics_update"]
    activity = random.choice(activities)
    print(f"Activity: {{activity}}")
"""
            
            # เขียน script ชั่วคราว
            temp_script = f"temp_game_{self.game_id}.py"
            with open(temp_script, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # รัน script ใน background
            subprocess.Popen(["python", temp_script], 
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            
            return True
            
        except Exception as e:
            print(f"Error simulating game presence: {e}")
            return False
    
    def send_steam_status_update(self):
        """ส่ง status update ให้ Steam (จำลอง)"""
        while self.is_running:
            try:
                # จำลองการส่งข้อมูลไปยัง Steam
                # ในความเป็นจริงต้องใช้ Steam Web API
                print(f"[{datetime.now()}] Game status: Playing {self.game_name}")
                print(f"Session duration: {int(time.time() - self.start_time)} seconds")
                
                # รอ 5-15 นาทีระหว่าง updates
                wait_time = random.randint(300, 900)
                time.sleep(wait_time)
                
            except Exception as e:
                print(f"Status update error: {e}")
                time.sleep(60)
    
    def start_fake_session(self):
        """เริ่ม session จำลอง"""
        if self.is_running:
            print("Game session already running!")
            return
        
        print(f"Starting fake game session for {self.game_name} (ID: {self.game_id})")
        
        # เช็คว่า Steam กำลังทำงานอยู่หรือไม่
        steam_proc = self.get_steam_process_info()
        if not steam_proc:
            print("Warning: Steam not detected. Please start Steam first.")
        else:
            print(f"Steam detected: PID {steam_proc['pid']}")
        
        # เริ่มจับเวลา
        self.start_time = time.time()
        self.is_running = True
        
        # เริ่ม simulation
        self.simulate_game_presence()
        
        # เริ่ม status update thread
        self.heartbeat_thread = threading.Thread(target=self.send_steam_status_update)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
        
        # เริ่ม Steam URL (แต่อาจไม่ทำงานจริง)
        print(f"Attempting to register game with Steam...")
        subprocess.Popen(f"start steam://rungameid/{self.game_id}", shell=True)
        
        print("Fake game session started successfully!")
        print(f"Session will run for 8 hours (until {datetime.fromtimestamp(self.start_time + 8*3600)})")
    
    def stop_session(self):
        """หยุด session"""
        self.is_running = False
        if self.start_time:
            duration = int(time.time() - self.start_time)
            print(f"Session stopped. Total duration: {duration} seconds ({duration//3600}h {(duration%3600)//60}m)")
        
        # ลบ temp files
        temp_file = f"temp_game_{self.game_id}.py"
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass

# ใช้งาน
if __name__ == "__main__":
    simulator = SteamGameSimulator("730", "Counter-Strike 2")
    
    try:
        simulator.start_fake_session()
        
        # รอ 8 ชั่วโมง
        time.sleep(60 * 60 * 8)
        
    except KeyboardInterrupt:
        print("\nSession interrupted by user")
    finally:
        simulator.stop_session()