import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open('Telegram Đơn Hàng').sheet1

async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    lines = message.strip().split('\n')
    if len(lines) < 5:
        return

    data = {line.split(':')[0].strip().lower(): line.split(':', 1)[1].strip() for line in lines if ':' in line}

    sheet.append_row([
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        data.get('tên khách hàng'),
        data.get('sản phẩm'),
        data.get('giá bán'),
        data.get('giá nhập'),
        data.get('nhà cung cấp'),
        data.get('ghi chú')
    ])
    await update.message.reply_text('✅ Đơn hàng đã được lưu vào Google Sheets!')

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order))
print("🤖 Bot đang chạy...")
app.run_polling()
