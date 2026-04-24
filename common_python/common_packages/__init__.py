import importlib

# TODO: common_packages --> common_utils


class CommonPackageManager:
    """公共包管理器"""

    def _check_dependencies(self, module_names: list[str]):
        """检查依赖项是否已安装"""
        for module_name in module_names:
            try:
                setattr(self, module_name, importlib.import_module(module_name))
            except ImportError:
                print(
                    f"Missing required dependencies. use pip install {module_name} to install it."
                )
