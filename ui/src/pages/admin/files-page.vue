<script setup lang="ts">
import { onMounted, ref, computed } from "vue"
import { 
  DocumentTextIcon, 
  MagnifyingGlassIcon, 
  ArrowPathIcon, 
  TrashIcon, 
  ServerIcon, 
  ClockIcon, 
  DocumentIcon,
  FunnelIcon,
  ArrowDownTrayIcon,
  ArrowTopRightOnSquareIcon
} from "@heroicons/vue/24/outline"
import type { UserFileItem } from "@/types/utils"
import { deleteAdminFile, downloadUserFile, listAdminFilesPaged } from "@/api/utils"
import { useMessage, NTag, NPopconfirm, NAvatar, NScrollbar, NTooltip, NPagination } from "naive-ui"
import gsap from "gsap"

const message = useMessage()
const rows = ref<UserFileItem[]>([])
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
    const data = await listAdminFilesPaged(page.value, pageSize.value)
    rows.value = data.results
    total.value = data.count
  } catch {
    message.error("加载系统文件列表失败")
  } finally {
    isLoading.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await deleteAdminFile(id)
    message.success("文件已从服务器物理删除")
    await refresh()
  } catch {
    message.error("删除失败")
  }
}

async function handleDownload(row: UserFileItem) {
  try {
    const { blob, filename } = await downloadUserFile(row.id)
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = filename || row.original_name || "download"
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
    message.success("已开始下载")
  } catch {
    message.error("下载失败")
  }
}

const filteredRows = computed(() => {
  if (!searchQuery.value) return rows.value
  const q = searchQuery.value.toLowerCase()
  return rows.value.filter(r => 
    r.original_name.toLowerCase().includes(q) || 
    r.id.toString().includes(q)
  )
})

function formatSize(bytes: number) {
  if (!bytes) return "0 B"
  const k = 1024
  const sizes = ["B", "KB", "MB", "GB"]
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
}

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
          <ServerIcon class="w-7 h-7 text-brand" />
          全站文件管理
        </h1>
        <p class="mt-1 text-gray-500 font-medium">物理文件存储审计，支持全局文件的查看与清理</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="relative">
          <MagnifyingGlassIcon class="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input 
            v-model="searchQuery"
            type="text" 
            placeholder="搜索文件名称..." 
            class="pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-figma text-sm w-64 focus:border-brand/30 outline-none transition-all shadow-sm"
          />
        </div>
        <button 
          @click="refresh"
          :class="['p-2 rounded-figma border border-gray-200 bg-white text-gray-500 hover:text-brand hover:border-brand/20 transition-all shadow-sm', isLoading && 'animate-spin text-brand']"
        >
          <ArrowPathIcon class="w-5 h-5" />
        </button>
      </div>
    </div>

    <!-- Storage Stats -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="bg-gray-900 rounded-figma-lg p-6 text-white shadow-2xl flex items-center justify-between overflow-hidden relative">
        <div class="relative z-10">
          <p class="text-xs font-bold text-white/40 uppercase tracking-widest mb-1">本页已用存储空间</p>
          <h2 class="text-3xl font-bold">{{ formatSize(rows.reduce((acc, r) => acc + (r.size || 0), 0)) }}</h2>
        </div>
        <div class="w-16 h-16 bg-white/10 rounded-full flex items-center justify-center relative z-10">
          <ServerIcon class="w-8 h-8 text-white/80" />
        </div>
        <div class="absolute -right-4 -bottom-4 w-32 h-32 bg-brand rounded-full blur-3xl opacity-20"></div>
      </div>
      <div class="bg-white rounded-figma-lg p-6 border border-gray-100 shadow-figma flex items-center justify-between">
        <div>
          <p class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">文件对象总数</p>
          <h2 class="text-3xl font-bold text-gray-900">{{ total }} <span class="text-sm font-medium text-gray-400 ml-1">Objects</span></h2>
        </div>
        <div class="w-16 h-16 bg-brand/5 rounded-full flex items-center justify-center">
          <DocumentTextIcon class="w-8 h-8 text-brand" />
        </div>
      </div>
    </div>

    <!-- Files Table -->
    <div class="bg-white rounded-figma-lg shadow-figma border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-100">
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">ID / 存储 Key</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">文件信息</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">物理容量</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">上传时间</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest text-right">管理</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr 
              v-for="(row, idx) in filteredRows" 
              :key="row.id"
              v-motion
              :initial="{ opacity: 0, x: -10 }"
              :enter="{ opacity: 1, x: 0, transition: { delay: idx * 20 } }"
              class="hover:bg-gray-50/30 transition-colors group"
            >
              <td class="px-6 py-4 text-xs font-mono text-gray-400">#{{ row.id }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 bg-gray-100 rounded-figma flex items-center justify-center text-gray-500 group-hover:bg-brand/10 group-hover:text-brand transition-all">
                    <DocumentIcon class="w-5 h-5" />
                  </div>
                  <div class="flex flex-col">
                    <span class="text-sm font-bold text-gray-900 truncate max-w-[300px]">{{ row.original_name }}</span>
                    <span class="text-[10px] text-gray-400 font-medium">Type: {{ row.original_name.split('.').pop()?.toUpperCase() }}</span>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <n-tag size="small" :bordered="false" class="!bg-gray-100 !text-gray-600 !text-[10px] font-bold">
                  {{ formatSize(row.size) }}
                </n-tag>
              </td>
              <td class="px-6 py-4 text-xs text-gray-500 font-medium">{{ row.created_at }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center justify-end gap-2">
                  <button
                    @click="handleDownload(row)"
                    class="p-2 text-gray-400 hover:text-brand hover:bg-brand/5 rounded-figma transition-all"
                    title="下载到本地"
                  >
                    <ArrowDownTrayIcon class="w-5 h-5" />
                  </button>
                  <n-popconfirm @positive-click="handleDelete(row.id)">
                    <template #trigger>
                      <button class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-figma transition-all">
                        <TrashIcon class="w-5 h-5" />
                      </button>
                    </template>
                    确认从物理存储中永久删除此文件吗？此操作无法恢复！
                  </n-popconfirm>
                </div>
              </td>
            </tr>
            <tr v-if="filteredRows.length === 0 && !isLoading">
              <td colspan="5" class="px-6 py-20 text-center text-gray-400 font-medium italic">
                存储库中没有发现任何文件对象
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

