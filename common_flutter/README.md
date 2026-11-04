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
- 网络：`DioClient`、`AuthInterceptor`、`ApiResponse`、`UIErrMessage`、`HandledRequestException`
- 示例控件：`MyCustomWidget`，文字跟随宿主主题

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

`common_flutter_old3` 的网络封装、示例及未完成的平台接口也已合并，详见
[old3 迁移记录](doc/common_flutter_old3_migration.md)。

## 网络封装

```dart
final client = DioClient(baseUrl: 'https://api.example.test');
try {
  final response = await client.get('/customers/', queryParameters: {'page': 1});
  if (!response.isSuccess) {
    final message = response.payload as UIErrMessage;
    // 400 时可读取字段错误，其余错误可读取 message.errorMessage['_']。
  }
} finally {
  client.close();
}
```

每个客户端独立维护服务地址，业务层可自行复用实例，并在不用时调用 `close()`。
GET / POST 成功返回响应数据；已处理的 HTTP、网络和认证读取错误返回
`ApiResponse(isSuccess: false, payload: UIErrMessage(...))`。
取消请求保留 Dio 的取消异常。

`AuthInterceptor` 延用旧项目的安全存储：

```dart
await secureStorage.write(key: 'access_token', value: token);
await secureStorage.write(key: 'headers', value: '{"x-customer-id":"4"}');
```

请求时自动添加 `Authorization: Bearer ...` 与存储的自定义请求头。
`headers` 必须是 JSON 对象；读取或解析失败会返回错误，结束本次请求。
认证存储使用 `flutter_secure_storage`，接入应用需配置相应平台的安全存储能力。
现有示例已补充 macOS 网络访问和 Android 网络权限配置。
macOS 正式使用安全存储前，需在宿主应用中配置开发签名及 Keychain Sharing；
默认示例不预置需要开发证书的 Keychain 共享声明，便于直接启动演示。

## 未完成的平台接口

`CommonFlutter`、`CommonFlutterPlatform`、`MethodChannelCommonFlutter` 保留了
旧 `getPlatformVersion` 通道协议，但没有配套的原生插件实现。
当前包没有声明该原生插件注册，直接调用可能抛出 `MissingPluginException`。
示例页面会显示未实现提示；本次没有补齐原生功能。

## 示例与验证

现有演示统一位于 `example`。首页可访问按钮、页签、隐私政策，以及迁入的
搜索、筛选和登录表单演示。
新增的 Dio 请求演示默认不配置地址、不会发起请求。需要连接自己的演示服务时：

```bash
cd example
flutter run -d macos --dart-define=DEMO_API_BASE_URL=https://api.example.test
```

上述域名是占位值，需要替换为自己的服务地址；旧演示保留的登录账号也为空。
401 / 400 / 500 按钮标签延用原示例意图，实际响应由服务端决定，不在客户端模拟状态码。

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
