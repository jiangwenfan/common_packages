import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

/// 手机验证码登录表单雏形，目前只有国家/地区只读输入框。
///
/// TODO: 自己实现 iOS 风格的输入框；国家选择和登录流程尚未实现。
class CPhoneForm extends HookWidget {
  const CPhoneForm({super.key});

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        children: [
          TextField(
            readOnly: true,
            decoration: InputDecoration(
              labelText: '国家/地区',
              floatingLabelBehavior: FloatingLabelBehavior.auto,
              suffixIcon: const Icon(Icons.expand_more),
              filled: true,
              fillColor: colors.surface,
              isDense: true,
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 14,
              ),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                gapPadding: 8,
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: BorderSide(
                  color: colors.onSurface.withValues(alpha: .87),
                  width: 1.4,
                ),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: BorderSide(color: colors.primary, width: 1.6),
              ),
            ),
            onTap: () {
              debugPrint('点击了');
            },
          ),
        ],
      ),
    );
  }
}
