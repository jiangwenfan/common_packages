# common_flutter

A new Flutter plugin project.

## Getting Started

This project is a starting point for a Flutter
[plug-in package](https://flutter.dev/to/develop-plugins),
a specialized package that includes platform-specific implementation code for
Android and/or iOS.

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev), which offers tutorials,
samples, guidance on mobile development, and a full API reference.


[pub.dev](https://pub.dev/packages/common_flutter)

登陆完成后:
```
// 写入token
await secureStorage.write(key: "access_token", value: token);

// 写入headers
final s = json.encode({"x-customer-id": "4"});
await secureStorage.write(key: "headers", value: s);
```