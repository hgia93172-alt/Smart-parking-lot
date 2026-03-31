<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import {
  ArrowLeftIcon,
  HandThumbUpIcon,
  BookmarkIcon,
  ChatBubbleLeftRightIcon,
  ArrowPathIcon,
} from "@heroicons/vue/24/outline"
import { useMessage, NButton, NInput, NPagination } from "naive-ui"
import type { ArticleCommentItem, ArticleItem } from "@/types/utils"
import {
  createArticleComment,
  getPublicArticleDetail,
  listArticleCommentsPaged,
  toggleArticleFavorite,
  toggleArticleLike,
} from "@/api/utils"

const route = useRoute()
const router = useRouter()
const message = useMessage()

const articleId = computed(() => Number(route.params.id))

const detail = ref<ArticleItem | null>(null)
const isLoading = ref(false)

const comments = ref<ArticleCommentItem[]>([])
const commentLoading = ref(false)
const commentContent = ref("")
const commentPage = ref(1)
const commentPageSize = ref(10)
const commentTotal = ref(0)

async function refreshDetail() {
  if (!articleId.value) return
  isLoading.value = true
  try {
    detail.value = await getPublicArticleDetail(articleId.value)
  } catch {
    message.error("加载文章失败")
  } finally {
    isLoading.value = false
  }
}

async function refreshComments() {
  if (!articleId.value) return
  commentLoading.value = true
  try {
    const data = await listArticleCommentsPaged(articleId.value, commentPage.value, commentPageSize.value)
    comments.value = data.results
    commentTotal.value = data.count
  } catch {
    message.error("加载评论失败")
  } finally {
    commentLoading.value = false
  }
}

function handleCommentPageSizeUpdate() {
  commentPage.value = 1
  refreshComments()
}

async function submitComment() {
  if (!articleId.value) return
  const content = commentContent.value.trim()
  if (!content) {
    message.error("请输入评论内容")
    return
  }
  try {
    await createArticleComment(articleId.value, { content })
    message.success("评论成功")
    commentContent.value = ""
    commentPage.value = 1
    await refreshComments()
    await refreshDetail()
  } catch {
    message.error("评论失败")
  }
}

async function handleToggleLike() {
  if (!articleId.value || !detail.value) return
  try {
    const out = await toggleArticleLike(articleId.value)
    detail.value.liked = out.liked
    detail.value.like_count = out.like_count
  } catch {
    message.error("操作失败")
  }
}

async function handleToggleFavorite() {
  if (!articleId.value || !detail.value) return
  try {
    const out = await toggleArticleFavorite(articleId.value)
    detail.value.favorited = out.favorited
    detail.value.favorite_count = out.favorite_count
  } catch {
    message.error("操作失败")
  }
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push({ name: "articles" })
}

onMounted(async () => {
  await refreshDetail()
  await refreshComments()
})

watch(articleId, async () => {
  commentPage.value = 1
  await refreshDetail()
  await refreshComments()
})
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-6 pb-12">
    <div class="flex items-center justify-between gap-3">
      <div class="flex items-center gap-2">
        <button
          class="p-2 rounded-figma border border-gray-200 bg-white text-gray-500 hover:text-brand hover:border-brand/20 transition-all shadow-sm"
          @click="goBack"
        >
          <ArrowLeftIcon class="w-5 h-5" />
        </button>
        <div class="text-sm text-gray-500 font-medium">文章详情</div>
      </div>
      <button
        @click="() => { refreshDetail(); refreshComments() }"
        :class="['p-2 rounded-figma border border-gray-200 bg-white text-gray-500 hover:text-brand hover:border-brand/20 transition-all shadow-sm', (isLoading || commentLoading) && 'animate-spin text-brand']"
      >
        <ArrowPathIcon class="w-5 h-5" />
      </button>
    </div>

    <div v-if="detail" class="bg-white rounded-figma-lg border border-gray-100 shadow-figma overflow-hidden">
      <div v-if="detail.cover_url" class="h-64 w-full bg-gray-100 overflow-hidden">
        <img :src="detail.cover_url" class="h-full w-full object-cover" />
      </div>
      <div class="p-6 space-y-4">
        <div class="space-y-1">
          <h1 class="text-2xl font-bold text-gray-900 tracking-tight">{{ detail.title }}</h1>
          <div class="text-xs text-gray-500 font-medium flex items-center justify-between">
            <span>{{ detail.category_name || "未分类" }}</span>
            <span class="font-mono">浏览 {{ detail.view_count }}</span>
          </div>
        </div>

        <p v-if="detail.summary" class="text-sm text-gray-600 font-medium">{{ detail.summary }}</p>

        <div class="flex items-center gap-2">
          <n-button :type="detail.liked ? 'primary' : 'default'" @click="handleToggleLike">
            <template #icon>
              <HandThumbUpIcon class="w-5 h-5" />
            </template>
            点赞（{{ detail.like_count }}）
          </n-button>
          <n-button :type="detail.favorited ? 'primary' : 'default'" @click="handleToggleFavorite">
            <template #icon>
              <BookmarkIcon class="w-5 h-5" />
            </template>
            收藏（{{ detail.favorite_count }}）
          </n-button>
          <div class="text-xs text-gray-500 font-medium flex items-center gap-1 ml-2">
            <ChatBubbleLeftRightIcon class="w-5 h-5" />
            评论 {{ detail.comment_count }}
          </div>
        </div>

        <div class="border-t border-gray-100 pt-4">
          <div class="text-sm font-bold text-gray-900 mb-2">正文</div>
          <div class="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">{{ detail.content || "" }}</div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-figma-lg border border-gray-100 shadow-figma p-6 space-y-4">
      <div class="text-lg font-bold text-gray-900">评论</div>
      <div class="flex gap-3">
        <n-input v-model:value="commentContent" type="textarea" :autosize="{ minRows: 2, maxRows: 4 }" placeholder="写下你的评论..." />
        <n-button type="primary" class="shrink-0" @click="submitComment">发送</n-button>
      </div>

      <div class="space-y-3">
        <div
          v-for="c in comments"
          :key="c.id"
          class="border border-gray-100 rounded-figma p-4 hover:bg-gray-50/30 transition-colors"
        >
          <div class="flex items-center justify-between">
            <div class="text-sm font-bold text-gray-900">{{ c.username || "匿名" }}</div>
            <div class="text-[11px] text-gray-400 font-mono">{{ c.created_at }}</div>
          </div>
          <div class="mt-2 text-sm text-gray-700 whitespace-pre-wrap">{{ c.content }}</div>
        </div>
        <div v-if="comments.length === 0 && !commentLoading" class="text-sm text-gray-400 italic text-center py-8">
          暂无评论
        </div>
      </div>

      <div class="flex justify-end">
        <n-pagination
          v-model:page="commentPage"
          v-model:page-size="commentPageSize"
          :item-count="commentTotal"
          :page-sizes="[10, 20, 50]"
          show-size-picker
          @update:page="refreshComments"
          @update:page-size="handleCommentPageSizeUpdate"
        />
      </div>
    </div>
  </div>
</template>

