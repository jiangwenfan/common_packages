import 'package:flutter/material.dart';

/// 筛选项，选中状态由调用方的 ValueNotifier 维护。
class FilterItem {
  const FilterItem({required this.text, this.icon, required this.isSelected});

  final String text;
  final IconData? icon;
  final bool isSelected;
}
