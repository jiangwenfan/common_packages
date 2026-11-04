import 'package:common_flutter/common_flutter.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';

import 'api_services.dart';

class DioWidget extends HookWidget {
  const DioWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final api = useMemoized(Api.new);
    useEffect(() => api.close, [api]);
    final configured = demoApiBaseUrl.isNotEmpty;

    Future<void> run(Future<ApiResponse> Function() request) async {
      try {
        final response = await request();
        // 只记录成功状态，不将登录 token 等响应内容输出到日志。
        debugPrint('演示请求${response.isSuccess ? '成功' : '失败'}');
      } catch (_) {
        if (!context.mounted) return;
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('请求失败，请检查演示服务配置')));
      }
    }

    return Column(
      children: [
        if (!configured) const Text('尚未配置演示服务地址'),
        ElevatedButton(
          onPressed: configured
              ? () => run(() => api.login({'email': '', 'password': ''}))
              : null,
          child: const Text('登录'),
        ),
        const Divider(),
        ElevatedButton(
          onPressed: configured ? () => run(api.getCustomersOk) : null,
          child: const Text('GET 普通资源 OK'),
        ),
        ElevatedButton(
          onPressed: configured ? () => run(api.getCustomersErr500) : null,
          child: const Text('GET 普通资源 500 error'),
        ),
        ElevatedButton(
          onPressed: configured ? () => run(api.getCustomersErr401) : null,
          child: const Text('GET 普通资源 401 error'),
        ),
        const Divider(),
        ElevatedButton(
          onPressed: configured
              ? () => run(
                  () => api.createEntitiesOk({
                    'name': '1',
                    'desc': '2',
                    'tag': {'id': '1'},
                  }),
                )
              : null,
          child: const Text('POST 普通资源 OK'),
        ),
        ElevatedButton(
          onPressed: configured
              ? () => run(
                  () => api.createEntitiesErr400({
                    'name': '1',
                    'desc': '2',
                    'tag': {'id': '9999'},
                  }),
                )
              : null,
          child: const Text('POST 普通资源 400 error'),
        ),
      ],
    );
  }
}
