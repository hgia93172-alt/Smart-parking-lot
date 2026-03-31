<template>
  <div class="management-page">
    <div class="page-header">
      <h2 class="page-title">🏢 停车场管理</h2>
      <el-button type="primary" @click="openDialog()">+ 新增停车场</el-button>
    </div>

    <el-table :data="lots" v-loading="loading" row-class-name="table-row" class="data-table">
      <el-table-column label="ID" prop="id" width="60" />
      <el-table-column label="名称" prop="name" />
      <el-table-column label="地址" prop="address" show-overflow-tooltip />
      <el-table-column label="总车位" prop="total_spaces" width="80" align="center" />
      <el-table-column label="空闲" prop="available_spaces" width="70" align="center">
        <template #default="{ row }"><el-tag type="success">{{ row.available_spaces }}</el-tag></template>
      </el-table-column>
      <el-table-column label="占用" prop="occupied_spaces" width="70" align="center">
        <template #default="{ row }"><el-tag type="danger">{{ row.occupied_spaces }}</el-tag></template>
      </el-table-column>
      <el-table-column label="占用率" width="120" align="center">
        <template #default="{ row }">
          <el-progress :percentage="row.occupancy_rate" :color="progressColor(row.occupancy_rate)" :show-text="false" />
          <span style="font-size:12px;color:#94a3b8">{{ row.occupancy_rate }}%</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" align="center">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteLot(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 对话框 -->
    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑停车场' : '新增停车场'" width="480px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="总车位数"><el-input-number v-model="form.total_spaces" :min="0" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" /></el-form-item>
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
import { lotApi } from '@/api/parking'

const lots = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = ref<any>({ name: '', address: '', total_spaces: 0, description: '', is_active: true })

const progressColor = (pct: number) => pct > 90 ? '#f5576c' : pct > 70 ? '#fda085' : '#43e97b'

async function load() {
  loading.value = true
  try { const res = await lotApi.list(); lots.value = res.data.data || [] }
  finally { loading.value = false }
}

function openDialog(row?: any) {
  form.value = row ? { ...row } : { name: '', address: '', total_spaces: 0, description: '', is_active: true }
  dialogVisible.value = true
}

async function save() {
  try {
    if (form.value.id) await lotApi.update(form.value.id, form.value)
    else await lotApi.create(form.value)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    await load()
  } catch { ElMessage.error('保存失败') }
}

async function deleteLot(id: number) {
  await ElMessageBox.confirm('确认删除该停车场及其所有数据吗？', '警告', { type: 'warning' })
  try { await lotApi.delete(id); ElMessage.success('删除成功'); await load() }
  catch { ElMessage.error('删除失败') }
}

onMounted(load)
</script>

<style scoped>
.management-page { padding: 24px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { color: #f1f5f9; font-size: 20px; margin: 0; }
.data-table { background: transparent; }
:deep(.el-table) { --el-table-bg-color: #1e293b; --el-table-tr-bg-color: #1e293b; --el-table-row-hover-bg-color: #334155; --el-table-border-color: #334155; color: #cbd5e1; }
:deep(.el-table th) { background: #0f172a !important; color: #94a3b8; }
</style>
