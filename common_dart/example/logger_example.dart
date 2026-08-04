import 'package:common_dart/common_dart.dart';

void main(List<String> args) {
  if (args.isEmpty) {
    print("""
开启debug: dart example/logger_example.dart true
关闭debug: dart example/logger_example.dart false
""");
    return;
  }
  final logger = getAppLogger(isDebug: args[0] == 'true');
  logger.d('Hello, world!');
  logger.i('Hello, world!');
  logger.w('Hello, world!');
  logger.e('Hello, world!');
}
