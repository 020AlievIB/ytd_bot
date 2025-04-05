import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from youtube_downloader import YouTubeDownloader
from config import BOT_TOKEN

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "👋 Hi! I'm a YouTube video downloader bot.\n\n"
        "Just send me a YouTube video URL and I'll download it for you!\n\n"
        "Supported formats:\n"
        "• Regular videos\n"
        "• Shorts\n"
        "• Playlists (first video only)\n\n"
        "Note: Videos must be under 50MB to be sent through Telegram."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "How to use this bot:\n\n"
        "1. Send me a YouTube video URL\n"
        "2. Wait while I download the video\n"
        "3. I'll send you the video file\n\n"
        "Limitations:\n"
        "• Maximum video size: 50MB\n"
        "• Only MP4 format is supported\n"
        "• For playlists, only the first video will be downloaded"
    )

async def handle_video_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming YouTube URLs."""
    url = update.message.text.strip()
    
    # Validate URL
    if not any(domain in url for domain in ['youtube.com', 'youtu.be']):
        await update.message.reply_text(
            "❌ Please send a valid YouTube URL.\n"
            "Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        return
    
    # Send initial message
    status_message = await update.message.reply_text("⏳ Downloading video...")
    
    try:
        # Download video
        video_path, error = YouTubeDownloader.download_video(url)
        
        if error:
            await status_message.edit_text(f"❌ {error}")
            return
        
        # Send video file
        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption="✅ Here's your video!",
                supports_streaming=True
            )
        
        # Clean up
        os.remove(video_path)
        await status_message.delete()
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        await status_message.edit_text(
            "❌ An error occurred while processing the video.\n"
            "Please try again later or contact the bot administrator."
        )
        if 'video_path' in locals() and video_path and os.path.exists(video_path):
            os.remove(video_path)

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video_url))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 