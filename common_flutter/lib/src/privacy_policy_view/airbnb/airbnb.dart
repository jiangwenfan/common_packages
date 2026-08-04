import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

class AirbnbPrivacyPolicyView extends HookWidget {
  final String msg1;
  final String msg2;
  const AirbnbPrivacyPolicyView({
    super.key,
    required this.msg1,
    required this.msg2,
  });

  @override
  Widget build(BuildContext context) {
    final horizontalPadding = 20.0;
    final verticalPadding = 25.0;
    final dividerHeight = 23.0;
    return SingleChildScrollView(
      child: Container(
        padding: EdgeInsets.fromLTRB(
          horizontalPadding,
          verticalPadding,
          horizontalPadding,
          verticalPadding,
        ),

        // 圆角大小
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(15),
          color: Colors.white,
        ),

        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "隐私政策",
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: dividerHeight),
            Text(msg1),
            SizedBox(height: dividerHeight),
            Text(msg2),
            SizedBox(height: dividerHeight),
            Divider(),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                // 增加下划线
                TextButton(
                  onPressed: () {},
                  child: Text(
                    "不同意",
                    style: TextStyle(decoration: TextDecoration.underline),
                  ),
                ),
                // 修改圆角大小
                FilledButton(
                  onPressed: () {},
                  style: FilledButton.styleFrom(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  child: Text("同意"),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
