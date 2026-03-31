<script setup lang="ts">
import { computed } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth-store"
import { 
  DocumentTextIcon, 
  UsersIcon,
  ShieldCheckIcon, 
  ArrowUpRightIcon,
  BoltIcon,
  ClockIcon,
  Squares2X2Icon,
  BookOpenIcon
} from "@heroicons/vue/24/outline"

const authStore = useAuthStore()
const router = useRouter()

const username = computed(() => authStore.me?.username || "访客")
const role = computed(() => authStore.me?.role || "标准用户")
const isAdmin = computed(() => authStore.isAdmin)

const quickActions = computed(() => {
  const actions = [
    { 
      title: "我的文件", 
      desc: "上传、下载与管理您的个人文件", 
      icon: DocumentTextIcon, 
      route: "my-files",
      color: "bg-blue-500" 
    },
  ]
  if (isAdmin.value) {
    actions.push({
      title: "用户管理",
      desc: "查看用户并调整业务角色",
      icon: UsersIcon,
      route: "admin-users",
      color: "bg-purple-500",
    })
  }
  return actions
})
</script>

<template>
  <div class="max-w-7xl mx-auto space-y-10 pb-12">
    <!-- Welcome Section -->
    <div 
      class="relative overflow-hidden rounded-figma-lg bg-brand p-10 text-white shadow-2xl"
    >
      <div class="relative z-10 max-w-2xl">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-xs font-bold uppercase tracking-wider mb-6">
          <BoltIcon class="w-4 h-4" />
          <span>欢迎回来，{{ role }}</span>
        </div>
        <h1 class="text-4xl md:text-5xl font-bold tracking-tight mb-4 leading-tight">
          你好, {{ username }} 👋
        </h1>
        <p class="text-lg text-white/80 font-medium leading-relaxed mb-8">
          今天想处理什么任务？您可以快速上传新文档，或者继续之前的智能对话。
          AI 助手已经准备好协助您处理复杂的知识网络。
        </p>
        <div class="flex flex-wrap gap-4">
          <button 
            @click="router.push({ name: 'my-files' })"
            class="px-6 py-3 bg-white text-brand rounded-figma font-bold hover:bg-gray-100 transition-all flex items-center gap-2 shadow-lg"
          >
            打开文件中心
            <DocumentTextIcon class="w-5 h-5" />
          </button>
          <button 
            @click="router.push({ name: isAdmin ? 'admin-users' : 'my-files' })"
            class="px-6 py-3 bg-white/10 hover:bg-white/20 text-white border border-white/20 rounded-figma font-bold transition-all flex items-center gap-2"
          >
            {{ isAdmin ? "进入管理" : "查看文件" }}
            <UsersIcon v-if="isAdmin" class="w-5 h-5" />
            <DocumentTextIcon v-else class="w-5 h-5" />
          </button>
        </div>
      </div>
      
      <!-- Abstract decorative elements -->
      <div class="absolute top-[-20%] right-[-10%] w-[500px] h-[500px] bg-white/5 rounded-full blur-3xl pointer-events-none" />
      <div class="absolute bottom-[-20%] left-[40%] w-[300px] h-[300px] bg-accent/20 rounded-full blur-3xl pointer-events-none" />
    </div>

    <!-- Quick Actions Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div 
        v-for="(action, idx) in quickActions" 
        :key="idx"
        @click="router.push({ name: action.route })"
        class="stat-card group cursor-pointer bg-white p-6 rounded-figma-lg shadow-figma hover:shadow-figma-hover border border-gray-100 transition-all relative overflow-hidden"
      >
        <div class="flex justify-between items-start mb-4">
          <div :class="[action.color, 'w-12 h-12 rounded-figma flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition-transform duration-300']">
            <component :is="action.icon" class="w-6 h-6" />
          </div>
          <ArrowUpRightIcon class="w-5 h-5 text-gray-300 group-hover:text-brand transition-colors" />
        </div>
        <h3 class="text-lg font-bold text-gray-900 mb-2">{{ action.title }}</h3>
        <p class="text-sm text-gray-500 font-medium leading-relaxed">{{ action.desc }}</p>
        
        <div class="absolute bottom-0 left-0 w-full h-1 bg-gray-50 group-hover:bg-brand/10 transition-colors" />
      </div>
    </div>

    <!-- Stats & Insights Section -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Activity Feed -->
      <div class="lg:col-span-2 bg-white rounded-figma-lg shadow-figma border border-gray-100 overflow-hidden">
        <div class="p-6 border-b border-gray-50 flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Squares2X2Icon class="w-5 h-5 text-brand" />
            系统概览
          </h2>
          <button class="text-sm font-bold text-brand hover:underline">查看全部</button>
        </div>
        <div class="p-8 grid grid-cols-1 sm:grid-cols-2 gap-8">
          <div class="space-y-2">
            <p class="text-sm font-bold text-gray-400 uppercase tracking-widest">知识库总量</p>
            <div class="flex items-end gap-3">
              <span class="text-4xl font-bold text-gray-900 leading-none">1,284</span>
              <span class="text-green-500 text-sm font-bold pb-1 flex items-center">
                +12% <ArrowUpRightIcon class="w-4 h-4" />
              </span>
            </div>
          </div>
          <div class="space-y-2">
            <p class="text-sm font-bold text-gray-400 uppercase tracking-widest">昨日对话数</p>
            <div class="flex items-end gap-3">
              <span class="text-4xl font-bold text-gray-900 leading-none">42</span>
              <span class="text-brand text-sm font-bold pb-1 flex items-center">
                稳定 <ClockIcon class="w-4 h-4 ml-1" />
              </span>
            </div>
          </div>
        </div>
        <div class="px-8 pb-8">
          <div class="bg-gray-50 rounded-figma p-6 border border-dashed border-gray-200 flex flex-col items-center justify-center text-center space-y-4">
            <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-sm">
              <BookOpenIcon class="w-5 h-5 text-gray-400" />
            </div>
            <div>
              <p class="font-bold text-gray-900">暂无深度分析报告</p>
              <p class="text-sm text-gray-500 font-medium mt-1">上传更多文档以激活语义分析图谱</p>
            </div>
          </div>
        </div>
      </div>

      <!-- System Health -->
      <div class="bg-white rounded-figma-lg shadow-figma border border-gray-100 overflow-hidden flex flex-col">
        <div class="p-6 border-b border-gray-50">
          <h2 class="text-xl font-bold text-gray-900 flex items-center gap-2">
            <ShieldCheckIcon class="w-5 h-5 text-green-500" />
            运行状态
          </h2>
        </div>
        <div class="flex-1 p-6 space-y-6">
          <div class="space-y-4">
            <div class="flex justify-between items-center text-sm">
              <span class="font-medium text-gray-600">向量检索引擎</span>
              <span class="text-green-500 font-bold px-2 py-0.5 bg-green-50 rounded-full text-xs uppercase">正常运行</span>
            </div>
            <div class="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
              <div class="h-full bg-green-500 w-[98%]" />
            </div>
          </div>

          <div class="space-y-4">
            <div class="flex justify-between items-center text-sm">
              <span class="font-medium text-gray-600">AI 推理 API</span>
              <span class="text-green-500 font-bold px-2 py-0.5 bg-green-50 rounded-full text-xs uppercase">延迟极低</span>
            </div>
            <div class="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
              <div class="h-full bg-green-500 w-[94%]" />
            </div>
          </div>

          <div class="mt-8 p-4 bg-gray-50 rounded-figma border border-gray-100">
            <div class="flex items-center gap-3 text-brand">
              <BoltIcon class="w-5 h-5" />
              <span class="font-bold text-sm">Pro 版本特权</span>
            </div>
            <p class="text-xs text-gray-500 font-medium mt-2 leading-relaxed">您的账户已启用高优先级推理，享受最快响应速度。</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stat-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-4px);
}
</style>

