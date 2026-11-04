import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

import 'filter_item.dart';
import 'type_card.dart';

/// 横向滚动的两行多选筛选列表。
class CFilterList extends HookWidget {
  const CFilterList({super.key, required this.items});

  final ValueNotifier<List<FilterItem>> items;

  @override
  Widget build(BuildContext context) {
    final currentItems = useValueListenable(items);

    return SizedBox(
      height: 70,
      child: GridView.builder(
        scrollDirection: Axis.horizontal,
        physics: const BouncingScrollPhysics(),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          mainAxisSpacing: 10,
          crossAxisSpacing: 10,
          childAspectRatio: 0.5,
        ),
        itemCount: currentItems.length,
        itemBuilder: (context, index) {
          final item = currentItems[index];
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
