import os
import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from PIL import Image, ImageDraw
import io

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 配置信息 - 从环境变量获取
BOT_TOKEN = os.getenv('BOT_TOKEN', '7638289671:AAHJDHEgQOhAdAnfmZs9IN4zY8EB6LykGDI')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', '@liulangsuo')
CHANNEL_ID = os.getenv('CHANNEL_ID', '-1002965920151')

print("=" * 60)
print("🤖 Telegram图片网格切割机器人 - 启动中...")
print("=" * 60)

class GridCutBot:
    def __init__(self):
        try:
            self.app = Application.builder().token(BOT_TOKEN).build()
            self.setup_handlers()
            logger.info("✅ 机器人初始化成功")
        except Exception as e:
            logger.error(f"❌ 初始化失败: {e}")
            raise
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """欢迎命令"""
        try:
            welcome_text = """
🎉 欢迎使用图片网格切割机器人！

🤖 核心功能：
• 🔲 自动3×4网格切割（12宫格）
• 💾 画质无损保持
• 📦 支持单独下载

💡 使用方法：
直接发送图片即可自动切割！
"""
            keyboard = [
                [InlineKeyboardButton("🚀 发送图片开始", callback_data="send_photo")],
                [InlineKeyboardButton("📢 关注频道去水印", url="https://t.me/liulangsuo")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(welcome_text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"start命令错误: {e}")
            await update.message.reply_text("❌ 系统错误，请重试")
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理图片切割"""
        try:
            await update.message.reply_text("🔄 收到图片，开始处理...")
            
            # 下载图片
            photo_file = await update.message.effective_attachment[-1].get_file()
            image_stream = io.BytesIO()
            await photo_file.download_to_memory(image_stream)
            image_stream.seek(0)
            
            # 打开并处理图片
            original_image = Image.open(image_stream)
            if original_image.mode != 'RGB':
                original_image = original_image.convert('RGB')
            
            width, height = original_image.size
            
            # 3×4网格切割
            rows, cols = 3, 4
            grid_images = self.cut_image_to_grid(original_image, rows, cols)
            
            # 发送结果
            await self.send_grid_results(update, grid_images, rows, cols)
            
        except Exception as e:
            logger.error(f"处理图片错误: {e}")
            await update.message.reply_text("❌ 处理失败，请检查图片格式后重试")
    
    def cut_image_to_grid(self, image: Image.Image, rows: int, cols: int):
        """切割图片到网格"""
        width, height = image.size
        cell_width = width // cols
        cell_height = height // rows
        
        grid_images = []
        
        for row in range(rows):
            for col in range(cols):
                # 计算切割区域
                left = col * cell_width
                upper = row * cell_height
                right = min(left + cell_width, width)
                lower = min(upper + cell_height, height)
                
                # 切割图片
                cell_image = image.crop((left, upper, right, lower))
                
                # 添加水印
                watermarked_image = self.add_watermark(cell_image, row, col)
                grid_images.append(watermarked_image)
        
        return grid_images
    
    def add_watermark(self, image: Image.Image, row: int, col: int):
        """添加水印"""
        try:
            drawable = image.copy()
            draw = ImageDraw.Draw(drawable)
            
            # 水印文字
            watermark_text = "曹丝妮"
            position_text = f"{row+1}-{col+1}"
            
            # 图片尺寸
            img_width, img_height = image.size
            
            # 添加主水印（左上角）
            draw.text((10, 10), watermark_text, fill=(255, 255, 255, 128))
            
            # 添加位置标记（右下角）
            draw.text((img_width-40, img_height-25), position_text, fill=(255, 255, 255, 128))
            
            return drawable
            
        except Exception as e:
            logger.warning(f"水印添加失败: {e}")
            return image
    
    async def send_grid_results(self, update: Update, grid_images: list, rows: int, cols: int):
        """发送切割结果"""
        total_parts = len(grid_images)
        
        # 发送摘要信息
        summary_text = (
            f"🎉 图片切割完成！\n\n"
            f"📊 网格布局: {rows}×{cols}\n"
            f"📦 生成片段: {total_parts}个\n\n"
            f"⬇️ 正在发送图片片段..."
        )
        
        await update.message.reply_text(summary_text)
        
        # 发送图片
        for i, img in enumerate(grid_images):
 
