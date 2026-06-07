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

---

## OpenRouter Automatic Safety Model Routing

**Status:** Pending
**Priority:** High

**Issue:**
OpenRouter automatically routes requests through NVIDIA Nemotron Content Safety model, which returns service messages like "User Safety: safe" instead of the actual LLM response. This behavior cannot be disabled through API parameters.

**Root Cause:**
OpenRouter has built-in content moderation that intercepts requests and routes them through safety models before reaching the target model. The safety model response is returned as part of the stream.

**Investigation Results:**
- Safety model: `nvidia/nemotron-3.5-content-safety-20260604:free`
- Response comes as normal stream chunks with `model` field set to safety model name
- No API parameter found to disable this behavior (checked `provider.ignore`, `provider.allowFallbacks`, etc.)
- Documentation does not mention how to opt out of automatic safety routing

**Possible Solutions:**
1. **Contact OpenRouter Support** - Request API parameter or account setting to disable automatic safety model routing
2. **Check Account Settings** - Verify if there's a privacy/security setting in OpenRouter account to disable this
3. **Use Direct Provider APIs** - Bypass OpenRouter and use provider APIs directly (OpenAI, Anthropic, etc.)
4. **Client-side Filtering** - Filter chunks from safety models by checking `model` field (not recommended as it's a workaround)

**Current State:**
- Issue documented, awaiting user decision on approach
- No code changes made yet
