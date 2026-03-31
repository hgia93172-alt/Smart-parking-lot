<script setup lang="ts">
import { computed, ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth-store"
import { useParkingStore } from "@/stores/parking-store"
import {
  NLayout,
  NLayoutSider,
  NLayoutHeader,
  NLayoutContent,
  NDropdown,
  NAvatar,
  NBadge,
} from "naive-ui"
import {
  ChartBarIcon,
  VideoCameraIcon,
  BuildingOffice2Icon,
  Squares2X2Icon,
  TruckIcon,
  CreditCardIcon,
  ShieldExclamationIcon,
  Cog6ToothIcon,
  Bars3Icon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from "@heroicons/vue/24/outline"

const authStore = useAuthStore()
const parkingStore = useParkingStore()
const route = useRoute()
const router = useRouter()

const collapsed = ref(false)
const username = computed(() => authStore.me?.username || "访客")
const pendingViolations = computed(() => parkingStore.pendingViolations)

onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.me) {
    await authStore.refreshMe()
  }
  await parkingStore.fetchOverview()
  // Refresh every 30s
  setInterval(() => parkingStore.fetchOverview(), 30000)
})

const activeKey = computed(() => route.name as string)

const menuGroups = computed(() => [
  {
    title: "监控中心",
    items: [
      { label: "数据仪表盘", name: "dashboard", icon: ChartBarIcon, badge: 0 },
      { label: "实时监控", name: "monitoring", icon: VideoCameraIcon, badge: 0 },
    ]
  },
  {
    title: "停车场管理",
    items: [
      { label: "停车场", name: "lots", icon: BuildingOffice2Icon, badge: 0 },
      { label: "车位管理", name: "spaces", icon: Squares2X2Icon, badge: 0 },
    ]
  },
  {
    title: "运营数据",
    items: [
      { label: "车辆进出记录", name: "vehicles", icon: TruckIcon, badge: 0 },
      { label: "停车会话 & 计费", name: "sessions", icon: CreditCardIcon, badge: 0 },
      { label: "违规报警", name: "violations", icon: ShieldExclamationIcon, badge: pendingViolations.value },
    ]
  },
  {
    title: "系统",
    items: [
      { label: "系统设置", name: "settings", icon: Cog6ToothIcon, badge: 0 },
    ]
  },
])

const userOptions = [
  { label: "退出登录", key: "logout" },
]

async function handleUserSelect(key: string) {
  if (key === "logout") {
    await authStore.logout()
    await router.replace({ name: "login" })
  }
}

const navigateTo = (name: string) => {
  router.push({ name })
}
</script>

<template>
  <n-layout has-sider class="h-full" style="background:#0f172a">
    <!-- Sidebar -->
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="72"
      :width="240"
      :collapsed="collapsed"
      style="background:#0f172a; border-right: 1px solid #1e293b;"
      class="h-full transition-all duration-300 ease-in-out"
    >
      <div class="flex flex-col h-full">
        <!-- Logo -->
        <div class="h-16 flex items-center px-4 gap-3 border-b" style="border-color:#1e293b">
          <div class="w-12 h-9 rounded-lg flex items-center justify-center shrink-0 text-white font-extrabold text-sm"
               style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">SPS</div>
          <span v-if="!collapsed" class="font-bold text-base tracking-tight" style="color:#f1f5f9">
            智能停车场系统
          </span>
        </div>

        <!-- Navigation -->
        <div class="flex-1 overflow-y-auto py-4 px-2">
          <div v-for="group in menuGroups" :key="group.title" class="mb-4">
            <p v-if="!collapsed" class="px-3 text-xs uppercase tracking-widest mb-1" style="color:#475569; font-weight:600">
              {{ group.title }}
            </p>
            <button
              v-for="item in group.items"
              :key="item.name"
              @click="navigateTo(item.name)"
              :class="[
                'w-full flex items-center px-3 py-2.5 rounded-lg mb-0.5 transition-all duration-150 relative group',
                activeKey === item.name
                  ? 'text-white'
                  : 'hover:text-white'
              ]"
              :style="activeKey === item.name
                ? 'background: linear-gradient(135deg, rgba(79,172,254,0.2) 0%, rgba(0,242,254,0.1) 100%); color:#4facfe; box-shadow: inset 0 0 0 1px rgba(79,172,254,0.3);'
                : 'color:#64748b'"
            >
              <div class="w-5 h-5 shrink-0 relative">
                <component :is="item.icon" class="w-5 h-5" />
                <span v-if="item.badge > 0"
                      class="absolute -top-1.5 -right-1.5 min-w-[16px] h-4 px-0.5 rounded-full text-white text-[10px] font-bold flex items-center justify-center"
                      style="background:#f5576c; line-height:1">
                  {{ item.badge > 99 ? '99+' : item.badge }}
                </span>
              </div>
              <span v-if="!collapsed" class="ml-3 text-sm font-medium whitespace-nowrap">
                {{ item.label }}
              </span>
              <!-- Active bar -->
              <div v-if="activeKey === item.name"
                   class="absolute left-0 top-1 bottom-1 w-0.5 rounded-r"
                   style="background:#4facfe" />
            </button>
          </div>
        </div>

        <!-- Collapse toggle -->
        <div class="p-3 border-t" style="border-color:#1e293b">
          <button @click="collapsed = !collapsed"
                  class="w-full flex items-center justify-center py-2 rounded-lg transition-colors"
                  style="color:#475569"
                  onmouseenter="this.style.background='#1e293b'" onmouseleave="this.style.background='transparent'">
            <ChevronLeftIcon v-if="!collapsed" class="w-4 h-4" />
            <ChevronRightIcon v-else class="w-4 h-4" />
          </button>
        </div>
      </div>
    </n-layout-sider>

    <n-layout class="h-full" style="background:#0f172a">
      <!-- Header -->
      <n-layout-header class="h-16 flex items-center justify-between px-6 border-b" style="background:#0f172a; border-color:#1e293b;">
        <div style="color:#94a3b8; font-size:14px">
          智能停车场车辆监测管理系统
        </div>
        <div class="flex items-center gap-3">
          <n-dropdown :options="userOptions" @select="handleUserSelect" trigger="click">
            <div class="flex items-center gap-2 cursor-pointer px-3 py-1.5 rounded-lg transition-colors"
                 style="color:#cbd5e1" @mouseenter="$el.style.background='#1e293b'" @mouseleave="$el.style.background='transparent'">
              <n-avatar round :size="32" style="background: linear-gradient(135deg,#667eea,#764ba2); color:#fff; font-weight:700">
                {{ username.charAt(0).toUpperCase() }}
              </n-avatar>
              <span class="text-sm font-medium">{{ username }}</span>
            </div>
          </n-dropdown>
        </div>
      </n-layout-header>

      <!-- Content -->
      <n-layout-content content-style="padding:0;" style="height:calc(100vh - 64px); background:#0f172a;">
        <div class="h-full w-full overflow-y-auto" style="background:#0f172a">
          <Suspense>
            <router-view v-slot="{ Component }">
              <transition
                enter-active-class="transition duration-200 ease-out"
                enter-from-class="opacity-0 translate-y-2"
                enter-to-class="opacity-100 translate-y-0"
                mode="out-in"
              >
                <component :is="Component" />
              </transition>
            </router-view>
            <template #fallback>
              <div class="flex items-center justify-center h-full" style="color:#475569">
                <div class="w-8 h-8 border-2 border-t-transparent rounded-full animate-spin" style="border-color:#4facfe; border-top-color:transparent"></div>
              </div>
            </template>
          </Suspense>
        </div>
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<style scoped>
:deep(.n-layout-sider-scroll-container) { overflow: hidden !important; }
</style>
