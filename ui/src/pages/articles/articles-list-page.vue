<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import { NewspaperIcon, MagnifyingGlassIcon, ArrowPathIcon } from "@heroicons/vue/24/outline"
import { useMessage, NPagination, NSelect, NButton } from "naive-ui"
import type { ArticleCategoryItem, ArticleItem } from "@/types/utils"
import { listPublicArticleCategories, listPublicArticlesPaged } from "@/api/utils"

const router = useRouter()
const message = useMessage()

const rows = ref<ArticleItem[]>([])
const isLoading = ref(false)
const keyword = ref("")
const categoryId = ref<number>(0)
const categories = ref<ArticleCategoryItem[]>([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

async function refresh() {
  isLoading.value = true
  try {
    const data = await listPublicArticlesPaged(page.value, pageSize.value, {
      keyword: keyword.value || undefined,
      category_id: categoryId.value ? categoryId.value : null,
    })
    rows.value = data.results
    total.value = data.count
  } catch {
    message.error("加载文章失败")
  } finally {
    isLoading.value = false
  }
}

async function refreshCategories() {
  try {
    categories.value = await listPublicArticleCategories()
  } catch {
    message.error("加载分类失败")
  }
}

function handlePageSizeUpdate() {
  page.value = 1
  refresh()
}

function openDetail(id: number) {
  router.push({ name: "article-detail", params: { id: String(id) } })
}

onMounted(() => {
  refreshCategories()
  refresh()
})

const categoryOptions = computed(() => [
  { label: "全部分类", value: 0 },
  ...categories.value.map(c => ({ label: c.name, value: c.id })),
])
</script>

<template>
  <div class="max-w-7xl mx-auto pb-12 min-h-[calc(100vh-64px-64px)] flex flex-col gap-8">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 tracking-tight flex items-center gap-3">
          <NewspaperIcon class="w-7 h-7 text-brand" />
          文章
        </h1>
        <p class="mt-1 text-gray-500 font-medium">查看已发布内容，支持评论、点赞与收藏</p>
      </div>
      <div class="flex flex-col md:flex-row md:items-center gap-3">
        <div class="relative">
          <MagnifyingGlassIcon class="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            v-model="keyword"
            type="text"
            placeholder="搜索标题..."
            class="pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-figma text-sm w-64 focus:border-brand/30 outline-none transition-all shadow-sm"
            @keyup.enter="page = 1; refresh()"
          />
        </div>
        <n-select v-model:value="categoryId" class="w-48" :options="categoryOptions" />
        <n-button size="small" @click="page = 1; refresh()">筛选</n-button>
        <button
          @click="refresh"
          :class="['p-2 rounded-figma border border-gray-200 bg-white text-gray-500 hover:text-brand hover:border-brand/20 transition-all shadow-sm', isLoading && 'animate-spin text-brand']"
        >
          <ArrowPathIcon class="w-5 h-5" />
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <button
        v-for="row in rows"
        :key="row.id"
        class="text-left bg-white rounded-figma-lg border border-gray-100 shadow-figma hover:shadow-lg transition-all overflow-hidden group"
        @click="openDetail(row.id)"
      >
        <div v-if="row.cover_url" class="h-40 w-full bg-gray-100 overflow-hidden">
          <img :src="row.cover_url" class="h-full w-full object-cover group-hover:scale-[1.02] transition-transform" />
        </div>
        <div class="p-5 space-y-3">
          <div class="flex items-start justify-between gap-3">
            <h3 class="text-base font-bold text-gray-900 leading-snug truncate">{{ row.title }}</h3>
            <span class="text-[10px] text-gray-400 font-mono shrink-0">#{{ row.id }}</span>
          </div>
          <p class="text-xs text-gray-500 font-medium truncate">{{ row.summary || "—" }}</p>
          <div class="flex items-center justify-between text-[11px] text-gray-500">
            <span class="font-medium">{{ row.category_name || "未分类" }}</span>
            <span class="font-mono">浏览 {{ row.view_count }}</span>
          </div>
          <div class="flex items-center gap-4 text-[11px] text-gray-500 font-medium">
            <span>赞 {{ row.like_count }}</span>
            <span>藏 {{ row.favorite_count }}</span>
            <span>评 {{ row.comment_count }}</span>
          </div>
        </div>
      </button>
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
