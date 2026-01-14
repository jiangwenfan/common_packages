import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:common_flutter/common_flutter.dart';

class ButtonExample extends HookWidget {
  const ButtonExample({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("ButtonExample")),
      body: Wrap(
        children: [
          CMenuButtonCard(title: "demo1", route: "/demo1"),
          CMenuButtonCard(title: "container1234"),
          CMenuButtonCard(title: "demo1", route: "/demo1", iconData: Icons.add),
          CMenuButtonFilled(title: "demo1", route: "/demo1"),
          CMenuButtonFilled(
            title: "demo1",
            route: "/demo1",
            iconData: Icons.add,
            status: ButtonStatus.green,
          ),
        ],
      ),
    );
  }
}
