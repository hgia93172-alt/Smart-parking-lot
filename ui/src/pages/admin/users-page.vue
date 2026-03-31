<script setup lang="ts">
import { onMounted, ref, computed } from "vue"
import { 
  UsersIcon, 
  MagnifyingGlassIcon, 
  ArrowPathIcon, 
  TrashIcon, 
  UserIcon as UserCheckIcon, 
  ShieldCheckIcon, 
  Cog6ToothIcon, 
  EnvelopeIcon,
  PlusIcon,
  PencilSquareIcon,
  CheckIcon
} from "@heroicons/vue/24/outline"
import type { AdminUserCreateRequest, AdminUserItem, AdminUserUpdateRequest } from "@/types/auth"
import { createAdminUser, deleteAdminUser, listAdminUsersPaged, patchAdminUser } from "@/api/auth"
import { useMessage, NTag, NPopconfirm, NAvatar, NModal, NForm, NFormItem, NInput, NSwitch, NButton, NPagination } from "naive-ui"
import gsap from "gsap"

const message = useMessage()
const rows = ref<AdminUserItem[]>([])
const isLoading = ref(false)
const searchQuery = ref("")
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const showCreate = ref(false)
const createForm = ref<AdminUserCreateRequest>({
  username: "",
  password: "",
  role: "user",
  is_active: true,
  is_staff: false,
  is_superuser: false,
})

const showEdit = ref(false)
const editUserId = ref<number | null>(null)
const editForm = ref<AdminUserUpdateRequest>({
  username: "",
  password: "",
  role: "",
  is_active: true,
  is_staff: false,
  is_superuser: false,
})

async function refresh() {
  isLoading.value = true
  try {
    const data = await listAdminUsersPaged(page.value, pageSize.value)
    rows.value = data.results
    total.value = data.count
  } catch {
    message.error("加载用户列表失败")
  } finally {
    isLoading.value = false
  }
}

function handlePageSizeUpdate() {
  page.value = 1
  refresh()
}

function openCreate() {
  createForm.value = {
    username: "",
    password: "",
    role: "user",
    is_active: true,
    is_staff: false,
    is_superuser: false,
  }
  showCreate.value = true
}

async function submitCreate() {
  try {
    if (!createForm.value.username || !createForm.value.password) {
      message.error("请输入用户名与初始密码")
      return
    }
    await createAdminUser(createForm.value)
    message.success("用户创建成功")
    showCreate.value = false
    page.value = 1
    await refresh()
  } catch {
    message.error("创建失败")
  }
}

function openEdit(row: AdminUserItem) {
  editUserId.value = row.id
  editForm.value = {
    username: row.username,
    password: "",
    role: row.role,
    is_active: row.is_active,
    is_staff: row.is_staff,
    is_superuser: row.is_superuser,
  }
  showEdit.value = true
}

async function submitEdit() {
  if (!editUserId.value) return
  try {
    const raw = { ...editForm.value }
    const payload: AdminUserUpdateRequest = {
      username: raw.username || undefined,
      role: raw.role || undefined,
      is_active: raw.is_active,
      is_staff: raw.is_staff,
      is_superuser: raw.is_superuser,
      password: raw.password ? raw.password : undefined,
    }
    await patchAdminUser(editUserId.value, payload)
    message.success("用户已更新")
    showEdit.value = false
    await refresh()
  } catch {
    message.error("更新失败")
  }
}

async function handleDelete(id: number) {
  try {
    await deleteAdminUser(id)
    message.success("用户已移除")
    await refresh()
  } catch {
    message.error("删除失败")
  }
}

const filteredRows = computed(() => {
  if (!searchQuery.value) return rows.value
  const q = searchQuery.value.toLowerCase()
  return rows.value.filter(r => 
    r.username.toLowerCase().includes(q) || 
    r.role?.toLowerCase().includes(q) ||
    r.id.toString().includes(q)
  )
})

onMounted(() => {
  refresh()
  gsap.from(".page-header", { opacity: 0, y: -20, duration: 0.5, ease: "power2.out" })
})
</script>

<template>
  <div class="max-w-7xl mx-auto pb-12 min-h-[calc(100vh-64px-64px)] flex flex-col gap-8">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 page-header">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 tracking-tight flex items-center gap-3">
          <UsersIcon class="w-7 h-7 text-brand" />
          用户与权限管理
        </h1>
        <p class="mt-1 text-gray-500 font-medium">管理系统成员、分配业务角色以及审计访问权限</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="relative">
          <MagnifyingGlassIcon class="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input 
            v-model="searchQuery"
            type="text" 
            placeholder="搜索用户名或角色..." 
            class="pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-figma text-sm w-64 focus:border-brand/30 outline-none transition-all shadow-sm"
          />
        </div>
        <button 
          @click="refresh"
          :class="['p-2 rounded-figma border border-gray-200 bg-white text-gray-500 hover:text-brand hover:border-brand/20 transition-all shadow-sm', isLoading && 'animate-spin text-brand']"
        >
          <ArrowPathIcon class="w-5 h-5" />
        </button>
        <button
          @click="openCreate"
          class="flex items-center gap-2 px-4 py-2 bg-brand text-white rounded-figma font-bold text-sm hover:bg-gray-900 active:scale-95 transition-all shadow-figma"
        >
          <PlusIcon class="w-5 h-5" />
          新建用户
        </button>
      </div>
    </div>

    <!-- Quick Stats Summary -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white p-6 rounded-figma-lg border border-gray-100 shadow-figma flex items-center gap-4">
        <div class="w-12 h-12 bg-brand/5 rounded-figma flex items-center justify-center text-brand">
          <UserCheckIcon class="w-6 h-6" />
        </div>
        <div>
          <p class="text-2xl font-bold text-gray-900 leading-none">{{ total }}</p>
          <p class="text-xs text-gray-400 font-bold uppercase tracking-widest mt-1">注册总数</p>
        </div>
      </div>
      <div class="bg-white p-6 rounded-figma-lg border border-gray-100 shadow-figma flex items-center gap-4">
        <div class="w-12 h-12 bg-purple-50 rounded-figma flex items-center justify-center text-purple-600">
          <ShieldCheckIcon class="w-6 h-6" />
        </div>
        <div>
          <p class="text-2xl font-bold text-gray-900 leading-none">{{ rows.filter(r => r.is_superuser).length }}</p>
          <p class="text-xs text-gray-400 font-bold uppercase tracking-widest mt-1">本页超级管理员</p>
        </div>
      </div>
      <div class="bg-white p-6 rounded-figma-lg border border-gray-100 shadow-figma flex items-center gap-4">
        <div class="w-12 h-12 bg-emerald-50 rounded-figma flex items-center justify-center text-emerald-600">
          <Cog6ToothIcon class="w-6 h-6" />
        </div>
        <div>
          <p class="text-2xl font-bold text-gray-900 leading-none">{{ rows.filter(r => r.is_staff).length }}</p>
          <p class="text-xs text-gray-400 font-bold uppercase tracking-widest mt-1">本页工作人员</p>
        </div>
      </div>
    </div>

    <!-- Users List -->
    <div class="bg-white rounded-figma-lg shadow-figma border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50/50 border-b border-gray-100">
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">用户 ID</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">基本信息</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">业务角色</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest text-center">系统标识</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest text-center">启用</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr 
              v-for="(row, idx) in filteredRows" 
              :key="row.id"
              class="hover:bg-gray-50/30 transition-colors group"
            >
              <td class="px-6 py-4 text-xs font-mono text-gray-400">#{{ row.id }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <n-avatar 
                    round 
                    :size="40" 
                    class="ring-2 ring-transparent group-hover:ring-brand/10 transition-all shadow-sm bg-brand text-white font-bold"
                  >
                    {{ row.username.charAt(0).toUpperCase() }}
                  </n-avatar>
                  <div class="flex flex-col">
                    <span class="text-sm font-bold text-gray-900">{{ row.username }}</span>
                    <div class="flex items-center gap-1 text-[10px] text-gray-400">
                      <EnvelopeIcon class="w-3 h-3" />
                      <span>无邮箱记录</span>
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="text-xs font-bold text-gray-700">{{ row.role || "未分配" }}</span>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center justify-center gap-2">
                  <n-tag v-if="row.is_superuser" size="small" :bordered="false" class="!bg-purple-50 !text-purple-600 !text-[10px] font-bold uppercase">Super</n-tag>
                  <n-tag v-if="row.is_staff" size="small" :bordered="false" class="!bg-emerald-50 !text-emerald-600 !text-[10px] font-bold uppercase">Staff</n-tag>
                  <n-tag v-if="!row.is_staff && !row.is_superuser" size="small" :bordered="false" class="!bg-gray-100 !text-gray-400 !text-[10px] font-bold uppercase">User</n-tag>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="flex justify-center">
                  <n-tag v-if="row.is_active" size="small" :bordered="false" class="!bg-emerald-50 !text-emerald-600 !text-[10px] font-bold uppercase">On</n-tag>
                  <n-tag v-else size="small" :bordered="false" class="!bg-red-50 !text-red-600 !text-[10px] font-bold uppercase">Off</n-tag>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center justify-end gap-2">
                  <button 
                    @click="openEdit(row)"
                    class="p-2 text-brand hover:bg-brand/5 rounded-figma transition-all"
                    title="编辑用户"
                  >
                    <PencilSquareIcon class="w-5 h-5" />
                  </button>
                  <n-popconfirm @positive-click="handleDelete(row.id)">
                    <template #trigger>
                      <button class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-figma transition-all">
                        <TrashIcon class="w-5 h-5" />
                      </button>
                    </template>
                    确认永久注销并删除该用户及其所有关联数据吗？
                  </n-popconfirm>
                </div>
              </td>
            </tr>
            <tr v-if="filteredRows.length === 0 && !isLoading">
              <td colspan="6" class="px-6 py-20 text-center text-gray-400 font-medium italic">
                没有找到匹配的用户
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="mt-auto flex justify-end">
      <n-pagination
        v-model:page="page"
        v-model:page-size="pageSize"
        :item-count="total"
        :page-sizes="[10, 20, 50]"
        show-size-picker
        @update:page="refresh"
        @update:page-size="handlePageSizeUpdate"
      />
    </div>

    <n-modal v-model:show="showCreate" preset="card" title="新建用户" class="w-[520px]">
      <n-form :model="createForm" label-placement="left" label-width="90">
        <n-form-item label="用户名">
          <n-input v-model:value="createForm.username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="初始密码">
          <n-input v-model:value="createForm.password" type="password" placeholder="请输入初始密码" />
        </n-form-item>
        <n-form-item label="业务角色">
          <n-input v-model:value="createForm.role" placeholder="例如：user / ops / admin" />
        </n-form-item>
        <n-form-item label="启用">
          <n-switch v-model:value="createForm.is_active" />
        </n-form-item>
        <n-form-item label="工作人员">
          <n-switch v-model:value="createForm.is_staff" />
        </n-form-item>
        <n-form-item label="超级管理员">
          <n-switch v-model:value="createForm.is_superuser" />
        </n-form-item>
        <div class="flex justify-end gap-2 pt-2">
          <n-button @click="showCreate = false">取消</n-button>
          <n-button type="primary" @click="submitCreate">创建</n-button>
        </div>
      </n-form>
    </n-modal>

    <n-modal v-model:show="showEdit" preset="card" title="编辑用户" class="w-[520px]">
      <n-form :model="editForm" label-placement="left" label-width="90">
        <n-form-item label="用户名">
          <n-input v-model:value="editForm.username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="新密码">
          <n-input v-model:value="editForm.password" type="password" placeholder="留空则不修改" />
        </n-form-item>
        <n-form-item label="业务角色">
          <n-input v-model:value="editForm.role" placeholder="例如：user / ops / admin" />
        </n-form-item>
        <n-form-item label="启用">
          <n-switch v-model:value="editForm.is_active" />
        </n-form-item>
        <n-form-item label="工作人员">
          <n-switch v-model:value="editForm.is_staff" />
        </n-form-item>
        <n-form-item label="超级管理员">
          <n-switch v-model:value="editForm.is_superuser" />
        </n-form-item>
        <div class="flex justify-end gap-2 pt-2">
          <n-button @click="showEdit = false">取消</n-button>
          <n-button type="primary" @click="submitEdit">
            <template #icon><CheckIcon class="w-4 h-4" /></template>
            保存
          </n-button>
        </div>
      </n-form>
    </n-modal>
  </div>
</template>

<style scoped>
:deep(.n-tag) {
  border-radius: 4px !important;
}
</style>

