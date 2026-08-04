// 手机和验证码登陆

// TODO: 自己实现ios风格的输入框
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

class CPhoneForm extends HookWidget {
  const CPhoneForm({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        children: [
          TextField(
            readOnly: true,

            decoration: InputDecoration(
              labelText: '国家/地区',
              floatingLabelBehavior: FloatingLabelBehavior.auto,
              suffixIcon: const Icon(Icons.expand_more), // 右侧下拉箭头
              filled: true,
              fillColor: Theme.of(
                context,
              ).colorScheme.surface, // 或 Colors.grey[50]
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
                  color: Theme.of(
                    context,
                  ).colorScheme.onSurface.withOpacity(.87),
                  width: 1.4,
                ),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: BorderSide(
                  color: Theme.of(context).colorScheme.primary,
                  width: 1.6,
                ),
              ),
            ),
            onTap: () {
              print("点击了");
            },
          ),
        ],
      ),
    );
  }
}
