import 'package:flutter/material.dart';
import './api_services.dart';

class DioWidget extends StatelessWidget {
  final u = Api();
  DioWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ElevatedButton(
          onPressed: () async {
            await u.login({
              "email": "admin1@cloudfall.cn",
              "password": "admin1234",
            });
          },
          child: Text("登陆"),
        ),
        Divider(),
        ElevatedButton(
          onPressed: () async {
            await u.getCustomersOk();
          },
          child: Text("get获取 普通资源 ok"),
        ),
        ElevatedButton(
          onPressed: () async {
            await u.getCustomersErr500();
          },
          child: Text("get获取 普通资源 500 error"),
        ),
        ElevatedButton(
          onPressed: () async {
            await u.getCustomersErr401();
          },
          child: Text("get获取 普通资源 401 error"),
        ),
        Divider(),
        ElevatedButton(
          onPressed: () async {
            await u.createEntitiesOk({
              "name": "1",
              "desc": "2",
              "tag": {"id": "1"},
            });
          },
          child: Text("post获取 普通资源 ok"),
        ),
        ElevatedButton(
          onPressed: () async {
            await u.createEntitiesOk({
              "name": "1",
              "desc": "2",
              "tag": {"id": "9999"},
            });
          },
          child: Text("post获取 普通资源 400 error"),
        ),
      ],
    );
  }
}
