<template>
  <div class="local-models">
    <h2>Локальные модели</h2>
    
    <!-- System Requirements -->
    <div class="system-check" v-if="systemCheck">
      <h3>Системные требования</h3>
      <div class="specs">
        <div class="spec-item">
          <span class="label">RAM:</span>
          <span class="value">{{ systemCheck.specs.total_ram_gb.toFixed(1) }} GB</span>
        </div>
        <div class="spec-item">
          <span class="label">CPU:</span>
          <span class="value">{{ systemCheck.specs.cpu_cores }} ядер</span>
        </div>
        <div class="spec-item">
          <span class="label">GPU:</span>
          <span class="value">{{ systemCheck.specs.gpu_available ? systemCheck.specs.gpu_name : 'Нет' }}</span>
        </div>
        <div class="spec-item">
          <span class="label">Диск:</span>
          <span class="value">{{ systemCheck.specs.disk_free_gb.toFixed(1) }} GB свободно</span>
        </div>
      </div>
      <div class="tier-info" :class="systemCheck.tier.tier">
        <span class="tier-label">Tier:</span>
        <span class="tier-value">{{ systemCheck.tier.tier }}</span>
        <span class="tier-message">{{ systemCheck.tier.message }}</span>
      </div>
    </div>

    <!-- Storage Info -->
    <div class="storage-info" v-if="localModels">
      <h3>Хранилище</h3>
      <div class="storage-stats">
        <div class="stat-item">
          <span class="label">Моделей:</span>
          <span class="value">{{ localModels.storage_info.model_count }}</span>
        </div>
        <div class="stat-item">
          <span class="label">Размер:</span>
          <span class="value">{{ localModels.storage_info.total_size_gb.toFixed(2) }} GB</span>
        </div>
      </div>
    </div>

    <!-- Models List -->
    <div class="models-list" v-if="localModels">
      <h3>Доступные модели</h3>
      <div class="model-card" v-for="(model, modelId) in localModels.models" :key="modelId" :class="{ 'downloaded': model.downloaded, 'cannot-run': !canRunModel(model) }">
        <div class="model-header">
          <h4>{{ model.name }}</h4>
          <span class="badge" :class="model.tier">{{ model.tier }}</span>
          <span class="badge downloaded" v-if="model.downloaded">Скачана</span>
        </div>
        
        <div class="model-info">
          <div class="info-item">
            <span class="label">Параметры:</span>
            <span class="value">{{ model.params }}</span>
          </div>
          <div class="info-item">
            <span class="label">Контекст:</span>
            <span class="value">{{ model.context_length }} токенов</span>
          </div>
          <div class="info-item">
            <span class="label">Квантование:</span>
            <span class="value">{{ model.quantization }}</span>
          </div>
        </div>

        <div class="model-requirements">
          <h5>Требования:</h5>
          <div class="req-item">
            <span class="label">RAM:</span>
            <span class="value">{{ model.requirements.ram_gb }} GB</span>
          </div>
          <div class="req-item">
            <span class="label">CPU:</span>
            <span class="value">{{ model.requirements.cpu_cores }} ядер</span>
          </div>
          <div class="req-item" v-if="model.requirements.gpu_vram_gb">
            <span class="label">VRAM:</span>
            <span class="value">{{ model.requirements.gpu_vram_gb }} GB</span>
          </div>
          <div class="req-item">
            <span class="label">Диск:</span>
            <span class="value">{{ model.requirements.disk_gb }} GB</span>
          </div>
        </div>

        <div class="model-actions">
          <button 
            v-if="!model.downloaded" 
            @click="downloadModel(modelId)"
            :disabled="!canRunModel(model) || downloading"
            class="btn btn-primary"
          >
            {{ downloading ? 'Скачивание...' : 'Скачать' }}
          </button>
          <button 
            v-if="model.downloaded" 
            @click="deleteModel(modelId)"
            class="btn btn-danger"
          >
            Удалить
          </button>
          <span v-if="!canRunModel(model)" class="error-message">
            Система не соответствует требованиям
          </span>
        </div>
      </div>
    </div>

    <div v-else class="loading">
      Загрузка...
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getSystemCheck, getLocalModels, downloadLocalModel, deleteLocalModel } from '@/api/settings'

const systemCheck = ref<any>(null)
const localModels = ref<any>(null)
const downloading = ref(false)

const canRunModel = (model: any) => {
  if (!systemCheck.value) return false
  const specs = systemCheck.value.specs
  const req = model.requirements
  
  if (specs.total_ram_gb < req.ram_gb) return false
  if (specs.cpu_cores < req.cpu_cores) return false
  if (req.gpu_vram_gb && (!specs.gpu_available || (specs.gpu_vram_gb || 0) < req.gpu_vram_gb)) return false
  
  return true
}

const loadSystemCheck = async () => {
  try {
    systemCheck.value = await getSystemCheck()
  } catch (error) {
    console.error('Failed to load system check:', error)
  }
}

const loadLocalModels = async () => {
  try {
    localModels.value = await getLocalModels()
  } catch (error) {
    console.error('Failed to load local models:', error)
  }
}

const downloadModel = async (modelId: string) => {
  downloading.value = true
  try {
    const result = await downloadLocalModel(modelId)
    if (result.success) {
      await loadLocalModels()
    } else {
      alert(result.message)
    }
  } catch (error) {
    console.error('Failed to download model:', error)
    alert('Ошибка при скачивании модели')
  } finally {
    downloading.value = false
  }
}

const deleteModel = async (modelId: string) => {
  if (!confirm('Удалить модель?')) return
  
  try {
    const result = await deleteLocalModel(modelId)
    if (result.success) {
      await loadLocalModels()
    } else {
      alert(result.message)
    }
  } catch (error) {
    console.error('Failed to delete model:', error)
    alert('Ошибка при удалении модели')
  }
}

onMounted(() => {
  loadSystemCheck()
  loadLocalModels()
})
</script>

<style scoped>
.local-models {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h2 {
  margin-bottom: 20px;
}

h3 {
  margin: 20px 0 10px 0;
  font-size: 1.2rem;
}

h4 {
  margin: 0 0 10px 0;
  font-size: 1.1rem;
}

h5 {
  margin: 10px 0 5px 0;
  font-size: 0.9rem;
  color: #666;
}

.system-check,
.storage-info {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.specs,
.storage-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.spec-item,
.stat-item,
.info-item,
.req-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
}

.label {
  font-weight: 500;
  color: #666;
}

.value {
  font-weight: 600;
}

.tier-info {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
  background: #e3f2fd;
}

.tier-info.very_light {
  background: #fff3e0;
}

.tier-info.light {
  background: #e8f5e9;
}

.tier-info.medium {
  background: #e3f2fd;
}

.tier-info.unsupported {
  background: #ffebee;
}

.tier-label {
  font-weight: 600;
  margin-right: 10px;
}

.tier-value {
  font-weight: 600;
  margin-right: 10px;
}

.tier-message {
  color: #666;
}

.models-list {
  display: grid;
  gap: 20px;
}

.model-card {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  transition: box-shadow 0.2s;
}

.model-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.model-card.downloaded {
  border-color: #4caf50;
  background: #f9fff9;
}

.model-card.cannot-run {
  opacity: 0.6;
}

.model-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.very_light {
  background: #fff3e0;
  color: #e65100;
}

.badge.light {
  background: #e8f5e9;
  color: #2e7d32;
}

.badge.medium {
  background: #e3f2fd;
  color: #1565c0;
}

.badge.downloaded {
  background: #4caf50;
  color: white;
}

.model-info,
.model-requirements {
  margin-bottom: 15px;
}

.model-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1976d2;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-danger:hover {
  background: #d32f2f;
}

.error-message {
  color: #f44336;
  font-size: 0.9rem;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}
</style>
