import 'package:common_flutter/common_flutter2.dart';
import 'dart:convert';

class Api {
  final DioClient _dioClient = DioClient(
    baseUrl: "http://192.168.90.xxxx:xxxx",
  );

  // 封装login登陆接口
  Future<ApiResponse> login(Map<String, dynamic> data) async {
    final response = await _dioClient.post("/users/login/", data: data);
    String token = response.payload["token"];

    // 写入token
    await secureStorage.write(key: "access_token", value: token);
    // 写入headers
    final s = json.encode({"x-customer-id": "4"});
    await secureStorage.write(key: "headers", value: s);

    return response;
  }

  // 封装 /customers/ 接口
  Future<ApiResponse> getCustomersOk() async {
    final ApiResponse response = await _dioClient.get("/customers/");
    print("---请求结果：$response, type: ${response.runtimeType}");
    return response;
  }

  // 封装 /customers/ 接口
  Future<ApiResponse> getCustomersErr500() async {
    await secureStorage.delete(key: "access_token");
    final ApiResponse response = await _dioClient.get("/customers/");
    print("---请求结果：$response, type: ${response.runtimeType}");
    return response;
  }

  // 封装 /customers/ 接口
  Future<ApiResponse> getCustomersErr401() async {
    await secureStorage.write(key: "access_token", value: "123");
    final ApiResponse response = await _dioClient.get("/customers/");
    print("---请求结果：$response, type: ${response.runtimeType}");
    return response;
  }

  // 封装创建 entities 接口
  Future<ApiResponse> createEntitiesOk(Map<String, dynamic> data) async {
    final response = await _dioClient.post("/entities/", data: data);
    print("---请求结果：$response, type: ${response.runtimeType}");
    return response;
  }

  // 封装创建 entities 接口
  Future<ApiResponse> createEntitiesErr400(Map<String, dynamic> data) async {
    final response = await _dioClient.post("/entities/", data: data);
    print("---请求结果：$response, type: ${response.runtimeType}");
    return response;
  }
}
