export 'phone_code.dart';
export 'clause.dart';

// 演示
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'phone_code.dart';

class AuthDemoPage extends HookWidget {
  const AuthDemoPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(children: [CPhoneForm()]);
  }
}
