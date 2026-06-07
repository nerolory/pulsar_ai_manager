# Этап 0: Исследования API провайдеров

Результаты исследования возможностей API провайдеров LLM для Pulsar AI Manager.

## VseLLM API (api.vsellm.ru)

### Базовая информация
- **Base URL:** `https://api.vsellm.ru/v1`
- **Совместимость:** OpenAI-совместимый API
- **Документация:** https://vsellm.ru/docs

### Список моделей
- **Endpoint:** Стандартный OpenAI `/v1/models`
- **Доступность:** Полный список моделей в каталоге на сайте vsellm.ru
- **Формат ответа:** Стандартный OpenAI формат с полями:
  - `id` - идентификатор модели
  - `context_length` - контекстное окно
  - `pricing` - цены за токены
  - `architecture` - архитектура модели

### Баланс и лимиты
- **API баланса:** Не найден в документации
- **Отслеживание использования:** Через `cached_tokens` в ответе
- **Лимиты:** Не документированы явно

### Кеширование (Prompt Caching)
- **Поддержка:** ✅ Да, через механизм `cached_tokens`
- **Тип:** Кеширование на стороне провайдера (не Anthropic prompt caching)
- **Как работает:** 
  - Повторяющийся контекст (system prompt, история) кешируется провайдером
  - Отражается в поле `cached_tokens` в `ResponseUsage`
  - Пример: `cached_tokens=256` из 259 input tokens
- **Sticky credential:** 
  - Привязка к провайдеру через `previous_response_id`
  - Гарантирует обработку диалога одним экземпляром модели
  - Параметр `store=True` для хранения истории

### Изображения (Vision)
- **Поддержка:** ✅ Да
- **Методы:**
  1. **Responses API (`/v1/responses`)** - универсальный способ
     - `input_image` для изображений (base64)
     - `input_file` для PDF (base64)
     - Работает с GPT-5.4, Gemini-2.5-pro, Claude-4.5
  2. **Chat Completions (`/v1/chat/completions`)** - стандартный OpenAI
     - `image_url` с PNG/JPEG
     - PDF через `image_url` с MIME `application/pdf` (только Gemini)
- **Форматы:** PNG, JPEG, PDF (ограниченно)

### Системные промты
- **Поддержка:** ✅ Да (стандартный OpenAI формат)
- **Реализация:** Через поле `messages` с role="system"

### Файлы
- **Поддержка:** ✅ PDF через Responses API
- **Ограничения:** Claude не поддерживает PDF через chat/completions

---

## OpenRouter API

### Базовая информация
- **Base URL:** `https://openrouter.ai/api/v1`
- **Документация:** https://openrouter.ai/docs
- **Совместимость:** OpenAI-совместимый

### Список моделей
- **Endpoint:** `GET /api/v1/models`
- **Аутентификация:** `Authorization: Bearer <token>`
- **Формат ответа:**
  ```json
  {
    "data": [
      {
        "id": "openai/gpt-4",
        "name": "GPT-4",
        "context_length": 8192,
        "pricing": {
          "prompt": "0.00003",
          "completion": "0.00006"
        },
        "architecture": {
          "input_modalities": ["text"],
          "output_modalities": ["text"],
          "modality": "text->text"
        },
        "supported_parameters": ["temperature", "top_p", "max_tokens"]
      }
    ]
  }
  ```

### Баланс и лимиты
- **API баланса:** `GET /api/v1/credits` (credits api)
- **Отслеживание:** Страница Activity в личном кабинете
- **Лимиты бесплатных моделей:**
  - Без покупки: 50 запросов/день
  - После покупки 10+ credits: 1000 запросов/день
- **Free Models Router:** `openrouter/free` - автоматический выбор бесплатной модели

### Кеширование (Prompt Caching)
- **Поддержка:** ❌ Не найдено в документации
- **Примечание:** Зависит от конкретного провайдера модели

### Изображения (Vision)
- **Поддержка:** ✅ Да (зависит от модели)
- **Фильтрация:** Free Models Router автоматически фильтрует модели с поддержкой vision

### Системные промты
- **Поддержка:** ✅ Да (стандартный OpenAI формат)

### Бесплатные модели
- **Коллекция:** https://openrouter.ai/collections/free-models
- **Router:** `openrouter/free` - случайный выбор из бесплатных
- **Ограничения:** Низкие rate limits, не для production

---

## Anthropic API

### Базовая информация
- **Base URL:** `https://api.anthropic.com`
- **Документация:** https://docs.anthropic.com
- **SDK:** Нативный Python SDK `anthropic`

### Список моделей
- **Endpoint:** `GET /v1/models` (нужно уточнить через документацию)
- **Модели:** Claude Opus 4.8, Sonnet 4.5, Haiku и др.

### Баланс и лимиты
- **Usage API:** `GET /v1/organizations/usage_report/messages`
- **Параметры:**
  - `starting_at` - начало периода
  - `ending_at` - конец периода
  - `bucket_width` - гранулярность (1d, 1h и т.д.)
- **Аутентификация:** `x-api-key: $ANTHROPIC_ADMIN_KEY`
- **Заголовки:** `anthropic-version: 2023-06-01`
- **Cost API:** Доступен для отслеживания расходов

### Кеширование (Prompt Caching)
- **Поддержка:** ✅ Да (нативный prompt caching)
- **Документация:** https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- **Типы:**
  - **Automatic caching:** `cache_control: {"type": "ephemeral"}` на верхнем уровне
  - **Explicit cache breakpoints:** На отдельных блоках контента
- **TTL:**
  - По умолчанию: 5 минут
  - Опционально: 1 час (`"ttl": "1h"`)
- **Цены:**
  - Cache write (5 min): 1.25x base input price
  - Cache write (1 hour): 2x base input price
  - Cache read: 0.1x base input price
- **Поддерживаемые модели:** Все активные Claude модели

### Изображения (Vision)
- **Поддержка:** ✅ Да (Claude 3.5 Sonnet, Opus и др.)
- **Форматы:** Изображения через нативный API

### Системные промты
- **Поддержка:** ✅ Да
- **Реализация:** Отдельное поле `system` в запросе

---

## OpenAI API

### Базовая информация
- **Base URL:** `https://api.openai.com/v1`
- **Документация:** https://platform.openai.com/docs
- **Совместимость:** Стандарт OpenAI

### Список моделей
- **Endpoint:** `GET /v1/models`
- **Формат:** Стандартный OpenAI формат
- **Примечание:** Доступ ограничен (403 при попытке чтения документации)

### Баланс и лимиты
- **Usage API:** `GET /v1/usage`
- **Billing endpoints:**
  - `GET /v1/dashboard/billing/subscription` - план и цикл
  - `GET /v1/dashboard/billing/credit_grants` - кредиты
- **Отслеживание:** Usage Dashboard в личном кабинете

### Кеширование (Prompt Caching)
- **Поддержка:** ❌ Не найдено в документации
- **Примечание:** OpenAI не имеет нативного prompt caching

### Изображения (Vision)
- **Поддержка:** ✅ Да (GPT-4o, GPT-4.1)
- **Форматы:** Стандартный OpenAI vision API

### Системные промты
- **Поддержка:** ✅ Да (стандартный формат)

---

## Сравнительная таблица

| Фича | VseLLM | OpenRouter | Anthropic | OpenAI |
|------|--------|------------|-----------|--------|
| **Список моделей** | ✅ /v1/models | ✅ /api/v1/models | ✅ /v1/models | ✅ /v1/models |
| **API баланса** | ❌ Не найден | ✅ /api/v1/credits | ✅ Usage API | ✅ /v1/usage |
| **Prompt caching** | ✅ cached_tokens | ❌ Зависит от модели | ✅ Нативный | ❌ Нет |
| **Изображения** | ✅ Responses API | ✅ Зависит от модели | ✅ Да | ✅ Да |
| **PDF файлы** | ✅ Responses API | ❌ Нет данных | ❌ Нет данных | ❌ Нет |
| **Системные промты** | ✅ Да | ✅ Да | ✅ Да | ✅ Да |
| **Бесплатные модели** | ❌ Нет данных | ✅ openrouter/free | ❌ Нет | ❌ Нет |
| **Sticky credential** | ✅ previous_response_id | ❌ Нет | ❌ Нет | ❌ Нет |

---

## Рекомендации по реализации

### 1. ProviderCapabilities
```python
class ProviderCapabilities(BaseModel):
    supports_caching: bool  # prompt caching
    supports_images: bool
    supports_pdf: bool
    supports_system_prompt: bool
    supports_files: List[str]  # ["pdf", "txt", ...]
    max_context_tokens: int
    streaming: bool
    pricing_model: str  # "per_token", "per_request"
    has_balance_api: bool
    has_models_list: bool
    free_tier_available: bool
```

### 2. List Models
- **VseLLM:** Использовать `/v1/models`
- **OpenRouter:** Использовать `/api/v1/models`
- **Anthropic:** Использовать `/v1/models` (нужно уточнить)
- **OpenAI:** Использовать `/v1/models`

### 3. Balance API
- **VseLLM:** Не доступен - использовать отслеживание через usage
- **OpenRouter:** `/api/v1/credits`
- **Anthropic:** `/v1/organizations/usage_report/messages`
- **OpenAI:** `/v1/dashboard/billing/credit_grants`

### 4. Prompt Caching
- **VseLLM:** Использовать `cached_tokens` для отслеживания, не требует специальной настройки
- **Anthropic:** Реализовать через нативный API с `cache_control`
- **OpenRouter/OpenAI:** Не поддерживается нативно

### 5. Бесплатные модели
- **OpenRouter:** Использовать `openrouter/free` router
- **Другие:** Нужно добавить вручную в реестр моделей

---

## Следующие шаги

1. Создать `ProviderCapabilities` схему
2. Реализовать `list_models()` для каждого провайдера
3. Реализовать `get_balance()` для провайдеров с API
4. Создать реестр моделей с metadata
5. Добавить поддержку prompt caching для Anthropic
