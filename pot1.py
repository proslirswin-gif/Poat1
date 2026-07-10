import yt_dlp
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    filters
)

# ضع التوكين الخاص بك هنا
TOKEN = '7294160898:AAFMfyKF8GamA1OJb7l_zWSK28vjp-6g5Kc'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('أهلاً! أرسل لي رابط فيديو من يوتيوب، تيك توك، أو إنستقرام وسأقوم بتحميله لك.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    context.user_data['url'] = url  # حفظ الرابط في ذاكرة البوت

    keyboard = [
        [InlineKeyboardButton("جودة عالية (High)", callback_data='high')],
        [InlineKeyboardButton("جودة متوسطة (Medium)", callback_data='medium')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("تم استلام الرابط، اختر جودة الفيديو:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    url = context.user_data.get('url')
    if not url:
        await query.edit_message_text(text="❌ حدث خطأ، يرجى إرسال الرابط مرة أخرى.")
        return

    quality = query.data
    status_msg = await query.edit_message_text(text=f"⏳ جاري التحميل بجودة {quality}، يرجى الانتظار...")

    # إعدادات التحميل
    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best' if quality == 'medium' else 'best',
        'outtmpl': 'video.mp4',
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        await context.bot.edit_message_text(
            chat_id=query.message.chat_id, 
            message_id=status_msg.message_id, 
            text="✅ تم التحميل، جاري إرسال الفيديو..."
        )
        
        await context.bot.send_video(
            chat_id=query.message.chat_id, 
            video=open('video.mp4', 'rb')
        )
        
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=status_msg.message_id)
        
        # حذف الملف بعد الإرسال لتوفير المساحة
        if os.path.exists('video.mp4'):
            os.remove('video.mp4')
            
    except Exception as e:
        await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=status_msg.message_id, text=f"❌ حدث خطأ: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(CallbackQueryHandler(button))
    
    print("البوت يعمل الآن...")
    application.run_polling()
