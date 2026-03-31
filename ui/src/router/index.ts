import { createRouter, createWebHistory } from "vue-router"
import { useAuthStore } from "@/stores/auth-store"

const AppShell = () => import("@/components/app-shell/app-shell.vue")
const LoginPage = () => import("@/pages/auth/login-page.vue")

// Parking pages
const DashboardPage = () => import("@/pages/parking/dashboard-page.vue")
const MonitoringPage = () => import("@/pages/parking/monitoring-page.vue")
const LotsPage = () => import("@/pages/parking/lots-page.vue")
const SpacesPage = () => import("@/pages/parking/spaces-page.vue")
const VehiclesPage = () => import("@/pages/parking/vehicles-page.vue")
const SessionsPage = () => import("@/pages/parking/sessions-page.vue")
const ViolationsPage = () => import("@/pages/parking/violations-page.vue")
const SettingsPage = () => import("@/pages/parking/settings-page.vue")

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: AppShell,
      meta: { requiresAuth: true },
      children: [
        { path: "", redirect: "/dashboard" },
        { path: "dashboard", name: "dashboard", component: DashboardPage },
        { path: "monitoring", name: "monitoring", component: MonitoringPage },
        { path: "parking-lots", name: "lots", component: LotsPage },
        { path: "spaces", name: "spaces", component: SpacesPage },
        { path: "vehicles", name: "vehicles", component: VehiclesPage },
        { path: "sessions", name: "sessions", component: SessionsPage },
        { path: "violations", name: "violations", component: ViolationsPage },
        { path: "settings", name: "settings", component: SettingsPage },
      ]
    },
    { path: "/login", name: "login", component: LoginPage },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  const isAuthed = authStore.isAuthenticated
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  if (requiresAuth && !isAuthed) {
    return { name: "login", query: { next: to.fullPath } }
  }
  if (to.name === "login" && isAuthed) {
    return { name: "dashboard" }
  }
})
