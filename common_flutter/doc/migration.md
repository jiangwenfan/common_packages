# _common_flutter2 合并记录

本次完整合并已有实现、半成品和仅含注释的占位内容，不补齐未完成功能。
公共入口为 `lib/common_flutter.dart`，演示与组件代码分离。

下表左侧相对旧 `_common_flutter2`，右侧相对当前 `common_flutter`：

| 原位置 | 合并位置或处理方式 |
| --- | --- |
| `lib/widgets/search/core.dart` | `lib/src/search/search.dart` |
| `lib/widgets/search/features.dart` | `example/lib/pages/search.dart`；导出归入公共入口 |
| `lib/widgets/filter_list/core.dart` | `lib/src/filter_list/filter_list.dart` 与 `filter_item.dart` |
| `lib/widgets/filter_list/type_card.dart` | `lib/src/filter_list/type_card.dart` |
| `lib/widgets/filter_list/features.dart` | `example/lib/pages/filter_list.dart`；导出归入公共入口 |
| `lib/widgets/button/feature.dart` | `lib/src/buttons/button.dart`；演示归入现有按钮页 |
| `lib/widgets/auth/phone_code.dart` | `lib/src/auth/phone_code.dart` |
| `lib/widgets/auth/clause.dart` | `lib/src/auth/clause.dart`，保留占位 |
| `lib/widgets/auth/feature.dart` | `example/lib/pages/auth.dart`；导出归入公共入口 |
| `lib/widgets/other/super_listview.dart` | `lib/src/other/super_listview.dart`，保留设想与参考链接 |
| `lib/widgets/other/super_title.dart` | `lib/src/other/super_title.dart`，保留设想 |
| `lib/widgets/popover/core.dart`、`feature.dart` | `lib/src/popover/popover.dart`，保留占位 |
| `lib/widgets/sheet/delete.dart` | `lib/src/sheet/delete.dart`，保留占位 |
| `lib/widgets/sheet/menu.dart` | `lib/src/sheet/menu.dart`，保留占位 |
| `lib/app.dart` | `example/lib/pages/widgets.dart`，保留原组件组合演示 |
| `lib/main.dart` | 合入现有 `example/lib/main.dart` 与 `router.dart`，移除重复的应用与页面壳 |
| `test/widget_test.dart` | 合入 `example/test/widget_test.dart`，以实际演示交互替换已失效的计数器模板测试 |
| `README.md` | Flutter 使用、运行和发布说明并入当前 README；通用 Flutter 入门模板去重 |

旧 README 中的 `common_dart` 段落属于独立 Dart 包，其源码与文档仍保留在仓库的
`common_dart` 目录，不引入 Flutter 包。旧 README 的“增加 codex 的 agents”备注未实现，
仅在此保留记录，不新增配置。

## 修复与清理

- `CFilterList` 自行监听传入的 `ValueNotifier`，不再依赖父页面监听后重建。
- 筛选卡片从固定蓝灰色改为使用宿主主题，并由 `Material` 承载点击水波纹。
- 搜索清空后保留焦点，显式发送一次空字符串回调。
- 日志改用 `debugPrint`；登录雏形替换已弃用的颜色透明度调用。
- 删除公共入口和测试中的 `Calculator` 脚手架，清理已有的分析警告。
- 所有原文件均完成上述归并后，删除旧目录，不保留重复实现。
