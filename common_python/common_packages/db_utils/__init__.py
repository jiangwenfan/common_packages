# try:
#     from .clickhouse_utils import ClickhouseOperator
# except ImportError:
#     pass
# try:
#     from .mysql_utils import MysqlOperator
# except ImportError:
#     pass


# class _LazyImport:
#     def __init__(self, module_name, class_name):
#         self.module_name = module_name
#         self.class_name = class_name
#         self._module = None

#     def _load(self):
#         if self._module is None:
#             self._module = __import__(self.module_name, fromlist=[self.class_name])

#     def __getattr__(self, item):
#         self._load()
#         return getattr(self._module, item)


# # 使用 _LazyImport 来实现延迟导入

# ClickhouseOperator = _LazyImport(
#     "common_packages.db_utils.clickhouse_utils", "ClickhouseOperator"
# )
# MysqlOperator = _LazyImport("common_packages.db_utils.mysql_utils", "MysqlOperator")
