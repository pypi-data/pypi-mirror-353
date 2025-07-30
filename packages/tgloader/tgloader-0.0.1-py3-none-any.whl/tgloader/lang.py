"""
Localization support for TgLoader
"""

# Localization strings
STRINGS = {
    'en': {
        'dialogs': {
            'header': '📄 ALL CHANNELS/CHATS:',
            'channel': '📢 Channel',
            'group': '👥 Group', 
            'private': '👤 Private chat',
            'chat': '👥 Chat'
        },
        'download': {
            'downloading': '📥',
            'completed': '✅',
            'error': '❌',
            'flood_wait': '⏱️ FloodWait: waiting {} seconds...',
            'file_reference_expired': '⚠️ FileReferenceExpired error for {}. Attempt {}/3. Waiting 10 seconds...',
            'file_reference_failed': '❌ FileReferenceExpired error for {} after 3 attempts.',
            'slot_info': 'SLOT[{}/{}]',
            'processing_channel': 'Processing channel/chat: {} ({}) [Created: {}]',
            'channel_completed': '✅ Channel processing: {} ({}) completed in {:.2f}s',
            'restarting_channel': '⚠️ Restarting channel processing with new from date = {} (error: {})'
        },
        'stats': {
            'folder_header': '===== FOLDER {} =====',
            'total_files': 'Total files: {}, total size: {:.1f} MB',
            'images': 'Images: {} files, size: {:.1f} MB',
            'videos': 'Videos: {} files, size: {:.1f} MB',
            'audio': 'Audio: {} files, size: {:.1f} MB'
        },
        'errors': {
            'config_not_found': 'Configuration file not found: {}',
            'config_yaml_error': 'Error reading YAML file {}: {}',
            'config_empty': 'Configuration file {} is empty',
            'invalid_date': 'Invalid date format: {}. Expected YYYY-MM-DD',
            'api_missing': 'api_id or api_hash not found in environment variables',
            'download_this_missing': 'Missing "download_this" key in configuration file',
            'unsupported_media': 'Unsupported media type'
        },
        'warnings': {
            'default_param': '⚠️ "{}" not specified for {}, using default "{}"'
        }
    },
    'ru': {
        'dialogs': {
            'header': '📄 ВСЕ КАНАЛЫ/ЧАТЫ:',
            'channel': '📢 Канал',
            'group': '👥 Группа',
            'private': '👤 Личный чат', 
            'chat': '👥 Чат'
        },
        'download': {
            'downloading': '📥',
            'completed': '✅',
            'error': '❌',
            'flood_wait': '⏱️ FloodWait: ждем {} секунд...',
            'file_reference_expired': '⚠️ Ошибка FileReferenceExpired для {}. Попытка {}/3. Ждем 10 секунд...',
            'file_reference_failed': '❌ Ошибка FileReferenceExpired для {} после 3 попыток.',
            'slot_info': 'СЛОТ[{}/{}]',
            'processing_channel': 'Обработка канала/чата: {} ({}) [Создан: {}]',
            'channel_completed': '✅ Обработка канала: {} ({}) завершена за {:.2f}s',
            'restarting_channel': '⚠️ Перезапуск обработки канала с новой датой from = {} (ошибка: {})'
        },
        'stats': {
            'folder_header': '===== ПАПКА {} =====',
            'total_files': 'Всего файлов: {}, общий вес: {:.1f} МБ',
            'images': 'Изображения: {} файлов, вес: {:.1f} МБ',
            'videos': 'Видео: {} файлов, вес: {:.1f} МБ',
            'audio': 'Аудио: {} файлов, вес: {:.1f} МБ'
        },
        'errors': {
            'config_not_found': 'Файл конфигурации не найден: {}',
            'config_yaml_error': 'Ошибка при чтении YAML файла {}: {}',
            'config_empty': 'Файл конфигурации {} пуст',
            'invalid_date': 'Неверный формат даты: {}. Ожидается YYYY-MM-DD',
            'api_missing': 'Не найдены api_id или api_hash в переменных окружения',
            'download_this_missing': 'Отсутствует ключ "download_this" в конфигурационном файле',
            'unsupported_media': 'Неподдерживаемый тип медиафайла'
        },
        'warnings': {
            'default_param': '⚠️ Не указан "{}" для {}, взят параметр "{}"'
        }
    }
}


def get_text(lang: str, key_path: str, *args, **kwargs) -> str:
    """
    Get localized string by key path
    
    Args:
        lang: Language code ('en' or 'ru')
        key_path: Dot-separated path to the string (e.g., 'dialogs.header')
        *args: Arguments for string formatting
        **kwargs: Keyword arguments for string formatting
    
    Returns:
        Formatted localized string
    """
    strings = STRINGS.get(lang, STRINGS['en'])
    keys = key_path.split('.')
    value = strings
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            # Fallback to English if key not found
            value = STRINGS['en']
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return f"[MISSING: {key_path}]"
            break
    
    if isinstance(value, str):
        try:
            return value.format(*args, **kwargs)
        except (KeyError, IndexError, ValueError):
            return value
    
    return str(value) 