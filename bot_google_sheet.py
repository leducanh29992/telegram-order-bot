
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from datetime import datetime

TOKEN = '7881994789:AAFGxxZ2S80WHqEmYyxiF0xrKrphuWyvNfQ'
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds_json = os.environ.get("GOOGLE_CREDS")
creds_dict = json.loads(creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

SPREADSHEET_NAME = 'Telegram Đơn Hàng'
HEADER = ['Thời Gian', 'Tên Khách Hàng', 'Sản Phẩm', 'Giá Bán', 'Giá Nhập', 'Nhà Cung Cấp', 'Ghi Chú']

def get_or_create_daily_sheet():
    today = datetime.now().strftime('%Y-%m-%d')
    spreadsheet = client.open(SPREADSHEET_NAME)
    
    try:
        worksheet = spreadsheet.worksheet(today)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=today, rows='1000', cols='10')
        worksheet.append_row(HEADER)
    return worksheet

def parse_multiline_block(lines, start_index):
    values = []
    for i in range(start_index + 1, len(lines)):
        if ':' in lines[i]:  # đoạn tiếp theo bắt đầu
            break
        values.append(lines[i].strip())
    return values

async def handle_order(update: Update, context):
    lines = update.message.text.strip().split('\n')
    data = {}
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            if value == '' and key in ['sản phẩm', 'giá bán', 'giá nhập', 'nhà cung cấp']:
                data[key] = parse_multiline_block(lines, i)
                i += len(data[key])
                continue
            else:
                data[key] = [value] if key in ['sản phẩm', 'giá bán', 'giá nhập', 'nhà cung cấp'] else value
        i += 1

    required_lists = ['sản phẩm', 'giá bán', 'giá nhập', 'nhà cung cấp']
    if not all(k in data and isinstance(data[k], list) for k in required_lists):
        return

    num_items = len(data['sản phẩm'])
    if not all(len(data[k]) == num_items for k in required_lists):
        return

    worksheet = get_or_create_daily_sheet()
    for idx in range(num_items):
        worksheet.append_row([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data.get('tên khách hàng', ''),
            data['sản phẩm'][idx],
            data['giá bán'][idx],
            data['giá nhập'][idx],
            data['nhà cung cấp'][idx],
            data.get('ghi chú', '')
        ])

    await update.message.reply_text("✅✅✅ Đã lưu vào trang tính!")

if __name__ == '__main__':
    # Tạo sheet ngay khi khởi động bot
    get_or_create_daily_sheet()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_order))
    app.run_polling()
