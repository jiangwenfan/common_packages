import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:go_router/go_router.dart';

/// 菜单按钮: 卡片样式的
class CMenuButtonCard extends HookWidget {
  final String title;
  final IconData? iconData;
  final void Function()? onTap;
  final String? route;
  final Color? color;

  const CMenuButtonCard({
    super.key,
    required this.title,
    this.iconData,
    this.onTap,
    this.route,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: color,
      // 关键：裁剪子组件InkWel的阴影
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        // 处理点击事件
        onTap: onTap ?? (route != null ? () => context.push(route!) : null),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            mainAxisSize: MainAxisSize.min,
            children: [
              if (iconData != null) Icon(iconData!),
              Flexible(
                child: Text(
                  title,
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

@Deprecated('使用: CMenuButtonCard')
typedef CMenuCardButton = CMenuButtonCard;
