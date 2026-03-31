<script setup lang="ts">
import { onMounted, ref, computed } from "vue"
import {
  ClipboardDocumentListIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
} from "@heroicons/vue/24/outline"
import type { OperationLogItem } from "@/types/utils"
import { clearAdminLogs, deleteAdminLog, listAdminLogsPaged } from "@/api/utils"
import { useMessage, NTag, NPopconfirm, NPagination } from "naive-ui"
import gsap from "gsap"

const message = useMessage()
const rows = ref<OperationLogItem[]>([])
const isLoading = ref(false)
const searchQuery = ref("")
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

function handlePageSizeUpdate() {
  page.value = 1
  refresh()
}

async function refresh() {
  isLoading.value = true
  try {
    const data = await listAdminLogsPaged(page.value, pageSize.value)
    rows.value = data.results
    total.value = data.count
  } catch {
    message.error("加载日志列表失败")
  } finally {
    isLoading.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await deleteAdminLog(id)
    message.success("日志已删除")
    await refresh()
  } catch {
    message.error("删除失败")
  }
}

async function handleClear() {
  try {
    await clearAdminLogs()
    message.success("日志已清空")
    page.value = 1
    await refresh()
  } catch {
    message.error("清空失败")
  }
}

const filteredRows = computed(() => {
  if (!searchQuery.value) return rows.value
  const q = searchQuery.value.toLowerCase()
  return rows.value.filter(r =>
    (r.operator_username || "").toLowerCase().includes(q) ||
    (r.action || "").toLowerCase().includes(q) ||
    (r.remark || "").toLowerCase().includes(q) ||
    (r.path || "").toLowerCase().includes(q) ||
    (r.method || "").toLowerCase().includes(q) ||
    String(r.id).includes(q)
  )
})

onMounted(() => {
  refresh()
  gsap.from(".page-header", { opacity: 0, y: -20, duration: 0.5, ease: "power2.out" })
})
</script>

<template>
  <div class="max-w-7xl mx-auto pb-12 min-h-[calc(100vh-64px-64px)] flex flex-col gap-8">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 page-header">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 tracking-tight flex items-center gap-3">
          <ClipboardDocumentListIcon class="w-7 h-7 text-brand" />
          操作日志
        </h1>
        <p class="mt-1 text-gray-500 font-medium">审计后台关键操作，支持分页浏览与清理</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="relative">
          <MagnifyingGlassIcon class="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索用户/路径/动作..."
            class="pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-figma text-sm w-64 focus:border-brand/30 outline-none transition-all shadow-sm"
          />
        </div>
        <button
          @click="refresh"
          :class="['p-2 rounded-figma border border-gray-200 bg-white text-gray-500 hover:text-brand hover:border-brand/20 transition-all shadow-sm', isLoading && 'animate-spin text-brand']"
        >
          <ArrowPathIcon class="w-5 h-5" />
        </button>
        <n-popconfirm @positive-click="handleClear">
          <template #trigger>
            <button
              class="px-4 py-2 rounded-figma border border-gray-200 bg-white text-gray-600 hover:text-red-600 hover:border-red-200 hover:bg-red-50 transition-all shadow-sm text-sm font-bold"
            >
              清空全部
            </button>
          </template>
          确认清空所有日志吗？此操作不可恢复。
        </n-popconfirm>
      </div>
    </div>

    <div class="bg-white rounded-figma-lg shadow-figma border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50/50 border-b border-gray-100">
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">ID</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">操作者</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">动作</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">请求</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest text-center">结果</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">时间</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr
              v-for="row in filteredRows"
              :key="row.id"
              class="hover:bg-gray-50/30 transition-colors group"
            >
              <td class="px-6 py-4 text-xs font-mono text-gray-400">#{{ row.id }}</td>
              <td class="px-6 py-4">
                <span class="text-xs font-bold text-gray-800">{{ row.operator_username || "匿名" }}</span>
                <div class="text-[10px] text-gray-400 font-medium">{{ row.ip || "-" }}</div>
              </td>
              <td class="px-6 py-4">
                <div class="flex flex-col">
                  <span class="text-xs font-bold text-gray-900">{{ row.action || "-" }}</span>
                  <span class="text-[10px] text-gray-400 font-medium truncate max-w-[320px]">{{ row.remark || "" }}</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                  <n-tag size="small" :bordered="false" class="!bg-gray-100 !text-gray-700 !text-[10px] font-bold uppercase">
                    {{ row.method || "-" }}
                  </n-tag>
                  <span class="text-xs text-gray-600 font-medium truncate max-w-[380px]">{{ row.path }}</span>
                </div>
                <div class="text-[10px] text-gray-400 font-medium">
                  http={{ row.status_code ?? "-" }} / code={{ row.response_code ?? "-" }}
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="flex justify-center">
                  <n-tag v-if="row.success" size="small" :bordered="false" class="!bg-emerald-50 !text-emerald-600 !text-[10px] font-bold uppercase">
                    <span class="inline-flex items-center gap-1">
                      <CheckCircleIcon class="w-4 h-4" /> OK
                    </span>
                  </n-tag>
                  <n-tag v-else size="small" :bordered="false" class="!bg-red-50 !text-red-600 !text-[10px] font-bold uppercase">
                    <span class="inline-flex items-center gap-1">
                      <XCircleIcon class="w-4 h-4" /> FAIL
                    </span>
                  </n-tag>
                </div>
              </td>
              <td class="px-6 py-4 text-xs text-gray-500 font-medium">{{ row.created_at }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center justify-end gap-2">
                  <n-popconfirm @positive-click="handleDelete(row.id)">
                    <template #trigger>
                      <button class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-figma transition-all">
                        <TrashIcon class="w-5 h-5" />
                      </button>
                    </template>
                    确认删除该条日志吗？
                  </n-popconfirm>
                </div>
              </td>
            </tr>
            <tr v-if="filteredRows.length === 0 && !isLoading">
              <td colspan="7" class="px-6 py-20 text-center text-gray-400 font-medium italic">
                暂无日志
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
  </div>
</template>

<style scoped>
:deep(.n-tag) {
  border-radius: 4px !important;
}
</style>
