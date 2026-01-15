/*
按钮区: category1, category2, category3
内容区: content1, content2, content3

并且content1还可以分组显示:
- group1,里面的内容是wrap
- group2
*/

import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'type.dart';

class CTabs extends HookWidget {
  /// 所有tab的配置
  final List<TabType> tabs;

  /// 默认选中的tab的key
  final String? initialKey;
  const CTabs({super.key, required this.tabs, this.initialKey});

  @override
  Widget build(BuildContext context) {
    // 如果initialKey在tabs中存在，则使用initialKey，否则使用tabs的第一个key
    final selectedIndex = useState(
      tabs.any((e) => e.key == initialKey) ? initialKey : tabs.first.key,
    );

    return Container(
      color: Colors.grey[200],
      padding: EdgeInsets.all(20),
      child: Column(
        children: [
          // 按钮区
          Wrap(
            children: [
              ...tabs.map(
                (e) => FilledButton(
                  onPressed: () {
                    selectedIndex.value = e.key!;
                  },
                  child: e.title,
                ),
              ),
            ],
          ),

          SizedBox(height: 20),

          // 内容区
          ...tabs
              .where((e) => e.key == selectedIndex.value)
              .map((e) => e.content),
        ],
      ),
    );
  }
}
