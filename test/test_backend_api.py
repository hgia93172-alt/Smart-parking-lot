#!/usr/bin/env python
"""
后端接口联调测试脚本（自动启动 runserver）

覆盖点：
1) 管理端用户增删改查 + 分页
2) 用户端文件增删改查 + 分页
3) 操作日志写入 + 管理端日志列表/删除 + 分页

运行方式（建议在 conda 环境 all 中执行）：
python test/test_backend_api.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:  # pragma: no cover
    print("正在安装 requests...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests


def _project_root() -> Path:
    """返回项目根目录路径。"""
    return Path(__file__).resolve().parent.parent


def _python_executable() -> str:
    """返回当前 Python 可执行路径（用于复用当前 conda 环境）。"""
    return sys.executable


def _ensure_admin_user(username: str, password: str) -> None:
    """通过 ORM 创建/更新管理员用户，便于后续走 API 测试管理端能力。"""
    root = _project_root()
    sys.path.insert(0, str(root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_main.settings")
    import django

    django.setup()

    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.filter(username=username).first()
    if user is None:
        user = User.objects.create_user(username=username, password=password)
    else:
        user.set_password(password)

    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()


def _run_manage_py(args: list[str]) -> None:
    """运行 manage.py 子命令（阻塞）。"""
    root = _project_root()
    subprocess.check_call([_python_executable(), "manage.py", *args], cwd=str(root))


def _start_server(host: str, port: int) -> subprocess.Popen:
    """启动 Django 开发服务器并返回进程句柄。"""
    root = _project_root()
    env = os.environ.copy()
    env.setdefault("DJANGO_SETTINGS_MODULE", "django_main.settings")
    return subprocess.Popen(
        [_python_executable(), "manage.py", "runserver", f"{host}:{port}"],
        cwd=str(root),
        env=env,
    )


def _wait_server_ready(base_url: str, timeout_sec: int = 30) -> None:
    """轮询等待后端服务就绪。"""
    start = time.time()
    last_err: Exception | None = None
    while time.time() - start < timeout_sec:
        try:
            r = requests.get(f"{base_url}/admin/", timeout=2, allow_redirects=False)
            if r.status_code in (200, 301, 302, 403):
                return
        except Exception as e:
            last_err = e
        time.sleep(0.5)
    raise RuntimeError(f"后端服务启动超时: {last_err}")


def _auth_headers(token: str | None) -> dict[str, str]:
    """构造 Token 认证请求头。"""
    if not token:
        return {}
    return {"Authorization": f"Token {token}"}


def _safe_json(resp: requests.Response) -> dict:
    """尽可能解析 JSON；失败时返回原始内容片段，便于定位问题。"""
    try:
        return resp.json()
    except Exception:
        text = resp.text or ""
        return {"_raw": text[:20000]}



def _post_json(base_url: str, path: str, payload: dict, token: str | None = None) -> dict:
    """POST JSON 并返回 JSON。"""
    r = requests.post(
        f"{base_url}{path}",
        json=payload,
        headers={"Accept": "application/json", **_auth_headers(token)},
        timeout=10,
    )
    return {"status": r.status_code, "json": _safe_json(r)}


def _patch_json(base_url: str, path: str, payload: dict, token: str | None = None) -> dict:
    """PATCH JSON 并返回 JSON。"""
    r = requests.patch(
        f"{base_url}{path}",
        json=payload,
        headers={"Accept": "application/json", **_auth_headers(token)},
        timeout=10,
    )
    return {"status": r.status_code, "json": _safe_json(r)}


def _get_json(base_url: str, path: str, token: str | None = None) -> dict:
    """GET 并返回 JSON。"""
    r = requests.get(
        f"{base_url}{path}",
        headers={"Accept": "application/json", **_auth_headers(token)},
        timeout=10,
    )
    return {"status": r.status_code, "json": _safe_json(r)}


def _delete(base_url: str, path: str, token: str | None = None) -> dict:
    """DELETE 并返回 JSON。"""
    r = requests.delete(
        f"{base_url}{path}",
        headers={"Accept": "application/json", **_auth_headers(token)},
        timeout=10,
    )
    return {"status": r.status_code, "json": _safe_json(r)}


def _upload_file(base_url: str, path: str, token: str, filename: str, content: bytes) -> dict:
    """上传文件并返回 JSON。"""
    r = requests.post(
        f"{base_url}{path}",
        files={"file": (filename, content, "application/octet-stream")},
        headers={"Accept": "application/json", **_auth_headers(token)},
        timeout=30,
    )
    return {"status": r.status_code, "json": _safe_json(r)}


def _assert_ok(resp: dict, msg: str) -> dict:
    """断言统一返回结构成功。"""
    assert resp["status"] == 200, f"{msg}: http={resp['status']} body={resp.get('json')}"
    body = resp["json"]
    assert body.get("code") == 20001, f"{msg}: code={body.get('code')} body={body}"
    return body


def main() -> int:
    """脚本入口。"""
    host = "127.0.0.1"
    port = 8000
    base_url = f"http://{host}:{port}"

    admin_username = "admin_test"
    admin_password = "AdminPass123!"

    user_username = f"user_{int(time.time())}"
    user_password = "UserPass123!"

    server: subprocess.Popen | None = None
    try:
        _run_manage_py(["migrate", "--noinput"])
        _ensure_admin_user(admin_username, admin_password)

        server = _start_server(host, port)
        _wait_server_ready(base_url)

        admin_login = _assert_ok(
            _post_json(base_url, "/api/auth/login/", {"username": admin_username, "password": admin_password}),
            "管理员登录失败",
        )
        admin_token = admin_login["data"]["token"]

        created = _assert_ok(
            _post_json(
                base_url,
                "/api/auth/admin/users/",
                {"username": user_username, "password": user_password, "role": "user"},
                token=admin_token,
            ),
            "管理员创建用户失败",
        )
        user_id = created["data"]["id"]

        users_page = _assert_ok(
            _get_json(base_url, "/api/auth/admin/users/?page=1&page_size=2", token=admin_token),
            "管理员用户列表分页失败",
        )
        assert isinstance(users_page["data"].get("results"), list), "用户分页 results 不是 list"

        detail = _assert_ok(
            _get_json(base_url, f"/api/auth/admin/users/{user_id}/", token=admin_token),
            "管理员获取用户详情失败",
        )
        assert detail["data"]["id"] == user_id

        new_password = "NewPass_123456"
        _assert_ok(
            _patch_json(
                base_url,
                f"/api/auth/admin/users/{user_id}/",
                {"password": new_password, "is_staff": True, "is_active": True, "role": "ops"},
                token=admin_token,
            ),
            "管理员修改用户密码/权限失败",
        )

        updated_detail = _assert_ok(
            _get_json(base_url, f"/api/auth/admin/users/{user_id}/", token=admin_token),
            "管理员修改后获取用户详情失败",
        )
        assert updated_detail["data"]["is_staff"] is True
        assert updated_detail["data"]["is_active"] is True
        assert updated_detail["data"]["role"] == "ops"

        user_login = _assert_ok(
            _post_json(base_url, "/api/auth/login/", {"username": user_username, "password": new_password}),
            "普通用户使用新密码登录失败",
        )
        user_token = user_login["data"]["token"]

        _assert_ok(
            _patch_json(base_url, f"/api/auth/admin/users/{user_id}/", {"is_active": False}, token=admin_token),
            "管理员禁用用户失败",
        )
        disabled_login = _post_json(base_url, "/api/auth/login/", {"username": user_username, "password": new_password})
        assert disabled_login["status"] in (400, 403), f"禁用用户后仍可登录: http={disabled_login['status']} body={disabled_login.get('json')}"

        _assert_ok(
            _patch_json(base_url, f"/api/auth/admin/users/{user_id}/", {"is_active": True}, token=admin_token),
            "管理员重新启用用户失败",
        )

        uploaded = _assert_ok(
            _upload_file(base_url, "/api/utils/files/upload/", user_token, "hello.txt", b"hello"),
            "上传文件失败",
        )
        file_id = uploaded["data"]["id"]

        files_page = _assert_ok(
            _get_json(base_url, "/api/utils/files/list/?page=1&page_size=5", token=user_token),
            "用户文件列表分页失败",
        )
        assert any(x["id"] == file_id for x in files_page["data"]["results"])

        patched = _assert_ok(
            _patch_json(
                base_url,
                f"/api/utils/files/{file_id}/",
                {"original_name": "renamed.txt"},
                token=user_token,
            ),
            "用户修改文件信息失败",
        )
        assert patched["data"]["original_name"] == "renamed.txt"

        fetched = _assert_ok(
            _get_json(base_url, f"/api/utils/files/{file_id}/", token=user_token),
            "用户获取文件详情失败",
        )
        assert fetched["data"]["original_name"] == "renamed.txt"

        _assert_ok(_delete(base_url, f"/api/utils/files/{file_id}/", token=user_token), "用户删除文件失败")

        logs_page = _assert_ok(
            _get_json(base_url, "/api/utils/admin/logs/list/?page=1&page_size=10", token=admin_token),
            "管理员日志列表分页失败",
        )
        assert logs_page["data"]["count"] >= 1
        first_log_id = logs_page["data"]["results"][0]["id"]
        _assert_ok(_delete(base_url, f"/api/utils/admin/logs/{first_log_id}/", token=admin_token), "管理员删除日志失败")

        _assert_ok(_delete(base_url, "/api/utils/admin/logs/clear/", token=admin_token), "管理员清空日志失败")

        print("全部测试通过")
        return 0
    finally:
        if server is not None and server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except Exception:
                server.kill()


if __name__ == "__main__":
    raise SystemExit(main())
