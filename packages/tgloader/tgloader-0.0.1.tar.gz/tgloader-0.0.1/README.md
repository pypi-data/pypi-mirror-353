# TgLoader

Python library for downloading media from Telegram channels and chats.

## Installation

```bash
pip install tgloader
```

## Setup

1. Go to [my.telegram.org](https://my.telegram.org) → API Development Tools → Create application
2. Create `.env` file:

```env
api_id=12345678
api_hash=your_api_hash_here
```

**First Run:** You'll need to authorize via phone number/code when you run it first time.  
**Files:** Downloaded media saved to current directory in folders like `Name_ID/`  
**Formats:** Supports photos (jpg), videos (mp4), audio (mp3)

## Usage

```python
from tgloader import TgLoader

# Create instance
loader = TgLoader()

# Show all available channels/chats
loader.print_all()

# Download by ID or @username
loader.run("-1001234567890")  # by ID
loader.run("@username")       # by username

# Download with date range
loader.run("-1001234567890", from_date="2025-01-01", to_date="NOW")

# Using config file
loader.run_conf("config.yaml")
```

## Date/ID Format

**Dates:**
- `"OLDEST"` - from the beginning
- `"NOW"` - current moment  
- `"2025-01-01"` - specific date
- `"NOW-3D"` - 3 days ago
- `"NOW-12H"` - 12 hours ago
- `"NOW-30m"` - 30 minutes ago

**Message IDs:**
- `"12345"` - specific message ID
- `"100"` to `"200"` - ID range

Examples:
```python
# Last week
loader.run("@name", from_date="NOW-7D", to_date="NOW")

# Specific month
loader.run("@name", from_date="2024-01-01", to_date="2025-01-31")

# Last 24 hours
loader.run("@name", from_date="NOW-1D", to_date="NOW")

# Message ID range
loader.run("@name", from_date="1000", to_date="2000")

# From specific message to now
loader.run("@name", from_date="12345", to_date="NOW")
```

## Config File (`config.yaml`)

```yaml
download_this:
  -1001234567890:
    from: "2025-01-01"
    to: "NOW"
    print_content: true
  
  "@username":
    from: "OLDEST"
    to: "NOW"
```

---

# TgLoader

Python библиотека для скачивания медиа из Telegram каналов и чатов.

## Установка

```bash
pip install tgloader
```

## Настройка

1. Зайдите на [my.telegram.org](https://my.telegram.org) → API Development Tools → Создать приложение
2. Создайте файл `.env`:

```env
api_id=12345678
api_hash=ваш_api_hash_здесь
```

**Первый запуск:** Потребуется авторизация через номер телефона/код при первом запуске.  
**Файлы:** Скачанные медиа сохраняются в текущую директорию в папки вида `Имя_ID/`  
**Форматы:** Поддерживает фото (jpg), видео (mp4), аудио (mp3)

## Использование

```python
from tgloader import TgLoader

# Создать экземпляр
loader = TgLoader(lang='ru')

# Показать все доступные каналы/чаты
loader.print_all()

# Скачать по ID или @имени
loader.run("-1001234567890")  # по ID
loader.run("@имя")           # по имени

# Скачать с диапазоном дат
loader.run("-1001234567890", from_date="2025-01-01", to_date="NOW")

# Использовать конфиг файл
loader.run_conf("config.yaml")
```

## Формат дат/ID

**Даты:**
- `"OLDEST"` - с самого начала
- `"NOW"` - текущий момент
- `"2025-01-01"` - конкретная дата
- `"NOW-3D"` - 3 дня назад
- `"NOW-12H"` - 12 часов назад
- `"NOW-30m"` - 30 минут назад

**ID сообщений:**
- `"12345"` - конкретный ID сообщения
- `"100"` до `"200"` - диапазон ID

Примеры:
```python
# Последняя неделя
loader.run("@имя", from_date="NOW-7D", to_date="NOW")

# Конкретный месяц
loader.run("@имя", from_date="2025-01-01", to_date="2025-01-31")

# Последние 24 часа
loader.run("@имя", from_date="NOW-1D", to_date="NOW")

# Диапазон ID сообщений
loader.run("@имя", from_date="1000", to_date="2000")

# От конкретного сообщения до сейчас
loader.run("@имя", from_date="12345", to_date="NOW")
```

## Конфиг файл (`config.yaml`)

```yaml
download_this:
  -1001234567890:
    from: "2025-01-01"
    to: "NOW"
    print_content: true
  
  "@имя":
    from: "OLDEST"
    to: "NOW"
``` 