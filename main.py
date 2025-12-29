"""
▓█████▄  ██▀███   ██▓ ▄▄▄        ██████  ██▓███  
▒██▀ ██▌▓██ ▒ ██▒▓██▒▒████▄    ▒██    ▒ ▓██░  ██▒
░██   █▌▓██ ░▄█ ▒▒██▒▒██  ▀█▄  ░ ▓██▄   ▓██░ ██▓▒
░▓█▄   ▌▒██▀▀█▄  ░██░░██▄▄▄▄██   ▒   ██▒▒██▄█▓▒ ▒
░▒████▓ ░██▓ ▒██▒░██░ ▓█   ▓██▒▒██████▒▒▒██▒ ░  ░
 ▒▒▓  ▒ ░ ▒▓ ░▒▓░░▓   ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░▒▓▒░ ░  ░
 ░ ▒  ▒   ░▒ ░ ▒░ ▒ ░  ▒   ▒▒ ░░ ░▒  ░ ░░▒ ░     
 ░ ░  ░   ░░   ░  ▒ ░  ░   ▒   ░  ░  ░  ░░       
   ░       ░      ░        ░  ░      ░           
 ░                                               
سلف بات حرفه‌ای - 700+ خط کد
"""

import asyncio
import time
import json
import os
import random
import string
import threading
import sqlite3
import http.server
import socketserver
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging
from dataclasses import dataclass
from contextlib import contextmanager

from telethon import TelegramClient, events, functions, types
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.messages import (
    SendReactionRequest, GetMessageReactionsListRequest,
    GetMessagesViewsRequest, GetDiscussionMessageRequest
)
from telethon.tl.functions.channels import (
    GetFullChannelRequest, JoinChannelRequest,
    LeaveChannelRequest, GetParticipantsRequest
)
from telethon.tl.functions.contacts import (
    GetContactsRequest, ImportContactsRequest,
    DeleteContactsRequest, BlockRequest, UnblockRequest
)
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import SearchRequest
from telethon.tl.types import (
    PeerUser, PeerChat, PeerChannel,
    InputPeerUser, InputPeerChat, InputPeerChannel,
    ReactionEmoji, ReactionCustomEmoji,
    User, Chat, Channel,
    Message, MessageService,
    InputMediaUploadedPhoto, InputMediaUploadedDocument,
    InputPhoneContact, UserStatusOnline, UserStatusOffline,
    UserStatusRecently, UserStatusLastWeek, UserStatusLastMonth,
    ChannelParticipantsRecent, ChannelParticipantsSearch,
    ReactionEmpty, MessageReactions
)

# ==================== تنظیمات ====================
class Config:
    # API اطلاعات - از متغیرهای محیطی استفاده می‌کنیم
    API_ID = int(os.environ.get("API_ID", "2040"))
    API_HASH = os.environ.get("API_HASH", "b18441a1ff607e10a989891a5462e627")
    SESSION_NAME = os.environ.get("SESSION_NAME", "ultra_self_bot")
    
    # تنظیمات پیشرفته
    MAX_BANNERS = 50
    MAX_MESSAGES_PER_MINUTE = 20
    AUTO_BACKUP_MINUTES = 30
    LOG_LEVEL = logging.INFO
    
    # مسیرها
    DATABASE_PATH = "selfbot.db"
    BACKUP_DIR = "backups/"
    LOGS_DIR = "logs/"
    
    # پورت HTTP برای Health Check
    HTTP_PORT = int(os.environ.get("PORT", "8000"))
    
    # ایموجی‌های پیشفرض
    EMOJIS = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "time": "⏰",
        "stats": "📊",
        "group": "👥",
        "user": "👤",
        "message": "💬",
        "settings": "⚙️",
        "lock": "🔒",
        "unlock": "🔓",
        "ban": "🚫",
        "mute": "🔇",
        "pin": "📌",
        "star": "⭐",
        "fire": "🔥",
        "crown": "👑",
        "robot": "🤖",
        "ping": "🏓",
        "banner": "📢",
        "money": "💰",
        "heart": "❤️",
        "like": "👍",
        "dislike": "👎"
    }
    
    # رنگ‌های ترمینال
    class Colors:
        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"
        MAGENTA = "\033[95m"
        CYAN = "\033[96m"
        WHITE = "\033[97m"
        RESET = "\033[0m"
        BOLD = "\033[1m"

# ==================== HTTP Server برای Health Check ====================
class HealthCheckHandler(http.server.BaseHTTPRequestHandler):
    """Handler ساده برای پاسخ به درخواست‌های Health Check"""
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "ok",
                "service": "telegram-selfbot",
                "timestamp": time.time()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Telegram Selfbot</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-align: center;
                        padding: 50px;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                        background: rgba(255, 255, 255, 0.1);
                        padding: 30px;
                        border-radius: 15px;
                        backdrop-filter: blur(10px);
                    }
                    h1 { 
                        color: white; 
                        font-size: 3em;
                        margin-bottom: 20px;
                    }
                    .status {
                        font-size: 1.2em;
                        margin: 20px 0;
                        padding: 15px;
                        background: rgba(0, 0, 0, 0.2);
                        border-radius: 10px;
                    }
                    .emoji { font-size: 2em; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 Telegram Selfbot</h1>
                    <div class="status">
                        <p class="emoji">✅</p>
                        <p>سلف بات تلگرام در حال اجرا است</p>
                        <p><small>Health Check Endpoint: <code>/health</code></small></p>
                    </div>
                    <p>این صفحه برای بررسی سلامت سرویس در Koyeb ایجاد شده است.</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """غیرفعال کردن لاگ HTTP در ترمینال"""
        pass

def start_http_server(port=8000):
    """شروع سرور HTTP در یک ترد جداگانه"""
    def run_server():
        try:
            with socketserver.TCPServer(("", port), HealthCheckHandler) as httpd:
                print(f"{Config.Colors.GREEN}✅ HTTP Server شروع شد روی پورت {port}{Config.Colors.RESET}")
                print(f"{Config.Colors.CYAN}🌐 Health Check: http://localhost:{port}/health{Config.Colors.RESET}")
                httpd.serve_forever()
        except Exception as e:
            print(f"{Config.Colors.RED}❌ خطا در شروع HTTP Server: {e}{Config.Colors.RESET}")
    
    # شروع سرور در ترد جداگانه
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    return server_thread

# ==================== دیتابیس ====================
class Database:
    def __init__(self, path: str = Config.DATABASE_PATH):
        self.path = path
        self.init_db()
    
    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # جدول بنرها
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS banners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    message_text TEXT,
                    media_type TEXT DEFAULT 'text',
                    interval_minutes INTEGER DEFAULT 5,
                    last_sent TIMESTAMP DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول تنظیمات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول دستورات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT UNIQUE NOT NULL,
                    response TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول لاگ
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول کاربران ویژه
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS special_users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    permissions TEXT DEFAULT 'user',
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول گروه‌ها
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    chat_id INTEGER PRIMARY KEY,
                    title TEXT,
                    banner_enabled BOOLEAN DEFAULT 0,
                    auto_delete INTEGER DEFAULT 0,
                    welcome_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def add_banner(self, chat_id: int, message_text: str, media_type: str = 'text', interval: int = 5) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO banners (chat_id, message_text, media_type, interval_minutes)
                VALUES (?, ?, ?, ?)
            """, (chat_id, message_text, media_type, interval))
            conn.commit()
            return cursor.lastrowid is not None
    
    def remove_banner(self, chat_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM banners WHERE chat_id = ?", (chat_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_banners(self) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM banners WHERE is_active = 1")
            return [dict(row) for row in cursor.fetchall()]
    
    def update_banner_time(self, chat_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE banners SET last_sent = ? WHERE chat_id = ?
            """, (int(time.time()), chat_id))
            conn.commit()
    
    def add_custom_command(self, command: str, response: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO custom_commands (command, response)
                    VALUES (?, ?)
                """, (command.lower(), response))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    def remove_custom_command(self, command: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM custom_commands WHERE command = ?", (command.lower(),))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_custom_command(self, command: str) -> Optional[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT response FROM custom_commands WHERE command = ?", (command.lower(),))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def get_all_commands(self) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT command, response FROM custom_commands ORDER BY command")
            return [dict(row) for row in cursor.fetchall()]
    
    def save_setting(self, key: str, value: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value)
                VALUES (?, ?)
            """, (key, value))
            conn.commit()
    
    def get_setting(self, key: str, default: str = "") -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default
    
    def add_special_user(self, user_id: int, username: str = "", permissions: str = "user"):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO special_users (user_id, username, permissions)
                VALUES (?, ?, ?)
            """, (user_id, username, permissions))
            conn.commit()
    
    def remove_special_user(self, user_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM special_users WHERE user_id = ?", (user_id,))
            conn.commit()
    
    def is_special_user(self, user_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM special_users WHERE user_id = ?", (user_id,))
            return cursor.fetchone() is not None
    
    def log_event(self, level: str, message: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO logs (level, message)
                VALUES (?, ?)
            """, (level, message))
            conn.commit()

# ==================== سیستم بنر ====================
class BannerSystem:
    def __init__(self, db: Database, client: TelegramClient):
        self.db = db
        self.client = client
        self.active_banners: Dict[int, Dict] = {}
        self.load_banners()
    
    def load_banners(self):
        """بارگذاری بنرها از دیتابیس"""
        banners = self.db.get_banners()
        for banner in banners:
            self.active_banners[banner['chat_id']] = {
                'message_text': banner['message_text'],
                'media_type': banner['media_type'],
                'interval': banner['interval_minutes'],
                'last_sent': banner['last_sent'],
                'message_obj': None  # پیام اصلی رو بعداً از چت میگیریم
            }
    
    async def add_banner(self, chat_id: int, message_obj: Any, interval: int = 5) -> Tuple[bool, str]:
        """اضافه کردن بنر جدید"""
        if len(self.active_banners) >= Config.MAX_BANNERS:
            return False, "حداکثر تعداد بنرها رسیده است"
        
        if chat_id in self.active_banners:
            return False, "بنر برای این گروه از قبل وجود دارد"
        
        # تشخیص نوع مدیا
        media_type = self._get_media_type(message_obj)
        
        # ذخیره متن برای نمایش
        message_text = message_obj.text[:100] if message_obj.text else f"[{media_type}]"
        
        # ذخیره در دیتابیس
        if self.db.add_banner(chat_id, message_text, media_type, interval):
            # ذخیره در حافظه
            self.active_banners[chat_id] = {
                'message_obj': message_obj,
                'message_text': message_text,
                'media_type': media_type,
                'interval': interval,
                'last_sent': 0
            }
            return True, "بنر با موفقیت اضافه شد"
        return False, "خطا در ذخیره بنر"
    
    def remove_banner(self, chat_id: int) -> bool:
        """حذف بنر"""
        if chat_id in self.active_banners:
            del self.active_banners[chat_id]
            return self.db.remove_banner(chat_id)
        return False
    
    def get_banner_stats(self) -> Dict:
        """گرفتن آمار بنرها"""
        return {
            'total': len(self.active_banners),
            'active': len([b for b in self.active_banners.values()]),
            'chats': list(self.active_banners.keys())
        }
    
    async def send_scheduled_banners(self):
        """ارسال بنرهای زمان‌بندی شده"""
        current_time = time.time()
        for chat_id, banner in self.active_banners.items():
            if current_time - banner['last_sent'] >= banner['interval'] * 60:
                try:
                    await self._send_banner_message(chat_id, banner)
                    banner['last_sent'] = current_time
                    self.db.update_banner_time(chat_id)
                    self.db.log_event("INFO", f"بنر ارسال شد به چت {chat_id}")
                except Exception as e:
                    self.db.log_event("ERROR", f"خطا در ارسال بنر به {chat_id}: {str(e)}")
    
    async def _send_banner_message(self, chat_id: int, banner: Dict):
        """ارسال پیام بنر"""
        message_obj = banner['message_obj']
        
        if not message_obj:
            # اگر message_obj نداریم، فقط متن رو بفرست
            await self.client.send_message(chat_id, banner['message_text'] or "📢 بنر")
            return
        
        try:
            # سعی کن پیام رو دوباره بفرستی
            if banner['media_type'] == 'text':
                await self.client.send_message(chat_id, message_obj.text)
            
            elif banner['media_type'] == 'photo':
                await self.client.send_file(
                    chat_id, 
                    message_obj.media, 
                    caption=message_obj.text
                )
            
            elif banner['media_type'] == 'video':
                await self.client.send_file(
                    chat_id, 
                    message_obj.media, 
                    caption=message_obj.text
                )
            
            elif banner['media_type'] == 'sticker':
                await self.client.send_file(chat_id, message_obj.media)
            
            elif banner['media_type'] == 'gif':
                await self.client.send_file(
                    chat_id, 
                    message_obj.media, 
                    caption=message_obj.text
                )
            
            elif banner['media_type'] in ['voice', 'audio']:
                await self.client.send_file(
                    chat_id, 
                    message_obj.media, 
                    caption=message_obj.text,
                    voice_note=(banner['media_type'] == 'voice')
                )
            
            elif banner['media_type'] == 'document':
                await self.client.send_file(
                    chat_id, 
                    message_obj.media, 
                    caption=message_obj.text
                )
            
            else:
                # برای سایر انواع، متن رو بفرست
                await self.client.send_message(chat_id, message_obj.text or "📢 بنر")
                
        except Exception as e:
            # اگر خطا خورد، فقط متن رو بفرست
            await self.client.send_message(chat_id, f"📢 {banner['message_text']}")
    
    def _get_media_type(self, message_obj: Any) -> str:
        """تشخیص نوع مدیا"""
        if not message_obj:
            return 'text'
        
        if message_obj.photo:
            return 'photo'
        elif message_obj.video:
            return 'video'
        elif message_obj.document:
            mime_type = getattr(message_obj.document, 'mime_type', '')
            if 'sticker' in mime_type:
                return 'sticker'
            elif 'gif' in mime_type:
                return 'gif'
            elif 'image' in mime_type:
                return 'photo'
            elif 'video' in mime_type:
                return 'video'
            elif 'audio' in mime_type:
                if message_obj.voice:
                    return 'voice'
                return 'audio'
            else:
                return 'document'
        elif message_obj.sticker:
            return 'sticker'
        elif message_obj.gif:
            return 'gif'
        elif message_obj.voice:
            return 'voice'
        elif message_obj.audio:
            return 'audio'
        elif message_obj.text:
            return 'text'
        else:
            return 'unknown'

# ==================== سیستم دستورات ====================
class CommandSystem:
    def __init__(self, db: Database, banner_system: BannerSystem, client: TelegramClient):
        self.db = db
        self.banner_system = banner_system
        self.client = client
        self.builtin_commands = self._get_builtin_commands()
        self.me = None
        self.start_time = time.time()
    
    async def initialize(self):
        self.me = await self.client.get_me()
    
    def _get_builtin_commands(self) -> Dict[str, callable]:
        commands = {}
        
        # دستورات اصلی
        commands['پینگ'] = self.cmd_ping
        commands['آمار'] = self.cmd_stats
        commands['بنر'] = self.cmd_banner
        commands['دستورات'] = self.cmd_commands
        commands['تنظیمات'] = self.cmd_settings
        commands['راهنما'] = self.cmd_help
        commands['خاموش'] = self.cmd_shutdown
        commands['روشن'] = self.cmd_startup
        
        # دستورات مدیریت بنر
        commands['حذف بنر'] = self.cmd_remove_banner
        commands['لیست بنرها'] = self.cmd_list_banners
        
        # دستورات اطلاعاتی
        commands['پروفایل'] = self.cmd_profile
        commands['زمان'] = self.cmd_time
        commands['تاریخ'] = self.cmd_date
        commands['ساعت'] = self.cmd_clock
        
        # دستورات مدیریتی
        commands['پاک کردن'] = self.cmd_delete
        commands['ویرایش'] = self.cmd_edit
        commands['فوروارد'] = self.cmd_forward
        commands['کپی'] = self.cmd_copy
        
        # دستورات گروه
        commands['اعضا'] = self.cmd_members
        commands['ادمین'] = self.cmd_admins
        commands['لینک'] = self.cmd_link
        
        # دستورات سرگرمی
        commands['تاس'] = self.cmd_dice
        commands['قرعه'] = self.cmd_lottery
        commands['جوک'] = self.cmd_joke
        commands['شعر'] = self.cmd_poem
        commands['معما'] = self.cmd_riddle
        
        # دستورات ابزار
        commands['تایمر'] = self.cmd_timer
        commands['یادآوری'] = self.cmd_reminder
        commands['محاسبه'] = self.cmd_calculate
        
        return commands
    
    async def cmd_ping(self, event, args):
        start_time = time.time()
        msg = await event.reply(f"{Config.EMOJIS['ping']} پینگ...")
        end_time = time.time()
        ping_ms = round((end_time - start_time) * 1000, 2)
        await msg.edit(f"{Config.EMOJIS['ping']} پینگ: `{ping_ms}ms`")
    
    async def cmd_stats(self, event, args):
        # تعداد چت‌های فعال
        dialogs = await self.client.get_dialogs(limit=100)
        
        # آمار بنرها
        banner_stats = self.banner_system.get_banner_stats()
        
        # آمار دیتابیس
        commands_count = len(self.db.get_all_commands())
        
        stats_text = f"""
{Config.EMOJIS['stats']} **آمار کامل سلف بات**

📊 **اطلاعات کلی:**
├ کاربری: @{self.me.username}
├ شناسه: `{self.me.id}`
├ شماره: `{self.me.phone if self.me.phone else 'نامشخص'}`
├ چت‌های فعال: {len(dialogs)}
└ دستورات سفارشی: {commands_count}

📢 **سیستم بنر:**
├ بنرهای فعال: {banner_stats['total']}
├ گروه‌های دارای بنر: {len(banner_stats['chats'])}
└ وضعیت: فعال

💾 **سیستم:**
├ حافظه مصرفی: {self._get_memory_usage()}
├ لاگ‌های امروز: {self._get_today_logs()}
└ کاربران ویژه: {self._count_special_users()}

{Config.EMOJIS['time']} **زمان کار:**
{self._get_uptime()}
        """
        await event.reply(stats_text)
    
    async def cmd_banner(self, event, args):
        """تنظیم بنر با ریپلای - پشتیبانی از همه انواع مدیا"""
        if not event.is_reply:
            await event.reply(f"{Config.EMOJIS['error']} لطفاً روی پیام مورد نظر ریپلای کنید")
            return
        
        if not args:
            await event.reply(f"{Config.EMOJIS['error']} فرمت صحیح: `بنر [دقیقه]`\nمثال: `بنر 5`")
            return
        
        try:
            minutes = int(args[0])
            if minutes < 1 or minutes > 1440:
                await event.reply(f"{Config.EMOJIS['error']} دامنه مجاز: 1 تا 1440 دقیقه")
                return
            
            replied = await event.get_reply_message()
            
            # بررسی اینکه پیام محتوایی دارد
            if not replied.text and not replied.media:
                await event.reply(f"{Config.EMOJIS['error']} پیام باید محتوایی داشته باشد")
                return
            
            chat_id = event.chat_id
            success, message = await self.banner_system.add_banner(chat_id, replied, minutes)
            
            if success:
                # تشخیص نوع محتوا برای نمایش پیام
                media_type = self.banner_system._get_media_type(replied)
                media_info = {
                    'text': '📝 متن',
                    'photo': '🖼️ عکس',
                    'video': '🎬 ویدیو',
                    'sticker': '😀 استیکر',
                    'gif': '🎞️ گیف',
                    'voice': '🎤 ویس',
                    'audio': '🎵 آهنگ',
                    'document': '📎 فایل',
                    'unknown': '📦 محتوا'
                }
                
                content_type = media_info.get(media_type, '📦 محتوا')
                preview = replied.text[:50] if replied.text else f"{content_type}"
                
                await event.reply(
                    f"{Config.EMOJIS['success']} **بنر تنظیم شد!**\n\n"
                    f"⏰ **زمان‌بندی:** هر {minutes} دقیقه\n"
                    f"📦 **نوع محتوا:** {content_type}\n"
                    f"📝 **پیش‌نمایش:** `{preview}...`\n\n"
                    f"{Config.EMOJIS['info']} برای حذف: `حذف بنر`"
                )
            else:
                await event.reply(f"{Config.EMOJIS['error']} {message}")
                
        except ValueError:
            await event.reply(f"{Config.EMOJIS['error']} لطفاً عدد معتبر وارد کنید")
    
    async def cmd_settings(self, event, args):
        settings_text = f"""
{Config.EMOJIS['settings']} **تنظیمات سلف بات**

⚙️ **تنظیمات عمومی:**
├ API ID: `{Config.API_ID}`
├ سشن: `{Config.SESSION_NAME}`
├ حداکثر بنر: `{Config.MAX_BANNERS}`
├ بک‌آپ خودکار: هر `{Config.AUTO_BACKUP_MINUTES}` دقیقه
└ سطح لاگ: `{Config.LOG_LEVEL}`

📊 **آمار فعلی:**
├ بنرهای فعال: {len(self.banner_system.active_banners)}
├ دستورات سفارشی: {len(self.db.get_all_commands())}
└ زمان کار: {self._get_uptime()}

🔧 **راهنما:**
برای تغییر تنظیمات، فایل کد را ویرایش کنید.
        """
        await event.reply(settings_text)
    
    async def cmd_commands(self, event, args):
        custom_cmds = self.db.get_all_commands()
        builtin_cmds = list(self.builtin_commands.keys())
        
        response = f"{Config.EMOJIS['settings']} **لیست دستورات**\n\n"
        
        response += "🔹 **دستورات داخلی:**\n"
        for cmd in builtin_cmds[:20]:  # نمایش 20 دستور اول
            response += f"• `{cmd}`\n"
        
        if len(builtin_cmds) > 20:
            response += f"• و {len(builtin_cmds) - 20} دستور دیگر...\n"
        
        if custom_cmds:
            response += "\n🔸 **دستورات سفارشی:**\n"
            for cmd in custom_cmds:
                response += f"• `{cmd['command']}`\n"
        
        response += f"\n📖 برای اطلاعات بیشتر: `راهنما [دستور]`"
        await event.reply(response)
    
    async def cmd_help(self, event, args):
        if args:
            cmd = args[0]
            if cmd in self.builtin_commands:
                help_text = self._get_command_help(cmd)
                await event.reply(help_text)
            else:
                custom_response = self.db.get_custom_command(cmd)
                if custom_response:
                    await event.reply(f"دستور `{cmd}`: {custom_response}")
                else:
                    await event.reply(f"{Config.EMOJIS['error']} دستور `{cmd}` یافت نشد")
        else:
            help_text = f"""
{Config.EMOJIS['info']} **راهنمای جامع سلف بات**

📚 **دسته‌بندی دستورات:**

🔹 **مدیریتی:**
├ `آمار` - نمایش آمار کامل
├ `تنظیمات` - تنظیمات بات
├ `دستورات` - لیست دستورات
├ `پروفایل` - اطلاعات پروفایل
├ `خاموش` - خاموش کردن بات
└ `روشن` - روشن کردن بات (در ترمینال)

🔸 **بنر:**
├ `بنر [دقیقه]` - تنظیم بنر (با ریپلای روی هر پیام)
├ `حذف بنر` - حذف بنر گروه فعلی
├ `لیست بنرها` - نمایش بنرهای فعال
└ `آمار بنر` - آمار بنرها

🔹 **پیام:**
├ `پاک کردن` - حذف پیام (با ریپلای)
├ `ویرایش` - ویرایش پیام (با ریپلای)
├ `فوروارد` - فوروارد کردن پیام
└ `کپی` - کپی پیام

🔸 **گروه:**
├ `اعضا` - لیست اعضا
├ `ادمین` - لیست ادمین‌ها
├ `لینک` - دریافت لینک
└ `اطلاعات گروه` - اطلاعات گروه

🔹 **سرگرمی:**
├ `جوک` - جوک تصادفی
├ `شعر` - شعر فارسی
├ `تاس` - پرتاب تاس
├ `قرعه` - قرعه کشی
└ `معما` - معما

🔸 **ابزار:**
├ `زمان` - زمان فعلی
├ `تاریخ` - تاریخ امروز
├ `تایمر` - تایمر
├ `یادآوری` - یادآور
└ `محاسبه` - ماشین حساب

📖 برای اطلاعات هر دستور: `راهنما [دستور]`
            """
            await event.reply(help_text)
    
    async def cmd_shutdown(self, event, args):
        """خاموش کردن بات"""
        await event.reply(f"{Config.EMOJIS['warning']} بات در حال خاموش شدن...")
        # این دستور فقط اطلاع میده، خاموش کردن واقعی در ترمینال انجام میشه
        await event.reply(f"{Config.EMOJIS['info']} برای خاموش کردن کامل، در ترمینال Ctrl+C بزنید")
    
    async def cmd_startup(self, event, args):
        """روشن کردن بات - فقط اطلاع‌رسانی"""
        await event.reply(
            f"{Config.EMOJIS['success']} **بات فعال است!**\n\n"
            f"{Config.EMOJIS['info']} بات هم اکنون فعال است. برای مدیریت کامل به ترمینال مراجعه کنید."
        )
    
    async def cmd_remove_banner(self, event, args):
        """حذف بنر از گروه فعلی"""
        if not event.is_group:
            await event.reply(f"{Config.EMOJIS['error']} این دستور فقط در گروه کار می‌کند")
            return
        
        chat_id = event.chat_id
        if self.banner_system.remove_banner(chat_id):
            await event.reply(f"{Config.EMOJIS['success']} بنر این گروه حذف شد")
        else:
            await event.reply(f"{Config.EMOJIS['error']} بنری برای این گروه وجود ندارد")
    
    async def cmd_list_banners(self, event, args):
        """لیست بنرهای فعال"""
        banners = self.banner_system.active_banners
        
        if not banners:
            await event.reply(f"{Config.EMOJIS['info']} هیچ بنر فعالی وجود ندارد")
            return
        
        response = f"{Config.EMOJIS['banner']} **لیست بنرهای فعال**\n\n"
        
        media_icons = {
            'text': '📝',
            'photo': '🖼️',
            'video': '🎬',
            'sticker': '😀',
            'gif': '🎞️',
            'voice': '🎤',
            'audio': '🎵',
            'document': '📎',
            'unknown': '📦'
        }
        
        for idx, (chat_id, banner) in enumerate(banners.items(), 1):
            try:
                chat = await self.client.get_entity(chat_id)
                title = chat.title if hasattr(chat, 'title') else f"چت {chat_id}"
                
                icon = media_icons.get(banner.get('media_type', 'unknown'), '📦')
                preview = banner.get('message_text', 'بدون متن')[:30]
                
                response += f"{idx}. **{title}**\n"
                response += f"   {icon} هر {banner['interval']} دقیقه\n"
                response += f"   📝 `{preview}...`\n\n"
            except:
                response += f"{idx}. چت {chat_id}\n"
                response += f"   📦 هر {banner['interval']} دقیقه\n\n"
        
        response += f"{Config.EMOJIS['info']} برای حذف هر بنر در گروه مربوطه: `حذف بنر`"
        await event.reply(response)
    
    async def cmd_profile(self, event, args):
        me = self.me
        
        profile_text = f"""
{Config.EMOJIS['user']} **پروفایل کاربر**

👤 **اطلاعات اصلی:**
├ نام: {me.first_name or ''} {me.last_name or ''}
├ یوزرنیم: @{me.username or 'ندارد'}
├ شناسه: `{me.id}`
├ شماره: `{me.phone or 'مخفی'}`
└ ربات: {'✅' if me.bot else '❌'}

📊 **وضعیت:**
├ محدودیت: {'✅' if me.restricted else '❌'}
├ تأیید: {'✅' if me.verified else '❌'}
├ کلاهبرداری: {'✅' if me.scam else '❌'}
└ جعلی: {'✅' if me.fake else '❌'}

🔗 **لینک:**
tg://user?id={me.id}
        """
        await event.reply(profile_text)
    
    async def cmd_time(self, event, args):
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y/%m/%d")
        
        await event.reply(
            f"{Config.EMOJIS['time']} **زمان فعلی**\n\n"
            f"🕒 ساعت: `{time_str}`\n"
            f"📅 تاریخ: `{date_str}`\n"
            f"📆 روز هفته: `{self._get_persian_weekday(now.weekday())}`"
        )
    
    async def cmd_date(self, event, args):
        now = datetime.now()
        persian_date = self._get_persian_date(now)
        
        await event.reply(
            f"{Config.EMOJIS['time']} **تاریخ امروز**\n\n"
            f"📅 میلادی: `{now.strftime('%Y/%m/%d')}`\n"
            f"📅 شمسی: `{persian_date}`\n"
            f"📆 روز: `{self._get_persian_weekday(now.weekday())}`"
        )
    
    async def cmd_clock(self, event, args):
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        
        await event.reply(
            f"{Config.EMOJIS['time']} **ساعت**\n\n"
            f"🕒 دیجیتال: `{time_str}`\n"
            f"📅 تاریخ: `{now.strftime('%Y/%m/%d')}`"
        )
    
    async def cmd_delete(self, event, args):
        if event.is_reply:
            replied = await event.get_reply_message()
            await replied.delete()
            await event.delete()
        else:
            await event.reply(f"{Config.EMOJIS['error']} لطفاً روی پیام مورد نظر ریپلای کنید")
    
    async def cmd_edit(self, event, args):
        if event.is_reply and args:
            replied = await event.get_reply_message()
            new_text = ' '.join(args)
            await replied.edit(new_text)
            await event.delete()
        else:
            await event.reply(f"{Config.EMOJIS['error']} لطفاً روی پیام مورد نظر ریپلای کنید و متن جدید را بنویسید")
    
    async def cmd_forward(self, event, args):
        if event.is_reply:
            replied = await event.get_reply_message()
            if args and args[0].isdigit():
                try:
                    target_chat = int(args[0])
                    await self.client.forward_messages(target_chat, replied)
                    await event.reply(f"{Config.EMOJIS['success']} پیام فوروارد شد")
                except:
                    await event.reply(f"{Config.EMOJIS['error']} خطا در فوروارد")
            else:
                await event.reply(f"{Config.EMOJIS['error']} آیدی مقصد را وارد کنید")
        else:
            await event.reply(f"{Config.EMOJIS['error']} لطفاً روی پیام مورد نظر ریپلای کنید")
    
    async def cmd_copy(self, event, args):
        if event.is_reply:
            replied = await event.get_reply_message()
            await self.client.send_message(event.chat_id, replied.text if replied.text else "📎 فایل کپی شد")
            await event.delete()
        else:
            await event.reply(f"{Config.EMOJIS['error']} لطفاً روی پیام مورد نظر ریپلای کنید")
    
    async def cmd_members(self, event, args):
        if not event.is_group:
            await event.reply(f"{Config.EMOJIS['error']} این دستور فقط در گروه کار می‌کند")
            return
        
        try:
            participants = await self.client.get_participants(event.chat_id, limit=50)
            members_text = f"{Config.EMOJIS['group']} **اعضای گروه**\n\n"
            
            for i, user in enumerate(participants[:20], 1):
                name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                username = f"@{user.username}" if user.username else "بدون یوزرنیم"
                members_text += f"{i}. {name} ({username})\n"
            
            if len(participants) > 20:
                members_text += f"\nو {len(participants) - 20} عضو دیگر..."
            
            await event.reply(members_text)
        except Exception as e:
            await event.reply(f"{Config.EMOJIS['error']} خطا در دریافت اعضا: {str(e)}")
    
    async def cmd_admins(self, event, args):
        if not event.is_group:
            await event.reply(f"{Config.EMOJIS['error']} این دستور فقط در گروه کار می‌کند")
            return
        
        try:
            from telethon.tl.functions.channels import GetParticipantsRequest
            from telethon.tl.types import ChannelParticipantsAdmins
            
            admins = await self.client(GetParticipantsRequest(
                channel=event.chat_id,
                filter=ChannelParticipantsAdmins(),
                offset=0,
                limit=50,
                hash=0
            ))
            
            admins_text = f"{Config.EMOJIS['crown']} **ادمین‌های گروه**\n\n"
            
            for i, admin in enumerate(admins.participants[:15], 1):
                user = await self.client.get_entity(admin.user_id)
                name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                username = f"@{user.username}" if user.username else "بدون یوزرنیم"
                admins_text += f"{i}. {name} ({username})\n"
            
            await event.reply(admins_text)
        except Exception as e:
            await event.reply(f"{Config.EMOJIS['error']} خطا در دریافت ادمین‌ها: {str(e)}")
    
    async def cmd_link(self, event, args):
        if not event.is_group:
            await event.reply(f"{Config.EMOJIS['error']} این دستور فقط در گروه کار می‌کند")
            return
        
        try:
            chat = await self.client.get_entity(event.chat_id)
            if hasattr(chat, 'username') and chat.username:
                link = f"https://t.me/{chat.username}"
                await event.reply(f"{Config.EMOJIS['link']} **لینک گروه:**\n{link}")
            else:
                await event.reply(f"{Config.EMOJIS['error']} این گروه یوزرنیم ندارد")
        except Exception as e:
            await event.reply(f"{Config.EMOJIS['error']} خطا در دریافت لینک: {str(e)}")
    
    async def cmd_dice(self, event, args):
        result = random.randint(1, 6)
        emoji = "🎲"
        
        dice_art = {
            1: "┌─────┐\n│     │\n│  ●  │\n│     │\n└─────┘",
            2: "┌─────┐\n│ ●   │\n│     │\n│   ● │\n└─────┘",
            3: "┌─────┐\n│ ●   │\n│  ●  │\n│   ● │\n└─────┘",
            4: "┌─────┐\n│ ● ● │\n│     │\n│ ● ● │\n└─────┘",
            5: "┌─────┐\n│ ● ● │\n│  ●  │\n│ ● ● │\n└─────┘",
            6: "┌─────┐\n│ ● ● │\n│ ● ● │\n│ ● ● │\n└─────┘"
        }
        
        await event.reply(
            f"{emoji} **تاس**\n\n"
            f"🎯 نتیجه: **{result}**\n\n"
            f"```\n{dice_art[result]}\n```"
        )
    
    async def cmd_lottery(self, event, args):
        numbers = random.sample(range(1, 50), 6)
        numbers.sort()
        
        lottery_text = f"""
{Config.EMOJIS['money']} **قرعه کشی**

🎯 **اعداد برنده:**
`{' - '.join(map(str, numbers))}`

💰 **جوایز:**
├ 6 عدد: 10,000,000 تومان
├ 5 عدد: 1,000,000 تومان
├ 4 عدد: 100,000 تومان
└ 3 عدد: 10,000 تومان

🎉 **موفق باشید!**
        """
        await event.reply(lottery_text)
    
    async def cmd_joke(self, event, args):
        jokes = [
            "چرا کامپیوتر نمی‌تونه شام درست کنه؟ چون رمش کمه!",
            "چرا ریاضی‌دان‌ها عاشق زمستونن؟ چون برف همیشه سرد و محاسبه‌ست!",
            "دوست برنامه‌نویس بهم گفت: زندگی مثل یه کد بدون کامنت!",
            "چرا API به مهمونی دعوت نشد؟ چون همیشه response می‌ده!",
            "دو متغیر تو یه حلقه بود. یکی به دیگری گفت: بیا بریم break بخوریم!",
            "چرا دیتابیس از دکتر نترسید؟ چون همیشه backup داشت!",
            "یک بار یه فایل txt بهم گفت: من هیچ وقت نمی‌ترسم، همیشه openم!",
            "چرا کامپایلر عصبی شد؟ چون کدهارو parse نمی‌کرد!",
            "دو تا آرایه تو خیابون راه می‌رفتن. یکی به دیگری گفت: من indexم رو گم کردم!",
            "چرا کد مورس با پایتون مشکل داشت؟ چون snake_case دوست نداشت!"
        ]
        
        joke = random.choice(jokes)
        await event.reply(f"{Config.EMOJIS['like']} **جوک برنامه‌نویسی**\n\n{joke}")
    
    async def cmd_poem(self, event, args):
        poems = [
            ("حافظ", "بیا تا گل برافشانیم و می در ساغر اندازیم\nفلک را سقف بشکافیم و طرحی نو در اندازیم"),
            ("سعدی", "بنى آدم اعضاى يك پيكرند\nكه در آفرينش ز يك گوهرند\nچو عضوى به درد آورد روزگار\nدگر عضوها را نماند قرار"),
            ("مولوی", "بشنو از نی چون حکایت می‌کند\nاز جدایی‌ها شکایت می‌کند"),
            ("خیام", "این کوزه چو من عاشق زاری بوده است\nدر بند سر زلف نگاری بوده است\nاین دسته که بر گردن او می‌بینی\nدستی است که بر گردن یاری بوده است"),
            ("فروغ فرخزاد", "ای مرز پر گهر، ای هستی من\nای آسمان فرخ، ای ماه من\nای سرزمین سربلند آزاد\nای خاک پاک، ای وطن")
        ]
        
        poet, poem = random.choice(poems)
        await event.reply(f"📜 **شعر از {poet}**\n\n{poem}")
    
    async def cmd_riddle(self, event, args):
        riddles = [
            ("چیزی که می‌گیرد اما هرگز نمی‌دهد؟", "عکس"),
            ("هرچه بیشتر بگیرد کمتر می‌ماند؟", "حفره"),
            ("پایه دارد اما نمی‌ایستد؟", "میز"),
            ("شهرها دارد اما خانه ندارد، کوه‌ها دارد اما درخت ندارد، آب دارد اما ماهی ندارد؟", "نقشه"),
            ("همیشه جلو می‌رود اما هرگز به جایی نمی‌رسد؟", "ساعت")
        ]
        
        riddle, answer = random.choice(ridles)
        
        # 10 ثانیه تأخیر برای جواب
        await event.reply(f"🤔 **معما**\n\n{riddle}")
        await asyncio.sleep(10)
        await event.reply(f"💡 **جواب:** {answer}")
    
    async def cmd_timer(self, event, args):
        if not args or not args[0].isdigit():
            await event.reply(f"{Config.EMOJIS['error']} فرمت صحیح: `تایمر [ثانیه]`\nمثال: `تایمر 60`")
            return
        
        seconds = int(args[0])
        if seconds > 3600:
            await event.reply(f"{Config.EMOJIS['error']} حداکثر زمان: 3600 ثانیه (1 ساعت)")
            return
        
        await event.reply(f"⏱️ تایمر {seconds} ثانیه‌ای شروع شد...")
        await asyncio.sleep(seconds)
        await event.reply(f"⏰ **زمان تمام شد!**\nتایمر {seconds} ثانیه‌ای به پایان رسید.")
    
    async def cmd_reminder(self, event, args):
        if len(args) < 2:
            await event.reply(f"{Config.EMOJIS['error']} فرمت صحیح: `یادآوری [زمان] [یادداشت]`\nمثال: `یادآوری 10 خرید نان`")
            return
        
        if not args[0].isdigit():
            await event.reply(f"{Config.EMOJIS['error']} زمان باید عدد باشد")
            return
        
        seconds = int(args[0])
        note = ' '.join(args[1:])
        
        if seconds > 86400:
            await event.reply(f"{Config.EMOJIS['error']} حداکثر زمان: 86400 ثانیه (24 ساعت)")
            return
        
        await event.reply(f"📝 **یادآوری ثبت شد**\n⏰ {seconds} ثانیه دیگر\n📌 {note}")
        
        await asyncio.sleep(seconds)
        await event.reply(f"🔔 **یادآوری!**\n\n{note}")
    
    async def cmd_calculate(self, event, args):
        if not args:
            await event.reply(f"{Config.EMOJIS['error']} فرمت صحیح: `محاسبه [عبارت ریاضی]`\nمثال: `محاسبه 2+2*3`")
            return
        
        try:
            # امنیت: فقط کاراکترهای ریاضی مجاز
            expression = ''.join(args)
            allowed_chars = set('0123456789+-*/(). ')
            
            if not all(c in allowed_chars for c in expression):
                await event.reply(f"{Config.EMOJIS['error']} فقط عبارات ریاضی ساده مجاز هستند")
                return
            
            result = eval(expression)
            await event.reply(f"🧮 **محاسبه**\n\n`{expression} = {result}`")
            
        except Exception as e:
            await event.reply(f"{Config.EMOJIS['error']} خطا در محاسبه: {str(e)}")
    
    def _get_memory_usage(self):
        try:
            import psutil
            return f"{psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB"
        except:
            return "نامشخص"
    
    def _get_today_logs(self):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM logs 
                    WHERE DATE(timestamp) = DATE('now')
                """)
                return cursor.fetchone()[0]
        except:
            return 0
    
    def _count_special_users(self):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM special_users")
                return cursor.fetchone()[0]
        except:
            return 0
    
    def _get_uptime(self):
        uptime = int(time.time() - self.start_time)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _get_persian_weekday(self, weekday):
        days = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یکشنبه"]
        return days[weekday]
    
    def _get_persian_date(self, date):
        # تبدیل ساده تاریخ
        year = date.year - 621
        month = date.month
        day = date.day
        
        persian_months = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]
        
        month_name = persian_months[month - 1] if 1 <= month <= 12 else "نامشخص"
        return f"{year}/{month_name}/{day}"
    
    def _get_command_help(self, cmd):
        helps = {
            'پینگ': 'اندازه‌گیری زمان پاسخ سرور',
            'آمار': 'نمایش آمار کامل بات',
            'بنر': 'تنظیم بنر زمان‌بندی شده (با ریپلای روی هر پیام)',
            'تنظیمات': 'نمایش تنظیمات بات',
            'دستورات': 'لیست همه دستورات',
            'راهنما': 'راهنمای دستورات',
            'خاموش': 'اطلاع‌رسانی خاموش شدن بات',
            'روشن': 'اطلاع‌رسانی روشن بودن بات',
            'حذف بنر': 'حذف بنر گروه فعلی',
            'لیست بنرها': 'نمایش بنرهای فعال',
            'پروفایل': 'نمایش اطلاعات پروفایل',
            'زمان': 'نمایش زمان فعلی',
            'تاریخ': 'نمایش تاریخ امروز',
            'ساعت': 'نمایش ساعت',
            'پاک کردن': 'حذف پیام (با ریپلای)',
            'ویرایش': 'ویرایش پیام (با ریپلای)',
            'فوروارد': 'فوروارد پیام به آیدی دیگر',
            'کپی': 'کپی کردن پیام',
            'اعضا': 'لیست اعضای گروه',
            'ادمین': 'لیست ادمین‌های گروه',
            'لینک': 'دریافت لینک گروه',
            'تاس': 'پرتاب تاس تصادفی',
            'قرعه': 'قرعه کشی اعداد',
            'جوک': 'جوک برنامه‌نویسی تصادفی',
            'شعر': 'شعر فارسی تصادفی',
            'معما': 'معما با جواب',
            'تایمر': 'تایمر (ثانیه)',
            'یادآوری': 'یادآوری با زمان',
            'محاسبه': 'ماشین حساب ریاضی'
        }
        return helps.get(cmd, f"دستور `{cmd}` - توضیحی موجود نیست")

# ==================== سیستم زمان‌بندی ====================
class Scheduler:
    def __init__(self):
        self.tasks = {}
        self.running = True
        
    def add_task(self, name, interval, func, *args, **kwargs):
        self.tasks[name] = {
            'interval': interval,
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'last_run': 0
        }
    
    def remove_task(self, name):
        if name in self.tasks:
            del self.tasks[name]
    
    async def run(self):
        while self.running:
            current_time = time.time()
            for name, task in self.tasks.items():
                if current_time - task['last_run'] >= task['interval']:
                    try:
                        if asyncio.iscoroutinefunction(task['func']):
                            await task['func'](*task['args'], **task['kwargs'])
                        else:
                            task['func'](*task['args'], **task['kwargs'])
                        task['last_run'] = current_time
                    except Exception as e:
                        print(f"خطا در اجرای تسک {name}: {e}")
            await asyncio.sleep(1)
    
    def stop(self):
        self.running = False

# ==================== سیستم امنیتی ====================
class SecuritySystem:
    def __init__(self, db: Database):
        self.db = db
        self.blocked_users = set()
        self.rate_limits = {}
        
    def check_rate_limit(self, user_id, limit=10, window=60):
        current_time = time.time()
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        
        # حذف درخواست‌های قدیمی
        self.rate_limits[user_id] = [
            t for t in self.rate_limits[user_id]
            if current_time - t < window
        ]
        
        if len(self.rate_limits[user_id]) >= limit:
            return False
        
        self.rate_limits[user_id].append(current_time)
        return True
    
    def is_user_allowed(self, user_id):
        return not self.is_user_blocked(user_id) and self.db.is_special_user(user_id)
    
    def block_user(self, user_id):
        self.blocked_users.add(user_id)
    
    def unblock_user(self, user_id):
        self.blocked_users.discard(user_id)
    
    def is_user_blocked(self, user_id):
        return user_id in self.blocked_users

# ==================== سلف بات اصلی ====================
class UltraSelfBot:
    def __init__(self):
        self.client = None
        self.db = Database()
        self.banner_system = None
        self.command_system = None
        self.scheduler = Scheduler()
        self.security = SecuritySystem(self.db)
        self.is_running = False
        self.start_time = time.time()
        
        # تنظیم لاگینگ
        self.setup_logging()
        
    def setup_logging(self):
        os.makedirs(Config.LOGS_DIR, exist_ok=True)
        logging.basicConfig(
            level=Config.LOG_LEVEL,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{Config.LOGS_DIR}/selfbot.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        try:
            self.client = TelegramClient(
                Config.SESSION_NAME,
                Config.API_ID,
                Config.API_HASH
            )
            
            # شروع HTTP Server برای Health Check
            print(f"{Config.Colors.GREEN}🚀 شروع HTTP Server برای Health Check...{Config.Colors.RESET}")
            start_http_server(Config.HTTP_PORT)
            
            # ایجاد session اگر وجود ندارد
            session_file = f"{Config.SESSION_NAME}.session"
            if not os.path.exists(session_file):
                print(f"{Config.Colors.YELLOW}⚠️ فایل session یافت نشد: {session_file}{Config.Colors.RESET}")
                print(f"{Config.Colors.YELLOW}📱 لطفاً با استفاده از QR Code یا دستی وارد شوید{Config.Colors.RESET}")
                
                # روش‌های مختلف لاگین
                print(f"{Config.Colors.CYAN}🔧 روش‌های ورود:{Config.Colors.RESET}")
                print("1. استفاده از QR Code")
                print("2. وارد کردن شماره تلفن و کد")
                
                # امتحان QR Code اول
                try:
                    print(f"{Config.Colors.YELLOW}🔐 تلاش برای ورود با QR Code...{Config.Colors.RESET}")
                    await self.client.connect()
                    
                    if not await self.client.is_user_authorized():
                        # QR Code
                        qr_login = await self.client.qr_login()
                        print(f"{Config.Colors.GREEN}📱 لطفاً QR Code زیر را در تلگرام اسکن کنید:{Config.Colors.RESET}")
                        print(f"\n{qr_login.url}")
                        await qr_login.wait()
                except Exception as qr_error:
                    print(f"{Config.Colors.RED}❌ خطا در ورود با QR: {qr_error}{Config.Colors.RESET}")
                    print(f"{Config.Colors.YELLOW}🔄 استفاده از روش دستی...{Config.Colors.RESET}")
                    await self.client.start()
            else:
                print(f"{Config.Colors.GREEN}✅ فایل session موجود است. اتصال...{Config.Colors.RESET}")
                await self.client.start()
            
            self.is_running = True
            
            me = await self.client.get_me()
            self.logger.info(f"✅ سلف بات شروع شد: @{me.username} (ID: {me.id})")
            
            # راه‌اندازی سیستم‌ها
            self.banner_system = BannerSystem(self.db, self.client)
            self.command_system = CommandSystem(self.db, self.banner_system, self.client)
            await self.command_system.initialize()
            
            # تنظیم هندلرها
            await self.setup_handlers()
            
            # شروع زمان‌بندها
            self.setup_schedulers()
            
            # آپدیت پروفایل
            asyncio.create_task(self.update_profile_loop())
            
            # اطلاع‌رسانی شروع
            await self.notify_startup()
            
            # چاپ اطلاعات سلامت
            print(f"{Config.Colors.GREEN}✅ سلف بات با موفقیت شروع شد!{Config.Colors.RESET}")
            print(f"{Config.Colors.CYAN}👤 کاربر: @{me.username}{Config.Colors.RESET}")
            print(f"{Config.Colors.CYAN}📱 شماره: {me.phone}{Config.Colors.RESET}")
            print(f"{Config.Colors.CYAN}🌐 Health Check: http://localhost:{Config.HTTP_PORT}/health{Config.Colors.RESET}")
            print(f"{Config.Colors.CYAN}📊 وضعیت: در حال اجرا...{Config.Colors.RESET}")
            
            await self.client.run_until_disconnected()
            
        except Exception as e:
            self.logger.error(f"خطا در شروع بات: {e}")
            raise
    
    async def setup_handlers(self):
        @self.client.on(events.NewMessage())
        async def message_handler(event):
            # فقط پیام‌های خود کاربر
            me = await self.client.get_me()
            if event.sender_id != me.id:
                return
            
            # بررسی ریت لیمیت
            if not self.security.check_rate_limit(event.sender_id):
                await event.reply(f"{Config.EMOJIS['warning']} درخواست‌های شما زیاد است! لطفاً صبر کنید.")
                return
            
            # پردازش دستور
            await self.process_command(event)
        
        @self.client.on(events.MessageEdited())
        async def edit_handler(event):
            me = await self.client.get_me()
            if event.sender_id == me.id:
                await self.process_command(event)
        
        @self.client.on(events.ChatAction())
        async def chat_action_handler(event):
            pass  # هندلر برای رویدادهای چت
    
    async def process_command(self, event):
        text = event.raw_text.strip()
        if not text:
            return
        
        # جداسازی دستور و آرگومان‌ها
        parts = text.split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # بررسی دستور سفارشی
        custom_response = self.db.get_custom_command(command)
        if custom_response:
            await event.reply(custom_response)
            return
        
        # بررسی دستور داخلی
        if command in self.command_system.builtin_commands:
            try:
                await self.command_system.builtin_commands[command](event, args)
            except Exception as e:
                await event.reply(f"{Config.EMOJIS['error']} خطا در اجرای دستور: {str(e)}")
        else:
            # اگر دستور ناشناس بود، نادیده بگیر
            pass
    
    def setup_schedulers(self):
        # زمان‌بند بنرها
        self.scheduler.add_task(
            'banners',
            30,  # هر 30 ثانیه چک کن
            self.banner_system.send_scheduled_banners
        )
        
        # آپدیت خودکار
        if Config.AUTO_BACKUP_MINUTES > 0:
            self.scheduler.add_task(
                'auto_backup',
                Config.AUTO_BACKUP_MINUTES * 60,
                self.auto_backup
            )
        
        # شروع زمان‌بند در پس‌زمینه
        asyncio.create_task(self.scheduler.run())
    
    async def update_profile_loop(self):
        while self.is_running:
            try:
                now = datetime.now()
                
                # آپدیت نام با ساعت
                time_str = now.strftime("%H:%M")
                await self.client(UpdateProfileRequest(
                    first_name=f"⏰ {time_str}",
                    about=f"سلف بات حرفه‌ای\n🆔 {self.client.uid}\n⏱ {self.get_uptime()}"
                ))
                
                # آپدیت هر دقیقه
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"خطا در آپدیت پروفایل: {e}")
                await asyncio.sleep(300)  # 5 دقیقه صبر کن
    
    async def notify_startup(self):
        try:
            me = await self.client.get_me()
            startup_msg = f"""
{Config.EMOJIS['robot']} **سلف بات فعال شد!**

👤 **کاربر:** @{me.username}
🆔 **شناسه:** `{me.id}`
📱 **تلفن:** `{me.phone}`
⏰ **زمان:** {datetime.now().strftime("%Y/%m/%d %H:%M:%S")}
🏓 **پینگ:** در حال اندازه‌گیری...

⚙️ **سیستم آماده به کار!**
📢 **دستور بنر:** روی هر پیام ریپلای کن و بنویس `بنر 5`
🗑️ **حذف بنر:** در هر گروه بنویس `حذف بنر`
            """
            await self.client.send_message('me', startup_msg)
        except Exception as e:
            self.logger.error(f"خطا در ارسال اطلاع شروع: {e}")
    
    async def auto_backup(self):
        try:
            os.makedirs(Config.BACKUP_DIR, exist_ok=True)
            backup_file = f"{Config.BACKUP_DIR}/backup_{int(time.time())}.db"
            
            import shutil
            shutil.copy2(Config.DATABASE_PATH, backup_file)
            
            # حذف بک‌آپ‌های قدیمی
            backups = sorted([
                f for f in os.listdir(Config.BACKUP_DIR)
                if f.startswith('backup_')
            ])
            
            if len(backups) > 10:  # فقط 10 بک‌آپ آخر را نگه دار
                for old_backup in backups[:-10]:
                    os.remove(f"{Config.BACKUP_DIR}/{old_backup}")
                    
            self.logger.info(f"بک‌آپ ایجاد شد: {backup_file}")
            
        except Exception as e:
            self.logger.error(f"خطا در بک‌آپ: {e}")
    
    def get_uptime(self):
        uptime = int(time.time() - self.start_time)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    async def stop(self):
        self.is_running = False
        self.scheduler.stop()
        
        if self.client:
            await self.client.disconnect()
        
        self.logger.info("سلف بات متوقف شد")

# ==================== اجرای اصلی ====================
async def main():
    bot = UltraSelfBot()
    
    print(f"{Config.Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                                                          ║")
    print("║  ░█▀▀░█▀█░█▀▄░█▀▀░▀█▀░█▀█░█▀▀  ░█▀▀░▀█▀░█▀█░█▀▀░█░█     ║")
    print("║  ░█▀▀░█░█░█░█░█▀▀░░█░░█░█░█░█  ░▀▀█░░█░░█░█░█▀▀░▄▀▄     ║")
    print("║  ░▀░░░▀▀▀░▀▀░░▀▀▀░░▀░░▀▀▀░▀▀▀  ░▀▀▀░░▀░░▀▀▀░▀▀▀░▀░▀     ║")
    print("║                                                          ║")
    print("║                  v2.0 - 700+ خط کد                      ║")
    print("║              سلف بات حرفه‌ای فارسی                     ║")
    print("║                    نسخه Cloud-Ready                     ║")
    print("║                                                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Config.Colors.RESET}")
    
    try:
        print(f"{Config.Colors.GREEN}🚀 در حال شروع سلف بات برای Koyeb...{Config.Colors.RESET}")
        print(f"{Config.Colors.YELLOW}📝 نکته: برای توقف، Ctrl+C بزنید{Config.Colors.RESET}")
        await bot.start()
    except KeyboardInterrupt:
        print(f"\n{Config.Colors.YELLOW}⏹️ توقف توسط کاربر{Config.Colors.RESET}")
        await bot.stop()
    except Exception as e:
        print(f"{Config.Colors.RED}❌ خطا: {e}{Config.Colors.RESET}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # ایجاد پوشه‌های لازم
    os.makedirs(Config.BACKUP_DIR, exist_ok=True)
    os.makedirs(Config.LOGS_DIR, exist_ok=True)
    
    # اجرای برنامه
    asyncio.run(main())
