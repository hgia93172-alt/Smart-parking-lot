<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import { UserCircleIcon, BookmarkIcon, ChevronDownIcon, ChevronUpIcon, ArrowPathIcon } from "@heroicons/vue/24/outline"
import { useMessage, NAvatar, NPagination } from "naive-ui"
import { useAuthStore } from "@/stores/auth-store"
import type { ArticleItem } from "@/types/utils"
import { listMyFavoriteArticlesPaged } from "@/api/utils"

const authStore = useAuthStore()
const router = useRouter()
const message = useMessage()

const me = computed(() => authStore.me)
const username = computed(() => me.value?.username || "访客")
const role = computed(() => me.value?.role || "-")
const isAdmin = computed(() => Boolean(me.value?.is_admin))

const showFavorites = ref(false)
const favRows = ref<ArticleItem[]>([])
const favLoading = ref(false)
const favPage = ref(1)
const favPageSize = ref(10)
const favTotal = ref(0)

async function refreshFavorites() {
  favLoading.value = true
  try {
    const data = await listMyFavoriteArticlesPaged(favPage.value, favPageSize.value)
    favRows.value = data.results
    favTotal.value = data.count
  } catch {
    message.error("加载收藏失败")
  } finally {
    favLoading.value = false
  }
}

function handleFavPageSizeUpdate() {
  favPage.value = 1
  refreshFavorites()
}

function openArticle(id: number) {
  router.push({ name: "article-detail", params: { id: String(id) } })
}

onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.me) {
    await authStore.refreshMe()
  }
  await refreshFavorites()
})
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-12">
    <div class="flex items-center justify-between gap-3">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 tracking-tight flex items-center gap-3">
          <UserCircleIcon class="w-7 h-7 text-brand" />
          个人信息
        </h1>
        <p class="mt-1 text-gray-500 font-medium">查看账号信息与收藏内容</p>
      </div>
      <button
        @click="refreshFavorites"
        :class="['p-2 rounded-figma border border-gray-200 bg-white text-gray-500 hover:text-brand hover:border-brand/20 transition-all shadow-sm', favLoading && 'animate-spin text-brand']"
      >
        <ArrowPathIcon class="w-5 h-5" />
      </button>
    </div>

    <div class="bg-white rounded-figma-lg border border-gray-100 shadow-figma p-6 flex items-center gap-5">
      <n-avatar round :size="56" class="bg-brand text-white font-bold">
        {{ username.charAt(0).toUpperCase() }}
      </n-avatar>
      <div class="flex-1">
        <div class="text-xl font-bold text-gray-900 leading-none">{{ username }}</div>
        <div class="mt-2 text-sm text-gray-600 font-medium flex items-center gap-4">
          <span>角色：{{ role }}</span>
          <span>权限：{{ isAdmin ? "管理员" : "标准用户" }}</span>
        </div>
      </div>
      <div class="text-right">
        <div class="text-2xl font-bold text-gray-900 leading-none">{{ favTotal }}</div>
        <div class="text-[11px] text-gray-400 font-bold uppercase tracking-widest mt-1">收藏文章</div>
      </div>
    </div>

    <div class="bg-white rounded-figma-lg border border-gray-100 shadow-figma overflow-hidden">
      <button
        class="w-full flex items-center justify-between px-6 py-4 hover:bg-gray-50/30 transition-colors"
        @click="showFavorites = !showFavorites"
      >
        <div class="flex items-center gap-3">
          <BookmarkIcon class="w-6 h-6 text-brand" />
          <div class="text-left">
            <div class="text-sm font-bold text-gray-900">我的收藏</div>
            <div class="text-[11px] text-gray-400 font-medium">点击展开查看</div>
          </div>
        </div>
        <div class="text-gray-400">
          <ChevronUpIcon v-if="showFavorites" class="w-5 h-5" />
          <ChevronDownIcon v-else class="w-5 h-5" />
        </div>
      </button>

      <div v-if="showFavorites" class="p-6 space-y-4 border-t border-gray-100">
        <div class="space-y-3">
          <button
            v-for="row in favRows"
            :key="row.id"
            class="w-full text-left border border-gray-100 rounded-figma p-4 hover:bg-gray-50/30 transition-colors"
            @click="openArticle(row.id)"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <div class="text-sm font-bold text-gray-900 truncate">{{ row.title }}</div>
                <div class="mt-1 text-xs text-gray-500 font-medium truncate">{{ row.summary || "—" }}</div>
              </div>
              <div class="text-[11px] text-gray-400 font-mono shrink-0">#{{ row.id }}</div>
            </div>
            <div class="mt-2 flex items-center gap-4 text-[11px] text-gray-500 font-medium">
              <span>{{ row.category_name || "未分类" }}</span>
              <span>赞 {{ row.like_count }}</span>
              <span>藏 {{ row.favorite_count }}</span>
              <span>评 {{ row.comment_count }}</span>
            </div>
          </button>

          <div v-if="favRows.length === 0 && !favLoading" class="text-sm text-gray-400 italic text-center py-8">
            暂无收藏
          </div>
        </div>

        <div class="flex justify-end">
          <n-pagination
            v-model:page="favPage"
            v-model:page-size="favPageSize"
            :item-count="favTotal"
            :page-sizes="[10, 20, 50]"
            show-size-picker
            @update:page="refreshFavorites"
            @update:page-size="handleFavPageSizeUpdate"
          />
        </div>
      </div>
    </div>
  </div>
</template>

