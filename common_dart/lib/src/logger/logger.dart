import 'package:logger/logger.dart';
import 'printer.dart';

Logger getAppLogger({bool isDebug = false}) {
  return Logger(
    filter: ProductionFilter(),
    level: isDebug ? Level.debug : Level.info,

    printer: HybridPrinter(
      PrettyPrinter(
        methodCount: isDebug ? 1 : 0,
        errorMethodCount: 8,
        // 会打印“时间 + 距离 PrettyPrinter.startTime 的耗时差
        dateTimeFormat: isDebug ? DateTimeFormat.none : DateTimeFormat.onlyTime,
      ),

      // 覆盖 printer：info: PrettyPrinter(...)，只在 Level.info 时替换基准 printer
      // debug: PrettyPrinter(
      //   // methodCount: 1,
      //   // dateTimeFormat: DateTimeFormat.onlyTime,
      //   // dateTimeFormat: DateTimeFormat.none,
      // ),

      // 默认格式修改
      // info: PrettyPrinter(
      //   methodCount: 0, // ✅ info 不打印方法栈
      //   excludeBox: {Level.info: true}, // ✅ info 不要那一圈框
      //   dateTimeFormat: DateTimeFormat.onlyTime,

      //   printEmojis: true,
      //   levelEmojis: {
      //     ...PrettyPrinter.defaultLevelEmojis,
      //     Level.info: '✅', // 你想要的 icon
      //   },
      // ),
      // info: OneLineShowPrinter(),
      info: OneLineShowPrinter(),
      warning: isDebug ? null : OneLineShowPrinter(icon: '⚠️ '),
      error: isDebug ? null : BoxingPrinter(OneLineShowPrinter(icon: '⛔')),
    ),
  );
}
