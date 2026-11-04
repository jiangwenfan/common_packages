import 'package:common_flutter/common_flutter.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

class FilterListDemoPage extends HookWidget {
  const FilterListDemoPage({super.key});

  @override
  Widget build(BuildContext context) {
    final items = useState(
      List.generate(
        100,
        (i) => FilterItem(text: '排序$i', icon: Icons.star, isSelected: false),
      ),
    );

    return Column(
      children: [
        CFilterList(items: items),
        Text(
          items.value
              .where((item) => item.isSelected)
              .map((item) => item.text)
              .join(','),
        ),
      ],
    );
  }
}
