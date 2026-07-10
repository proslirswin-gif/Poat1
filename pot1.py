import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import yt_dlp

# إعداد السجلات (Logs) لمتابعة ما يحدث
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# جلب التوكين من إعدادات Render (المتغير الذي أضفناه باسم TOKEN)
TOKEN = os.getenv('TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="أهلاً بك! أرسل لي رابط فيديو وسأقوم بتحميله لك."
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text="جاري التحميل، يرجى الانتظار...")

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open('video.mp4', 'rb'))
        os.remove('video.mp4') # حذف الملف بعد الإرسال
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"حدث خطأ: {str(e)}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), download_video)
    
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    
    application.run_polling()
