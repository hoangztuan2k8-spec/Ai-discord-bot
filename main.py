import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Mở web server giả lập để Render không báo lỗi port binding
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Thay Toan Bot is running!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
import os
import time
import discord
import google.generativeai as genai

# Cấu hình API Key cho Gemini từ biến môi trường
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Sử dụng model gemini-1.5-flash
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Thầy Toàn đã sẵn sàng kết nối với tài khoản: {client.user}')

@client.event
async def on_message(message):
    # Bỏ qua tin nhắn do chính bot gửi
    if message.author == client.user:
        return

    # Lắng nghe lệnh bắt đầu bằng !hoa 
    if message.content.startswith('!hoa '):
        prompt = message.content[5:].strip()
        
        # Hướng dẫn phong cách trả lời cho AI
        system_instruction = (
            "Bạn là một gia sư Hóa học thân thiện, tận tâm, tên là Thầy Toàn. "
            "Hãy giải đáp câu hỏi hóa học bằng tiếng Việt một cách dễ hiểu. "
            "QUY TẮC BẮT BUỘC: Tuyệt đối không dùng ký hiệu LaTeX, không dùng dấu đô la ($), không dùng dấu gạch chéo ngược (\\). "
            "Tất cả công thức hóa học phải viết bằng chữ và số bình thường (ví dụ: H2SO4, Al2(SO4)3, H2, ->) để hiển thị thật sạch sẽ trên Discord."
        )
        
        full_prompt = f"{system_instruction}\n\nCâu hỏi của học sinh: {prompt}"
        
        # Cơ chế thử lại (Retry) khi gặp lỗi quá tải (503 hoặc các lỗi mạng tạm thời)
        max_retries = 3
        response_text = None
        
        for attempt in range(max_retries):
            try:
                response = model.generate_content(full_prompt)
                if response and response.text:
                    response_text = response.text
                    break
            except Exception as e:
                # Nếu chưa hết số lần thử, chờ 2 giây rồi gọi lại
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    # Nếu đã thử hết số lần mà vẫn lỗi, lưu lại lỗi
                    response_text = f"Thầy đang bận một chút do hệ thống quá tải. Em đợi vài giây rồi hỏi lại thầy nhé!"

        # Gửi kết quả về khung chat Discord
        if response_text:
            await message.channel.send(response_text)

# Khởi động bot bằng Discord Token từ biến môi trường
client.run(os.environ.get("DISCORD_TOKEN"))
