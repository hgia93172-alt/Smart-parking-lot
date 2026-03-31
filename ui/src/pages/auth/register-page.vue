<script setup lang="ts">
import { reactive, ref } from "vue"
import { useRouter } from "vue-router"
import { NForm, NFormItem, NInput, NButton, useMessage } from "naive-ui"
import { UserPlusIcon, UserIcon, LockClosedIcon, ArrowRightIcon, CheckCircleIcon, ShieldCheckIcon } from "@heroicons/vue/24/outline"
import { useAuthStore } from "@/stores/auth-store"

const authStore = useAuthStore()
const router = useRouter()
const message = useMessage()

const form = reactive({ username: "", password: "", confirmPassword: "" })
const isSubmitting = ref(false)

async function handleSubmit() {
  if (!form.username || !form.password) {
    message.warning("请输入用户名和密码")
    return
  }
  
  if (form.password !== form.confirmPassword) {
    message.warning("两次输入的密码不一致")
    return
  }

  isSubmitting.value = true
  try {
    await authStore.register(form.username, form.password)
    message.success("注册成功，开启智能之旅")
    await router.replace({ name: "home" })
  } catch (e) {
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="flex h-full min-h-screen bg-canvas overflow-hidden relative">
    <!-- Background Accents -->
    <div class="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-brand/5 rounded-full blur-[120px] pointer-events-none" />
    <div class="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-accent/5 rounded-full blur-[120px] pointer-events-none" />

    <!-- Left Side: Registration Form -->
    <div class="flex-1 flex items-center justify-center p-6 md:p-12 z-10">
      <div 
        class="w-full max-w-md space-y-8"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { duration: 600 } }"
      >
        <div class="text-center lg:text-left">
          <h2 class="text-3xl font-bold text-gray-900 tracking-tight">创建新账号</h2>
          <p class="mt-2 text-gray-500 font-medium">加入我们，体验下一代 AI 协作工具</p>
        </div>

        <div class="space-y-6">
          <n-form @submit.prevent="handleSubmit" label-placement="top">
            <n-form-item label="用户名" class="font-medium">
              <n-input 
                v-model:value="form.username" 
                placeholder="设置您的用户名" 
                size="large"
                class="!rounded-figma !bg-white !border-gray-200"
              >
                <template #prefix>
                  <UserIcon class="w-4 h-4 text-gray-400 mr-2" />
                </template>
              </n-input>
            </n-form-item>
            
            <n-form-item label="密码" class="font-medium">
              <n-input
                v-model:value="form.password"
                type="password"
                show-password-on="click"
                placeholder="设置您的登录密码"
                size="large"
                class="!rounded-figma !bg-white !border-gray-200"
              >
                <template #prefix>
                  <LockClosedIcon class="w-4 h-4 text-gray-400 mr-2" />
                </template>
              </n-input>
            </n-form-item>

            <n-form-item label="确认密码" class="font-medium">
              <n-input
                v-model:value="form.confirmPassword"
                type="password"
                show-password-on="click"
                placeholder="请再次输入密码以确认"
                size="large"
                class="!rounded-figma !bg-white !border-gray-200"
                @keyup.enter="handleSubmit"
              >
                <template #prefix>
                  <ShieldCheckIcon class="w-4 h-4 text-gray-400 mr-2" />
                </template>
              </n-input>
            </n-form-item>

            <div class="flex items-start gap-2 mb-6">
              <input type="checkbox" class="mt-1 w-4 h-4 rounded border-gray-300 text-brand focus:ring-brand" checked />
              <p class="text-xs text-gray-500 leading-relaxed">
                我已阅读并同意 <a href="#" class="text-brand font-bold hover:underline">服务条款</a> 和 <a href="#" class="text-brand font-bold hover:underline">隐私政策</a>
              </p>
            </div>

            <button 
              @click="handleSubmit"
              :disabled="isSubmitting"
              class="w-full h-12 bg-brand text-white rounded-figma font-bold text-base flex items-center justify-center gap-2 hover:bg-gray-900 active:scale-[0.98] transition-all disabled:opacity-50 shadow-figma"
            >
              <span>{{ isSubmitting ? '正在注册...' : '立即注册' }}</span>
              <ArrowRightIcon v-if="!isSubmitting" class="w-5 h-5" />
            </button>
          </n-form>
        </div>

        <p class="text-center text-sm font-medium text-gray-500">
          已有账号？
          <router-link 
            class="text-brand font-bold hover:underline ml-1" 
            to="/login"
          >
            返回登录
          </router-link>
        </p>
      </div>
    </div>

    <!-- Right Side: Visual/Features -->
    <div class="hidden lg:flex flex-1 items-center justify-center p-12 relative overflow-hidden bg-gray-50 border-l border-gray-100">
      <div 
        class="absolute inset-0 opacity-20" 
        style="background-image: linear-gradient(#000 1px, transparent 1px), linear-gradient(90deg, #000 1px, transparent 1px); background-size: 50px 50px;"
      />
      <div 
        class="relative z-10 max-w-lg text-brand"
        v-motion
        :initial="{ opacity: 0, x: 50 }"
        :enter="{ opacity: 1, x: 0, transition: { duration: 800 } }"
      >
        <div class="w-16 h-16 bg-brand rounded-figma-lg flex items-center justify-center mb-8 shadow-xl">
          <UserPlusIcon class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-5xl font-bold tracking-tight mb-8 leading-tight">
          构建您的专属<br/>智能知识网
        </h1>
        
        <div class="space-y-6">
          <div class="flex items-start gap-4 p-5 bg-white rounded-figma shadow-figma border border-gray-100">
            <div class="w-8 h-8 rounded-full bg-brand/5 flex items-center justify-center shrink-0">
              <CheckCircleIcon class="w-5 h-5 text-brand" />
            </div>
            <div>
              <p class="font-bold text-gray-900 mb-1">无缝文档集成</p>
              <p class="text-sm text-gray-500 font-medium leading-relaxed">一键上传 PDF、Word 或 Markdown，自动完成语义分块与向量化。</p>
            </div>
          </div>
          
          <div class="flex items-start gap-4 p-5 bg-white rounded-figma shadow-figma border border-gray-100 translate-x-4">
            <div class="w-8 h-8 rounded-full bg-brand/5 flex items-center justify-center shrink-0">
              <CheckCircleIcon class="w-5 h-5 text-brand" />
            </div>
            <div>
              <p class="font-bold text-gray-900 mb-1">精准 RAG 对话</p>
              <p class="text-sm text-gray-500 font-medium leading-relaxed">基于您自有数据的精准问答，告别 AI 幻觉，提供可靠的知识支持。</p>
            </div>
          </div>

          <div class="flex items-start gap-4 p-5 bg-white rounded-figma shadow-figma border border-gray-100">
            <div class="w-8 h-8 rounded-full bg-brand/5 flex items-center justify-center shrink-0">
              <CheckCircleIcon class="w-5 h-5 text-brand" />
            </div>
            <div>
              <p class="font-bold text-gray-900 mb-1">多维度管理</p>
              <p class="text-sm text-gray-500 font-medium leading-relaxed">灵活的知识库合集、精细的提示词模板，随心掌控 AI 输出。</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
:deep(.n-input) {
  --n-border-radius: 8px !important;
  --n-border: 1px solid #E5E7EB !important;
  --n-border-hover: 1px solid #000000 !important;
  --n-border-focus: 1px solid #000000 !important;
  --n-box-shadow-focus: 0 0 0 2px rgba(0,0,0,0.05) !important;
}

:deep(.n-form-item .n-form-item-label) {
  font-size: 0.875rem;
  color: #4B5563;
  margin-bottom: 0.5rem;
}
</style>
