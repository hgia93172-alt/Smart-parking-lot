<template>
  <div class="management-page">
    <div class="page-header">
      <h2 class="page-title">🚗 车辆进出记录</h2>
      <div class="filter-row">
        <el-select v-model="filters.lot_id" placeholder="停车场" clearable style="width:160px" @change="load">
          <el-option v-for="l in lots" :key="l.id" :label="l.name" :value="l.id" />
        </el-select>
        <el-select v-model="filters.direction" placeholder="方向" clearable style="width:100px" @change="load">
          <el-option label="入场" value="entry" />
          <el-option label="出场" value="exit" />
        </el-select>
        <el-input v-model="filters.license_plate" placeholder="车牌号" clearable style="width:140px" @input="load" />
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </div>

    <el-table :data="records" v-loading="loading" class="data-table">
      <el-table-column label="ID" prop="id" width="60" />
      <el-table-column label="停车场" prop="lot_name" width="120" />
      <el-table-column label="车牌" prop="license_plate" width="110">
        <template #default="{row}"><span class="plate">{{ row.license_plate || '未识别' }}</span></template>
      </el-table-column>
      <el-table-column label="车型" prop="vehicle_type_label" width="90" />
      <el-table-column label="方向" width="80" align="center">
        <template #default="{row}">
          <el-tag :type="row.direction === 'entry' ? 'success' : 'warning'" size="small">
            {{ row.direction === 'entry' ? '↑ 入场' : '↓ 出场' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="置信度" width="90" align="center">
        <template #default="{row}">{{ (row.confidence * 100).toFixed(0) }}%</template>
      </el-table-column>
      <el-table-column label="记录时间" prop="recorded_at" width="160" />
      <el-table-column label="跟踪ID" prop="track_id" width="80" align="center" />
    </el-table>

    <div class="pagination-row">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @change="load"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { vehicleApi, lotApi } from '@/api/parking'

const lots = ref<any[]>([])
const records = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = ref({ lot_id: null as number | null, direction: '', license_plate: '' })

async function load() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (filters.value.lot_id) params.lot_id = filters.value.lot_id
    if (filters.value.direction) params.direction = filters.value.direction
    if (filters.value.license_plate) params.license_plate = filters.value.license_plate
    const res = await vehicleApi.list(params)
    const d = res.data.data
    if (d?.results) { records.value = d.results; total.value = d.count }
    else { records.value = d || [] }
  } finally { loading.value = false }
}

function resetFilters() {
  filters.value = { lot_id: null, direction: '', license_plate: '' }; load()
}

onMounted(async () => {
  const res = await lotApi.list(); lots.value = res.data.data || []; await load()
})
</script>

<style scoped>
.management-page { padding: 24px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.page-title { color: #f1f5f9; font-size: 20px; margin: 0; }
.filter-row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.plate { font-family: monospace; font-size: 14px; color: #4facfe; font-weight: 700; }
.pagination-row { margin-top: 16px; display: flex; justify-content: flex-end; }
:deep(.el-table) { --el-table-bg-color: #1e293b; --el-table-tr-bg-color: #1e293b; --el-table-row-hover-bg-color: #334155; --el-table-border-color: #334155; color: #cbd5e1; }
:deep(.el-table th) { background: #0f172a !important; color: #94a3b8; }
</style>
