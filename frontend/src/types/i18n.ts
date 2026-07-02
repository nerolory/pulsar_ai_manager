export interface LocaleData {
  name: string
  settings?: {
    title?: string
    subtitle?: string
    sections?: {
      providers?: string
      local?: string
      chat?: string
      appearance?: string
      privacy?: string
    }
    provider?: {
      title?: string
      description?: string
      not_configured?: string
      configure?: string
      change?: string
      label?: string
      model_label?: string
      balance?: string
      not_tracked?: string
      capabilities?: string
      caching?: string
      images?: string
      pdf?: string
      free_tier?: string
      context?: string
      tokens?: string
      pricing?: string
      per_token?: string
      per_request?: string
    }
    chat?: {
      title?: string
      creativity?: string
      creativity_hint?: string
      max_length?: string
      max_length_hint?: string
    }
    appearance?: {
      title?: string
      description?: string
    }
    language?: {
      title?: string
    }
    modal?: {
      title?: string
      simple_mode?: string
      manual_mode?: string
      provider_label?: string
      select_provider?: string
      model_label?: string
      default_model?: string
      api_key_label?: string
      base_url_label?: string
      cancel?: string
      save?: string
      connecting?: string
      refresh_models?: string
      source?: string
      cached?: string
      api?: string
    }
    local_llm?: {
      checking?: string
      no_models?: string
      install_model?: string
    }
  }
  chat?: {
    input_placeholder?: string
    send?: string
    stop?: string
    new_chat?: string
    delete_chat?: string
    remember_history?: string
    system_prompt_hint?: string
  }
  sidebar?: {
    settings?: string
  }
  message?: {
    read_aloud?: string
    stop_reading?: string
  }
  input?: {
    voice_input?: string
    recording?: string
    processing?: string
    attach_image?: string
    fine_tune?: string
    hint?: string
  }
  [key: string]: any
}
