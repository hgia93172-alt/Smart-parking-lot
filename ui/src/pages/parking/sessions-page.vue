<template>
  <div class="management-page">
    <div class="page-header">
      <h2 class="page-title">💳 停车会话 & 计费</h2>
      <div class="filter-row">
        <el-select v-model="filters.lot_id" placeholder="停车场" clearable style="width:160px" @change="load">
          <el-option v-for="l in lots" :key="l.id" :label="l.name" :value="l.id" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态" clearable style="width:110px" @change="load">
          <el-option label="停车中" value="active" />
          <el-option label="已离场" value="completed" />
        </el-select>
        <el-input v-model="filters.license_plate" placeholder="车牌" clearable style="width:130px" @input="load" />
      </div>
    </div>

    <el-table :data="sessions" v-loading="loading" class="data-table">
      <el-table-column label="ID" prop="id" width="65" />
      <el-table-column label="车牌" width="110">
        <template #default="{row}"><span class="plate">{{ row.license_plate || '未知' }}</span></template>
      </el-table-column>
      <el-table-column label="停车场" prop="lot_name" width="120" />
      <el-table-column label="车位" prop="space_no" width="80" />
      <el-table-column label="状态" width="90" align="center">
        <template #default="{row}">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">{{ row.status_label }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="入场时间" prop="entry_time" width="160" />
      <el-table-column label="离场时间" prop="exit_time" width="160" />
      <el-table-column label="时长(分)" prop="duration_minutes" width="90" align="center" />
      <el-table-column label="费用(元)" width="90" align="center">
        <template #default="{row}"><span class="fee">¥{{ row.fee }}</span></template>
      </el-table-column>
      <el-table-column label="缴费" width="80" align="center">
        <template #default="{row}">
          <el-tag :type="row.is_paid ? 'success' : 'warning'" size="small">{{ row.is_paid ? '已缴' : '未缴' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="90" align="center">
        <template #default="{row}">
          <el-button v-if="!row.is_paid && row.status==='completed'" size="small" type="primary" @click="pay(row.id)">
            缴费
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-row">
      <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total"
        layout="total, prev, pager, next" @change="load" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { sessionApi, lotApi } from '@/api/parking'

const lots = ref<any[]>([])
const sessions = ref<any[]>([])
const loading = ref(false)
const page = ref(1), pageSize = ref(20), total = ref(0)
const filters = ref({ lot_id: null as number | null, status: '', license_plate: '' })

async function load() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (filters.value.lot_id) params.lot_id = filters.value.lot_id
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.license_plate) params.license_plate = filters.value.license_plate
    const res = await sessionApi.list(params)
    const d = res.data.data
    if (d?.results) { sessions.value = d.results; total.value = d.count }
    else { sessions.value = d || [] }
  } finally { loading.value = false }
}

async function pay(id: number) {
  try { await sessionApi.pay(id); ElMessage.success('缴费成功'); await load() }
  catch { ElMessage.error('操作失败') }
}

onMounted(async () => {
  const res = await lotApi.list(); lots.value = res.data.data || []; await load()
})
</script>

<style scoped>
.management-page { padding: 24px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.page-title { color: #f1f5f9; font-size: 20px; margin: 0; }
.filter-row { display: flex; gap: 10px; align-items: center; }
.plate { font-family: monospace; font-size: 14px; color: #4facfe; font-weight: 700; }
.fee { color: #f5a623; font-weight: 700; }
.pagination-row { margin-top: 16px; display: flex; justify-content: flex-end; }
:deep(.el-table) { --el-table-bg-color: #1e293b; --el-table-tr-bg-color: #1e293b; --el-table-row-hover-bg-color: #334155; --el-table-border-color: #334155; color: #cbd5e1; }
:deep(.el-table th) { background: #0f172a !important; color: #94a3b8; }
</style>
