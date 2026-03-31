import { defineStore } from "pinia"
import { computed, ref } from "vue"
import { useStorage } from "@vueuse/core"

import type { UserMe } from "@/types/auth"
import { getMe, login as loginApi, logout as logoutApi, register as registerApi } from "@/api/auth"

export const useAuthStore = defineStore("auth", () => {
  const token = useStorage<string | null>("auth_token", null)
  const me = ref<UserMe | null>(null)
  const isLoading = ref(false)
  const hasError = ref(false)

  const isAuthenticated = computed(() => Boolean(token.value))
  const isAdmin = computed(() => Boolean(me.value?.is_admin))

  async function refreshMe() {
    if (!token.value) return
    isLoading.value = true
    hasError.value = false
    try {
      me.value = await getMe()
    } catch {
      hasError.value = true
    } finally {
      isLoading.value = false
    }
  }

  async function login(username: string, password: string) {
    isLoading.value = true
    hasError.value = false
    try {
      const out = await loginApi({ username, password })
      token.value = out.token
      me.value = { id: out.id, username: out.username, role: out.role, is_admin: out.is_admin }
    } catch {
      hasError.value = true
      throw new Error("登录失败")
    } finally {
      isLoading.value = false
    }
  }

  async function register(username: string, password: string) {
    isLoading.value = true
    hasError.value = false
    try {
      const out = await registerApi({ username, password })
      token.value = out.token
      me.value = { id: out.id, username: out.username, role: out.role, is_admin: out.is_admin }
    } catch {
      hasError.value = true
      throw new Error("注册失败")
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    try {
      if (token.value) {
        await logoutApi()
      }
    } finally {
      token.value = null
      me.value = null
    }
  }

  return {
    token,
    me,
    isLoading,
    hasError,
    isAuthenticated,
    isAdmin,
    refreshMe,
    login,
    register,
    logout,
  }
})
