"""
Core TgLoader implementation
"""

import os
import asyncio
import datetime
import time
import yaml
from pathlib import Path
from typing import Dict, Optional, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

import dotenv
from telethon import TelegramClient
from telethon.tl.types import (
    Channel, User, Chat, MessageMediaPhoto, MessageMediaDocument,
    DocumentAttributeFilename, DocumentAttributeVideo, DocumentAttributeAudio,
    Message, Dialog
)
from telethon.errors import FileReferenceExpiredError, FloodWaitError

from .lang import get_text


class MediaType(Enum):
    """Media file types"""
    PHOTO = ('🖼️', 'jpg')
    VIDEO = ('📽️', 'mp4')
    AUDIO = ('🔉', 'mp3')
    GIF = ('📽️(gif)', 'gif')
    DOCUMENT = ('📄', 'file')


@dataclass
class DownloadStats:
    """Download statistics"""
    total_files: int = 0
    total_size: int = 0
    images: Tuple[int, int] = (0, 0)
    videos: Tuple[int, int] = (0, 0)
    audio: Tuple[int, int] = (0, 0)
    processing_time: float = 0.0


@dataclass
class TimeRange:
    """Time range for downloading"""
    from_date: Optional[datetime.datetime] = None
    to_date: Optional[datetime.datetime] = None
    from_id: Optional[int] = None
    to_id: Optional[int] = None


class TgLoaderError(Exception):
    """Base exception for TgLoader"""
    pass


class RestartChannelProcessing(TgLoaderError):
    """Exception for restarting channel processing"""
    
    def __init__(self, error_date: datetime.datetime, error_msg: str):
        self.error_date = error_date
        self.error_msg = error_msg
        super().__init__(f'Restart required from {error_date}: {error_msg}')


class TgLoader:
    """Modern Telegram media downloader library"""
    
    # File extensions by type
    FILE_EXTENSIONS = {
        'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'},
        'videos': {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.mpeg'},
        'audio': {'.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'}
    }

    def __init__(self, env_path: str = '.env', lang: str = 'en', concurrency: int = 1):
        """
        Initialize TgLoader
        
        Args:
            env_path: Path to .env file (default: '.env' in current directory)
            lang: Language for messages ('en' or 'ru', default: 'en')  
            concurrency: Maximum concurrent downloads (default: 1)
        """
        self.env_path = env_path
        self.lang = lang
        self.concurrency = concurrency
        
        dotenv.load_dotenv(env_path)
        
        self.api_id = os.getenv('api_id')
        self.api_hash = os.getenv('api_hash')
        
        if not self.api_id or not self.api_hash:
            raise TgLoaderError(get_text(lang, 'errors.api_missing'))
        
        self.api_id = int(self.api_id)
        
        self.semaphore = None
        self.slot_queue = None
        self.slot_colors = self._generate_slot_colors()
        self.client: Optional[TelegramClient] = None

    def _generate_slot_colors(self) -> Dict[int, str]:
        """Generate colors for download slots"""
        if self.concurrency <= 1:
            return {1: '\033[38;2;0;255;0m'}
        
        return {
            i: f'\033[38;2;0;{int(255 - (255 - 100) * ((i - 1) / (self.concurrency - 1)))};0m'
            for i in range(1, self.concurrency + 1)
        }

    async def _init_async_components(self):
        """Initialize async components"""
        if self.semaphore is None:
            self.semaphore = asyncio.Semaphore(self.concurrency)
            self.slot_queue = asyncio.Queue()
            
            for i in range(1, self.concurrency + 1):
                self.slot_queue.put_nowait(i)

    async def _get_client(self):
        """Get or create Telegram client"""
        if self.client is None:
            self.client = TelegramClient(
                'session',
                self.api_id, 
                self.api_hash,
                system_version="4.16.30-vxCUSTOM",
                device_model="Samsung Galaxy S24 Ultra",
                app_version="1.0.1", 
                lang_code='en',
                system_lang_code='en'
            )
            await self.client.start()
        return self.client

    @staticmethod
    def parse_date_or_id(value_str: str, is_end_of_day: bool = False) -> Tuple[Optional[datetime.datetime], Optional[int]]:
        """Parse date or message ID from string"""
        if value_str is None:
            return None, None
            
        value_str = value_str.strip()
        
        if value_str.isdigit():
            return None, int(value_str)
        
        value_str = value_str.upper()
        
        if value_str == 'NOW':
            return datetime.datetime.now(datetime.timezone.utc), None
        
        if value_str == 'OLDEST':
            return None, None
        
        if value_str.startswith('NOW-'):
            try:
                time_part = value_str[4:]
                if time_part.endswith('D'):
                    days = int(time_part[:-1])
                    dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
                    return dt, None
                elif time_part.endswith('H'):
                    hours = int(time_part[:-1])
                    dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours)
                    return dt, None
                elif time_part.endswith('m'):
                    minutes = int(time_part[:-1])
                    dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=minutes)
                    return dt, None
            except ValueError:
                pass
        
        try:
            dt = datetime.datetime.strptime(value_str, '%Y-%m-%d')
            if is_end_of_day:
                dt = dt.replace(hour=23, minute=59, second=59)
            return dt.replace(tzinfo=datetime.timezone.utc), None
        except ValueError as e:
            raise ValueError(f'Invalid format: {value_str}. Expected YYYY-MM-DD or message ID') from e

    def _get_media_type_and_extension(self, media) -> Tuple[str, str]:
        """Determine media type and extension"""
        if isinstance(media, MessageMediaPhoto):
            return MediaType.PHOTO.value
        
        if isinstance(media, MessageMediaDocument):
            attributes = media.document.attributes
            
            if any(isinstance(attr, DocumentAttributeVideo) for attr in attributes):
                return MediaType.VIDEO.value
            
            if any(isinstance(attr, DocumentAttributeAudio) for attr in attributes):
                return MediaType.AUDIO.value
            
            if any(isinstance(attr, DocumentAttributeFilename) and 
                   attr.file_name.lower().endswith('.gif') for attr in attributes):
                return MediaType.GIF.value
            
            return MediaType.DOCUMENT.value
        
        raise ValueError(get_text(self.lang, 'errors.unsupported_media'))

    def _get_dialog_type(self, entity) -> str:
        """Determine dialog type"""
        if hasattr(entity, 'broadcast') and entity.broadcast:
            return get_text(self.lang, 'dialogs.channel')
        if hasattr(entity, 'megagroup') and entity.megagroup:
            return get_text(self.lang, 'dialogs.group')
        if isinstance(entity, User):
            return get_text(self.lang, 'dialogs.private')
        return get_text(self.lang, 'dialogs.chat')

    def _calculate_folder_stats(self, folder_path: Path) -> DownloadStats:
        """Calculate folder statistics"""
        stats = DownloadStats()
        
        if not folder_path.exists():
            return stats
        
        for file_path in folder_path.iterdir():
            if file_path.is_file():
                stats.total_files += 1
                file_size = file_path.stat().st_size
                stats.total_size += file_size
                
                ext = file_path.suffix.lower()
                
                if ext in self.FILE_EXTENSIONS['images']:
                    stats.images = (stats.images[0] + 1, stats.images[1] + file_size)
                elif ext in self.FILE_EXTENSIONS['videos']:
                    stats.videos = (stats.videos[0] + 1, stats.videos[1] + file_size)
                elif ext in self.FILE_EXTENSIONS['audio']:
                    stats.audio = (stats.audio[0] + 1, stats.audio[1] + file_size)
        
        return stats

    def _print_folder_stats(self, folder_name: str, stats: DownloadStats):
        """Print folder statistics"""
        print(get_text(self.lang, 'stats.folder_header', folder_name))
        print(get_text(self.lang, 'stats.total_files', stats.total_files, stats.total_size/(1024*1024)))
        print(get_text(self.lang, 'stats.images', stats.images[0], stats.images[1]/(1024*1024)))
        print(get_text(self.lang, 'stats.videos', stats.videos[0], stats.videos[1]/(1024*1024)))
        print(get_text(self.lang, 'stats.audio', stats.audio[0], stats.audio[1]/(1024*1024)))

    async def _download_media(self, message: Message, folder_path: Path) -> bool:
        """Download media from message"""
        await self._init_async_components()
        
        async with self.semaphore:
            slot = await self.slot_queue.get()
            start_time = time.time()
            
            try:
                media_label, extension = self._get_media_type_and_extension(message.media)
                reset_color = '\033[0m'
                white_color = '\033[38;5;15m'
                slot_color = self.slot_colors.get(slot, white_color)
                slot_info = get_text(self.lang, 'download.slot_info', 
                                   f"{slot_color}{slot}{reset_color}", 
                                   self.concurrency)
                
                file_name = f'{message.id}.{extension}'
                file_path = folder_path / file_name
                
                print(f'{get_text(self.lang, "download.downloading")}{media_label}:{message.id}'.ljust(14) + f'{slot_info}')
                
                for attempt in range(3):
                    try:
                        await self.client.download_media(message.media, file=str(file_path))
                        break
                    except FileReferenceExpiredError:
                        if attempt < 2:
                            print(get_text(self.lang, 'download.file_reference_expired', message.id, attempt+1))
                            await asyncio.sleep(10)
                            message = await self.client.get_messages(message.chat_id, ids=message.id)
                        else:
                            print(get_text(self.lang, 'download.file_reference_failed', message.id))
                            raise RestartChannelProcessing(message.date, f'Error in message {message.id}')
                    except FloodWaitError as e:
                        print(get_text(self.lang, 'download.flood_wait', e.seconds))
                        await asyncio.sleep(e.seconds)
                
                elapsed_time = time.time() - start_time
                print(f'{get_text(self.lang, "download.completed")}{media_label}:{message.id}'.ljust(14) + f'{slot_info}>>{elapsed_time:.2f}s')
                
                return True
                
            except Exception as e:
                print(f'{get_text(self.lang, "download.error")} Error downloading {message.id}: {e}')
                raise
            finally:
                self.slot_queue.put_nowait(slot)

    async def _print_all_dialogs(self) -> List[Dialog]:
        """Print all available dialogs"""
        client = await self._get_client()
        print(get_text(self.lang, 'dialogs.header'))
        dialogs = []
        
        async for dialog in client.iter_dialogs():
            dialog_type = self._get_dialog_type(dialog.entity)
            white_color = '\033[38;5;15m'
            reset_color = '\033[0m'
            print(f'{white_color}{str(dialog.id).ljust(14)}{reset_color} || '
                  f'{dialog_type.ljust(12)} || {dialog.name}')
            dialogs.append(dialog)
        
        return dialogs

    async def _print_all_dialogs_with_cleanup(self) -> List[Dialog]:
        """Print all available dialogs with proper cleanup"""
        try:
            return await self._print_all_dialogs()
        finally:
            if self.client:
                await self.client.disconnect()
                self.client = None

    async def _process_channel(self, channel_key: str, time_range: TimeRange, 
                             print_content: bool = False) -> DownloadStats:
        """Process channel/chat with media downloads"""
        client = await self._get_client()
        await self._init_async_components()
        
        while True:
            start_time = time.time()
            
            try:
                # Try to convert to int if it's a numeric channel ID
                if channel_key.startswith('-') and channel_key[1:].isdigit():
                    entity_id = int(channel_key)
                    entity = await client.get_entity(entity_id)
                else:
                    entity = await client.get_entity(channel_key)
                print(f'\n{get_text(self.lang, "download.processing_channel", entity.title, channel_key, entity.date)}')
                
                folder_name = f'{entity.title}_{entity.id}'
                folder_path = Path(folder_name)
                folder_path.mkdir(exist_ok=True)
                
                download_tasks = []
                
                if time_range.from_id or time_range.to_id:
                    messages_to_process = []
                    async for message in client.iter_messages(entity):
                        if time_range.from_id and message.id < time_range.from_id:
                            continue
                        if time_range.to_id and message.id > time_range.to_id:
                            continue
                        messages_to_process.append(message)
                    
                    messages_to_process.sort(key=lambda m: m.id)
                    
                    for message in messages_to_process:
                        if print_content and message.text:
                            print(f'{message.date} - ID {message.id}: {message.text}')
                        
                        if message.media:
                            task = asyncio.create_task(
                                self._download_media(message, folder_path)
                            )
                            download_tasks.append(task)
                else:
                    async for message in client.iter_messages(
                        entity, 
                        offset_date=time_range.from_date, 
                        reverse=True
                    ):
                        if time_range.to_date and message.date > time_range.to_date:
                            continue
                        
                        if print_content and message.text:
                            print(f'{message.date} - ID {message.id}: {message.text}')
                        
                        if message.media:
                            task = asyncio.create_task(
                                self._download_media(message, folder_path)
                            )
                            download_tasks.append(task)
                
                await asyncio.gather(*download_tasks, return_exceptions=True)
                
                elapsed_time = time.time() - start_time
                print(f'{get_text(self.lang, "download.channel_completed", entity.title, channel_key, elapsed_time)}')
                
                stats = self._calculate_folder_stats(folder_path)
                stats.processing_time = elapsed_time
                self._print_folder_stats(folder_name, stats)
                
                return stats
                
            except RestartChannelProcessing as e:
                new_from = e.error_date.strftime('%Y-%m-%d')
                print(get_text(self.lang, 'download.restarting_channel', new_from, e.error_msg))
                time_range.from_date, _ = self.parse_date_or_id(new_from)

    async def _process_channels_from_config(self, download_config: Dict[str, Any]):
        """Process channels from configuration"""
        await self._print_all_dialogs()
        
        for ch_key, cfg in download_config.items():
            from_date, from_id = self.parse_date_or_id(cfg.get('from', 'OLDEST'))
            to_date, to_id = self.parse_date_or_id(cfg.get('to', 'NOW'), is_end_of_day=True)
            
            time_range = TimeRange(from_date=from_date, to_date=to_date, from_id=from_id, to_id=to_id)
            
            for key, default in [('from', 'OLDEST'), ('to', 'NOW')]:
                if key not in cfg:
                    print(get_text(self.lang, 'warnings.default_param', key, ch_key, default))
            
            print_content = cfg.get('print_content', True)
            
            await self._process_channel(ch_key, time_range, print_content)

    def print_all(self):
        """Print all available dialogs (channels/chats)"""
        return asyncio.run(self._print_all_dialogs_with_cleanup())

    def run_conf(self, config_path: str, channel_key: Optional[str] = None):
        """
        Run downloads according to configuration
        
        Args:
            config_path: Path to configuration file
            channel_key: Optional channel key to process only one channel
        """
        asyncio.run(self._run_async(config_path=config_path, channel_key=channel_key))

    def run(self, channel_key: str, **kwargs):
        """
        Run simple download without config
        
        Args:
            channel_key: Channel key (ID, username or name)
            **kwargs: from_date, to_date parameters
        """
        from_date = kwargs.get('from_date') or kwargs.get('from')
        to_date = kwargs.get('to_date') or kwargs.get('to')
        
        temp_config = {
            'download_this': {
                channel_key: {
                    'from': from_date or 'OLDEST',
                    'to': to_date or 'NOW',
                    'print_content': False
                }
            }
        }
        
        asyncio.run(self._run_async(config_dict=temp_config))

    async def _run_async(self, config_path: Optional[str] = None, config_dict: Optional[Dict[str, Any]] = None, channel_key: Optional[str] = None):
        """Single async implementation for all cases"""
        try:
            if config_path:
                config_file = Path(config_path)
                
                if not config_file.exists():
                    raise TgLoaderError(get_text(self.lang, 'errors.config_not_found', config_path))
                
                try:
                    with config_file.open('r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    raise TgLoaderError(get_text(self.lang, 'errors.config_yaml_error', config_path, e))
                
                if not config:
                    raise TgLoaderError(get_text(self.lang, 'errors.config_empty', config_path))
                
                download_config = config.get('download_this')
                if not download_config:
                    raise TgLoaderError(get_text(self.lang, 'errors.download_this_missing'))
            
            elif config_dict:
                download_config = config_dict.get('download_this')
                if not download_config:
                    raise TgLoaderError(get_text(self.lang, 'errors.download_this_missing'))
            
            else:
                raise TgLoaderError("Either config_path or config_dict must be provided")
            
            if channel_key:
                if channel_key not in download_config:
                    raise TgLoaderError(f'Channel {channel_key} not found in config')
                download_config = {channel_key: download_config[channel_key]}
            
            await self._process_channels_from_config(download_config)
        finally:
            if self.client:
                await self.client.disconnect()
                self.client = None