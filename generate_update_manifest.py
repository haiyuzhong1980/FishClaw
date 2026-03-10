#!/usr/bin/env python3
"""
更新清单生成工具

此脚本用于生成更新清单，包含所有可更新文件的MD5哈希值和大小信息。
生成的清单可用于 GitHub Releases + tag 文件热更新方案。

使用方法：
    python generate_update_manifest.py

输出：
    - 生成 update_files.json 文件
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

DEFAULT_GITHUB_OWNER = "GuDong2003"
DEFAULT_GITHUB_REPO = "xianyu-auto-reply-fix"

# 可更新的文件列表（相对路径）
UPDATABLE_FILES = [
    # 前端文件（不需要重启）
    'static/version.txt',
    'static/index.html',
    'static/js/app.js',
    # 后端核心文件（需要重启）
    'auto_updater.py',
    'reply_server.py',
    'XianyuAutoAsync.py',
    'db_manager.py',
    # 'cookie_manager.py',
    # 'ai_reply_engine.py',
    # 'auto_updater.py',
    # 'config.py',
    # 'Start.py',
    
    # 工具文件
    # 'utils/xianyu_utils.py',
    # 'utils/message_utils.py',
    # 'utils/image_utils.py',
    # 'utils/qr_login.py',
    # 'utils/refresh_util.py',
    
    # 配置文件模板（不更新用户的实际配置）
    # 'global_config.yml',  # 用户配置，不更新
]

# 不需要重启的文件扩展名
NO_RESTART_EXTENSIONS = {'.js', '.css', '.html', '.json', '.yml', '.yaml'}


def calculate_md5(file_path: Path) -> str:
    """计算文件MD5"""
    if not file_path.exists():
        return ""
    
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def get_file_size(file_path: Path) -> int:
    """获取文件大小"""
    if not file_path.exists():
        return 0
    return file_path.stat().st_size


def needs_restart(file_path: str) -> bool:
    """判断文件更新是否需要重启"""
    ext = Path(file_path).suffix.lower()
    return ext not in NO_RESTART_EXTENSIONS


def build_raw_download_url(owner: str, repo: str, version: str, relative_path: str) -> str:
    """构建 GitHub raw 文件下载地址"""
    relative_path = relative_path.replace('\\', '/').lstrip('/')
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{version}/{relative_path}"


def read_version(base_dir: Path, fallback: str = "v1.0.0") -> str:
    """读取版本号"""
    version_file = base_dir / "static" / "version.txt"
    if version_file.exists():
        version = version_file.read_text(encoding='utf-8').strip()
        if version:
            return version
    return fallback


def read_repo_config() -> tuple[str, str]:
    """读取 GitHub 仓库配置，优先环境变量，其次默认值"""
    owner = os.environ.get("UPDATE_GITHUB_OWNER", "").strip()
    repo = os.environ.get("UPDATE_GITHUB_REPO", "").strip()
    if owner and repo:
        return owner, repo

    repository = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if repository and "/" in repository:
        repo_owner, repo_name = repository.split("/", 1)
        if repo_owner and repo_name:
            return repo_owner, repo_name

    return DEFAULT_GITHUB_OWNER, DEFAULT_GITHUB_REPO


def generate_manifest(
    base_dir: Path,
    version: str = "v1.0.0",
    owner: str = DEFAULT_GITHUB_OWNER,
    repo: str = DEFAULT_GITHUB_REPO
) -> dict:
    """生成更新清单"""
    files = []
    
    for file_path in UPDATABLE_FILES:
        full_path = base_dir / file_path
        
        if not full_path.exists():
            print(f"警告: 文件不存在 - {file_path}")
            continue
        
        md5 = calculate_md5(full_path)
        size = get_file_size(full_path)
        
        files.append({
            'path': file_path.replace('\\', '/'),
            'md5': md5,
            'size': size,
            'download_url': build_raw_download_url(owner, repo, version, file_path),
            'requires_restart': needs_restart(file_path),
            'description': '',
        })
    
    manifest = {
        'version': version,
        'release_date': datetime.now().strftime('%Y-%m-%d'),
        'description': f'版本 {version} 更新',
        'min_version': 'v1.0.0',
        'changelog': [
            'GitHub Releases 热更新清单',
        ],
        'files': files,
    }
    
    return manifest


def print_manifest_summary(manifest: dict):
    """打印清单摘要"""
    print("\n" + "=" * 60)
    print("更新清单摘要")
    print("=" * 60 + "\n")

    print(f"版本号: {manifest['version']}")
    print(f"发布日期: {manifest['release_date']}")
    print(f"文件数量: {len(manifest['files'])}")
    total_size = sum(f['size'] for f in manifest['files'])
    print(f"总大小: {total_size / 1024:.2f} KB")
    print("示例下载地址:")
    if manifest['files']:
        print(f"  {manifest['files'][0]['download_url']}")


def main():
    # 获取项目根目录
    if len(sys.argv) > 1:
        base_dir = Path(sys.argv[1])
    else:
        base_dir = Path(__file__).parent
    
    # 获取版本号
    version = read_version(base_dir)
    if len(sys.argv) > 2:
        version = sys.argv[2]

    owner, repo = read_repo_config()
    if len(sys.argv) > 3:
        owner = sys.argv[3]
    if len(sys.argv) > 4:
        repo = sys.argv[4]
    
    print(f"项目目录: {base_dir}")
    print(f"版本号: {version}")
    print(f"GitHub 仓库: {owner}/{repo}")
    
    # 生成清单
    manifest = generate_manifest(base_dir, version, owner, repo)
    
    # 保存JSON文件
    output_file = base_dir / "update_files.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\n已生成: {output_file}")
    
    # 打印摘要
    print_manifest_summary(manifest)
    
    print("\n" + "=" * 60)
    print("使用说明")
    print("=" * 60)
    print("""
1. 将当前版本代码提交并打上 Git tag（如 v1.5.0）
2. 发布 GitHub Release，并确保对应 tag 已存在
3. 生成的 update_files.json 会上传到 GitHub Release 作为更新清单
4. 用户在前端点击"一键热更新"后，会先读取 GitHub Releases 最新版本，再从对应 tag 下载文件
""")


if __name__ == '__main__':
    main()

