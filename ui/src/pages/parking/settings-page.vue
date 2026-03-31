<template>
  <div class="management-page">
    <h2 class="page-title">⚙ 系统设置</h2>

    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- 摄像头配置 -->
      <el-tab-pane label="摄像头配置" name="cameras">
        <div class="tab-actions">
          <el-select v-model="camLotId" placeholder="选择停车场" style="width:180px" @change="loadCameras">
            <el-option v-for="l in lots" :key="l.id" :label="l.name" :value="l.id" />
          </el-select>
          <el-button type="primary" @click="openCamDialog()">+ 新增摄像头</el-button>
        </div>
        <el-table :data="cameras" class="data-table" style="margin-top:12px">
          <el-table-column label="ID" prop="id" width="60" />
          <el-table-column label="名称" prop="name" />
          <el-table-column label="视频流地址" prop="stream_url" show-overflow-tooltip />
          <el-table-column label="状态" width="90" align="center">
            <template #default="{row}">
              <el-tag :type="row.status === 'online' ? 'success' : 'danger'" size="small">
                {{ row.status === 'online' ? '在线' : '离线' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" align="center">
            <template #default="{row}">
              <el-button size="small" @click="openCamDialog(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteCam(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 计费规则 -->
      <el-tab-pane label="计费规则" name="billing">
        <div class="tab-actions">
          <el-select v-model="ruleFilter.lot_id" placeholder="选择停车场" style="width:180px" @change="loadRules">
            <el-option v-for="l in lots" :key="l.id" :label="l.name" :value="l.id" />
          </el-select>
          <el-button type="primary" @click="openRuleDialog()">+ 新增规则</el-button>
        </div>
        <el-table :data="rules" class="data-table" style="margin-top:12px">
          <el-table-column label="ID" prop="id" width="60" />
          <el-table-column label="车型" prop="vehicle_type" width="90" />
          <el-table-column label="免费时长(分)" prop="free_minutes" width="110" align="center" />
          <el-table-column label="每小时费率(元)" prop="rate_per_hour" width="130" align="center" />
          <el-table-column label="日封顶(元)" prop="daily_max" width="110" align="center" />
          <el-table-column label="状态" width="80" align="center">
            <template #default="{row}">
              <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" align="center">
            <template #default="{row}">
              <el-button size="small" @click="openRuleDialog(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteRule(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 摄像头对话框 -->
    <el-dialog v-model="camDialogVisible" :title="camForm.id ? '编辑摄像头' : '新增摄像头'" width="480px">
      <el-form :model="camForm" label-width="100px">
        <el-form-item label="停车场">
          <el-select v-model="camForm.lot" style="width:100%">
            <el-option v-for="l in lots" :key="l.id" :label="l.name" :value="l.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称"><el-input v-model="camForm.name" /></el-form-item>
        <el-form-item label="视频流地址"><el-input v-model="camForm.stream_url" placeholder="rtsp://... 或本地文件路径" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="camForm.status" style="width:100%">
            <el-option label="在线" value="online" />
            <el-option label="离线" value="offline" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="camDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCam">保存</el-button>
      </template>
    </el-dialog>

    <!-- 计费规则对话框 -->
    <el-dialog v-model="ruleDialogVisible" :title="ruleForm.id ? '编辑规则' : '新增规则'" width="420px">
      <el-form :model="ruleForm" label-width="110px">
        <el-form-item label="停车场">
          <el-select v-model="ruleForm.lot" style="width:100%">
            <el-option v-for="l in lots" :key="l.id" :label="l.name" :value="l.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="车型">
          <el-select v-model="ruleForm.vehicle_type" style="width:100%">
            <el-option label="小型车" value="car" /><el-option label="货车" value="truck" />
            <el-option label="大型车/公交" value="bus" /><el-option label="摩托车" value="motorcycle" />
          </el-select>
        </el-form-item>
        <el-form-item label="免费时长(分)"><el-input-number v-model="ruleForm.free_minutes" :min="0" /></el-form-item>
        <el-form-item label="每小时费率(元)"><el-input-number v-model="ruleForm.rate_per_hour" :precision="2" :step="1" /></el-form-item>
        <el-form-item label="日封顶(元)"><el-input-number v-model="ruleForm.daily_max" :precision="2" :step="10" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="ruleForm.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ruleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { cameraApi, billingApi, lotApi } from '@/api/parking'

const lots = ref<any[]>([])
const activeTab = ref('cameras')
const cameras = ref<any[]>([])
const camLotId = ref<number | null>(null)
const camDialogVisible = ref(false)
const camForm = ref<any>({ lot: null, name: '', stream_url: '', status: 'offline' })
const rules = ref<any[]>([])
const ruleFilter = ref({ lot_id: null as number | null })
const ruleDialogVisible = ref(false)
const ruleForm = ref<any>({ lot: null, vehicle_type: 'car', free_minutes: 15, rate_per_hour: 5, daily_max: 50, is_active: true })

async function loadCameras() {
  const p: any = {}; if (camLotId.value) p.lot_id = camLotId.value
  const res = await cameraApi.list(p); cameras.value = res.data.data || []
}
async function loadRules() {
  const p: any = {}; if (ruleFilter.value.lot_id) p.lot_id = ruleFilter.value.lot_id
  const res = await billingApi.list(p); rules.value = res.data.data || []
}
function openCamDialog(row?: any) {
  camForm.value = row ? { ...row } : { lot: camLotId.value, name: '', stream_url: '', status: 'offline' }
  camDialogVisible.value = true
}
async function saveCam() {
  try {
    if (camForm.value.id) await cameraApi.update(camForm.value.id, camForm.value)
    else await cameraApi.create(camForm.value)
    ElMessage.success('保存成功'); camDialogVisible.value = false; await loadCameras()
  } catch { ElMessage.error('保存失败') }
}
async function deleteCam(id: number) {
  await ElMessageBox.confirm('确认删除？', '警告', { type: 'warning' })
  try { await cameraApi.delete(id); ElMessage.success('删除成功'); await loadCameras() }
  catch { ElMessage.error('删除失败') }
}
function openRuleDialog(row?: any) {
  ruleForm.value = row ? { ...row } : { lot: ruleFilter.value.lot_id, vehicle_type: 'car', free_minutes: 15, rate_per_hour: 5, daily_max: 50, is_active: true }
  ruleDialogVisible.value = true
}
async function saveRule() {
  try {
    if (ruleForm.value.id) await billingApi.update(ruleForm.value.id, ruleForm.value)
    else await billingApi.create(ruleForm.value)
    ElMessage.success('保存成功'); ruleDialogVisible.value = false; await loadRules()
  } catch { ElMessage.error('保存失败') }
}
async function deleteRule(id: number) {
  await ElMessageBox.confirm('确认删除？', '警告', { type: 'warning' })
  try { await billingApi.delete(id); ElMessage.success('删除成功'); await loadRules() }
  catch { ElMessage.error('删除失败') }
}

onMounted(async () => {
  const res = await lotApi.list(); lots.value = res.data.data || []
  if (lots.value.length) { camLotId.value = lots.value[0].id; ruleFilter.value.lot_id = lots.value[0].id }
  await Promise.all([loadCameras(), loadRules()])
})
</script>

<style scoped>
.management-page { padding: 24px; }
.page-title { color: #f1f5f9; font-size: 20px; margin: 0 0 20px; }
.tab-actions { display: flex; gap: 10px; align-items: center; }
:deep(.el-tabs__header) { border-bottom: 1px solid #334155; }
:deep(.el-tabs__item) { color: #94a3b8; }
:deep(.el-tabs__item.is-active) { color: #4facfe; }
:deep(.el-tabs__active-bar) { background: #4facfe; }
:deep(.el-table) { --el-table-bg-color: #1e293b; --el-table-tr-bg-color: #1e293b; --el-table-row-hover-bg-color: #334155; --el-table-border-color: #334155; color: #cbd5e1; }
:deep(.el-table th) { background: #0f172a !important; color: #94a3b8; }
</style>
