import 'package:common_flutter/common_flutter.dart';
import 'package:flutter/material.dart';

class AuthDemoPage extends StatelessWidget {
  const AuthDemoPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Column(children: [CPhoneForm()]);
  }
}
