# common_flutter_old3 合并记录

来源为 `_backup_code/common_flutter_old3`，共 83 个文件。
已有实现、半成品与演示全部归并后删除来源目录。没有补齐原生插件或后台服务。
以下目标路径均相对当前 `common_flutter`。

## 组件、工具和入口

| 原位置 | 合并位置或处理方式 |
| --- | --- |
| `lib/src_utils/dio_utils/dio_client.dart` | `lib/src/utils/dio_utils/dio_client.dart` |
| `lib/src_utils/dio_utils/auth_interceptor.dart` | `lib/src/utils/dio_utils/auth_interceptor.dart` |
| `lib/src_utils/dio_utils/data_model.dart` | `lib/src/utils/dio_utils/data_model.dart` |
| `lib/src_utils/dio_utils/exception.dart` | `lib/src/utils/dio_utils/exception.dart` |
| `lib/src_widgets/my_custom_widget.dart` | `lib/src/widgets/my_custom_widget.dart`，使用宿主文字主题 |
| `lib/common_flutter.dart` | `lib/src/platform/platform.dart`，保留 `CommonFlutter` 外壳 |
| `lib/common_flutter_platform_interface.dart` | `lib/src/platform/platform_interface.dart` |
| `lib/common_flutter_method_channel.dart` | `lib/src/platform/method_channel.dart` |
| `lib/common_flutter2.dart` | 全部有效导出归入 `lib/common_flutter.dart`，删除注释掉的 Calculator 模板 |
| `pubspec.yaml` | 依赖归入当前 `pubspec.yaml`，保留当前包名和版本；不复制缺少实现的插件注册声明 |

平台接口只保留 Dart 外壳。来源中没有对应的 Android / iOS 插件源码，
故不将当前包声明为自有原生插件。`getPlatformVersion` 仍可能抛出
`MissingPluginException`，示例页面处理该情况，不伪造平台结果。

## 演示、文档和测试

| 原位置 | 合并位置或处理方式 |
| --- | --- |
| `example/lib/demo_dio/api_services.dart` | `example/lib/demo_dio/api_services.dart` |
| `example/lib/demo_dio/widgets.dart` | `example/lib/demo_dio/widgets.dart` |
| `example/lib/main.dart` | 平台查询内容迁入 `example/lib/pages/platform.dart`；网络演示归入 `pages/dio.dart`，统一使用现有 main 与 router |
| `test/common_flutter_test.dart` | 平台委托与默认实现测试合入 `test/platform_test.dart`，每次恢复全局平台状态 |
| `test/common_flutter_method_channel_test.dart` | 通道协议测试合入 `test/platform_test.dart` |
| `example/test/widget_test.dart` | 实际路由与缺少原生实现的页面测试合入 `example/test/widget_test.dart` |
| `example/integration_test/plugin_integration_test.dart` | 缺失原生实现，原集成测试无法满足；由 `test/platform_test.dart` 验证通道协议和缺失实现错误，未将 mock 测试当作原生集成验证 |
| `README.md` | token、headers 存储说明归入当前 README，入门模板去重 |
| `example/README.md` | 归入当前 example README，补充服务地址占位和运行说明 |
| `example/pubspec.yaml` | 使用现有示例工程依赖，不保留无法执行的原生插件集成测试依赖 |
| `example/pubspec.lock` | 按合并后的实际依赖重新解析，不复制过时锁文件 |
| `example/analysis_options.yaml`、`example/.gitignore` | 保留现有示例工程的规则，重复模板去重 |

新增 `test/dio_client_test.dart` 覆盖实际网络处理路径，使用内存适配器，
不访问真实服务；新增 `example/test/demo_api_test.dart` 验证登录结果与 token 存储。

## 平台工程去重

旧 example 的 Android 目录共 19 个文件、iOS 目录共 41 个文件，均为示例宿主工程。
保留当前 example 的应用身份、工程配置、启动图、图标与测试宿主，不复制第二套工程。

- Android `MainActivity.kt` 使用现有 `com/example/example/MainActivity.kt`；其余对应文件保留当前版本。
- iOS 使用现有 Runner、Xcode 工程和资源。旧 `RunnerTests.swift` 引用不存在的自有原生插件，保留当前宿主测试。
- 旧 Podfile 与 Podfile.lock 不覆盖当前工程；按实际安全存储依赖生成 CocoaPods 配置。
- 现有示例补充 Android INTERNET 权限和 macOS 网络客户端能力；
  平台插件注册文件由 Flutter 按真实依赖生成，不注册旧 `CommonFlutterPlugin`。
- macOS Keychain Sharing 需要宿主配置开发签名。默认示例不加入会要求开发证书的
  共享声明，真实存储接入要求记录在 README；存储自动化测试使用 mock。

## 保留的行为和修复

- 保留 GET / POST、认证存储键名、Bearer token、自定义请求头与字段错误解析约定。
- 去除进程级客户端单例，每个实例持有独立地址，调用方自行复用并关闭。
- 安全存储或 headers JSON 解析失败时完成错误处理，不让请求挂起。
- 错误响应支持 Map、字符串、列表、空值等形式，保留请求上下文与 Dio 异常类型。
- HTTP 和网络错误返回 `ApiResponse` 失败结果，取消请求继续抛出取消异常。
- 登录失败不读取 token；成功响应缺失有效 token 时返回错误，不覆盖已有存储。
- 演示保留 `/users/login/`、`/customers/`、`/entities/` 及原请求数据。
- 原地址 `http://192.168.90.xxxx:xxxx` 是无效占位；改用 `DEMO_API_BASE_URL` 配置，
  未配置时禁用演示请求按钮，避免打开示例就发生地址解析错误。
- 原 500 / 401 示例分别删除 token、写入无效 token，仍保留此行为；
  实际错误码取决于后端，不新增服务端模拟逻辑。
- 原 400 按钮误调用普通创建方法，现调用对应 `createEntitiesErr400`，不改动原请求数据。
