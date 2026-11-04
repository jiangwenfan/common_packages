import 'package:go_router/go_router.dart';

import 'pages/button.dart';
import 'pages/dio.dart';
import 'pages/home.dart';
import 'pages/platform.dart';
import 'pages/privacy_policy_view.dart';
import 'pages/tabs.dart';
import 'pages/widgets.dart';

final routes = [
  GoRoute(path: "/home", builder: (context, state) => MyHomePage()),
  GoRoute(path: "/button", builder: (context, state) => ButtonExample()),
  GoRoute(path: "/tabs", builder: (context, state) => TabsExample()),
  GoRoute(path: '/dio', builder: (context, state) => const DioExample()),
  GoRoute(
    path: '/platform',
    builder: (context, state) => const PlatformExample(),
  ),
  GoRoute(
    path: "/widgets",
    builder: (context, state) => const WidgetsExample(),
  ),
  GoRoute(
    path: "/privacy_policy_view",
    builder: (context, state) => PrivacyPolicyViewExample(),
  ),
];

final router = GoRouter(initialLocation: "/home", routes: routes);
