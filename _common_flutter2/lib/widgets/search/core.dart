import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:flutter/material.dart';

class CSearch extends HookWidget {
  const CSearch({super.key, required this.onChanged});

  final Function(String) onChanged;

  @override
  Widget build(BuildContext context) {
    // 文本的单一数据源（Single Source of Truth）。读取/修改文本都靠它（controller.text / controller.clear()）。
    final controller = useTextEditingController();

    // 控制焦点与键盘（requestFocus() 让键盘保持/再次出现）。
    final focusNode = useFocusNode();

    // 让输入变化时自动重建 UI（显示/隐藏清空按钮）
    // 当 controller.text 变化时触发重建。
    // controller.text 变了，TextField 自己会更新“文字显示”，但你的这个 Widget 的 build() 不会因为它自动重建。
    //所以你在 build() 里用 controller.text.isNotEmpty 决定要不要显示清空按钮，没有订阅的话就不会跟着变。
    // -- 如果没有这个，也就是input中的文本会变，但是build中ui不会重建
    useListenable(controller);

    // 清空按钮
    final clearButton = IconButton(
      onPressed: () {
        // 清空文本
        controller.clear();
        // 重新获取焦点,继续保持焦点与键盘
        focusNode.requestFocus();
        // 通知父组件,清空文本
        // 因为程序性修改 controller.text 并不保证一定触发 TextField.onChanged（onChanged更多是用户输入时回调）。为了逻辑稳定，我们显式回调一次。
        onChanged('');
      },
      icon: const Icon(Icons.clear),
      tooltip: "清空",
    );

    return TextField(
      controller: controller,
      focusNode: focusNode,

      decoration: InputDecoration(
        prefixIcon: Icon(Icons.search),
        hintText: "搜索",
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(20)),
        suffixIcon: controller.text.isNotEmpty ? clearButton : null,
      ),
      // 移动端键盘把“回车”换成“搜索”样式，更符合搜索场景。
      textInputAction: TextInputAction.search,

      onChanged: onChanged,
    );
  }
}
