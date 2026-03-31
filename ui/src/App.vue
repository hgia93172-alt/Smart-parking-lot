<script setup lang="ts">
import { NConfigProvider, NGlobalStyle, NMessageProvider, NDialogProvider, NNotificationProvider } from "naive-ui"
import type { GlobalThemeOverrides } from "naive-ui"
import { zhCN, dateZhCN } from "naive-ui"

/**
 * Figma-inspired theme overrides for Naive UI
 * Using bold blacks, refined grays, and precise border radiuses
 */
const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#000000',
    primaryColorHover: '#262626',
    primaryColorPressed: '#000000',
    primaryColorSuppl: '#404040',
    borderRadius: '8px',
    fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
  },
  Button: {
    borderRadiusMedium: '8px',
    fontWeightStrong: '700',
  },
  Card: {
    borderRadius: '12px',
    titleFontWeight: '800',
  },
  Input: {
    borderRadius: '8px',
    borderHover: '1px solid #000',
    borderFocus: '1px solid #000',
    boxShadowFocus: '0 0 0 2px rgba(0,0,0,0.05)',
  },
  InternalSelectMenu: {
    borderRadius: '8px',
  },
  InternalSelection: {
    borderRadius: '8px',
  }
}
</script>

<template>
  <n-config-provider 
    :locale="zhCN" 
    :date-locale="dateZhCN" 
    :theme-overrides="themeOverrides"
    class="h-full"
  >
    <n-global-style />
    <n-message-provider>
      <n-dialog-provider>
        <n-notification-provider>
          <router-view />
        </n-notification-provider>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
  background-color: #F5F5F5; /* Matches Tailwind canvas DEFAULT */
}

body {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Global scrollbar styling */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #E5E7EB;
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: #D1D5DB;
}
</style>
