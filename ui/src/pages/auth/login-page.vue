<script setup lang="ts">
import { reactive, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { NForm, NFormItem, NInput, useMessage } from "naive-ui"
import { 
  ArrowRightOnRectangleIcon, 
  UserIcon, 
  LockClosedIcon, 
  ArrowRightIcon 
} from "@heroicons/vue/24/outline"
import { useAuthStore } from "@/stores/auth-store"

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const message = useMessage()

const form = reactive({ username: "", password: "" })
const isSubmitting = ref(false)

async function handleSubmit() {
  if (!form.username || !form.password) {
    message.warning("请输入用户名和密码")
    return
  }
  
  isSubmitting.value = true
  try {
    await authStore.login(form.username, form.password)
    message.success("欢迎回来")
    const next = typeof route.query.next === "string" ? route.query.next : "/"
    await router.replace(next)
  } catch (e) {
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="flex h-full min-h-screen bg-canvas overflow-hidden relative">
    <!-- Background Accents -->
    <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-brand/5 rounded-full blur-[120px] pointer-events-none" />
    <div class="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-accent/5 rounded-full blur-[120px] pointer-events-none" />

    <!-- Left Side: Visual/Branding -->
    <div class="hidden lg:flex flex-1 items-center justify-center p-12 relative overflow-hidden bg-brand">
      <div 
        class="absolute inset-0 opacity-10" 
        style="background-image: radial-gradient(circle at 2px 2px, white 1px, transparent 0); background-size: 40px 40px;"
      />
      <div 
        class="relative z-10 max-w-lg text-white"
        v-motion
        :initial="{ opacity: 0, x: -50 }"
        :enter="{ opacity: 1, x: 0, transition: { duration: 800 } }"
      >
        <div class="w-16 h-16 bg-white rounded-figma-lg flex items-center justify-center mb-8 shadow-2xl">
          <ArrowRightOnRectangleIcon class="w-8 h-8 text-brand" />
        </div>
        <h1 class="text-5xl font-bold tracking-tight mb-6 leading-tight">
          开启您的智能<br/>停车场管理之旅
        </h1>
        <p class="text-xl text-white/80 font-medium leading-relaxed">
          智能识别，高效运营。基于 YOLOv11 的实时车辆监测与自动计费管理系统。
        </p>
        
        <div class="mt-12 space-y-4">
          <div class="flex items-center gap-4 bg-white/10 p-4 rounded-figma border border-white/10 backdrop-blur-sm">
            <div class="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
              <span class="font-bold text-sm">01</span>
            </div>
            <p class="font-medium text-sm">实时车辆检测与自动计费</p>
          </div>
          <div class="flex items-center gap-4 bg-white/10 p-4 rounded-figma border border-white/10 backdrop-blur-sm">
            <div class="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
              <span class="font-bold text-sm">02</span>
            </div>
            <p class="font-medium text-sm">车位状态全自动化监测</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Side: Login Form -->
    <div class="flex-1 flex items-center justify-center p-6 md:p-12">
      <div 
        class="w-full max-w-md space-y-8"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { duration: 600 } }"
      >
        <div class="text-center lg:text-left">
          <h2 class="text-3xl font-bold text-gray-900 tracking-tight">登录账号</h2>
          <p class="mt-2 text-gray-500 font-medium">输入您的凭据以继续访问</p>
        </div>

        <div class="space-y-6">
          <n-form @submit.prevent="handleSubmit" label-placement="top">
            <n-form-item label="用户名" class="font-medium">
              <n-input 
                v-model:value="form.username" 
                placeholder="请输入您的用户名" 
                size="large"
                class="!rounded-figma !bg-white !border-gray-200"
              >
                <template #prefix>
                  <UserIcon class="w-5 h-5 text-gray-400 mr-2" />
                </template>
              </n-input>
            </n-form-item>
            
            <n-form-item label="密码" class="font-medium">
              <n-input
                v-model:value="form.password"
                type="password"
                show-password-on="click"
                placeholder="请输入您的密码"
                size="large"
                class="!rounded-figma !bg-white !border-gray-200"
                @keyup.enter="handleSubmit"
              >
                <template #prefix>
                  <LockClosedIcon class="w-5 h-5 text-gray-400 mr-2" />
                </template>
              </n-input>
            </n-form-item>

            <div class="flex items-center justify-between mb-4">
              <label class="flex items-center gap-2 cursor-pointer group">
                <input type="checkbox" class="w-4 h-4 rounded border-gray-300 text-brand focus:ring-brand" />
                <span class="text-sm font-medium text-gray-600 group-hover:text-gray-900 transition-colors">记住我</span>
              </label>
              <a href="#" class="text-sm font-bold text-brand hover:underline">忘记密码？</a>
            </div>

            <button 
              @click="handleSubmit"
              :disabled="isSubmitting"
              class="w-full h-12 bg-brand text-white rounded-figma font-bold text-base flex items-center justify-center gap-2 hover:bg-gray-900 active:scale-[0.98] transition-all disabled:opacity-50 shadow-figma mt-2"
            >
              <span>{{ isSubmitting ? '正在登录...' : '登录' }}</span>
              <ArrowRightIcon v-if="!isSubmitting" class="w-5 h-5" />
            </button>
          </n-form>
        </div>

        <p class="text-center text-sm font-medium text-gray-500">
          还没有账号？
          <router-link 
            class="text-brand font-bold hover:underline ml-1" 
            to="/register"
          >
            立即注册
          </router-link>
        </p>
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

