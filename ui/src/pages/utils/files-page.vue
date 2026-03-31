<script setup lang="ts">
import { onMounted, ref, computed } from "vue"
import { 
  FolderIcon, 
  MagnifyingGlassIcon, 
  ArrowPathIcon, 
  ArrowUpTrayIcon, 
  ArrowDownTrayIcon, 
  TrashIcon, 
  DocumentTextIcon, 
  DocumentIcon,
  ServerIcon,
  ClockIcon,
  EllipsisVerticalIcon,
  PlusIcon
} from "@heroicons/vue/24/outline"
import type { UserFileItem } from "@/types/utils"
import { deleteUserFile, downloadUserFile, listUserFilesPaged, uploadUserFile } from "@/api/utils"
import { useMessage, NTag, NPopconfirm, NAvatar, NScrollbar, NTooltip, NUpload, NPagination } from "naive-ui"
import gsap from "gsap"

const message = useMessage()
const rows = ref<UserFileItem[]>([])
const isLoading = ref(false)
const searchQuery = ref("")
const isUploading = ref(false)
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
    const data = await listUserFilesPaged(page.value, pageSize.value)
    rows.value = data.results
    total.value = data.count
  } catch {
    message.error("获取文件列表失败")
  } finally {
    isLoading.value = false
  }
}

async function handleUpload(data: { fileList: any }) {
  const file = data.fileList[0]?.file
  if (!file) return
  
  isUploading.value = true
  try {
    await uploadUserFile(file)
    message.success("文件上传成功")
    page.value = 1
    await refresh()
  } catch {
    message.error("上传失败")
  } finally {
    isUploading.value = false
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

async function handleDelete(id: number) {
  try {
    await deleteUserFile(id)
    message.success("文件已删除")
    await refresh()
  } catch {
    message.error("删除失败")
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
  <div class="max-w-6xl mx-auto pb-12 min-h-[calc(100vh-64px-64px)] flex flex-col gap-8">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 page-header">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 tracking-tight flex items-center gap-3">
          <FolderIcon class="w-7 h-7 text-brand" />
          我的私有文件
        </h1>
        <p class="mt-1 text-gray-500 font-medium">存放您的个人文档，支持随时上传、预览与下载</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="relative">
          <MagnifyingGlassIcon class="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input 
            v-model="searchQuery"
            type="text" 
            placeholder="搜索我的文件..." 
            class="pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-figma text-sm w-64 focus:border-brand/30 outline-none transition-all shadow-sm"
          />
        </div>
        <button 
          @click="refresh"
          :class="['p-2 rounded-figma border border-gray-200 bg-white text-gray-500 hover:text-brand hover:border-brand/20 transition-all shadow-sm', isLoading && 'animate-spin text-brand']"
        >
          <ArrowPathIcon class="w-5 h-5" />
        </button>
        <n-upload
          multiple
          :show-file-list="false"
          @change="handleUpload"
        >
          <button 
            class="flex items-center gap-2 px-4 py-2 bg-brand text-white rounded-figma font-bold text-sm hover:bg-gray-900 active:scale-95 transition-all shadow-figma"
          >
            <ArrowUpTrayIcon class="w-5 h-5" />
            上传文件
          </button>
        </n-upload>
      </div>
    </div>

    <!-- Storage Summary Banner -->
    <div class="bg-gray-50 border border-gray-100 rounded-figma-lg p-6 flex items-center justify-between relative overflow-hidden">
      <div class="flex items-center gap-6 relative z-10">
        <div class="w-14 h-14 bg-white rounded-figma flex items-center justify-center text-brand shadow-sm border border-gray-100">
          <ServerIcon class="w-7 h-7" />
        </div>
        <div>
          <p class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">本页占用空间</p>
          <div class="flex items-end gap-2">
            <h2 class="text-3xl font-bold text-gray-900 leading-none">{{ formatSize(rows.reduce((acc, r) => acc + (r.size || 0), 0)) }}</h2>
            <span class="text-xs font-bold text-gray-400 mb-1">/ 不受限制</span>
          </div>
        </div>
      </div>
      <div class="hidden md:flex flex-col items-end gap-1 relative z-10">
        <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">文件存放在安全加密区域</p>
        <div class="flex gap-1">
          <div v-for="i in 5" :key="i" class="w-8 h-1 rounded-full bg-brand/10"></div>
        </div>
      </div>
      <div class="absolute -right-8 -bottom-8 w-40 h-40 bg-brand/5 rounded-full blur-3xl"></div>
    </div>

    <!-- Files Table -->
    <div class="bg-white rounded-figma-lg shadow-figma border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50/50 border-b border-gray-100">
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">ID</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">文件名称</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">容量</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest text-center">类型</th>
              <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest text-right">管理操作</th>
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
                    <span class="text-sm font-bold text-gray-900 truncate max-w-[340px]">{{ row.original_name }}</span>
                    <div class="flex items-center gap-2 mt-0.5">
                      <ClockIcon class="w-3 h-3 text-gray-300" />
                      <span class="text-[10px] text-gray-400 font-medium">{{ row.created_at }}</span>
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="text-xs font-bold text-gray-600">{{ formatSize(row.size) }}</span>
              </td>
              <td class="px-6 py-4">
                <div class="flex justify-center">
                  <n-tag size="small" :bordered="false" class="!bg-gray-100 !text-gray-500 !text-[10px] font-bold uppercase">
                    {{ row.original_name.split('.').pop() }}
                  </n-tag>
                </div>
              </td>
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
                    确定从服务器删除该个人文件吗？
                  </n-popconfirm>
                </div>
              </td>
            </tr>
            <tr v-if="filteredRows.length === 0 && !isLoading">
              <td colspan="5" class="px-6 py-20 text-center">
                <div class="flex flex-col items-center justify-center space-y-4 opacity-40">
                  <FolderIcon class="w-12 h-12" />
                  <p class="text-sm font-bold">空空如也，快去上传您的第一个文档吧</p>
                </div>
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
:deep(.n-upload-trigger) {
  display: block;
}
</style>
