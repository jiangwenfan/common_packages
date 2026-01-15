import 'pages/button.dart';
import 'pages/home.dart';
import 'package:go_router/go_router.dart';
import 'pages/tabs.dart';

final routes = [
  GoRoute(path: "/home", builder: (context, state) => MyHomePage()),
  GoRoute(path: "/button", builder: (context, state) => ButtonExample()),
  GoRoute(path: "/tabs", builder: (context, state) => TabsExample()),
];

final router = GoRouter(initialLocation: "/home", routes: routes);
