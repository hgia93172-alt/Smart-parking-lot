<template>
  <div class="monitoring-page">
    <div class="monitor-header">
      <h2 class="page-title">🎥 实时监控</h2>
      <div class="header-actions">
        <el-select v-model="selectedLotId" placeholder="选择停车场" style="width:200px" @change="loadSpaces">
          <el-option v-for="lot in lots" :key="lot.id" :label="lot.name" :value="lot.id" />
        </el-select>
        <el-tag :type="isRunning ? 'success' : 'danger'" size="large">
          {{ isRunning ? '● 检测运行中' : '○ 已停止' }}
        </el-tag>
        <el-button :type="isRunning ? 'danger' : 'success'" @click="toggleDetection">
          {{ isRunning ? '停止检测' : '启动模拟检测' }}
        </el-button>
      </div>
    </div>

    <div class="monitor-body">
      <!-- 模拟摄像头画面 -->
      <div class="camera-view card">
        <canvas ref="canvasEl" width="800" height="500" class="camera-canvas"></canvas>
        <div class="camera-overlay-info">
          <span>FPS: {{ fps }}</span>
          <span>检测目标: {{ detections.length }}</span>
          <span>{{ currentTime }}</span>
        </div>
      </div>

      <!-- 右侧信息面板 -->
      <div class="side-panel">
        <!-- 当前车位状态 -->
        <div class="card spaces-card">
          <div class="card-title">车位状态</div>
          <div class="spaces-grid">
            <div v-for="space in spaces" :key="space.id"
                 :class="['space-cell', space.status]"
                 :title="space.space_no">
              <div class="space-no">{{ space.space_no }}</div>
              <div class="space-status-dot"></div>
            </div>
          </div>
          <div class="spaces-legend">
            <span class="legend-item available">■ 空闲 {{ availableCount }}</span>
            <span class="legend-item occupied">■ 占用 {{ occupiedCount }}</span>
          </div>
        </div>

        <!-- 实时检测结果 -->
        <div class="card detections-card">
          <div class="card-title">检测结果 (最近20条)</div>
          <div class="detection-list">
            <div v-for="(d, i) in recentDetections" :key="i" class="detection-item">
              <span class="det-type">{{ d.type }}</span>
              <span class="det-conf">{{ (d.conf * 100).toFixed(0) }}%</span>
              <span class="det-time">{{ d.time }}</span>
            </div>
            <div v-if="!recentDetections.length" class="empty-hint">暂无检测数据</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { lotApi, spaceApi } from '@/api/parking'
import { useParkingStore } from '@/stores/parking-store'

const parkingStore = useParkingStore()
const lots = ref<any[]>([])
const selectedLotId = ref<number | null>(null)
const spaces = ref<any[]>([])
const canvasEl = ref<HTMLCanvasElement>()
const isRunning = ref(false)
const fps = ref(0)
const detections = ref<any[]>([])
const recentDetections = ref<any[]>([])
const currentTime = ref('')

let animFrameId: number | null = null
let detectionTimer: number | null = null
let fpsTimer: number | null = null
let frameCount = 0

const vehicleColors: Record<string, string> = {
  car: '#4facfe', truck: '#fda085', bus: '#f093fb', motorcycle: '#43e97b'
}
const vehicleTypes = ['car', 'car', 'car', 'truck', 'bus', 'motorcycle']

const availableCount = computed(() => spaces.value.filter(s => s.status === 'available').length)
const occupiedCount = computed(() => spaces.value.filter(s => s.status === 'occupied').length)

async function loadSpaces() {
  if (!selectedLotId.value) return
  const res = await spaceApi.list({ lot_id: selectedLotId.value })
  spaces.value = (res.data.data || []).slice(0, 24)
}

// ── Canvas 渲染 ───────────────────────────────────────────────────────────
function drawFrame() {
  const canvas = canvasEl.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')!
  ctx.fillStyle = '#0f172a'
  ctx.fillRect(0, 0, 800, 500)

  // 网格线
  ctx.strokeStyle = '#1e293b'
  for (let x = 0; x < 800; x += 50) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, 500); ctx.stroke() }
  for (let y = 0; y < 500; y += 50) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(800, y); ctx.stroke() }

  // 停车位区域
  const cols = 6, rows = 3
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const x = 50 + c * 115, y = 30 + r * 130
      const idx = r * cols + c
      const space = spaces.value[idx]
      const occupied = space?.status === 'occupied'
      ctx.strokeStyle = occupied ? '#f5576c' : '#43e97b'
      ctx.lineWidth = 2
      ctx.strokeRect(x, y, 100, 110)
      ctx.fillStyle = occupied ? 'rgba(245,87,108,0.15)' : 'rgba(67,233,123,0.08)'
      ctx.fillRect(x, y, 100, 110)
      ctx.fillStyle = '#94a3b8'; ctx.font = '11px monospace'
      ctx.fillText(space?.space_no || `A-${(idx + 1).toString().padStart(2, '0')}`, x + 4, y + 14)
    }
  }

  // 绘制检测框
  for (const det of detections.value) {
    const [x1, y1, x2, y2] = det.bbox
    const color = vehicleColors[det.type] || '#fff'
    ctx.strokeStyle = color; ctx.lineWidth = 2
    ctx.strokeRect(x1, y1, x2 - x1, y2 - y1)
    ctx.fillStyle = color + 'cc'; ctx.font = 'bold 12px monospace'
    ctx.fillText(`${det.type} ${(det.conf * 100).toFixed(0)}% #${det.id}`, x1, y1 - 4)
    // 轨迹
    if (det.trail && det.trail.length > 1) {
      ctx.strokeStyle = color + '88'; ctx.lineWidth = 1; ctx.beginPath()
      ctx.moveTo(det.trail[0][0], det.trail[0][1])
      for (const pt of det.trail.slice(1)) ctx.lineTo(pt[0], pt[1])
      ctx.stroke()
    }
  }

  // 时间戳
  ctx.fillStyle = '#94a3b8'; ctx.font = '12px monospace'
  ctx.fillText(new Date().toLocaleTimeString(), 10, 490)
  frameCount++
}

// ── 模拟检测 ───────────────────────────────────────────────────────────────
let simVehicles: any[] = []
let nextId = 1

function updateSimDetections() {
  // 随机新建车辆
  if (simVehicles.length < 6 && Math.random() > 0.7) {
    simVehicles.push({
      id: nextId++, type: vehicleTypes[Math.floor(Math.random() * vehicleTypes.length)],
      x: Math.random() * 600 + 50, y: Math.random() * 350 + 30,
      vx: (Math.random() - 0.5) * 3, vy: (Math.random() - 0.5) * 3,
      conf: 0.75 + Math.random() * 0.23, trail: [], life: 80 + Math.floor(Math.random() * 100),
    })
  }

  simVehicles = simVehicles.filter(v => v.life > 0)
  simVehicles.forEach(v => {
    v.x = Math.max(20, Math.min(760, v.x + v.vx))
    v.y = Math.max(20, Math.min(480, v.y + v.vy))
    if (v.x <= 20 || v.x >= 760) v.vx *= -1
    if (v.y <= 20 || v.y >= 480) v.vy *= -1
    v.trail.push([v.x + 50, v.y + 50])
    if (v.trail.length > 20) v.trail.shift()
    v.life--
  })

  detections.value = simVehicles.map(v => ({
    id: v.id, type: v.type, conf: v.conf,
    bbox: [v.x, v.y, v.x + 100, v.y + 70],
    trail: v.trail.slice(),
  }))

  // 记录到检测历史
  for (const det of detections.value) {
    recentDetections.value.unshift({
      type: det.type, conf: det.conf,
      time: new Date().toLocaleTimeString(),
    })
  }
  if (recentDetections.value.length > 20) recentDetections.value.length = 20

  currentTime.value = new Date().toLocaleString()
}

function renderLoop() {
  drawFrame()
  if (isRunning.value) animFrameId = requestAnimationFrame(renderLoop)
}

function toggleDetection() {
  isRunning.value = !isRunning.value
  if (isRunning.value) {
    detectionTimer = window.setInterval(updateSimDetections, 200)
    fpsTimer = window.setInterval(() => { fps.value = frameCount; frameCount = 0 }, 1000)
    renderLoop()
  } else {
    if (detectionTimer) clearInterval(detectionTimer)
    if (fpsTimer) clearInterval(fpsTimer)
    if (animFrameId) cancelAnimationFrame(animFrameId)
  }
}

onMounted(async () => {
  const res = await lotApi.list()
  lots.value = res.data.data || []
  if (lots.value.length) { selectedLotId.value = lots.value[0].id; await loadSpaces() }
  drawFrame() // 静态首帧
})

onUnmounted(() => {
  if (detectionTimer) clearInterval(detectionTimer)
  if (fpsTimer) clearInterval(fpsTimer)
  if (animFrameId) cancelAnimationFrame(animFrameId)
})
</script>

<style scoped>
.monitoring-page { padding: 24px; height: 100%; display: flex; flex-direction: column; gap: 16px; }
.monitor-header { display: flex; justify-content: space-between; align-items: center; }
.page-title { color: #f1f5f9; font-size: 22px; margin: 0; }
.header-actions { display: flex; align-items: center; gap: 12px; }
.monitor-body { display: flex; gap: 16px; flex: 1; min-height: 0; }
.camera-view { flex: 1; position: relative; display: flex; flex-direction: column; background: #0f172a; }
.camera-canvas { width: 100%; height: auto; border-radius: 8px; }
.camera-overlay-info { display: flex; gap: 20px; padding: 8px; font-family: monospace; font-size: 13px; color: #94a3b8; background: #0f172a; border-radius: 0 0 8px 8px; }
.side-panel { width: 280px; display: flex; flex-direction: column; gap: 16px; overflow-y: auto; }
.card { background: #1e293b; border-radius: 12px; padding: 16px; border: 1px solid #334155; }
.card-title { font-size: 14px; font-weight: 600; color: #e2e8f0; margin-bottom: 12px; }
.spaces-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
.space-cell { border-radius: 6px; padding: 6px; display: flex; flex-direction: column; align-items: center; cursor: default; transition: transform .15s; }
.space-cell:hover { transform: scale(1.05); }
.space-cell.available { background: rgba(67,233,123,0.15); border: 1px solid #43e97b; }
.space-cell.occupied { background: rgba(245,87,108,0.15); border: 1px solid #f5576c; }
.space-cell.disabled { background: rgba(148,163,184,0.1); border: 1px solid #475569; }
.space-no { font-size: 10px; color: #cbd5e1; }
.space-status-dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 4px; }
.available .space-status-dot { background: #43e97b; }
.occupied .space-status-dot { background: #f5576c; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
.spaces-legend { display: flex; gap: 16px; margin-top: 10px; font-size: 12px; }
.legend-item.available { color: #43e97b; }
.legend-item.occupied { color: #f5576c; }
.detections-card { flex: 1; overflow: hidden; display: flex; flex-direction: column; }
.detection-list { flex: 1; overflow-y: auto; }
.detection-item { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #334155; font-size: 12px; }
.det-type { color: #4facfe; font-weight: 600; }
.det-conf { color: #43e97b; }
.det-time { color: #64748b; }
.empty-hint { color: #64748b; text-align: center; padding: 20px; }
</style>
