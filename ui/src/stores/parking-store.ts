import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { statsApi, lotApi } from '@/api/parking'
import type { Ref } from 'vue'

interface Overview {
  total_lots: number
  total_spaces: number
  available_spaces: number
  occupied_spaces: number
  occupancy_rate: number
  active_sessions: number
  pending_violations: number
  today_entries: number
  today_revenue: string
}

export const useParkingStore = defineStore('parking', () => {
  const overview: Ref<Overview | null> = ref(null)
  const lots: Ref<any[]> = ref([])
  const activeLotId: Ref<number | null> = ref(null)
  const loading = ref(false)

  async function fetchOverview() {
    try {
      const res = await statsApi.overview()
      overview.value = res.data.data
    } catch (e) {
      console.error('fetchOverview error', e)
    }
  }

  async function fetchLots() {
    try {
      const res = await lotApi.list()
      lots.value = res.data.data
    } catch (e) {
      console.error('fetchLots error', e)
    }
  }

  const occupancyRate = computed(() => overview.value?.occupancy_rate ?? 0)
  const pendingViolations = computed(() => overview.value?.pending_violations ?? 0)

  return {
    overview,
    lots,
    activeLotId,
    loading,
    occupancyRate,
    pendingViolations,
    fetchOverview,
    fetchLots,
  }
})
