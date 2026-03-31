<template>
  <div class="management-page">
    <div class="page-header">
      <h2 class="page-title">🅿 车位管理</h2>
      <div class="header-actions">
        <el-select v-model="selectedLotId" placeholder="选择停车场" style="width:180px" @change="load">
          <el-option v-for="l in lots" :key="l.id" :label="l.name" :value="l.id" />
        </el-select>
        <el-button type="primary" @click="openDialog()">+ 新增车位</el-button>
      </div>
    </div>

    <!-- 车位俯视图 -->
    <div class="card spaces-visual" v-if="spaces.length">
      <div class="visual-title">车位分布图</div>
      <div class="spaces-bird-view">
        <div v-for="space in spaces" :key="space.id"
             :class="['space-tile', space.status]"
             @click="openDialog(space)">
          <div class="space-tile-no">{{ space.space_no }}</div>
          <div class="space-tile-type">{{ typeLabel(space.space_type) }}</div>
        </div>
      </div>
      <div class="legend-row">
        <span class="legend available">■ 空闲 ({{ spaces.filter(s=>s.status==='available').length }})</span>
        <span class="legend occupied">■ 占用 ({{ spaces.filter(s=>s.status==='occupied').length }})</span>
        <span class="legend disabled">■ 禁用 ({{ spaces.filter(s=>s.status==='disabled').length }})</span>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-table :data="spaces" v-loading="loading" class="data-table" style="margin-top:16px">
      <el-table-column label="编号" prop="space_no" width="90" />
      <el-table-column label="类型" width="90">
        <template #default="{row}">{{ typeLabel(row.space_type) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="90" align="center">
        <template #default="{row}">
          <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="占用开始" prop="occupied_since" show-overflow-tooltip />
      <el-table-column label="操作" width="180" align="center">
        <template #default="{row}">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="success" v-if="row.status==='occupied'"
                     @click="updateStatus(row.id, 'available')">释放</el-button>
          <el-button size="small" type="danger" @click="deleteSpace(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑车位' : '新增车位'" width="420px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="停车场">
          <el-select v-model="form.lot" style="width:100%">
            <el-option v-for="l in lots" :key="l.id" :label="l.name" :value="l.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="编号"><el-input v-model="form.space_no" placeholder="如 A-01" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.space_type" style="width:100%">
            <el-option label="小型车" value="small" />
            <el-option label="大型车" value="large" />
            <el-option label="无障碍" value="disabled_person" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option label="空闲" value="available" />
            <el-option label="占用" value="occupied" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { lotApi, spaceApi } from '@/api/parking'

const lots = ref<any[]>([])
const spaces = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const selectedLotId = ref<number | null>(null)
const form = ref<any>({ lot: null, space_no: '', space_type: 'small', status: 'available' })

const typeLabel = (t: string) => ({ small: '小型', large: '大型', disabled_person: '无障碍' }[t] ?? t)
const statusLabel = (s: string) => ({ available: '空闲', occupied: '占用', disabled: '禁用' }[s] ?? s)
const statusType = (s: string) => ({ available: 'success', occupied: 'danger', disabled: 'info' }[s] ?? '')

async function load() {
  loading.value = true
  try {
    const params: any = {}
    if (selectedLotId.value) params.lot_id = selectedLotId.value
    const res = await spaceApi.list(params)
    spaces.value = res.data.data || []
  } finally { loading.value = false }
}

function openDialog(row?: any) {
  form.value = row ? { ...row, lot: row.lot } : { lot: selectedLotId.value, space_no: '', space_type: 'small', status: 'available' }
  dialogVisible.value = true
}

async function save() {
  try {
    if (form.value.id) await spaceApi.update(form.value.id, form.value)
    else await spaceApi.create(form.value)
    ElMessage.success('保存成功'); dialogVisible.value = false; await load()
  } catch { ElMessage.error('保存失败') }
}

async function updateStatus(id: number, status: string) {
  await spaceApi.updateStatus(id, status); await load()
}

async function deleteSpace(id: number) {
  await ElMessageBox.confirm('确认删除该车位？', '警告', { type: 'warning' })
  try { await spaceApi.delete(id); ElMessage.success('删除成功'); await load() }
  catch { ElMessage.error('删除失败') }
}

onMounted(async () => {
  const res = await lotApi.list()
  lots.value = res.data.data || []
  if (lots.value.length) { selectedLotId.value = lots.value[0].id }
  await load()
})
</script>

<style scoped>
.management-page { padding: 24px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { color: #f1f5f9; font-size: 20px; margin: 0; }
.header-actions { display: flex; gap: 10px; }
.card { background: #1e293b; border-radius: 12px; padding: 16px; border: 1px solid #334155; }
.spaces-visual { margin-bottom: 16px; }
.visual-title { font-size: 14px; color: #94a3b8; margin-bottom: 12px; }
.spaces-bird-view { display: flex; flex-wrap: wrap; gap: 8px; }
.space-tile { width: 80px; height: 60px; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; transition: all .2s; border: 1px solid; }
.space-tile:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.3); }
.space-tile.available { background: rgba(67,233,123,.15); border-color: #43e97b; }
.space-tile.occupied { background: rgba(245,87,108,.15); border-color: #f5576c; }
.space-tile.disabled { background: rgba(148,163,184,.08); border-color: #475569; }
.space-tile-no { font-size: 13px; font-weight: 700; color: #e2e8f0; }
.space-tile-type { font-size: 10px; color: #94a3b8; }
.legend-row { display: flex; gap: 20px; margin-top: 12px; font-size: 12px; }
.legend.available { color: #43e97b; }
.legend.occupied { color: #f5576c; }
.legend.disabled { color: #64748b; }
:deep(.el-table) { --el-table-bg-color: #1e293b; --el-table-tr-bg-color: #1e293b; --el-table-row-hover-bg-color: #334155; --el-table-border-color: #334155; color: #cbd5e1; }
:deep(.el-table th) { background: #0f172a !important; color: #94a3b8; }
</style>
