
import 'common_flutter_platform_interface.dart';

class CommonFlutter {
  Future<String?> getPlatformVersion() {
    return CommonFlutterPlatform.instance.getPlatformVersion();
  }
}
