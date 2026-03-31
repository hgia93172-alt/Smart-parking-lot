import ElementPlus from "element-plus"
import "element-plus/dist/index.css"
import { createApp } from "vue"
import { MotionPlugin } from "@vueuse/motion"
import "./style.css"
import App from "./App.vue"
import { router } from "./router"
import { pinia } from "./stores"

const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(ElementPlus)
app.use(MotionPlugin)

app.mount("#app")
