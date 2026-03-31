#!/usr/bin/env python
"""
前端功能测试脚本
测试前端页面加载、API 连接和基本功能
"""

import subprocess
import sys
import time
import json
from pathlib import Path

try:
    import requests
except ImportError:
    print("正在安装 requests...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

# 配置
BACKEND_URL = "http://127.0.0.1:8001"
FRONTEND_URL = "http://localhost:5175"  # Vite 端口

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

def log_pass(msg):
    print(f"{Colors.GREEN}✓ PASS{Colors.RESET} {msg}")

def log_fail(msg):
    print(f"{Colors.RED}✗ FAIL{Colors.RESET} {msg}")

def log_warn(msg):
    print(f"{Colors.YELLOW}⚠ WARN{Colors.RESET} {msg}")

def log_info(msg):
    print(f"{Colors.BLUE}ℹ INFO{Colors.RESET} {msg}")

def test_backend_health():
    """测试后端服务是否运行"""
    print("\n" + "="*50)
    print("1. 后端服务检测")
    print("="*50)
    
    try:
        resp = requests.get(f"{BACKEND_URL}/api/", timeout=5)
        log_pass(f"后端服务运行中 (状态码: {resp.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        log_fail("后端服务未运行，请先启动: python manage.py runserver")
        return False
    except Exception as e:
        log_fail(f"后端连接错误: {e}")
        return False

def test_frontend_dev_server():
    """测试前端开发服务器是否运行"""
    print("\n" + "="*50)
    print("2. 前端开发服务器检测")
    print("="*50)
    
    try:
        resp = requests.get(FRONTEND_URL, timeout=5)
        if resp.status_code == 200:
            log_pass("前端开发服务器运行中")
            return True
        else:
            log_warn(f"前端服务器响应异常 (状态码: {resp.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        log_fail("前端开发服务器未运行，请在 ui 目录下运行: npm run dev")
        return False
    except Exception as e:
        log_fail(f"前端连接错误: {e}")
        return False

def test_api_endpoints():
    """测试后端 API 端点"""
    print("\n" + "="*50)
    print("3. API 端点测试")
    print("="*50)
    
    endpoints = [
        ("/api/auth/login/", "POST", "登录接口"),
        ("/api/auth/register/", "POST", "注册接口"),
        ("/api/utils/files/list/", "GET", "文件列表"),
        ("/api/auth/me/", "GET", "当前用户信息"),
        ("/api/auth/admin/users/", "GET", "管理员用户列表"),
        ("/api/utils/admin/files/list/", "GET", "管理员文件列表"),
    ]
    
    results = []
    for path, method, desc in endpoints:
        try:
            if method == "GET":
                resp = requests.get(f"{BACKEND_URL}{path}", timeout=5)
            else:
                resp = requests.options(f"{BACKEND_URL}{path}", timeout=5)
            
            # 401/403 表示需要认证，但端点存在
            if resp.status_code in [200, 401, 403, 405]:
                log_pass(f"{desc} ({path}) - 端点可访问")
                results.append(True)
            else:
                log_warn(f"{desc} ({path}) - 状态码: {resp.status_code}")
                results.append(False)
        except Exception as e:
            log_fail(f"{desc} ({path}) - 错误: {e}")
            results.append(False)
    
    return all(results)

def test_static_files():
    """测试前端静态资源"""
    print("\n" + "="*50)
    print("4. 前端静态资源测试")
    print("="*50)
    
    try:
        resp = requests.get(FRONTEND_URL, timeout=5)
        html = resp.text
        
        # 检查关键元素
        checks = [
            ("<!DOCTYPE html>" in html or "<html" in html, "HTML 文档结构"),
            ("<div id=\"app\"" in html or "id=\"app\"" in html, "Vue 挂载点"),
            (".js" in html or "type=\"module\"" in html, "JavaScript 引用"),
        ]
        
        all_pass = True
        for passed, desc in checks:
            if passed:
                log_pass(desc)
            else:
                log_fail(desc)
                all_pass = False
        
        return all_pass
    except Exception as e:
        log_fail(f"静态资源检测失败: {e}")
        return False

def test_frontend_build():
    """检查前端构建配置"""
    print("\n" + "="*50)
    print("5. 前端配置检查")
    print("="*50)
    
    ui_path = Path("ui")
    
    checks = [
        (ui_path / "package.json", "package.json"),
        (ui_path / "vite.config.ts", "Vite 配置"),
        (ui_path / "tailwind.config.js", "Tailwind 配置"),
        (ui_path / "src" / "style.css", "样式文件"),
        (ui_path / "src" / "main.ts", "入口文件"),
        (ui_path / "src" / "App.vue", "根组件"),
    ]
    
    all_pass = True
    for file_path, desc in checks:
        if file_path.exists():
            log_pass(f"{desc} 存在")
        else:
            log_fail(f"{desc} 缺失 ({file_path})")
            all_pass = False
    
    # 检查 node_modules
    if (ui_path / "node_modules").exists():
        log_pass("依赖已安装 (node_modules)")
    else:
        log_fail("依赖未安装，请运行: cd ui && npm install")
        all_pass = False
    
    return all_pass

def test_tailwind_config():
    """检查 Tailwind CSS 配置"""
    print("\n" + "="*50)
    print("6. Tailwind CSS 配置检查")
    print("="*50)
    
    style_path = Path("ui/src/style.css")
    if not style_path.exists():
        log_fail("style.css 不存在")
        return False
    
    content = style_path.read_text(encoding="utf-8")
    
    # Tailwind v4 使用 @import "tailwindcss"
    # Tailwind v3 使用 @tailwind base/components/utilities
    if '@import "tailwindcss"' in content:
        log_pass("使用 Tailwind v4 语法")
        if "@theme" in content:
            log_pass("自定义主题配置存在")
        else:
            log_warn("未找到 @theme 配置块")
    elif "@tailwind" in content:
        log_pass("使用 Tailwind v3 语法")
    else:
        log_fail("未找到 Tailwind 导入语句")
        return False
    
    return True

def test_vue_components():
    """检查关键 Vue 组件"""
    print("\n" + "="*50)
    print("7. Vue 组件检查")
    print("="*50)
    
    components = [
        "ui/src/pages/home-page.vue",
        "ui/src/pages/auth/login-page.vue",
        "ui/src/pages/auth/register-page.vue",
        "ui/src/pages/utils/files-page.vue",
        "ui/src/pages/admin/users-page.vue",
        "ui/src/pages/admin/files-page.vue",
        "ui/src/components/app-shell/app-shell.vue",
    ]
    
    all_pass = True
    for comp_path in components:
        path = Path(comp_path)
        if path.exists():
            content = path.read_text(encoding="utf-8")
            # 基本语法检查
            has_script = "<script" in content
            has_template = "<template" in content
            
            if has_script and has_template:
                log_pass(f"{path.name}")
            else:
                log_warn(f"{path.name} - 结构不完整")
        else:
            log_fail(f"{path.name} 不存在")
            all_pass = False
    
    return all_pass

def check_import_errors():
    """检查常见的导入错误"""
    print("\n" + "="*50)
    print("8. 导入错误检查")
    print("="*50)
    
    # 检查 lucide-vue-next 图标导入
    vue_files = list(Path("ui/src").rglob("*.vue"))
    
    # 已知不存在的图标名称
    invalid_icons = ["ShieldCheckmark"]  # 正确的是 ShieldCheck
    
    issues = []
    for vue_file in vue_files:
        try:
            content = vue_file.read_text(encoding="utf-8")
            for icon in invalid_icons:
                if icon in content:
                    issues.append((vue_file.name, icon))
        except:
            pass
    
    if issues:
        for file_name, icon in issues:
            log_fail(f"{file_name} 使用了无效图标: {icon}")
        return False
    else:
        log_pass("未发现已知的导入错误")
        return True

def main():
    print("\n" + "="*50)
    print("   前端功能测试脚本")
    print("="*50)
    
    results = {
        "后端服务": test_backend_health(),
        "前端服务": test_frontend_dev_server(),
        "API 端点": test_api_endpoints(),
        "静态资源": test_static_files(),
        "前端配置": test_frontend_build(),
        "Tailwind": test_tailwind_config(),
        "Vue 组件": test_vue_components(),
        "导入检查": check_import_errors(),
    }
    
    print("\n" + "="*50)
    print("   测试结果汇总")
    print("="*50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = f"{Colors.GREEN}通过{Colors.RESET}" if result else f"{Colors.RED}失败{Colors.RESET}"
        print(f"  {name}: {status}")
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print(f"\n{Colors.GREEN}所有测试通过！{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.YELLOW}部分测试未通过，请检查上述问题。{Colors.RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
