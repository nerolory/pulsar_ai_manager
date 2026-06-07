# PulsarAI Chat

LLM чат-бот с поддержкой множества провайдеров (VseLLM, OpenRouter, Mock).

## Установка

### Через инсталлер (Windows)

1. Скачайте установочный файл `pulsar-chat-setup.exe` из релизов
2. Запустите установщик и следуйте инструкциям
3. После установки запустите приложение через ярлык на рабочем столе

### Через Docker

```bash
# Клонирование репозитория
git clone <repo-url>
cd llm_chat

# Запуск в режиме разработки
docker-compose --profile dev up -d

# Запуск в режиме продакшн
docker-compose --profile prod up -d
```

### Локальная разработка

**Backend (Python 3.13+):**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

**Frontend (Node.js 18+):**
```bash
cd frontend
npm install
npm run dev
```

## Сборка

### Использование build.ps1

Скрипт `build.ps1` предназначен для удобной сборки проекта:

```powershell
# Полная сборка (backend + frontend)
.\build.ps1

# Только backend
.\build.ps1 -Target backend

# Только frontend
.\build.ps1 -Target frontend

# Сборка Electron приложения
.\build.ps1 -Target electron
```

**Требования:**
- Windows PowerShell 5.1+
- Python 3.13+ (для backend)
- Node.js 18+ (для frontend)

### Ручная сборка

**Backend:**
```bash
cd backend
python -m PyInstaller --onefile --name pulsar_backend run.py
```

**Frontend:**
```bash
cd frontend
npm run build
```

## Настройка

### Настройка провайдера

1. Откройте чат
2. Нажмите кнопку "Настройки" (⚙)
3. Перейдите в раздел "Провайдеры ИИ"
4. Выберите провайдер и введите API ключ:
   - **VseLLM**: введите API ключ VseLLM
   - **OpenRouter**: введите API ключ OpenRouter
   - **Mock**: не требует ключа (для тестирования)

### Настройка параметров чата

В настройках можно изменить:
- Модель чата
- Температура (креативность ответов)
- Максимальное количество токенов
- Системный промпт

### Настройки хранилища

Чаты сохраняются локально в файле `chats.json` в папке приложения.

## Интеграция на сайт

**В разработке**

В будущем будет доступна интеграция через:
- Встраиваемый виджет
- API для встраивания в существующие проекты
- Плагины для популярных CMS

## Разработка

### Структура проекта

```
llm_chat/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── providers/   # Адаптеры LLM провайдеров
│   │   ├── routes/      # API endpoints
│   │   └── storage.py   # Хранилище чатов
│   └── requirements.txt
├── frontend/         # Vue 3 + Vite frontend
│   ├── src/
│   │   ├── components/  # Vue компоненты
│   │   ├── stores/      # Pinia stores
│   │   └── themes/      # Темы оформления
│   └── package.json
└── docker-compose.yml
```

### Запуск тестов

```bash
# Frontend тесты
cd frontend
npm test

# Backend тесты
cd backend
pytest
```

## Перезапуск контейнеров

Для перезапуска всех контейнеров используйте:

```bash
docker-compose restart
```

**Важно:** Не используйте `docker compose --profile dev restart frontend-dev` — она не перезапускает сервер корректно.

## Особенности Windows

Если у вас настроен SOCKS прокси (например, `socks=127.0.0.1:10808`), перед запуском установите:

```powershell
$env:no_proxy="*"
```

## Темы

Приложение поддерживает смену тем оформления. Темы находятся в папке `frontend/src/themes/`.

Доступные темы:
- Dark Space (по умолчанию)
- Neutral Gray
- Light Clean
- Light Warm
- Ocean Dark
- Forest
- Steampunk

### Как добавить свою тему

Для создания новой темы необходимо:

1. **Создать папку темы**

   В папке `frontend/src/themes/` создайте новую папку с названием вашей темы, например `my-theme/`.

2. **Добавить файлы темы**

   В папке темы создайте два файла:
   - `index.scss` — стили темы
   - `index.css` — скомпилированные стили (если используете препроцессор)

3. **Зарегистрировать тему в index.ts**

   Откройте файл `frontend/src/themes/index.ts` и добавьте новую тему в массив `THEMES`:

   ```typescript
   {
     id: 'my-theme',              // Уникальный идентификатор темы
     name: 'My Theme',            // Отображаемое название
     description: 'Описание темы', // Краткое описание
     dark: true,                  // true для тёмной темы, false для светлой
     vars: {
       accent:       '#6366F1',    // Основной акцентный цвет
       accentL:      '#818CF8',   // Светлый акцентный цвет
       accentDim:    'rgba(99,102,241,0.18)', // Затемнённый акцент
       accentBorder: 'rgba(99,102,241,0.45)', // Граница акцента
       bg:           '#0a0a0f',    // Основной фон
       bgS:          'rgba(255,255,255,0.06)', // Фон поверхностей
       bgG:          'rgba(255,255,255,0.08)', // Фон групп
       bgGh:         'rgba(255,255,255,0.13)', // Фон при наведении
       bgPanel:      '#13131f',    // Фон панелей
       brd:          'rgba(255,255,255,0.13)', // Границы
       brdA:         'rgba(99,102,241,0.55)', // Акцентные границы
       t1:           '#F1F1F5',    // Основной текст
       t2:           '#A9A9C0',    // Вторичный текст
       t3:           '#6B6B85',    // Третичный текст
       blur:         'blur(20px)',  // Эффект размытия
       shadowPop:    '0 20px 60px rgba(0,0,0,0.6),0 0 0 1px rgba(255,255,255,0.07)', // Тени
       bodyGradient: 'radial-gradient(...)', // Градиент фона (или 'none')
       codeInlineColor: '#e2b96f', // Цвет инлайн-кода
       hljsStyle:    'github-dark', // Стиль подсветки синтаксиса
     },
   },
   ```

4. **Выбор стиля подсветки синтаксиса**

   Доступные значения для `hljsStyle`:
   - `github-dark` — тёмная тема GitHub
   - `github` — светлая тема GitHub
   - `base16-tomorrow` — тема Base16 Tomorrow
   - `atom-one-light` — тема Atom One Light

5. **Применение темы**

   После добавления темы в `THEMES` массив, она автоматически станет доступной в настройках приложения в выпадающем списке тем.

6. **Тестирование**

   Запустите приложение в режиме разработки:
   ```bash
   cd frontend
   npm run dev
   ```

   Откройте настройки и выберите вашу тему из списка.

### Пример создания темы

Полный пример создания тёмной темы с зелёным акцентом:

```typescript
{
  id: 'green-dark',
  name: 'Green Dark',
  description: 'Тёмная тема с зелёным акцентом',
  dark: true,
  vars: {
    accent:       '#10B981',
    accentL:      '#34D399',
    accentDim:    'rgba(16,185,129,0.15)',
    accentBorder: 'rgba(16,185,129,0.40)',
    bg:           '#0a0f0a',
    bgS:          'rgba(255,255,255,0.05)',
    bgG:          'rgba(255,255,255,0.07)',
    bgGh:         'rgba(255,255,255,0.11)',
    bgPanel:      '#0d1f14',
    brd:          'rgba(255,255,255,0.10)',
    brdA:         'rgba(52,211,153,0.5)',
    t1:           '#ECFDF5',
    t2:           '#6EE7B7',
    t3:           '#2D5A3D',
    blur:         'blur(20px)',
    shadowPop:    '0 20px 60px rgba(0,0,0,0.7),0 0 0 1px rgba(16,185,129,0.10)',
    bodyGradient: 'radial-gradient(ellipse 60% 50% at 15% 20%,rgba(16,185,129,0.10) 0%,transparent 60%)',
    codeInlineColor: '#34D399',
    hljsStyle:    'github-dark',
  },
}
```

## Лицензия

MIT License
