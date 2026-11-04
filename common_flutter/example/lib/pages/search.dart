import 'package:common_flutter/common_flutter.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

class SearchDemoPage extends HookWidget {
  const SearchDemoPage({super.key});

  @override
  Widget build(BuildContext context) {
    final inputText = useState('');

    return Column(
      children: [
        CSearch(onChanged: (value) => inputText.value = value),
        Text(inputText.value),
      ],
    );
  }
}
