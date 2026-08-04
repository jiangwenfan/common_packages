import 'package:flutter/material.dart';
import 'widgets/search/features.dart';
import 'widgets/filter_list/features.dart';
import 'widgets/auth/feature.dart';

class AppWidget extends StatelessWidget {
  const AppWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        Text('Hello World'),
        SearchDemoPage(),
        FilterListDemoPage(),
        Divider(),
        AuthDemoPage(),
        SizedBox(height: 20),
      ],
    );
  }
}
