## APK Note

⚠️ **`app-release.apk` (73MB) has been excluded from this repository** to keep the 
submission size under GitHub's 50MB file limit (and to stay under [X]MB overall 
submission limit, if applicable).

If you need to run the app and a pre-built APK is not available or does not 
install correctly, please build it yourself from source using the steps below.

### Build Instructions

The complete Flutter source code is included in `flutter_app_source.zip`. 
To build the APK:

```bash
flutter pub get
flutter build apk --release
```

The generated APK will be located at:
