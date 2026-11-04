# common_flutter

Flutter 公共组件封装，统一通过以下入口导入：

```dart
import 'package:common_flutter/common_flutter.dart';
```

## 组件

- 菜单按钮：`CMenuButtonCard`、`CMenuButtonFilled`
- 复选框与分隔线：`CCheckboxPlus`、`CDividerPlus`
- 页面与页签：`CPageBase`、`CPageMenu`、`CTabs`、`TabType`
- 隐私政策展示：`AirbnbPrivacyPolicyView`
- 搜索：`CSearch`，支持输入和清空回调
- 筛选：`CFilterList`、`FilterItem`、`TypeCard`，支持横向两行多选

搜索与筛选延续 Flutter Hooks 风格。筛选状态由调用方创建、维护并释放
`ValueNotifier<List<FilterItem>>`，组件会自行监听变化；卡片颜色使用宿主
`ThemeData.colorScheme`，支持明暗主题。

```dart
final items = useState<List<FilterItem>>([
  const FilterItem(text: '推荐', isSelected: false),
  const FilterItem(text: '收藏', icon: Icons.star, isSelected: true),
]);

return CFilterList(items: items);
```

上例在 `HookWidget.build` 中使用，需导入 `flutter/material.dart` 和
`flutter_hooks/flutter_hooks.dart`。

## 迁入的半成品与占位

这些内容保留了旧项目的进度，本次未补齐功能：

- `CButton`：基础按钮雏形，点击仅输出日志，尚无业务回调。
- `CPhoneForm`：只有国家/地区只读输入框，点击仅输出日志；无国家选择、手机号、验证码或登录流程。
- `src/auth/clause.dart`：隐私声明与服务条款确认占位。
- `src/popover/popover.dart`：居中弹层占位。
- `src/sheet/delete.dart`、`menu.dart`：底部删除与菜单占位。
- `src/other/super_listview.dart`：刷新与分页列表设想。
- `src/other/super_title.dart`：左滑操作设想。

完整迁移对应关系见 [迁移记录](doc/migration.md)。旧 `_common_flutter2` 项目已合并删除。

## 示例与验证

现有演示统一位于 `example`。首页可访问按钮、页签、隐私政策，以及迁入的
搜索、筛选和登录表单演示。

```bash
flutter pub get
dart format lib test example/lib example/test
flutter analyze
flutter test
cd example
flutter test
flutter run -d macos
```

需要重新生成 Freezed 代码时：

```bash
dart run build_runner watch -d
```

发布前运行 `flutter pub publish --dry-run`。仓库保留了按版本标签触发的发布工作流，
发布前需核对工作流的 Flutter SDK 版本与当前包的 SDK 约束。
