import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

class CDividerPlus extends HookWidget {
  final String title;
  final double size;
  final double thickness;
  const CDividerPlus({
    super.key,
    required this.title,
    this.size = 20.0,
    this.thickness = 2.0,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      spacing: 20,
      children: [
        Expanded(
          child: Divider(height: size, thickness: thickness),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(0, 16, 0, 16),
          child: Text(
            title,
            style: TextStyle(fontSize: size, fontWeight: FontWeight.bold),
          ),
        ),
        Expanded(
          child: Divider(height: size, thickness: thickness),
        ),
      ],
    );
  }
}
