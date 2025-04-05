import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from youtube_downloader import YouTubeDownloader
from config import BOT_TOKEN
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Hi! Send me a YouTube video or Shorts URL, and I'll download it for you!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Just send me a YouTube video or Shorts URL, and I'll download it for you!"
    )

async def process_video_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    
    if not ("youtube.com" in url or "youtu.be" in url):
        await update.message.reply_text("Please send a valid YouTube URL.")
        return
    
    status_message = await update.message.reply_text("⏳ Downloading video...")
    
    try:
        video_path, error = YouTubeDownloader.download_video(url)
        
        if error:
            await status_message.edit_text(f"❌ {error}")
            return
        
        # Send video file
        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption="✅ Here's your video!"
            )
        
        # Clean up
        os.remove(video_path)
        await status_message.delete()
        
    except Exception as e:
        error_message = str(e)
        if "CERTIFICATE_VERIFY_FAILED" in error_message:
            await status_message.edit_text("❌ SSL Certificate verification failed. Please contact the bot administrator.")
        else:
            await status_message.edit_text(f"❌ Error processing video: {error_message}")
        if 'video_path' in locals() and video_path and os.path.exists(video_path):
            os.remove(video_path)

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_video_url))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main() 