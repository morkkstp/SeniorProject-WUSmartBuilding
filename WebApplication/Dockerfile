# เริ่มต้นจากการใช้ภาพ (image) ของ Python รุ่น 3.11.1 เป็นฐานในการสร้าง Docker image
FROM python:3.11.1

# กำหนดโฟลเดอร์ทำงานเป็น /app ซึ่งเป็นที่เก็บโค้ดของแอปพลิเคชันใน Docker container
WORKDIR /app 

# คัดลอกไฟล์ requirements.txt จากโฟลเดอร์ที่เดียวกันกับ Dockerfile เข้าไปใน /app ใน Docker container
RUN pip install --upgrade pip

# ติดตั้ง dependencies ที่ระบุในไฟล์ requirements.txt ลงใน Docker container โดยใช้ pip
COPY requirements.txt .

# คัดลอกโค้ดทั้งหมดจากโฟลเดอร์ปัจจุบันของโฮสต์เข้าไปใน /app ใน Docker container
RUN pip install --no-cache-dir -r  requirements.txt

# คัดลอกโค้ดทั้งหมดจากโฟลเดอร์ปัจจุบันของโฮสต์เข้าไปใน /app ใน Docker container
COPY . /app/

# กำหนดตัวแปรสภาพแวดล้อม PORT เป็น 8080 ซึ่งเป็นพอร์ตที่แอปพลิเคชันจะใช้ในการรัน
ENV PORT 8080

# กำหนดคำสั่งที่จะถูกรันเมื่อ Docker container ถูกเริ่มต้น ในที่นี้คือการรัน uvicorn เพื่อเริ่มต้นแอปพลิเคชัน Python โดยใช้ไฟล์ main.py 
# และแอปพลิเคชันชื่อ app บนโฮสต์ "0.0.0.0" ที่พอร์ต 8080 โดยมีการใช้งานโหมด --reload เพื่อให้รันโค้ดใหม่โดยอัตโนมัติเมื่อโค้ดถูกแก้ไข
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
