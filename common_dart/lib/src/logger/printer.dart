import 'package:logger/logger.dart';

/// 一行显示格式: 时间 + icon + 消息
class OneLineShowPrinter extends LogPrinter {
  final String icon;
  OneLineShowPrinter({this.icon = '✅'});

  @override
  List<String> log(LogEvent event) {
    final t = event.time;
    final ts =
        '${t.hour.toString().padLeft(2, '0')}:'
        '${t.minute.toString().padLeft(2, '0')}:'
        '${t.second.toString().padLeft(2, '0')}';

    return ['$ts $icon ${event.message}'];
  }
}

/// 一行显示+虚线边框
/// 一行显示+实线边框

class BoxingPrinter extends LogPrinter {
  BoxingPrinter(this._inner, {this.lineLength = 80});

  final LogPrinter _inner;
  final int lineLength;

  String _repeat(String s, int n) => List.filled(n, s).join();

  @override
  List<String> log(LogEvent event) {
    final innerLines = _inner.log(event);

    // top/bottom border 使用 PrettyPrinter 的公开常量
    final top =
        PrettyPrinter.topLeftCorner +
        _repeat(PrettyPrinter.singleDivider, lineLength);
    final bottom =
        PrettyPrinter.bottomLeftCorner +
        _repeat(PrettyPrinter.singleDivider, lineLength);

    final boxed = <String>[top];
    for (final line in innerLines) {
      boxed.add('${PrettyPrinter.verticalLine} $line');
    }
    boxed.add(bottom);
    return boxed;
  }
}
