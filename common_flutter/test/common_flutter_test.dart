import 'package:common_flutter/common_flutter.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('搜索输入和清空各通知一次，清空后保留焦点', (tester) async {
    final changes = <String>[];
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: CSearch(onChanged: changes.add)),
      ),
    );

    expect(find.byTooltip('清空'), findsNothing);
    await tester.enterText(find.byType(TextField), 'flutter');
    await tester.pump();
    expect(changes, ['flutter']);
    expect(find.byTooltip('清空'), findsOneWidget);

    await tester.tap(find.byTooltip('清空'));
    await tester.pump();
    expect(changes, ['flutter', '']);
    expect(find.byTooltip('清空'), findsNothing);
    final field = tester.widget<TextField>(find.byType(TextField));
    expect(field.controller!.text, isEmpty);
    expect(field.focusNode!.hasFocus, isTrue);
  });

  testWidgets('筛选组件自行监听状态，点击支持多选和取消', (tester) async {
    const originalItems = [
      FilterItem(text: '第一项', icon: Icons.star, isSelected: false),
      FilterItem(text: '第二项', isSelected: true),
    ];
    final items = ValueNotifier<List<FilterItem>>(originalItems);
    addTearDown(items.dispose);
    // 外层不监听 notifier，确保组件独立使用时也会刷新。
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: CFilterList(items: items)),
      ),
    );

    await tester.tap(find.text('第一项'));
    await tester.pump();
    expect(items.value.map((item) => item.isSelected), [true, true]);
    expect(originalItems.first.isSelected, isFalse);
    expect(items.value.first.icon, Icons.star);
    expect(
      tester.widgetList<TypeCard>(find.byType(TypeCard)).first.isSelected,
      isTrue,
    );

    await tester.tap(find.text('第一项'));
    await tester.pump();
    expect(items.value.map((item) => item.isSelected), [false, true]);
    expect(
      tester.widgetList<TypeCard>(find.byType(TypeCard)).first.isSelected,
      isFalse,
    );
  });

  testWidgets('外部替换空筛选列表后自动刷新', (tester) async {
    final items = ValueNotifier<List<FilterItem>>([]);
    addTearDown(items.dispose);
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: CFilterList(items: items)),
      ),
    );
    expect(find.byType(TypeCard), findsNothing);

    items.value = [const FilterItem(text: '外部添加', isSelected: true)];
    await tester.pump();
    expect(find.text('外部添加'), findsOneWidget);
    expect(tester.widget<TypeCard>(find.byType(TypeCard)).isSelected, isTrue);
    await tester.tap(find.text('外部添加'));
    await tester.pump();
    expect(items.value.single.isSelected, isFalse);
  });

  for (final brightness in Brightness.values) {
    testWidgets('筛选卡片跟随宿主 ${brightness.name} 主题', (tester) async {
      final colors = ColorScheme.fromSeed(
        seedColor: Colors.deepOrange,
        brightness: brightness,
      );
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData(colorScheme: colors),
          home: Scaffold(
            body: Column(
              children: [
                TypeCard(text: '已选', isSelected: true, onTap: () {}),
                TypeCard(text: '未选', isSelected: false, onTap: () {}),
              ],
            ),
          ),
        ),
      );

      Material backgroundOf(String text) => tester.widget<Material>(
        find.descendant(
          of: find.widgetWithText(TypeCard, text),
          matching: find.byType(Material),
        ),
      );
      expect(backgroundOf('已选').color, colors.primaryContainer);
      expect(backgroundOf('未选').color, colors.surfaceContainerHighest);
      expect(
        tester.widget<Text>(find.text('已选')).style!.color,
        colors.onPrimaryContainer,
      );
      expect(
        tester.widget<Text>(find.text('未选')).style!.color,
        colors.onSurface,
      );
      expect(tester.takeException(), isNull);
    });
  }
}
