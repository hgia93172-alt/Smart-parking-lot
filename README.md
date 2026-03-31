# 智能停车场车辆监测管理系统 (Smart Parking System)

基于 **YOLOv11**、**DeepSORT**、**Django 5.2** 以及 **Vue 3** 开发的智慧停车场全栈管理系统。该系统集成了车辆实时检测、车位自动监测、阶梯计费以及违规预警功能。

---

## 🌟 核心功能

*   **智能车辆检测与跟踪**：使用 YOLOv11 进行多车型（轿车、卡车、巴士、摩托车）识别，并配合 DeepSORT 实现跨帧稳定跟踪。
*   **车位自动占用监测**：基于 IOU 算法，自动判断预设车位是否被车辆占用，实时更新前端库位图。
*   **阶梯化计费系统**：支持针对不同车型（如小型车、货车）设置差异化计费规则，支持免费时长及日封顶金额。
*   **违规报警系统**：支持划定“消防通道”或“禁止停车区”，对长时间停留车辆自动触发违规报警。
*   **可视化仪表盘**：基于 ECharts 提供 24 小时流量统计、实战占用率分析及营收报表。
*   **模拟演示模式**：提供内置模拟器，无需 GPU 或摄像头即可在本地演示完整的检测流程。

---

## 🛠️ 技术栈

*   **后端**: Python 3.13+, Django 5.2, Django REST Framework (DRF)
*   **前端**: Vue 3, Vite, Naive UI / Element Plus, Pinia, ECharts
*   **AI 引擎**: Ultralytics YOLOv11, DeepSORT-Realtime (可选)
*   **数据库**: SQLite (默认), 可轻松切换至 MySQL 或 PostgreSQL

---

## 🚀 快速启动

### 1. 克隆与环境配置 (后端)
确保已安装 Python，在根目录下执行：

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 初始化数据库
python manage.py makemigrations parking
python manage.py migrate

# 生成演示数据 (包含 admin 账号)
python seed_demo.py
```

### 2. 前端环境配置
在 `ui` 目录下执行：

```bash
cd ui
npm install
npm run dev
```

### 3. 启动 AI 检测模块 (模拟模式)
在另一个终端窗口运行 AI 演示程序。使用 `--simulate` 参数可在无摄像头和模型文件时生成模拟轨迹：

```bash
python parking_ai/main.py --simulate --token <YOUR_TOKEN>
```

---

## 🔐 演示账号

*   **系统地址**: `http://localhost:5173`
*   **后端 API**: `http://127.0.0.1:8000`
*   **用户名**: `admin`
*   **密码**: 运行 `python seed_demo.py` 时会在控制台输出（或通过环境变量 `DEMO_ADMIN_PASSWORD` 指定）

---

## 📸 如何切换到真实视频/摄像头？

若要使用真实的 YOLO 模型识别真实视频或 RTSP 流，请修改启动命令：

1.  准备 YOLOv11 权重文件 `yolov11n.pt` 存放在根目录。
2.  运行以下命令：

```bash
# --source 0 为本地摄像头，也可填 RTSP 地址或视频文件路径
python parking_ai/main.py --model yolov11n.pt --source 0 --token <YOUR_TOKEN>
```

---

## 📝 目录结构

*   `parking/`: Django 后端应用（模型、计费逻辑、API）。
*   `parking_ai/`: AI 检测核心模块（YOLO、跟踪器、监控逻辑）。
*   `ui/`: Vue 3 前端工程代码。
*   `seed_demo.py`: 初始化脚本。

---

## 📜 许可证

本项目基于 MIT License 协议开发。用于教学或二次开发。
