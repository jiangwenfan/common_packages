import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

/// 菜单按钮: 卡片样式的
class CMenuButtonCard extends HookWidget {
  final String title;
  final IconData? iconData;
  final void Function() onTap;
  final Color color;

  const CMenuButtonCard({
    super.key,
    required this.title,
    this.iconData,
    required this.onTap,
    this.color = Colors.white,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      // 处理点击事件
      onTap: onTap,

      child: Card(
        color: color,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [if (iconData != null) Icon(iconData!), Text(title)],
          ),
        ),
      ),
    );
  }
}

@Deprecated('使用: CMenuButtonCard')
typedef CMenuCardButton = CMenuButtonCard;
