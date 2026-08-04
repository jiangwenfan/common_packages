import 'package:common_flutter/common_flutter.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

class PrivacyPolicyViewExample extends HookWidget {
  const PrivacyPolicyViewExample({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("PrivacyPolicyViewExample")),
      body: ListView(
        padding: EdgeInsets.only(top: 20),
        children: [
          Text("Airbnb隐私政策"),
          AirbnbPrivacyPolicyView(
            msg1: """欢迎来到爱彼迎社区。为打造一个令人信赖的社区,更好地保护您的权益并遵守相关监管要求,请您在使用爱彼迎服务之前,认真阅读
《隐私政策》和《中国用户隐私补充条款》。重点条款包括:我们收集的个人信息、使用方式、第三方数据处理者、敏感个人信息和您的数据主体权利等。""",
            msg2:
                """点击「同意」即表示您已仔细阅读、充分理解并接受其全部条款,并授权我们按照《隐私政策》和《中国用户隐私补充条款》处理您的个人信息。""",
          ),
        ],
      ),
    );
  }
}
