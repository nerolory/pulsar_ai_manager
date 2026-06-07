# Known Issues

This document lists known issues and limitations in the current version of PulsarAI Chat.

---

## Multi-language Support (i18n)

**Status:** Pending
**Priority:** Medium

**Issue:**
The application currently only supports Russian language. All UI text is hardcoded in Russian.

**Solution:**
1. Install vue-i18n library
2. Create translation files for supported languages
3. Extract all text strings from components to translation files
4. Add language switcher to settings
5. Save selected language in localStorage

**Supported Languages:**
- Russian (default)
- English

**Translation Files:**
- `frontend/src/locales/ru.json` - Russian
- `frontend/src/locales/en.json` - English

**Example Translation Structure:**
```json
{
  "settings": {
    "provider": "Провайдер",
    "model": "Модель",
    "apiKey": "API-ключ"
  }
}
```

**Action Plan:**
1. Install vue-i18n
2. Create locale structure
3. Replace hardcoded strings with $t()
4. Add language switcher to settings
5. Testing

---

## VseLLM Billing

**Status:** Pending
**Priority:** Low

**Issue:**
VseLLM does not provide a public API endpoint for checking balance. Balance can only be tracked through the personal cabinet.

**Possible Solutions:**
1. Contact VseLLM support to get API endpoint
2. Use web scraping of personal cabinet (not recommended)
3. Leave as is - user checks balance in personal cabinet

**Current State:**
- `has_balance_api: False` in `VseLLMProvider`
- Displays "не отслеживается" in UI
