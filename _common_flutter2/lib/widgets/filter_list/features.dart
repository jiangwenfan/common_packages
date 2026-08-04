export 'core.dart';

// 演示
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'core.dart';

class FilterListDemoPage extends HookWidget {
  const FilterListDemoPage({super.key});

  @override
  Widget build(BuildContext context) {
    // -1. 原始数据
    final items = List.generate(
      100,
      (i) => FilterItem(text: "排序${i}", icon: Icons.star, isSelected: false),
    );
    // 1. 维护状态
    final itemsAll = useState(items);

    return Column(
      children: [
        CFilterList(items: itemsAll),
        Text(
          itemsAll.value
              .where((item) => item.isSelected)
              .map((item) => item.text)
              .join(","),
        ),
      ],
    );
  }
}
