import asyncio
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import (
    Channel, Chat, User,
    MessageMediaPhoto, MessageMediaDocument,
    MessageMediaContact, MessageMediaGeo,
    MessageMediaPoll, DocumentAttributeSticker,
    DocumentAttributeAudio, DocumentAttributeFilename,
    DocumentAttributeVideo, DocumentAttributeAnimated,
    UserStatusOnline, UserStatusOffline,
    UserStatusRecently, UserStatusLastWeek,
    UserStatusLastMonth, UserStatusEmpty,
    MessageEntityCustomEmoji
)
from telethon.tl.functions.messages import GetCustomEmojiDocumentsRequest



import config

class TelegramManager:
    def __init__(self):
        self.client = TelegramClient(config.SESSION_FILE, config.API_ID, config.API_HASH)
        self.me = None
        self.dialogs = []
        self.active_entity = None
        self.new_message_callback = None

    async def init(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            return False
        self.me = await self.client.get_me()
        self.setup_listeners()
        return True

    async def login_interactive(self):
        """Interactive terminal login"""
        await self.client.start()
        self.me = await self.client.get_me()
        self.setup_listeners()
        return True

    def setup_listeners(self):
        @self.client.on(events.NewMessage)
        async def handler(event):
            if self.new_message_callback:
                chat_id = event.chat_id
                msg_info = self.format_message(event.message)
                await self.new_message_callback(chat_id, event.message, msg_info)

    def set_on_new_message(self, callback):
        self.new_message_callback = callback

    def format_message(self, message):
        """Format message to clean, monochrome, distraction-free text"""
        date_str = ""
        if message.date:
            try:
                date_str = message.date.astimezone().strftime("%H:%M")
            except Exception:
                date_str = message.date.strftime("%H:%M")

        is_outgoing = message.out
        sender_name = "You" if is_outgoing else "User"

        if not is_outgoing and message.sender:
            if hasattr(message.sender, 'first_name'):
                name_parts = [message.sender.first_name or ""]
                if getattr(message.sender, 'last_name', None):
                    name_parts.append(message.sender.last_name)
                sender_name = " ".join(filter(None, name_parts)) or "Unknown"
            elif hasattr(message.sender, 'title'):
                sender_name = message.sender.title

        # Media tags (clean and simple, no clutter)
        media_tag = ""
        if message.media:
            if isinstance(message.media, MessageMediaPhoto):
                media_tag = "[Photo]"
            elif isinstance(message.media, MessageMediaDocument):
                doc = message.media.document
                is_sticker = False
                is_voice = False
                is_audio = False
                is_video = False
                is_gif = False
                file_name = None
                audio_title = ""

                if doc and hasattr(doc, 'attributes'):
                    for attr in doc.attributes:
                        if isinstance(attr, DocumentAttributeAnimated):
                            is_gif = True
                        elif isinstance(attr, DocumentAttributeSticker):
                            is_sticker = True
                        elif isinstance(attr, DocumentAttributeAudio):
                            if getattr(attr, 'voice', False):
                                is_voice = True
                                media_tag = f"[Voice {attr.duration}s]"
                            else:
                                is_audio = True
                                audio_title = attr.title or attr.performer or "Audio"
                                media_tag = f"[Audio: {audio_title}]"
                        elif isinstance(attr, DocumentAttributeVideo):
                            is_video = True
                        elif isinstance(attr, DocumentAttributeFilename):
                            file_name = attr.file_name

                if is_gif:
                    media_tag = "[GIF]"
                elif is_sticker:
                    media_tag = "[Sticker]"
                elif is_video:
                    media_tag = "[Video]"
                elif not is_voice and not is_audio:
                    if file_name:
                        media_tag = f"[File: {file_name}]"
                    else:
                        media_tag = "[File]"
            elif isinstance(message.media, MessageMediaContact):
                media_tag = f"[Contact: {message.media.phone_number}]"
            elif isinstance(message.media, MessageMediaGeo):
                media_tag = "[Location]"
            elif isinstance(message.media, MessageMediaPoll):
                media_tag = f"[Poll: {message.media.poll.question}]"
            else:
                media_tag = "[Attachment]"

        # Check for Telegram Premium custom emojis
        custom_emojis = [e for e in (message.entities or []) if isinstance(e, MessageEntityCustomEmoji)]
        if not media_tag and custom_emojis:
            media_tag = f"[Emoji x{len(custom_emojis)}]" if len(custom_emojis) > 1 else "[Emoji]"

        text = message.raw_text or ""
        if media_tag:
            full_text = f"{media_tag} {text}".strip()
        else:
            full_text = text.strip() or "[Empty message]"


        return {
            "id": message.id,
            "sender_name": sender_name,
            "is_outgoing": is_outgoing,
            "time": date_str,
            "text": full_text,
            "raw_message": message
        }

    async def get_dialogs_list(self, show_channels=False):
        """Fetch dialogs (chats) list"""
        dialogs = []
        async for dialog in self.client.iter_dialogs(limit=config.DIALOGS_LIMIT):
            entity = dialog.entity
            is_channel = isinstance(entity, Channel) and not entity.megagroup
            
            if not show_channels and is_channel:
                continue

            dialogs.append({
                "id": dialog.id,
                "name": (dialog.name or "Unnamed").strip(),
                "entity": entity,
                "unread_count": dialog.unread_count,
                "is_channel": is_channel,
                "dialog": dialog
            })
        self.dialogs = dialogs
        return dialogs

    async def get_chat_history(self, entity, limit=config.MESSAGE_LIMIT):
        """Fetch chat history"""
        messages = []
        async for msg in self.client.iter_messages(entity, limit=limit):
            messages.append(self.format_message(msg))
        messages.reverse()
        return messages

    async def send_text(self, entity, text):
        """Send message"""
        if not text or not text.strip():
            return None
        msg = await self.client.send_message(entity, text)
        return self.format_message(msg)

    async def mark_as_read(self, entity, max_id=None):
        """Mark chat messages as read on Telegram servers"""
        try:
            await self.client.send_read_acknowledge(entity, max_id=max_id)
            return True
        except Exception:
            return False

    async def send_media_file(self, entity, file_path, caption=None):
        """Send photo, video, audio, or document file"""
        from pathlib import Path
        import os

        clean_path = file_path.strip().strip("'\"")
        expanded = os.path.expanduser(clean_path)
        path_obj = Path(expanded).resolve()

        if not path_obj.exists():
            return None, f"File not found: {clean_path}"
        if not path_obj.is_file():
            return None, f"Not a valid file: {clean_path}"

        try:
            msg = await self.client.send_file(entity, str(path_obj), caption=caption)
            return self.format_message(msg), None
        except Exception as e:
            return None, f"Failed to upload: {e}"



    async def download_and_open_media(self, message):
        """Download and open media or premium custom emoji upon explicit user request"""
        if not message:
            return False, "No message selected."

        has_media = bool(message.media)
        custom_emojis = [e for e in (message.entities or []) if isinstance(e, MessageEntityCustomEmoji)]

        if not has_media and not custom_emojis:
            return False, "No media or premium emoji found in this message."

        cache_dir = config.PROJECT_DIR / "cache"
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            cache_dir = config.PROJECT_DIR

        try:
            if has_media:
                file_path = await self.client.download_media(message, file=str(cache_dir))
            else:
                # Fetch premium custom emoji document from Telegram
                emoji_id = custom_emojis[0].document_id
                docs = await self.client(GetCustomEmojiDocumentsRequest(document_id=[emoji_id]))
                if docs:
                    file_path = await self.client.download_media(docs[0], file=str(cache_dir))
                else:
                    return False, "Could not fetch premium emoji."

            if file_path:
                import subprocess
                import shutil
                opener = None
                for cmd in ["termux-open", "xdg-open", "open"]:
                    if shutil.which(cmd):
                        opener = cmd
                        break
                if opener:
                    subprocess.Popen([opener, file_path])
                    return True, f"Opened with {opener}: {file_path}"
                return True, f"Saved to {file_path}"
            return False, "Failed to download."
        except Exception as e:
            return False, f"Error: {e}"


    def get_entity_status(self, entity):
        """Format online/offline status and last seen timestamp"""
        if not entity:
            return ""

        if isinstance(entity, User):
            if getattr(entity, 'bot', False):
                return "bot"
            if getattr(entity, 'is_self', False):
                return ""

            status = getattr(entity, 'status', None)
            if not status:
                return ""

            if isinstance(status, UserStatusOnline):
                return "online"
            elif isinstance(status, UserStatusOffline):
                if status.was_online:
                    try:
                        local_dt = status.was_online.astimezone()
                        now = datetime.now(local_dt.tzinfo)
                        if local_dt.date() == now.date():
                            return f"last seen today at {local_dt.strftime('%H:%M')}"
                        elif (now.date() - local_dt.date()).days == 1:
                            return f"last seen yesterday at {local_dt.strftime('%H:%M')}"
                        else:
                            return f"last seen {local_dt.strftime('%d.%m.%y %H:%M')}"
                    except Exception:
                        return f"last seen {status.was_online.strftime('%H:%M')}"
                return "offline"
            elif isinstance(status, UserStatusRecently):
                return "last seen recently"
            elif isinstance(status, UserStatusLastWeek):
                return "last seen within a week"
            elif isinstance(status, UserStatusLastMonth):
                return "last seen within a month"
            elif isinstance(status, UserStatusEmpty):
                return ""
            return "offline"

        elif isinstance(entity, Channel):
            if not entity.megagroup:
                return "channel"
            return "group"
        elif isinstance(entity, Chat):
            return "group"

        return ""

    async def get_fresh_entity_status(self, entity):
        """Fetch fresh user/chat status from Telegram"""
        try:
            fresh_entity = await self.client.get_entity(entity)
            return self.get_entity_status(fresh_entity)
        except Exception:
            return self.get_entity_status(entity)


