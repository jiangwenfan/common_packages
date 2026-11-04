# common_flutter 示例

```bash
flutter pub get
flutter run -d macos
```

首页包含原有按钮、页签、隐私政策示例，以及合并后的搜索、筛选和登录表单示例。
基础按钮与登录表单保留雏形状态，尚未实现业务回调和登录流程。

另外包含从 `common_flutter_old3` 合并的 Dio 请求演示和平台接口雏形。
平台查询缺少原生实现时会显示提示，不影响其他页面。

Dio 演示默认没有服务地址，所有请求按钮禁用；配置自己的演示服务后可运行：

```bash
flutter run -d macos --dart-define=DEMO_API_BASE_URL=https://api.example.test
```

域名是占位值，需要替换。登录账号在 `lib/demo_dio/widgets.dart` 中仍为空，
本次未补齐登录表单或后台服务。错误按钮延用原请求及请求数据，实际状态码由服务端决定。
演示会修改本应用存储的 `access_token`、`headers`，沿用原示例行为。
macOS 实际使用安全存储前需配置开发签名和 Keychain Sharing。
默认示例未加入需要开发证书的 Keychain 共享声明；自动化测试使用模拟存储。

运行演示交互测试：

```bash
flutter test
```
