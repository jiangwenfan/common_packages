import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

/// 筛选卡片，颜色跟随宿主主题。
class TypeCard extends HookWidget {
  const TypeCard({
    super.key,
    required this.text,
    this.icon,
    required this.isSelected,
    required this.onTap,
  });

  final String text;
  final IconData? icon;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final foreground = isSelected
        ? colors.onPrimaryContainer
        : colors.onSurface;

    return Material(
      borderRadius: BorderRadius.circular(10),
      clipBehavior: Clip.antiAlias,
      color: isSelected
          ? colors.primaryContainer
          : colors.surfaceContainerHighest,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(4),
          child: Row(
            children: [
              if (icon != null) ...[
                CircleAvatar(radius: 10, child: Icon(icon, size: 10)),
                const SizedBox(width: 3),
              ],
              Expanded(
                child: Text(
                  text,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: theme.textTheme.labelSmall?.copyWith(
                    fontSize: 10,
                    height: 1.2,
                    color: foreground,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
