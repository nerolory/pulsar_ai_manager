# Current Memories Export

## Memory: plan-location
**ID:** 8ed3ae09-7444-4879-98a7-8d5713a7857a  
**Title:** Location of Pulsar AI Manager development plan  
**Content:** Current development plan is located at C:\Users\nerolory\.windsurf\plans\pulsar-ai-manager-refactor-a398a7.md. This file contains the step-by-step plan for Pulsar AI Manager refactoring with 8 stages.  
**Tags:** plan, refactor, windsurf  
**CorpusNames:** nerolory/pulsar_ai_manager

---

## Memory: versioning
**ID:** 37d4eea8-a796-4308-818c-ab4e198a0458  
**Title:** Версионирование Pulsar AI Manager  
**Content:** Версионирование Pulsar AI Manager: текущая версия v1.1.2. Формат тегов: vX.Y.Z (семантическое версионирование).  
**Tags:** versioning, release  
**CorpusNames:** nerolory/pulsar_ai_manager

---

## Memory: git-workflow
**ID:** 514667f1-35a2-4c9b-bc96-a13ff6f6f569  
**Title:** Правило работы с Pulsar AI Manager проектом  
**Content:** Правило работы с Pulsar AI Manager проектом: после завершения каждого этапа рефакторинга делать git commit и создавать git tag. Коммит только после подтверждения "всё ок" от пользователя. Формат тега: vX.Y.Z (например, v0.0.1, v0.0.2 и т.д.). Между релизами меняется патч-версия. Каждый коммит = версия приложения. После завершения всех этапов: релиз (git tag release-vX.Y.Z).  
**Tags:** git, workflow, pulsar_ai_manager, release  
**CorpusNames:** nerolory/pulsar_ai_manager

---

## Memory: git-workflow-simple
**ID:** 5dd0e510-60b0-40b7-bdd3-d43c07f0092a  
**Title:** Правило работы с Pulsar AI Manager проектом  
**Content:** Правило работы с Pulsar AI Manager проектом: после завершения каждого этапа рефакторинга делать git commit и создавать git tag. Коммит только после подтверждения "всё ок" от пользователя. Формат тега: vX.Y.Z (например, v0.0.1, v0.0.2 и т.д.). Между релизами меняется патч-версия.  
**Tags:** git, workflow, pulsar_ai_manager  
**CorpusNames:** nerolory/pulsar_ai_manager

---

## Memory: ux-model-switching
**ID:** d58a4ff2-1cf2-4012-8c8f-a68bf3e2b956  
**Title:** UX требование для Pulsar AI Manager  
**Content:** UX требование для Pulsar AI Manager: при исчерпании баланса платной модели показывать сообщение в чате с предложением переключиться на free версию той же модели (если есть). Блок должен содержать переключатель и ссылку на настройки для пополнения баланса. Модели группируются по model_group_id для связывания free/paid версий.  
**Tags:** ux, model_switching, free_paid, pulsar_ai_manager  
**CorpusNames:** nerolory/pulsar_ai_manager

---

## Memory: micro-llm-requirements
**ID:** df718470-6d03-473d-ba82-b5655fef3b8f  
**Title:** Требование для микро-LLM в Pulsar AI Manager  
**Content:** Требование для микро-LLM в Pulsar AI Manager: опциональная функция, требует проверки системных требований перед включением. Проверка: RAM (минимум 8GB), VRAM (если GPU), CPU (ядра, AVX/AVX2), дисковое пространство. Если железо не тянет - микро-LLM не включается, используется только облачные LLM.  
**Tags:** micro_llm, hardware_check, pulsar_ai_manager  
**CorpusNames:** nerolory/pulsar_ai_manager

---

## Memory: curl-powershell-issue
**ID:** d19c11a2-01fa-49ed-81fd-71f9aeccab7f  
**Title:** curl в PowerShell не работает  
**Content:** curl в PowerShell не работает для тестирования API endpoints. Использовать другие методы (Python httpx, Invoke-RestMethod с правильными параметрами, или браузер).  
**Tags:** development, debugging, api  
**CorpusNames:** nerolory/pulsar_ai_manager

---
