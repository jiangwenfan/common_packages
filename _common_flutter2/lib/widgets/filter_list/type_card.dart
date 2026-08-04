import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

typedef OnTapCallback = void Function();

class TypeCard extends HookWidget {
  final String text;
  final IconData? icon;
  final bool isSelected;
  final OnTapCallback onTap;
  const TypeCard({
    super.key,
    required this.text,
    this.icon,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final textWidget = Text(
      text,
      // 最大显示1行,超出用省略号
      maxLines: 1,
      overflow: TextOverflow.ellipsis,
      style: const TextStyle(fontSize: 10, height: 1.2),
    );
    final rowWidget = Row(
      children: [
        if (icon != null) CircleAvatar(radius: 10, child: Icon(icon, size: 10)),
        const SizedBox(width: 3),
        Expanded(child: textWidget),
      ],
    );

    // final c = Card(
    //   elevation: 1,
    //   clipBehavior: Clip.antiAlias,
    //   child: ,
    // );

    // final isClicked = useState(false);

    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        color: isSelected ? Colors.blue : Colors.grey,
      ),

      padding: const EdgeInsets.all(4.0),

      child: InkWell(onTap: onTap, child: rowWidget),
    );
  }
}
