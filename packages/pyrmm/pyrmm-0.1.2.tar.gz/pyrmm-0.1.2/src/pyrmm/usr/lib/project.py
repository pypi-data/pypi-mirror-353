from pathlib import Path
import toml
import shutil
from typing import Any
from pyrmm.usr.lib.fs import RmmFileSystem
from pyrmm.usr.lib.config import Config
from .base import RmmBaseMeta, RmmBase

class RmmProjectMeta(RmmBaseMeta):
    """Meta class for RMM Project"""
    # 项目信息缓存
    _project_cache: dict[str, dict[str, Any]] = {}
    _project_mtime: dict[str, float] = {}
    
    @property
    def META(cls):
        """Get the project metadata."""
        meta: dict[str, str | dict[str, str]] = Config.META
        projects: str | dict[str, str] = meta.get("projects", {})
        if isinstance(projects, str):
            raise AttributeError(f"项目配置错误!： '{projects}' 请检查：{RmmFileSystem.META}")
        return projects
    
    def get_config_key(cls) -> str:
        """获取配置键名"""
        return "projects"
    
    def get_reserved_key(cls) -> str:
        """获取保留关键字"""
        return "rmm"  # 移除 last 保留关键字    def get_item_config(cls, item_name: str) -> dict[str, Any]:
        """获取项目配置"""
        return cls.project_info(cls.project_path(item_name))

    def _set_item_config(cls, name: str, value: dict[str, Any]) -> None:
        """设置项目配置"""
        try:
            project_path = cls.project_path(name)
            project_info = cls.project_info(project_path)
            if project_info:
                project_info.update(value)
                # 将更新后的信息写入项目元数据文件
                meta_file = project_path / "rmmproject.toml"
                with open(meta_file, 'w', encoding='utf-8') as f:
                    toml.dump(project_info, f)
                
                # 清理缓存，确保下次读取时获取最新数据
                cache_key = str(meta_file.resolve())
                if cache_key in cls._project_cache:
                    del cls._project_cache[cache_key]
                if cache_key in cls._project_mtime:
                    del cls._project_mtime[cache_key]
        except Exception as e:
            print(f"设置项目配置时出现错误: {e}")
    def _delete_item_config(cls, name: str) -> None:
        """删除项目配置"""
        try:
            # 尝试获取项目路径
            try:
                project_path = cls.project_path(name)
                # 如果路径存在，删除项目目录及其内容
                if project_path.exists():
                    shutil.rmtree(project_path)
                    print(f"项目目录 '{project_path}' 已删除")
            except (KeyError, FileNotFoundError):
                # 路径不存在或项目不在配置中，这是正常情况，不需要报错
                pass
            
            # 从配置中移除项目记录（无论路径是否存在）
            projects = Config.META.get("projects", {})
            if isinstance(projects, dict) and name in projects:
                del projects[name]
                Config.projects = projects
                print(f"项目 '{name}' 已从配置中移除")
        except Exception as e:
            print(f"删除项目时出现未知错误: {e}")

    def project_path(cls, project_name: str) -> Path:
        """Get the path of a project by its name."""
        projects = cls.META
        if project_name in projects:
            projectpath: Path = Path(projects[project_name])
            if projectpath.exists():
                return projectpath
            else:
                raise FileNotFoundError(f"项目路径不存在: {projectpath}")
        else:
            raise KeyError(f"项目 '{project_name}' 不存在于配置中。")
    
    @classmethod
    def project_info(cls, project_path: Path) -> dict[str, Any]:
        """Get the project information from the project path with caching."""
        if not project_path.exists():
            raise FileNotFoundError(f"项目路径不存在: {project_path}")
        
        # 读取项目的元数据文件
        meta_file = project_path / "rmmproject.toml"
        if not meta_file.exists():
            raise FileNotFoundError(f"项目元数据文件不存在: {meta_file}")
        
        # 使用文件路径作为缓存键
        cache_key = str(meta_file.resolve())
        
        # 检查文件修改时间
        current_mtime = meta_file.stat().st_mtime
        
        # 如果缓存中有数据且文件未修改，直接返回缓存
        if (cache_key in cls._project_cache and 
            cache_key in cls._project_mtime and 
            cls._project_mtime[cache_key] == current_mtime):
            return cls._project_cache[cache_key]
        
        # 读取文件并更新缓存
        with open(meta_file, 'r', encoding='utf-8') as f:
            project_info = toml.load(f)
        
        # 更新缓存
        cls._project_cache[cache_key] = project_info
        cls._project_mtime[cache_key] = current_mtime
        
        return project_info

    def __getattr__(cls, item: str):
        """Get an attribute from the project metadata."""
        if item == cls.get_reserved_key():
            raise KeyError(f"项目 '{cls.get_reserved_key()}' 是保留关键字! 请使用实际项目名称。")
        project_info = cls.project_info(cls.project_path(item))
        if project_info:
            return project_info
        else:
            raise AttributeError(f"项目 '{item}' 的信息未找到。")
class RmmProject(RmmBase, metaclass=RmmProjectMeta):
    """RMM Project class"""
    
    @classmethod
    def add_project(cls, project_name: str, project_path: str) -> None:
        """Add an existing project to the configuration"""
        project_path_obj = Path(project_path)
        
        # 验证项目路径存在且是 RMM 项目
        if not project_path_obj.exists():
            raise FileNotFoundError(f"项目路径不存在: {project_path}")
        
        if not cls.is_rmmproject(project_path_obj):
            raise ValueError(f"路径 {project_path} 不是一个有效的 RMM 项目")
        
        # 获取当前项目配置
        projects = Config.META.get("projects", {})
        if isinstance(projects, dict):
            projects[project_name] = str(project_path_obj.resolve())
            Config.projects = projects
        else:
            raise AttributeError("项目配置格式错误")
    
    @classmethod
    def is_valid_item(cls, item_name: str) -> bool:
        """Check if the given project name corresponds to a valid RMM project."""
        try:
            project_path = cls.project_path(item_name)
            return RmmProject.is_rmmproject(project_path)
        except (KeyError, FileNotFoundError):
            return False
    
    @classmethod
    def get_sync_prompt(cls, item_name: str) -> str:
        """获取同步提示信息"""
        return f"项目 '{item_name}' 不是一个有效的 RMM 项目。移除？"
    
    @classmethod
    def init(cls, project_path: Path):
        """Initialize a new RMM project."""
        project_name = project_path.name
        
        # 确保项目目录存在
        project_path.mkdir(parents=True, exist_ok=True)
          # 创建项目信息
        project_info: dict[str, Any] = {
            "id": project_name,
            "name": project_name,
            "requires_rmm": f">={Config.version}",
            "versionCode": str(project_path.resolve()),
            "updateJson": f"https://raw.githubusercontent.com/{Config.username}/{project_name}/main/update.json",
            "readme": "README.MD",
            "changelog": "CHANGELOG.MD",
            "lecense": "LICENSE",
            "urls": {
                "github": f"https://github.com/{Config.username}/{project_name}"
            },
            "dependencies": [
                {
                    "dep?": "?version",
                }
            ],
            "authors": [
                {
                    "name": Config.username,
                    "email": Config.email
                }
            ],
            "scripts": [
                {
                    "build": "rmm build",
                }
            ],
        }
          # 将项目信息写入项目元数据文件
        meta_file = project_path / "rmmproject.toml"
        with open(meta_file, 'w', encoding='utf-8') as f:
            toml.dump(project_info, f)
          # 创建 module.prop 文件
        module_prop: Path = project_path / "module.prop"
        
        # 获取作者信息
        authors = project_info.get("authors", [{}])
        author_name = authors[0].get("name", Config.username) if authors else Config.username
        
        module_prop_content = {
            "id": str(project_info.get("id", project_name)),
            "name": str(project_info.get("name", project_name)),
            "version": "v1.0.0",  # 默认版本
            "versionCode": "2025060801",  # 默认版本代码
            "author": str(author_name),
            "description": f"RMM项目 {project_name}",
            "updateJson": str(project_info.get("updateJson", ""))
        }
        
        # 写入 module.prop 文件（使用标准的key=value格式）
        with open(module_prop, 'w', encoding='utf-8') as f:
            for key, value in module_prop_content.items():
                f.write(f"{key}={value}\n")
            
        
        # 将项目路径添加到配置中
        projects = Config.META.get("projects", {})
        if isinstance(projects, dict):
            projects[project_name] = str(project_path.resolve())
            Config.projects = projects


        return project_info

    @staticmethod
    def is_rmmproject(project_path: Path) -> bool:
        """Check if the given path is a valid RMM project."""
        meta_file = project_path / "rmmproject.toml"
        return meta_file.exists() and meta_file.is_file()

    @classmethod
    def sync(cls, project_name: str):
        """Sync a project by its name."""
        cls.sync_item(project_name)

    @classmethod
    def init_basic(cls, project_path: Path):
        """Initialize a basic RMM project."""
        cls.init(project_path)
        system_dir = project_path / "system"
        system_dir.mkdir(exist_ok=True)
        return {"message": "RMM basic project initialized."}

    @classmethod
    def init_library(cls, project_path: Path):
        """Initialize a RMM library project."""
        cls.init(project_path)
        # 这里可以添加特定于库项目的初始化逻辑
        # 例如，创建特定的目录结构或文件
        lib_dir = project_path / "lib"
        lib_dir.mkdir(exist_ok=True)
        return {"message": "RMM library project initialized."}


