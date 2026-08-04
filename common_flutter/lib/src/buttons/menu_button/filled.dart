import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'base.dart';

/// 菜单按钮: Filled样式的
class CMenuButtonFilled extends StatelessWidget {
  final IconData? iconData;
  final String title;
  final ButtonStatus status;
  final String route;
  const CMenuButtonFilled({
    super.key,
    this.iconData,
    required this.title,
    this.status = ButtonStatus.red,
    required this.route,
  });

  @override
  Widget build(BuildContext context) {
    return FilledButton(
      style: ButtonStyle(
        backgroundColor: WidgetStatePropertyAll(
          // 使用match
          switch (status) {
            ButtonStatus.red => Colors.red[300],
            ButtonStatus.green => Colors.green[300],
            ButtonStatus.yellow => Colors.yellow[300],
          },
        ),
      ),
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
