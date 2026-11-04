import 'package:common_flutter/common_flutter.dart';
import 'package:example/main.dart';
import 'package:example/router.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('从首页访问合并后的演示并操作搜索和筛选', (tester) async {
    router.go('/home');
    await tester.pumpWidget(const MyApp());
    await tester.pumpAndSettle();
    await tester.tap(find.text('搜索、筛选与登录表单'));
    await tester.pumpAndSettle();

    expect(find.byType(CSearch), findsOneWidget);
    expect(find.byType(CFilterList), findsOneWidget);
    expect(find.byType(CPhoneForm), findsOneWidget);
    final phoneInput = find.descendant(
      of: find.byType(CPhoneForm),
      matching: find.byType(TextField),
    );
    expect(tester.widget<TextField>(phoneInput).readOnly, isTrue);

    await tester.enterText(
      find.descendant(
        of: find.byType(CSearch),
        matching: find.byType(TextField),
      ),
      '搜索示例',
    );
    await tester.pump();
    expect(find.text('搜索示例'), findsNWidgets(2));
    await tester.tap(find.byTooltip('清空'));
    await tester.pump();
    expect(find.text('搜索示例'), findsNothing);

    await tester.tap(find.text('排序0'));
    await tester.pump();
    expect(find.text('排序0'), findsNWidgets(2));
    expect(tester.takeException(), isNull);
  });

  testWidgets('基础按钮雏形合并到现有按钮演示', (tester) async {
    router.go('/home');
    await tester.pumpWidget(const MyApp());
    await tester.pumpAndSettle();
    await tester.tap(find.text('button 例子'));
    await tester.pumpAndSettle();
    expect(find.byType(CButton), findsOneWidget);
    await tester.tap(find.text('基础按钮（雏形）'));
    await tester.pump();
    expect(tester.takeException(), isNull);
  });
}
