<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import {
  NewspaperIcon,
  PlusIcon,
  PencilSquareIcon,
  TrashIcon,
  ArrowPathIcon,
  MagnifyingGlassIcon,
} from "@heroicons/vue/24/outline"
import {
  useMessage,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NButton,
  NPopconfirm,
  NPagination,
  NTabs,
  NTabPane,
  NSelect,
  NSwitch,
  NUpload,
} from "naive-ui"
import type { ArticleCategoryItem, ArticleItem, ArticleStatus } from "@/types/utils"
import {
  createAdminArticle,
  createAdminArticleCategory,
  deleteAdminArticle,
  deleteAdminArticleCategory,
  listAdminArticleCategoriesPaged,
  listAdminArticlesPaged,
  patchAdminArticle,
  patchAdminArticleCategory,
} from "@/api/utils"

const message = useMessage()

const activeTab = ref<"categories" | "articles">("articles")

const catRows = ref<ArticleCategoryItem[]>([])
const catKeyword = ref("")
const catPage = ref(1)
const catPageSize = ref(10)
const catTotal = ref(0)
const catLoading = ref(false)

const showCatModal = ref(false)
const catEditingId = ref<number | null>(null)
const catForm = ref<Partial<ArticleCategoryItem>>({
  name: "",
  description: "",
  sort_order: 0,
  is_active: true,
})

async function refreshCategories() {
  catLoading.value = true
  try {
    const data = await listAdminArticleCategoriesPaged(catPage.value, catPageSize.value, catKeyword.value || undefined)
    catRows.value = data.results
    catTotal.value = data.count
  } catch {
    message.error("加载分类失败")
  } finally {
    catLoading.value = false
  }
}

function openCreateCategory() {
  catEditingId.value = null
  catForm.value = { name: "", description: "", sort_order: 0, is_active: true }
  showCatModal.value = true
}

function openEditCategory(row: ArticleCategoryItem) {
  catEditingId.value = row.id
  catForm.value = {
    name: row.name,
    description: row.description,
    sort_order: row.sort_order,
    is_active: row.is_active,
  }
  showCatModal.value = true
}

async function submitCategory() {
  try {
    if (!catForm.value.name) {
      message.error("请输入分类名称")
      return
    }
    if (!catEditingId.value) {
      await createAdminArticleCategory(catForm.value)
      message.success("分类已创建")
    } else {
      await patchAdminArticleCategory(catEditingId.value, catForm.value)
      message.success("分类已更新")
    }
    showCatModal.value = false
    catPage.value = 1
    await refreshCategories()
  } catch {
    message.error("保存失败")
  }
}

async function handleDeleteCategory(id: number) {
  try {
    await deleteAdminArticleCategory(id)
    message.success("分类已删除")
    await refreshCategories()
  } catch {
    message.error("删除失败")
  }
}

const articleRows = ref<ArticleItem[]>([])
const articleKeyword = ref("")
const articleStatus = ref<ArticleStatus | "">("")
const articleCategoryId = ref<number>(0)
const articlePage = ref(1)
const articlePageSize = ref(10)
const articleTotal = ref(0)
const articleLoading = ref(false)

const showArticleModal = ref(false)
const articleEditingId = ref<number | null>(null)
const articleCoverFile = ref<File | null>(null)
const articleCurrentCoverUrl = ref<string>("")
const articleCoverPreviewUrl = ref<string>("")
const articleForm = ref<{
  title: string
  summary: string
  content: string
  status: ArticleStatus
  category_id: number
}>({
  title: "",
  summary: "",
  content: "",
  status: "draft",
  category_id: 0,
})

function setCoverFile(file: File | null) {
  if (articleCoverPreviewUrl.value) URL.revokeObjectURL(articleCoverPreviewUrl.value)
  articleCoverFile.value = file
  articleCoverPreviewUrl.value = file ? URL.createObjectURL(file) : ""
}

const categoryFilterOptions = computed(() => [
  { label: "全部分类", value: 0 },
  ...catRows.value.map(c => ({ label: c.name, value: c.id })),
])

const categoryEditOptions = computed(() => [
  { label: "未分类", value: 0 },
  ...catRows.value.map(c => ({ label: c.name, value: c.id })),
])

const statusOptions = [
  { label: "全部", value: "" },
  { label: "草稿", value: "draft" },
  { label: "已发布", value: "published" },
  { label: "已归档", value: "archived" },
]

async function refreshArticles() {
  articleLoading.value = true
  try {
    const data = await listAdminArticlesPaged(articlePage.value, articlePageSize.value, {
      keyword: articleKeyword.value || undefined,
      category_id: articleCategoryId.value ? articleCategoryId.value : null,
      status: articleStatus.value,
    })
    articleRows.value = data.results
    articleTotal.value = data.count
  } catch {
    message.error("加载文章失败")
  } finally {
    articleLoading.value = false
  }
}

function openCreateArticle() {
  articleEditingId.value = null
  setCoverFile(null)
  articleCurrentCoverUrl.value = ""
  articleForm.value = { title: "", summary: "", content: "", status: "draft", category_id: 0 }
  showArticleModal.value = true
}

function openEditArticle(row: ArticleItem) {
  articleEditingId.value = row.id
  setCoverFile(null)
  articleCurrentCoverUrl.value = row.cover_url || ""
  articleForm.value = {
    title: row.title,
    summary: row.summary || "",
    content: row.content || "",
    status: (row.status || "draft") as ArticleStatus,
    category_id: row.category_id ?? 0,
  }
  showArticleModal.value = true
}

function handleCoverChange(data: { fileList: any[] }) {
  const file = data.fileList[0]?.file || null
  setCoverFile(file)
}

async function submitArticle() {
  try {
    if (!articleForm.value.title) {
      message.error("请输入文章标题")
      return
    }
    if (!articleEditingId.value) {
      await createAdminArticle({
        ...articleForm.value,
        category_id: articleForm.value.category_id ? articleForm.value.category_id : null,
        cover: articleCoverFile.value,
      })
      message.success("文章已创建")
      showArticleModal.value = false
      articlePage.value = 1
      await refreshArticles()
      return
    }
    await patchAdminArticle(articleEditingId.value, {
      ...articleForm.value,
      category_id: articleForm.value.category_id ? articleForm.value.category_id : null,
      cover: articleCoverFile.value ?? undefined,
    })
    message.success("文章已更新")
    showArticleModal.value = false
    await refreshArticles()
  } catch {
    message.error("保存失败")
  }
}

async function handleDeleteArticle(id: number) {
  try {
    await deleteAdminArticle(id)
    message.success("文章已删除")
    await refreshArticles()
  } catch {
    message.error("删除失败")
  }
}

function handleCatPageSizeUpdate() {
  catPage.value = 1
  refreshCategories()
}

function handleArticlePageSizeUpdate() {
  articlePage.value = 1
  refreshArticles()
}

onMounted(async () => {
  await refreshCategories()
  await refreshArticles()
})
</script>

<template>
  <div class="max-w-7xl mx-auto pb-12 min-h-[calc(100vh-64px-64px)] flex flex-col gap-8">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 tracking-tight flex items-center gap-3">
          <NewspaperIcon class="w-7 h-7 text-brand" />
          文章管理
        </h1>
        <p class="mt-1 text-gray-500 font-medium">管理分类与文章内容（封面/标题/类别/正文）</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          @click="activeTab === 'categories' ? refreshCategories() : refreshArticles()"
          :class="['p-2 rounded-figma border border-gray-200 bg-white text-gray-500 hover:text-brand hover:border-brand/20 transition-all shadow-sm', (catLoading || articleLoading) && 'animate-spin text-brand']"
        >
          <ArrowPathIcon class="w-5 h-5" />
        </button>
        <button
          v-if="activeTab === 'categories'"
          @click="openCreateCategory"
          class="flex items-center gap-2 px-4 py-2 bg-brand text-white rounded-figma font-bold text-sm hover:bg-gray-900 active:scale-95 transition-all shadow-figma"
        >
          <PlusIcon class="w-5 h-5" />
          新建分类
        </button>
        <button
          v-else
          @click="openCreateArticle"
          class="flex items-center gap-2 px-4 py-2 bg-brand text-white rounded-figma font-bold text-sm hover:bg-gray-900 active:scale-95 transition-all shadow-figma"
        >
          <PlusIcon class="w-5 h-5" />
          新建文章
        </button>
      </div>
    </div>

    <div class="bg-white rounded-figma-lg shadow-figma border border-gray-100 overflow-hidden flex flex-col flex-1">
      <n-tabs v-model:value="activeTab" type="line" class="px-6 pt-4">
        <n-tab-pane name="articles" tab="文章" />
        <n-tab-pane name="categories" tab="分类" />
      </n-tabs>

      <div v-if="activeTab === 'categories'" class="p-6 flex flex-col gap-4 flex-1">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div class="relative">
            <MagnifyingGlassIcon class="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              v-model="catKeyword"
              type="text"
              placeholder="搜索分类名称..."
              class="pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-figma text-sm w-64 focus:border-brand/30 outline-none transition-all shadow-sm"
              @keyup.enter="catPage = 1; refreshCategories()"
            />
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50/50 border-b border-gray-100">
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">ID</th>
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">名称</th>
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">描述</th>
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">排序</th>
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">启用</th>
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest text-right">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="row in catRows" :key="row.id" class="hover:bg-gray-50/30 transition-colors">
                <td class="px-6 py-4 text-xs font-mono text-gray-400">#{{ row.id }}</td>
                <td class="px-6 py-4 text-sm font-bold text-gray-900">{{ row.name }}</td>
                <td class="px-6 py-4 text-xs text-gray-600">{{ row.description || "-" }}</td>
                <td class="px-6 py-4 text-xs text-gray-600">{{ row.sort_order }}</td>
                <td class="px-6 py-4 text-xs text-gray-600">{{ row.is_active ? "是" : "否" }}</td>
                <td class="px-6 py-4">
                  <div class="flex items-center justify-end gap-2">
                    <button
                      class="p-2 text-gray-400 hover:text-brand hover:bg-gray-50 rounded-figma transition-all"
                      @click="openEditCategory(row)"
                    >
                      <PencilSquareIcon class="w-5 h-5" />
                    </button>
                    <n-popconfirm @positive-click="handleDeleteCategory(row.id)">
                      <template #trigger>
                        <button class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-figma transition-all">
                          <TrashIcon class="w-5 h-5" />
                        </button>
                      </template>
                      确认删除该分类吗？
                    </n-popconfirm>
                  </div>
                </td>
              </tr>
              <tr v-if="catRows.length === 0 && !catLoading">
                <td colspan="6" class="px-6 py-16 text-center text-gray-400 font-medium italic">暂无分类</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="mt-auto flex justify-end">
          <n-pagination
            v-model:page="catPage"
            v-model:page-size="catPageSize"
            :item-count="catTotal"
            :page-sizes="[10, 20, 50]"
            show-size-picker
            @update:page="refreshCategories"
            @update:page-size="handleCatPageSizeUpdate"
          />
        </div>
      </div>

      <div v-else class="p-6 flex flex-col gap-4 flex-1">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
          <div class="flex flex-col md:flex-row md:items-center gap-3">
            <div class="relative">
              <MagnifyingGlassIcon class="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                v-model="articleKeyword"
                type="text"
                placeholder="搜索文章标题..."
                class="pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-figma text-sm w-64 focus:border-brand/30 outline-none transition-all shadow-sm"
                @keyup.enter="articlePage = 1; refreshArticles()"
              />
            </div>
            <n-select v-model:value="articleStatus" :options="statusOptions" class="w-40" />
            <n-select v-model:value="articleCategoryId" :options="categoryFilterOptions" class="w-48" />
            <n-button size="small" @click="articlePage = 1; refreshArticles()">筛选</n-button>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50/50 border-b border-gray-100">
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">ID</th>
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">标题</th>
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">分类</th>
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">状态</th>
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest">数据</th>
                <th class="px-6 py-4 text-[10px] font-bold text-gray-400 uppercase tracking-widest text-right">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="row in articleRows" :key="row.id" class="hover:bg-gray-50/30 transition-colors">
                <td class="px-6 py-4 text-xs font-mono text-gray-400">#{{ row.id }}</td>
                <td class="px-6 py-4">
                  <div class="flex flex-col">
                    <span class="text-sm font-bold text-gray-900">{{ row.title }}</span>
                    <span class="text-[11px] text-gray-400 font-medium truncate max-w-[520px]">{{ row.summary || "" }}</span>
                  </div>
                </td>
                <td class="px-6 py-4 text-xs text-gray-600">{{ row.category_name || "未分类" }}</td>
                <td class="px-6 py-4 text-xs text-gray-600">{{ row.status === 'published' ? "已发布" : (row.status === 'archived' ? "已归档" : "草稿") }}</td>
                <td class="px-6 py-4 text-xs text-gray-500">
                  <div>赞 {{ row.like_count }} / 藏 {{ row.favorite_count }} / 评 {{ row.comment_count }}</div>
                  <div>浏览 {{ row.view_count }}</div>
                </td>
                <td class="px-6 py-4">
                  <div class="flex items-center justify-end gap-2">
                    <button
                      class="p-2 text-gray-400 hover:text-brand hover:bg-gray-50 rounded-figma transition-all"
                      @click="openEditArticle(row)"
                    >
                      <PencilSquareIcon class="w-5 h-5" />
                    </button>
                    <n-popconfirm @positive-click="handleDeleteArticle(row.id)">
                      <template #trigger>
                        <button class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-figma transition-all">
                          <TrashIcon class="w-5 h-5" />
                        </button>
                      </template>
                      确认删除该文章吗？
                    </n-popconfirm>
                  </div>
                </td>
              </tr>
              <tr v-if="articleRows.length === 0 && !articleLoading">
                <td colspan="6" class="px-6 py-16 text-center text-gray-400 font-medium italic">暂无文章</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="mt-auto flex justify-end">
          <n-pagination
            v-model:page="articlePage"
            v-model:page-size="articlePageSize"
            :item-count="articleTotal"
            :page-sizes="[10, 20, 50]"
            show-size-picker
            @update:page="refreshArticles"
            @update:page-size="handleArticlePageSizeUpdate"
          />
        </div>
      </div>
    </div>

    <n-modal v-model:show="showCatModal" preset="card" title="分类" class="w-[520px]">
      <n-form>
        <n-form-item label="名称">
          <n-input v-model:value="(catForm as any).name" placeholder="例如：产品动态" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input v-model:value="(catForm as any).description" placeholder="可选" />
        </n-form-item>
        <n-form-item label="排序">
          <n-input-number v-model:value="(catForm as any).sort_order" class="w-full" :min="0" />
        </n-form-item>
        <n-form-item label="启用">
          <n-switch v-model:value="(catForm as any).is_active" />
        </n-form-item>
        <div class="flex justify-end gap-2">
          <n-button @click="showCatModal = false">取消</n-button>
          <n-button type="primary" @click="submitCategory">保存</n-button>
        </div>
      </n-form>
    </n-modal>

    <n-modal v-model:show="showArticleModal" preset="card" title="文章" class="w-[720px]">
      <n-form>
        <n-form-item label="标题">
          <n-input v-model:value="articleForm.title" placeholder="请输入标题" />
        </n-form-item>
        <n-form-item label="摘要">
          <n-input v-model:value="articleForm.summary" placeholder="可选" />
        </n-form-item>
        <n-form-item label="分类">
          <n-select v-model:value="articleForm.category_id" :options="categoryEditOptions" />
        </n-form-item>
        <n-form-item label="状态">
          <n-select v-model:value="articleForm.status" :options="statusOptions.filter(x => x.value !== '')" />
        </n-form-item>
        <n-form-item label="封面">
          <div class="flex flex-col gap-2 w-full">
            <div class="flex items-center gap-3">
              <n-upload :default-upload="false" :max="1" :show-file-list="false" @change="handleCoverChange">
                <button
                  class="px-3 py-1.5 bg-white border border-gray-200 rounded-figma text-sm font-bold text-gray-700 hover:border-brand/30 hover:text-brand transition-all shadow-sm"
                  type="button"
                >
                  选择文件
                </button>
              </n-upload>
              <div class="text-xs text-gray-500 truncate">
                <span v-if="articleCoverFile">已选择：{{ articleCoverFile.name }}</span>
                <span v-else>未选择任何文件</span>
              </div>
            </div>

            <div v-if="articleCoverPreviewUrl" class="space-y-1">
              <div class="text-xs font-bold text-gray-600">新封面预览（保存后将替换旧封面）</div>
              <img :src="articleCoverPreviewUrl" class="w-28 h-28 rounded-figma object-cover border border-gray-100 bg-gray-50" />
            </div>
            <div v-else-if="articleEditingId && articleCurrentCoverUrl" class="space-y-1">
              <div class="text-xs font-bold text-gray-600">当前封面</div>
              <img :src="articleCurrentCoverUrl" class="w-28 h-28 rounded-figma object-cover border border-gray-100 bg-gray-50" />
            </div>
          </div>
        </n-form-item>
        <n-form-item label="内容">
          <n-input v-model:value="articleForm.content" type="textarea" :autosize="{ minRows: 8, maxRows: 16 }" placeholder="请输入正文" />
        </n-form-item>
        <div class="flex justify-end gap-2">
          <n-button @click="showArticleModal = false">取消</n-button>
          <n-button type="primary" @click="submitArticle">保存</n-button>
        </div>
      </n-form>
    </n-modal>
  </div>
</template>
