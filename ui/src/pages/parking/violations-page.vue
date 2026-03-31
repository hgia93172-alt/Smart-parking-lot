<template>
  <div class="management-page">
    <div class="page-header">
      <h2 class="page-title">⚠ 违规报警</h2>
      <div class="filter-row">
        <el-select v-model="filters.status" placeholder="状态" clearable style="width:120px" @change="load">
          <el-option label="待处理" value="pending" />
          <el-option label="已处理" value="resolved" />
        </el-select>
        <el-select v-model="filters.lot_id" placeholder="停车场" clearable style="width:160px" @change="load">
          <el-option v-for="l in lots" :key="l.id" :label="l.name" :value="l.id" />
        </el-select>
        <el-button @click="load">刷新</el-button>
      </div>
    </div>

    <!-- 待处理提示 -->
    <el-alert v-if="pendingCount > 0" :title="`有 ${pendingCount} 条违规待处理`" type="error"
              :closable="false" show-icon style="margin-bottom:16px" />

    <el-table :data="violations" v-loading="loading" class="data-table"
              :row-class-name="rowClass">
      <el-table-column label="ID" prop="id" width="60" />
      <el-table-column label="停车场" prop="lot_name" width="110" />
      <el-table-column label="摄像头" prop="camera_name" width="110" />
      <el-table-column label="车牌" width="110">
        <template #default="{row}"><span class="plate">{{ row.license_plate || '未识别' }}</span></template>
      </el-table-column>
      <el-table-column label="违规类型" width="130">
        <template #default="{row}">
          <el-tag type="danger" size="small">{{ row.violation_type_label }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="区域" prop="zone_name" width="100" />
      <el-table-column label="驻留(秒)" prop="duration_seconds" width="85" align="center" />
      <el-table-column label="违规时间" prop="violated_at" width="155" />
      <el-table-column label="状态" width="90" align="center">
        <template #default="{row}">
          <el-tag :type="row.status === 'pending' ? 'danger' : 'success'" size="small">{{ row.status_label }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" align="center">
        <template #default="{row}">
          <el-button v-if="row.status === 'pending'" size="small" type="success" @click="resolve(row)">
            标记处理
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-row">
      <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total"
        layout="total, prev, pager, next" @change="load" />
    </div>

    <!-- 处理对话框 -->
    <el-dialog v-model="resolveDialogVisible" title="处理违规记录" width="380px">
      <el-form>
        <el-form-item label="处理备注">
          <el-input v-model="resolveRemark" type="textarea" :rows="3" placeholder="输入处理说明..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resolveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmResolve">确认处理</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { violationApi, lotApi } from '@/api/parking'

const lots = ref<any[]>([])
const violations = ref<any[]>([])
const loading = ref(false)
const page = ref(1), pageSize = ref(20), total = ref(0)
const filters = ref({ lot_id: null as number | null, status: '' })
const resolveDialogVisible = ref(false)
const resolveRemark = ref('')
const currentViolationId = ref<number | null>(null)

const pendingCount = computed(() => violations.value.filter(v => v.status === 'pending').length)
const rowClass = ({ row }: any) => row.status === 'pending' ? 'pending-row' : ''

async function load() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (filters.value.lot_id) params.lot_id = filters.value.lot_id
    if (filters.value.status) params.status = filters.value.status
    const res = await violationApi.list(params)
    const d = res.data.data
    if (d?.results) { violations.value = d.results; total.value = d.count }
    else { violations.value = d || [] }
  } finally { loading.value = false }
}

function resolve(row: any) {
  currentViolationId.value = row.id
  resolveRemark.value = ''
  resolveDialogVisible.value = true
}

async function confirmResolve() {
  if (!currentViolationId.value) return
  try {
    await violationApi.resolve(currentViolationId.value, resolveRemark.value)
    ElMessage.success('处理成功')
    resolveDialogVisible.value = false
    await load()
  } catch { ElMessage.error('处理失败') }
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
.pagination-row { margin-top: 16px; display: flex; justify-content: flex-end; }
:deep(.el-table) { --el-table-bg-color: #1e293b; --el-table-tr-bg-color: #1e293b; --el-table-row-hover-bg-color: #334155; --el-table-border-color: #334155; color: #cbd5e1; }
:deep(.el-table th) { background: #0f172a !important; color: #94a3b8; }
:deep(.pending-row) { background: rgba(245, 87, 108, 0.07) !important; }
:deep(.pending-row:hover td) { background: rgba(245, 87, 108, 0.12) !important; }
</style>
