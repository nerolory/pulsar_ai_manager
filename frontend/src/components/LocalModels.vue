<template>
  <div class="local-models">
    <h2>{{ t('local_models.title') }}</h2>

    <div class="system-check" v-if="systemCheck">
      <h3>{{ t('local_models.system_requirements') }}</h3>
      <div class="specs">
        <div class="spec-item">
          <span class="label">RAM:</span>
          <span class="value">{{ systemCheck.specs.total_ram_gb.toFixed(1) }} GB</span>
        </div>
        <div class="spec-item">
          <span class="label">CPU:</span>
          <span class="value">{{ t('common.cores', { count: systemCheck.specs.cpu_cores }) }}</span>
        </div>
        <div class="spec-item">
          <span class="label">GPU:</span>
          <span class="value">{{ systemCheck.specs.gpu_available ? systemCheck.specs.gpu_name : t('common.no') }}</span>
        </div>
        <div class="spec-item">
          <span class="label">{{ t('local_models.disk') }}</span>
          <span class="value">{{ t('common.disk_free', { size: systemCheck.specs.disk_free_gb.toFixed(1) }) }}</span>
        </div>
      </div>
      <div class="tier-info" :class="systemCheck.tier.tier">
        <span class="tier-label">{{ t('local_models.tier') }}</span>
        <span class="tier-value">{{ systemCheck.tier.tier }}</span>
        <span class="tier-message">{{ tierMessage }}</span>
      </div>
    </div>

    <div class="storage-info" v-if="localModels">
      <h3>{{ t('local_models.storage') }}</h3>
      <div class="storage-stats">
        <div class="stat-item">
          <span class="label">{{ t('local_models.models_count') }}</span>
          <span class="value">{{ localModels.storage_info.model_count }}</span>
        </div>
        <div class="stat-item">
          <span class="label">{{ t('local_models.size') }}</span>
          <span class="value">{{ localModels.storage_info.total_size_gb.toFixed(2) }} GB</span>
        </div>
      </div>
    </div>

    <div class="models-list" v-if="localModels">
      <h3>{{ t('local_models.available_models') }}</h3>
      <div
        class="model-card"
        v-for="(model, modelId) in localModels.models"
        :key="modelId"
        :class="{ downloaded: model.downloaded, 'cannot-run': !canRunModel(model) }"
      >
        <div class="model-header">
          <h4>{{ model.name }}</h4>
          <span class="badge" :class="model.tier">{{ model.tier }}</span>
          <span class="badge downloaded" v-if="model.downloaded">{{ t('local_models.downloaded') }}</span>
        </div>

        <div class="model-info">
          <div class="info-item">
            <span class="label">{{ t('local_models.params') }}</span>
            <span class="value">{{ model.params }}</span>
          </div>
          <div class="info-item">
            <span class="label">{{ t('local_models.context') }}</span>
            <span class="value">{{ t('common.tokens', { count: model.context_length }) }}</span>
          </div>
          <div class="info-item">
            <span class="label">{{ t('local_models.quantization') }}</span>
            <span class="value">{{ model.quantization }}</span>
          </div>
        </div>

        <div class="model-requirements">
          <h5>{{ t('local_models.requirements') }}</h5>
          <div class="req-item">
            <span class="label">RAM:</span>
            <span class="value">{{ model.requirements.ram_gb }} GB</span>
          </div>
          <div class="req-item">
            <span class="label">CPU:</span>
            <span class="value">{{ t('common.cores', { count: model.requirements.cpu_cores }) }}</span>
          </div>
          <div class="req-item" v-if="model.requirements.gpu_vram_gb">
            <span class="label">VRAM:</span>
            <span class="value">{{ model.requirements.gpu_vram_gb }} GB</span>
          </div>
          <div class="req-item">
            <span class="label">{{ t('local_models.disk') }}</span>
            <span class="value">{{ model.requirements.disk_gb }} GB</span>
          </div>
        </div>

        <div class="model-actions">
          <button
            v-if="!model.downloaded"
            @click="downloadModel(String(modelId))"
            :disabled="!canRunModel(model) || isDownloading(String(modelId))"
            class="btn btn-primary"
          >
            {{ downloadButtonLabel(String(modelId)) }}
          </button>
          <div v-if="isDownloading(String(modelId))" class="download-progress">
            <div class="download-progress__bar">
              <div
                class="download-progress__fill"
                :style="{ width: `${downloadPercent(String(modelId))}%` }"
              />
            </div>
            <span class="download-progress__text">{{ downloadProgressLabel(String(modelId)) }}</span>
          </div>
          <button
            v-if="model.downloaded"
            @click="deleteModel(String(modelId))"
            class="btn btn-danger"
          >
            {{ t('local_models.delete') }}
          </button>
          <span v-if="!canRunModel(model)" class="error-message">
            {{ modelRunReason(model) }}
          </span>
        </div>
      </div>
    </div>

    <div v-else class="loading">
      {{ t('common.loading') }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  getSystemCheck,
  getLocalModels,
  downloadLocalModel,
  deleteLocalModel,
  getLocalDownloadJobs,
  type LocalDownloadJob,
} from '@/api/settings'
import { ApiHttpError } from '@/api/apiService'

type LocalModelsResponse = Awaited<ReturnType<typeof getLocalModels>>
type LocalModelEntry = LocalModelsResponse['models'][string]
type SystemCheckResponse = Awaited<ReturnType<typeof getSystemCheck>>
import { useI18n } from '@/composables/useI18n'
import { useToast } from '@/composables/useToast'

const { t, parseErrorCode } = useI18n()
const { show: showToast } = useToast()

const systemCheck = ref<SystemCheckResponse | null>(null)
const localModels = ref<LocalModelsResponse | null>(null)
const downloadJobs = ref<Record<string, LocalDownloadJob>>({})
const notifiedFailures = new Set<string>()
let pollTimer: ReturnType<typeof setInterval> | null = null

const hasActiveDownloads = computed(() =>
  Object.values(downloadJobs.value).some(job => job.status === 'downloading'),
)

const getJob = (modelId: string): LocalDownloadJob | undefined => downloadJobs.value[modelId]

const isDownloading = (modelId: string) => getJob(modelId)?.status === 'downloading'

const downloadPercent = (modelId: string) => getJob(modelId)?.percent ?? 0

const formatMb = (bytes: number) => (bytes / (1024 * 1024)).toFixed(1)

const downloadButtonLabel = (modelId: string) => {
  if (isDownloading(modelId)) return t('local_models.downloading')
  return t('local_models.download')
}

const downloadProgressLabel = (modelId: string) => {
  const job = getJob(modelId)
  if (!job) return t('local_models.downloading')
  if (job.bytes_total > 0) {
    return t('local_models.downloading_size', {
      done: formatMb(job.bytes_done),
      total: formatMb(job.bytes_total),
    })
  }
  return t('local_models.downloading_percent', { percent: job.percent })
}

const mergeJobs = (jobs: LocalDownloadJob[]) => {
  const next = { ...downloadJobs.value }
  for (const job of jobs) {
    if (job.status === 'idle') {
      delete next[job.model_id]
    } else {
      next[job.model_id] = job
    }
  }
  downloadJobs.value = next
}

const syncDownloadJobs = async () => {
  try {
    const { downloads } = await getLocalDownloadJobs()
    mergeJobs(downloads)

    const completed = downloads.filter(job => job.status === 'completed')
    const failed = downloads.filter(job => job.status === 'failed')

    if (completed.length > 0 || failed.length > 0) {
      await loadLocalModels()
    }

    for (const job of failed) {
      if (job.error && !notifiedFailures.has(job.model_id)) {
        notifiedFailures.add(job.model_id)
        showToast('❌', t('app.brand'), job.error, 4000)
      }
    }

    if (!hasActiveDownloads.value && pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  } catch (error) {
    console.error('Failed to sync download jobs:', error)
  }
}

const startPolling = () => {
  if (pollTimer) return
  pollTimer = setInterval(() => { void syncDownloadJobs() }, 1500)
}

const tierMessage = computed(() => {
  const tier = systemCheck.value?.tier
  if (!tier) return ''
  if (tier.reason_code) {
    return parseErrorCode(tier.reason_code, tier.reason_params ?? undefined)
  }
  return tier.reason ?? ''
})

const modelRunReason = (model: LocalModelEntry) => {
  const entry = model as LocalModelEntry & {
    can_run_reason_code?: string
    can_run_reason_params?: Record<string, string | number>
  }
  if (entry.can_run_reason_code) {
    return parseErrorCode(entry.can_run_reason_code, entry.can_run_reason_params)
  }
  return entry.can_run_reason || t('local_models.requirements_not_met')
}

const canRunModel = (model: LocalModelEntry) => {
  if (typeof model.can_run === 'boolean') return model.can_run
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
  try {
    const result = await downloadLocalModel(modelId)
    if (result.success) {
      downloadJobs.value = {
        ...downloadJobs.value,
        [modelId]: {
          model_id: modelId,
          status: result.status === 'completed' ? 'completed' : 'downloading',
          bytes_done: 0,
          bytes_total: 0,
          percent: 0,
        },
      }
      if (result.status === 'completed') {
        await loadLocalModels()
      } else {
        startPolling()
        void syncDownloadJobs()
      }
    } else {
      showToast('❌', t('app.brand'), result.message, 4000)
    }
  } catch (error) {
    if (error instanceof ApiHttpError && error.status === 409) {
      const body = error.body as { detail?: { job?: LocalDownloadJob } } | undefined
      if (body?.detail?.job) mergeJobs([body.detail.job])
      showToast('ℹ️', t('app.brand'), t('local_models.download_in_progress_server'), 3000)
      startPolling()
      void syncDownloadJobs()
      return
    }
    console.error('Failed to download model:', error)
    showToast('❌', t('app.brand'), t('local_models.download_failed'), 4000)
  }
}

const deleteModel = async (modelId: string) => {
  if (!confirm(t('local_models.delete_confirm'))) return

  try {
    const result = await deleteLocalModel(modelId)
    if (result.success) {
      await loadLocalModels()
    } else {
      showToast('❌', t('app.brand'), result.message, 4000)
    }
  } catch (error) {
    console.error('Failed to delete model:', error)
    showToast('❌', t('app.brand'), t('local_models.delete_failed'), 4000)
  }
}

onMounted(() => {
  loadSystemCheck()
  loadLocalModels()
  void syncDownloadJobs().then(() => {
    if (hasActiveDownloads.value) startPolling()
  })
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
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
  color: var(--t2, #666);
}

.system-check,
.storage-info {
  background: var(--bg-s, #f5f5f5);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid var(--brd, #ddd);
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
  color: var(--t2, #666);
}

.value {
  font-weight: 600;
}

.tier-info {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
  background: var(--info-bg);
}

.tier-info.very_light {
  background: var(--warning-bg);
}

.tier-info.light {
  background: var(--success-bg);
}

.tier-info.medium {
  background: var(--info-bg);
}

.tier-info.unsupported {
  background: var(--error-bg);
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
  color: var(--t2, #666);
}

.models-list {
  display: grid;
  gap: 20px;
}

.model-card {
  background: var(--bg-panel, white);
  border: 1px solid var(--brd, #ddd);
  border-radius: 8px;
  padding: 20px;
  transition: box-shadow 0.2s;
}

.model-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.model-card.downloaded {
  border-color: var(--success);
  background: var(--success-bg);
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
  background: var(--warning-bg);
  color: var(--warning);
}

.badge.light {
  background: var(--success-bg);
  color: var(--success);
}

.badge.medium {
  background: var(--info-bg);
  color: var(--info);
}

.badge.downloaded {
  background: var(--success);
  color: var(--on-accent);
}

.model-info,
.model-requirements {
  margin-bottom: 15px;
}

.model-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}

.download-progress {
  width: 100%;
  max-width: 320px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.download-progress__bar {
  height: 6px;
  border-radius: 3px;
  background: var(--bg-g);
  border: 1px solid var(--brd);
  overflow: hidden;
}

.download-progress__fill {
  height: 100%;
  background: var(--accent);
  transition: width 0.3s ease;
}

.download-progress__text {
  font-size: 0.85rem;
  color: var(--t2);
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
  background: var(--accent);
  color: var(--on-accent);
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-l);
}

.btn-primary:disabled {
  background: var(--disabled);
  cursor: not-allowed;
}

.btn-danger {
  background: var(--danger);
  color: var(--on-accent);
}

.btn-danger:hover {
  filter: brightness(0.92);
}

.error-message {
  color: var(--error);
  font-size: 0.9rem;
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--t2, #666);
}
</style>
