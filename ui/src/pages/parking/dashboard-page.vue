<template>
  <div class="dashboard-page">
    <!-- Welcome Banner -->
    <div class="welcome-banner card">
      <div class="welcome-text">
        <h2>欢迎使用智能停车场管理系统</h2>
        <p>今天是 {{ currentDay }}，系统为您实时监控车辆动态与计费状态。</p>
      </div>
    </div>

    <!-- Overview Cards -->
    <div class="overview-cards">
      <div class="card stat-card" v-for="stat in statCards" :key="stat.label">
        <div class="stat-icon" :style="{ background: stat.color }">
          <component :is="stat.icon" />
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="card chart-card">
        <div class="card-title">24小时车流量</div>
        <div ref="hourlyChartEl" class="chart-container"></div>
      </div>
      <div class="card chart-card">
        <div class="card-title">车位占用率</div>
        <div ref="occupancyChartEl" class="chart-container"></div>
      </div>
    </div>

    <!-- Revenue Row -->
    <div class="charts-row">
      <div class="card chart-card chart-wide">
        <div class="card-title-row">
          <span class="card-title">收费统计</span>
          <el-radio-group v-model="revenuePeriod" size="small" @change="loadRevenue">
            <el-radio-button value="daily">近7天</el-radio-button>
            <el-radio-button value="monthly">近12月</el-radio-button>
          </el-radio-group>
        </div>
        <div ref="revenueChartEl" class="chart-container chart-tall"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'
import { statsApi } from '@/api/parking'
import { useParkingStore } from '@/stores/parking-store'

const parkingStore = useParkingStore()
const hourlyChartEl = ref<HTMLElement>()
const occupancyChartEl = ref<HTMLElement>()
const revenueChartEl = ref<HTMLElement>()
let hourlyChart: echarts.ECharts | null = null
let occupancyChart: echarts.ECharts | null = null
let revenueChart: echarts.ECharts | null = null
const revenuePeriod = ref<'daily' | 'monthly'>('daily')
let refreshTimer: number | null = null

const overview = computed(() => parkingStore.overview)
const currentDay = ref(new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }))

const statCards = computed(() => {
  const o = overview.value
  if (!o) return []
  return [
    { label: '停车场数量', value: o.total_lots, color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', icon: 'div' },
    { label: '总车位数', value: o.total_spaces, color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', icon: 'div' },
    { label: '空闲车位', value: o.available_spaces, color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', icon: 'div' },
    { label: '当前停车中', value: o.active_sessions, color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', icon: 'div' },
    { label: '今日进场', value: o.today_entries, color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', icon: 'div' },
    { label: '今日收入(元)', value: parseFloat(o.today_revenue).toFixed(2), color: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)', icon: 'div' },
    { label: '未处理违规', value: o.pending_violations, color: 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)', icon: 'div' },
    { label: '占用率%', value: o.occupancy_rate + '%', color: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)', icon: 'div' },
  ]
})

async function loadHourly() {
  const res = await statsApi.hourly()
  const data = res.data.data as any[]
  const hours = data.map(d => `${d.hour}:00`)
  const entries = data.map(d => d.entries)
  const exits = data.map(d => d.exits)
  hourlyChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['入场', '出场'] },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', name: '辆' },
    series: [
      { name: '入场', type: 'line', smooth: true, data: entries, areaStyle: { opacity: 0.3 }, itemStyle: { color: '#4facfe' } },
      { name: '出场', type: 'line', smooth: true, data: exits, areaStyle: { opacity: 0.3 }, itemStyle: { color: '#f093fb' } },
    ],
  })
}

async function loadOccupancy() {
  const o = overview.value
  if (!o) return
  occupancyChart?.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['50%', '80%'],
      data: [
        { value: o.occupied_spaces, name: '占用', itemStyle: { color: '#f5576c' } },
        { value: o.available_spaces, name: '空闲', itemStyle: { color: '#43e97b' } },
        { value: o.total_spaces - o.occupied_spaces - o.available_spaces, name: '禁用', itemStyle: { color: '#aaa' } },
      ],
      label: { formatter: '{b}: {d}%' },
    }],
  })
}

async function loadRevenue() {
  const res = await statsApi.revenue(revenuePeriod.value)
  const data = res.data.data as any[]
  revenueChart?.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.map(d => d.label) },
    yAxis: [
      { type: 'value', name: '收入(元)', position: 'left' },
      { type: 'value', name: '笔数', position: 'right' },
    ],
    series: [
      { name: '收入', type: 'bar', data: data.map(d => parseFloat(d.revenue)), itemStyle: { color: '#667eea' }, yAxisIndex: 0 },
      { name: '笔数', type: 'line', smooth: true, data: data.map(d => d.count), itemStyle: { color: '#fa709a' }, yAxisIndex: 1 },
    ],
  })
}

async function loadAll() {
  await parkingStore.fetchOverview()
  await loadHourly()
  await loadOccupancy()
  await loadRevenue()
}

onMounted(async () => {
  if (hourlyChartEl.value) hourlyChart = echarts.init(hourlyChartEl.value, 'dark')
  if (occupancyChartEl.value) occupancyChart = echarts.init(occupancyChartEl.value, 'dark')
  if (revenueChartEl.value) revenueChart = echarts.init(revenueChartEl.value, 'dark')
  await loadAll()
  refreshTimer = window.setInterval(loadAll, 30000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
  hourlyChart?.dispose()
  occupancyChart?.dispose()
  revenueChart?.dispose()
})
</script>

<style scoped>
.dashboard-page { padding: 24px; display: flex; flex-direction: column; gap: 20px; }
.overview-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; }
.card { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }
.stat-card { display: flex; align-items: center; gap: 16px; transition: transform .2s; }
.stat-card:hover { transform: translateY(-3px); }
.stat-icon { width: 52px; height: 52px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0; }
.stat-body { flex: 1; }
.stat-value { font-size: 26px; font-weight: 700; color: #f1f5f9; }
.stat-label { font-size: 13px; color: #94a3b8; margin-top: 2px; }
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.chart-card { display: flex; flex-direction: column; gap: 12px; }
.chart-wide { grid-column: 1 / -1; }
.card-title { font-size: 16px; font-weight: 600; color: #e2e8f0; }
.card-title-row { display: flex; justify-content: space-between; align-items: center; }
.chart-container { height: 280px; }
.chart-tall { height: 320px; }

.welcome-banner {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  border-left: 4px solid #4facfe;
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.welcome-text h2 { margin: 0; font-size: 20px; color: #f1f5f9; }
.welcome-text p { margin: 5px 0 0; font-size: 14px; color: #94a3b8; }
</style>
