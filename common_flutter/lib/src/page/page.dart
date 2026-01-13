import 'package:flutter/material.dart';

/// 基础页面,可以传入1个或者多个widget
///  \n 建议使用 children
class CPageBase extends StatelessWidget {
  final String title;
  final List<Widget>? children;
  final Widget? child;
  const CPageBase({super.key, required this.title, this.children, this.child});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: Padding(
        padding: EdgeInsetsGeometry.fromLTRB(15, 5, 15, 10),
        child: Column(children: children ?? [child ?? SizedBox.shrink()]),
      ),
    );
  }
}

/// 菜单页面，来自BasePage
class CPageMenu extends StatelessWidget {
  final String title;
  final List<Widget> children;
  const CPageMenu({super.key, required this.title, required this.children});

  @override
  Widget build(BuildContext context) {
    return CPageBase(
      title: title,
      children: [Wrap(spacing: 12, runSpacing: 5, children: children)],
    );
  }
}
