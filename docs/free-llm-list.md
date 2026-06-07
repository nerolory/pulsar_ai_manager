# Список бесплатных LLM для Pulsar AI Manager

Полный список бесплатных языковых моделей с лимитами, доступных для интеграции.

## Российские провайдеры (без VPN)

### GigaChat (Сбер)

**Бесплатный тариф (Freemium):**
- **Лимит:** 1,000,000 токенов бесплатно
- **Период:** Обновляется раз в 12 месяцев
- **Модели:**
  - GigaChat
  - GigaChat-2
  - GigaChat-Pro
  - GigaChat-2-Pro
  - GigaChat-Max
  - GigaChat-2-Max
- **Ограничения:** Генерация в одном потоке
- **API:** https://developers.sber.ru/docs/ru/gigachat/api/overview
- **Документация:** https://developers.sber.ru/docs/ru/gigachat/tariffs/individual-tariffs

### YandexGPT

**Бесплатный тариф для физлиц:**
- **Лимит:** 50,000 токенов на год
- **Модели:**
  - YandexGPT Lite
  - YandexGPT Pro (частично)
- **API:** Через Yandex Cloud
- **Цена после лимита:** ~40 копеек за 1000 токенов (снижена втрое)
- **Документация:** https://cloud.yandex.ru/docs/yandexgpt/

### ProTalk

**Бесплатные модели:**
1. **Microsoft 3.5 Phi mini Free**
   - Базовая модель для простых задач
   - Не требует API ключа
   - Подходит для тестирования

2. **Groq (gemma-7) Free+Fast**
   - Быстрая модель от Groq
   - Не требует оплаты
   - Хорошая производительность

3. **Groq (mixtral-8x7b) Free**
   - Открытая модель Mixtral
   - Бесплатный доступ
   - Широкий спектр возможностей

4. **Groq (llama3-70b) Free**
   - Мощная модель семейства Llama
   - Бесплатное использование
   - Подходит для сложных задач

5. **Groq (llama3-8b) Free**
   - Облегченная версия Llama
   - Не требует оплаты
   - Оптимальна для простых задач

**Бонус:** 500K токенов при регистрации (примерно 1M английских или 500K русских слов)
**Сайт:** https://pro-talk.ru/
**Документация:** https://pro-talk.ru/top-of-llm

---

## Зарубежные провайдеры с ежедневными лимитами

### Groq

**Free Tier:**
- **RPM:** ~30 requests per minute
- **TPM:** ~30,000 tokens per minute (input + output combined)
- **Daily:** ~14,400 requests per day
- **Модели:**
  - Llama 3.1 70B
  - Llama 3.1 8B
  - Mixtral 8x7B
  - Gemma 7B
- **Особенности:** Самая быстрая инференция (LPU silicon)
- **API:** https://console.groq.com/docs
- **Rate Limits:** https://console.groq.com/docs/rate-limits

### Cerebras

**Free Trial:**
- **Лимит:** 1,000,000 токенов в день
- **RPM:** 30 requests per minute
- **Context:** 8K tokens
- **Модели:**
  - Llama 3.1 8B
  - GPT-OSS 120B
  - Zai GLM 4.7
- **Особенности:** Очень высокая скорость (2600 tokens/sec на Llama 4 Scout)
- **API:** https://inference-docs.cerebras.ai/
- **Rate Limits:** https://inference-docs.cerebras.ai/support/rate-limits

### OpenRouter

**Free Models:**
- **Лимит без покупки:** 50 запросов в день
- **Лимит после покупки 10+ credits:** 1000 запросов в день
- **Free Models Router:** `openrouter/free` - автоматический выбор бесплатной модели
- **Модели:**
  - Qwen/Qwen3-235b-a22b:free
  - Множество других free tier моделей
- **API:** https://openrouter.ai/docs
- **Список моделей:** https://openrouter.ai/collections/free-models

### Google Gemini (Gemini API)

**Free Tier:**
- **Лимиты:** Зависят от usage tier (Free, Tier 1, Tier 2, Tier 3)
- **Автоматический апгрейд:** При увеличении использования
- **Примерные лимиты (Free tier):**
  - Gemini 2.5 Flash: 10 RPM, 250K TPM
  - Gemini 2.0 Flash: 15 RPM, 1M TPM
  - Gemini 2.5 Pro: 5 RPM, 50 RPD
- **API:** https://ai.google.dev/gemini-api/docs
- **Rate Limits:** https://ai.google.dev/gemini-api/docs/rate-limits

### Mistral AI

**Free Mode:**
- **Лимиты:** Ограничены, предназначены для оценки и прототипирования
- **RPS:** 1 request per second (глобальный лимит для Free tier)
- **Модели:**
  - Mistral 7B
  - Mixtral 8x7B
  - Mixtral 8x22B
- **API:** https://docs.mistral.ai/
- **Tiers:** https://docs.mistral.ai/admin/user-management-finops/tier

### Hugging Face (Serverless Inference)

**Free Tier:**
- **Лимит:** ~few hundred requests per hour
- **Модели:** Тысячи моделей на платформе
- **Особенности:** Serverless Inference API
- **API:** https://huggingface.co/docs/api-inference
- **Rate Limits:** https://huggingface.co/docs/api-inference/index#rate-limits

### DeepSeek

**Пricing:**
- **Цены:** Очень конкурентные (но не нашел четкого бесплатного tier)
- **Модели:**
  - deepseek-chat
  - deepseek-reasoner
  - deepseek-v4-flash
- **API:** https://api-docs.deepseek.com/
- **Pricing:** https://api-docs.deepseek.com/quick_start/pricing
- **Примечание:** Бесплатный доступ через chat.deepseek.com, но API требует оплаты

### Qwen (Alibaba Cloud)

**Free Tier (Singapore region):**
- **Лимит:** 1,000,000 free tokens per model
- **Период:** 90 дней после активации Model Studio
- **Регион:** Только Singapore deployment (нет free quota для Chinese Mainland или Global)
- **Модели:**
  - Qwen 3 Max
  - Qwen 3.6 Plus
  - QwQ-Plus
  - И другие proprietary Qwen модели
- **Ограничения:**
  - Только real-time inference
  - Исключает batch calls, context caching, fine-tuning, model deployment
  - Free quota pooled across account и всех RAM (sub) users
- **Особенность:** Можно включить "Free quota only" toggle - сервис остановится вместо перехода на pay-as-you-go
- **API:** https://www.alibabacloud.com/help/en/model-studio/model-pricing
- **Документация:** https://inferencehub.org/blog/alibaba-cloud-qwen-api-pricing-2026/

**Qwen через OpenRouter:**
- **Бесплатные модели:**
  - Qwen3.6 Plus Preview (free)
  - Qwen3.5-9B
  - Qwen3.5-35B-A3B
  - Qwen3.5-27B
  - Qwen3.5-122B-A10B
  - Qwen3.5-Flash
- **Лимиты:** Следуют общим лимитам OpenRouter (50-1000 запросов/день)
- **API:** https://openrouter.ai/qwen/

### Together AI

**Free Credits:**
- **Бонус:** $25 free credits для новых пользователей
- **Модели:** 200+ open-source моделей
- **Особенности:** Serverless inference + fine-tuning
- **API:** https://api.together.xyz/
- **Startup Program:** До $50K credits для стартапов

---

## Зарубежные провайдеры с free credits

### Perplexity AI

**Free Tier:**
- **Веб-версия:** Бесплатно
- **API:** Pro пользователи получают $5 API credits
- **Особенности:** Research-oriented модели
- **API:** Требует оплаты после free credits

### Replicate

**Free Access:**
- **Модели:** 50,000+ моделей
- **Особенности:** GPU infrastructure
- **API:** https://replicate.com/
- **Примечание:** Free tier с ограничениями

---

## Сводная таблица

| Провайдер | Регион | Лимит | Период | Модели | API |
|-----------|--------|-------|--------|--------|-----|
| **GigaChat** | РФ | 1M токенов | 12 мес | GigaChat, GigaChat-2, Pro, Max | ✅ |
| **YandexGPT** | РФ | 50K токенов | 1 год | Lite, Pro | ✅ |
| **ProTalk** | РФ | 500K токенов + 5 моделей | Разово | Phi, Groq (gemma, mixtral, llama) | ✅ |
| **Groq** | Global | 14.4K req/день | Ежедневно | Llama 3.1, Mixtral, Gemma | ✅ |
| **Cerebras** | Global | 1M токенов/день | Ежедневно | Llama 3.1, GPT-OSS, GLM | ✅ |
| **OpenRouter** | Global | 50-1000 req/день | Ежедневно | Множество free моделей | ✅ |
| **Gemini** | Global | Зависит от tier | Авто | Gemini 2.0/2.5 Flash/Pro | ✅ |
| **Mistral** | Global | 1 RPS | Постоянно | Mistral 7B, Mixtral | ✅ |
| **HuggingFace** | Global | ~few hundred/hour | Постоянно | Тысячи моделей | ✅ |
| **Together AI** | Global | $25 credits | Разово | 200+ моделей | ✅ |
| **DeepSeek** | Global | Очень дешевый | - | deepseek-chat, reasoner | ✅ |
| **Qwen (Alibaba)** | Global | 1M токенов/модель | 90 дней | Qwen 3 Max, 3.6 Plus, QwQ-Plus | ✅ |
| **Qwen (OpenRouter)** | Global | 50-1000 req/день | Ежедневно | Qwen3.6 Plus, Qwen3.5 series | ✅ |

---

## Рекомендации по интеграции

### Для пользователей в РФ (без VPN)

1. **GigaChat** - лучший выбор для русского языка, 1M токенов на год
2. **YandexGPT** - 50K токенов на год, хорошая альтернатива
3. **ProTalk** - 5 бесплатных моделей + 500K токенов бонус

### Для глобальных пользователей

1. **Groq** - самая быстрая инференция, 14.4K запросов/день
2. **Cerebras** - 1M токенов/день, высокая скорость
3. **OpenRouter** - агрегатор free моделей, 50-1000 запросов/день
4. **Qwen (Alibaba)** - 1M токенов/модель на 90 дней (Singapore region)
5. **Gemini** - автоматические апгрейды tier, хорошие лимиты

### Для прототипирования

1. **Mistral** - Free mode для тестирования
2. **HuggingFace** - тысячи моделей для экспериментов
3. **Together AI** - $25 free credits

---

## Реализация в Pulsar AI Manager

### 1. Добавить провайдеры

```python
# backend/app/providers/gigachat.py
class GigaChatProvider(BaseLLMProvider):
    # Реализация GigaChat API

# backend/app/providers/yandexgpt.py
class YandexGPTProvider(BaseLLMProvider):
    # Реализация YandexGPT API

# backend/app/providers/groq.py
class GroqProvider(BaseLLMProvider):
    # Реализация Groq API
```

### 2. Реестр бесплатных моделей

```python
FREE_MODELS = {
    "gigachat": {
        "provider": "gigachat",
        "is_free": True,
        "limit_tokens": 1000000,
        "limit_period": "12_months",
        "region": "ru",
    },
    "yandexgpt_lite": {
        "provider": "yandexgpt",
        "is_free": True,
        "limit_tokens": 50000,
        "limit_period": "1_year",
        "region": "ru",
    },
    "groq_llama3-70b": {
        "provider": "groq",
        "is_free": True,
        "limit_requests": 14400,
        "limit_period": "1_day",
        "region": "global",
    },
    "qwen_3_max": {
        "provider": "alibaba",
        "is_free": True,
        "limit_tokens": 1000000,
        "limit_period": "90_days",
        "region": "global",
        "region_restriction": "singapore_only",
    },
    "qwen_3_6_plus": {
        "provider": "alibaba",
        "is_free": True,
        "limit_tokens": 1000000,
        "limit_period": "90_days",
        "region": "global",
        "region_restriction": "singapore_only",
    },
    # ... остальные модели
}
```

### 3. Отслеживание лимитов

- Создать таблицу `usage_limits` в БД
- Отслеживать использование по дням/месяцам
- Предупреждать при приближении к лимиту
- Автоматическое переключение на платные версии

### 4. UI индикаторы

- Показывать "Бесплатно" рядом с моделью
- Отображать оставшийся лимит
- Показывать когда лимит исчерпан
- Предлагать переключиться на платную версию

---

## Отслеживание лимитов и метрик

### Провайдеры с API для отслеживания

#### Groq
- **Rate Limit Headers:** Возвращаются в каждом ответе
- **Spend Limits API:** https://console.groq.com/docs/spend-limits
- **Отслеживание:** Near real-time (обновляется каждые 10-15 минут)
- **Headers:**
  - `x-ratelimit-limit-requests`
  - `x-ratelimit-remaining-requests`
  - `x-ratelimit-reset-requests`
- **Spend Limits:** Можно установить monthly budget с alert thresholds (50%, 75%, 90%)
- **Блокировка:** При достижении лимита возвращает 400 с кодом `blocked_api_access`

#### Cerebras
- **Rate Limit Headers:** Подробная информация в каждом ответе
- **Headers:**
  - `x-ratelimit-limit-requests-day` - лимит запросов в день
  - `x-ratelimit-limit-tokens-minute` - лимит токенов в минуту
  - `x-ratelimit-remaining-requests-day` - оставшиеся запросы
  - `x-ratelimit-remaining-tokens-minute` - оставшиеся токены
  - `x-ratelimit-reset-requests-day` - время сброса (секунды)
  - `x-ratelimit-reset-tokens-minute` - время сброса (секунды)
- **Пример:**
  ```
  x-ratelimit-limit-requests-day: 1000000000
  x-ratelimit-remaining-requests-day: 999997455
  x-ratelimit-reset-requests-day: 33011.38
  ```

#### OpenRouter
- **Credits API:** `GET /api/v1/credits`
- **Аутентификация:** Требуется Management API key
- **Ответ:**
  ```json
  {
    "data": {
      "total_credits": 100.5,
      "total_usage": 25.755
    }
  }
  ```
- **Rate Limits:** https://openrouter.ai/docs/api/reference/limits
- **Отслеживание:** Через Activity page в личном кабинете

#### Gemini (Google AI)
- **Rate Limits:** Зависят от usage tier (Free, Tier 1, Tier 2, Tier 3)
- **Отслеживание:** Через Google AI Studio dashboard
- **429 Response:** Включает metadata headers с информацией о превышении
- **Автоматический апгрейд:** При увеличении использования
- **Dashboard:** https://aistudio.google.com/rate-limit

#### Mistral AI
- **Rate Limits:** Возвращают 429 Too Many Requests при превышении
- **Headers:** `Retry-After` (обычно 1 секунда, может быть больше)
- **Free Tier:** Глобальный лимит 1 RPS на API key
- **Отслеживание:** Через Admin›Limits в Mistral Studio
- **Документация:** https://docs.mistral.ai/resources/known-limitations

#### Hugging Face
- **Rate Limits:** Основаны на количестве запросов
- **429 Handling:** SDK автоматически парсит Rate headers и делает retry
- **Inference Endpoints:** Более высокие rate limits для production
- **Документация:** https://huggingface.co/docs/api-inference/en/rate-limits

### Провайдеры без явного API метрик

#### GigaChat
- **Лимит:** 1M токенов на 12 месяцев
- **Отслеживание:** Не найдено явного API для проверки остатка
- **Рекомендация:** Локальное отслеживание использования токенов

#### YandexGPT
- **Лимит:** 50K токенов на год
- **Отслеживание:** Через Yandex Cloud consumption details
- **Billing:** https://yandex.cloud/en/docs/billing/

#### ProTalk
- **Лимит:** 500K токенов бонус + 5 бесплатных моделей
- **Отслеживание:** Не найдено явного API
- **Рекомендация:** Локальное отслеживание

### Стратегия отслеживания для Pulsar AI Manager

#### 1. Локальное отслеживание (для всех провайдеров)
```python
# Таблица в БД
CREATE TABLE usage_tracking (
    id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    date TEXT NOT NULL,  -- YYYY-MM-DD
    tokens_used INTEGER DEFAULT 0,
    requests_count INTEGER DEFAULT 0,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);
```

#### 2. Парсинг response headers (где доступно)
```python
def parse_rate_limit_headers(headers: dict) -> dict:
    return {
        "remaining_requests": headers.get("x-ratelimit-remaining-requests-day"),
        "remaining_tokens": headers.get("x-ratelimit-remaining-tokens-minute"),
        "reset_time": headers.get("x-ratelimit-reset-requests-day"),
    }
```

#### 3. Periodic API checks (где доступно)
```python
# OpenRouter
async def check_openrouter_credits(api_key: str) -> dict:
    response = await httpx.get(
        "https://openrouter.ai/api/v1/credits",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    return response.json()
```

#### 4. Предупреждения в UI
- Показывать оставшийся лимит
- Предупреждать при 80%, 90%, 95% использования
- Блокировать запросы при 100%
- Предлагать переключиться на платную версию

#### 5. Сводная таблица возможностей отслеживания

| Провайдер | Rate Limit Headers | Balance API | Локальное отслеживание | Рекомендация |
|-----------|-------------------|-------------|----------------------|--------------|
| Groq | ✅ | ✅ Spend Limits | ✅ | Комбинировать |
| Cerebras | ✅ Подробные | ❌ | ✅ | Headers + локальное |
| OpenRouter | ❌ | ✅ Credits API | ✅ | API + локальное |
| Gemini | ⚠️ 429 metadata | ❌ | ✅ | Dashboard + локальное |
| Mistral | ⚠️ Retry-After | ❌ | ✅ | Локальное |
| HuggingFace | ⚠️ 429 | ❌ | ✅ | Локальное |
| GigaChat | ❌ | ❌ | ✅ | Только локальное |
| YandexGPT | ❌ | ⚠️ Cloud billing | ✅ | Локальное + Cloud |
| ProTalk | ❌ | ❌ | ✅ | Только локальное |

---

## Источники

- GigaChat: https://developers.sber.ru/docs/ru/gigachat/tariffs/individual-tariffs
- ProTalk: https://pro-talk.ru/top-of-llm
- Groq: https://console.groq.com/docs/rate-limits
- Cerebras: https://inference-docs.cerebras.ai/support/rate-limits
- OpenRouter: https://openrouter.ai/docs/faq
- Gemini: https://ai.google.dev/gemini-api/docs/rate-limits
- Mistral: https://docs.mistral.ai/admin/user-management-finops/tier
- HuggingFace: https://huggingface.co/docs/api-inference
- DeepSeek: https://api-docs.deepseek.com/quick_start/pricing
- Qwen (Alibaba): https://www.alibabacloud.com/help/en/model-studio/model-pricing
- Qwen (OpenRouter): https://openrouter.ai/qwen/
- Together AI: https://api.together.xyz/
