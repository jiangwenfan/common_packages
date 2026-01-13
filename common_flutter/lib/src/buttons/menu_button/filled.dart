import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// 菜单按钮: Filled样式的
class CMenuButtonFilled extends StatelessWidget {
  final IconData? iconData;
  final String title;
  final String route;
  const CMenuButtonFilled({
    super.key,
    this.iconData,
    required this.title,
    required this.route,
  });

  @override
  Widget build(BuildContext context) {
    return FilledButton(
      onPressed: () {
        context.push(route);
      },
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (iconData != null) Icon(iconData!, size: 22),
          if (iconData != null) SizedBox(width: 12),
          Text(title),
        ],
      ),
    );
  }
}
