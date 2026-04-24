import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

import 'type_card.dart';

class FilterItem {
  final String text;
  final IconData? icon;
  final bool isSelected;

  FilterItem({required this.text, this.icon, required this.isSelected});
}

class CFilterList extends HookWidget {
  final ValueNotifier<List<FilterItem>> items;
  const CFilterList({super.key, required this.items});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 70,
      child: GridView.builder(
        // 横向滚动
        scrollDirection: Axis.horizontal,

        // ios弹性
        physics: const BouncingScrollPhysics(),

        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          // 2行
          crossAxisCount: 2,
          // 水平列间距
          mainAxisSpacing: 10,
          // 交叉轴（垂直）间距
          crossAxisSpacing: 10,

          childAspectRatio: 0.5,
        ),
        itemCount: items.value.length,
        itemBuilder: (context, index) {
          final item = items.value[index];
          return TypeCard(
            text: item.text,
            icon: item.icon,
            isSelected: item.isSelected,
            onTap: () {
              final newList = [...items.value];
              newList[index] = FilterItem(
                text: item.text,
                icon: item.icon,
                isSelected: !item.isSelected,
              );
              items.value = newList;
            },
          );
        },
      ),
    );
  }
}
