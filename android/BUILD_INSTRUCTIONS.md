# 🔨 Android App - Quick Build Instructions

## 🚀 **Quick Start (5 Minutes)**

### **Method 1: Android Studio (Recommended)**

```bash
1. Open Android Studio
2. File → Open → Select "android" folder
3. Wait for Gradle sync
4. Click ▶️ Run button
5. Select your device
6. Done! App installs automatically
```

---

### **Method 2: Command Line**

```bash
# Navigate to android folder
cd android

# Build debug APK
./gradlew assembleDebug

# APK location:
# android/app/build/outputs/apk/debug/app-debug.apk

# Install on connected device
./gradlew installDebug
```

---

### **Method 3: Windows Command Line**

```cmd
cd android
gradlew.bat assembleDebug
```

---

## ⚙️ **Configuration**

### **Before Building:**

1. **Set Backend URL** (Optional - can be changed in app)

Edit: `android/app/src/main/java/com/textguard/sms/ApiClient.java`

```java
// Line 15: Change to your server IP
private static final String DEFAULT_API_URL = "http://YOUR_IP:8000/api";
```

Example:
```java
private static final String DEFAULT_API_URL = "http://192.168.1.100:8000/api";
```

---

## 📱 **Installation**

### **Option A: Direct Install (USB)**

```bash
1. Enable USB Debugging on phone:
   Settings → About Phone → Tap "Build Number" 7 times
   Settings → Developer Options → USB Debugging ON

2. Connect phone to computer

3. In Android Studio: Run → Run 'app'
   OR
   Command line: ./gradlew installDebug
```

### **Option B: APK File**

```bash
1. Build APK (see Method 2 above)

2. Copy APK to phone:
   - Via USB
   - Via email
   - Via cloud storage

3. On phone:
   - Open file manager
   - Tap app-debug.apk
   - Allow "Install from unknown sources"
   - Install
```

---

## 🔐 **Permissions Setup**

### **After Installation:**

```
1. Open TextGuard AI app

2. Grant SMS permissions when asked:
   ✅ Receive SMS
   ✅ Read SMS

3. Grant notification permission (Android 13+):
   ✅ Post Notifications

4. Optional - Enable notification monitoring:
   - Toggle "Notification Monitoring" ON
   - Tap "Open Settings"
   - Find "TextGuard AI"
   - Toggle ON
```

---

## 🧪 **Testing**

### **Test 1: Send Test SMS**

```
1. From another phone, send SMS to your phone:
   "WINNER! You won $1000 prize! Click here now!"

2. Check notification appears:
   🚨 High Risk SMS Detected!

3. Open app to see analysis in feed
```

### **Test 2: Check Backend Connection**

```
1. Open app
2. Tap ⚙️ Settings
3. Verify backend URL
4. Send test SMS
5. Check if analysis appears
```

### **Test 3: Background Monitoring**

```
1. Close app completely
2. Send SMS from another phone
3. Notification should still appear
4. Open app to see message in feed
```

---

## 🐛 **Troubleshooting**

### **Build Errors:**

```bash
# Clear Gradle cache
cd android
./gradlew clean

# Rebuild
./gradlew assembleDebug
```

### **Sync Issues:**

```
In Android Studio:
File → Invalidate Caches → Invalidate and Restart
```

### **Permission Errors:**

```
Settings → Apps → TextGuard AI → Permissions
→ Enable all required permissions
```

---

## 📦 **Build Variants**

### **Debug Build (Development):**
```bash
./gradlew assembleDebug
# Output: app-debug.apk
# Includes debugging info
# Larger file size
```

### **Release Build (Production):**
```bash
./gradlew assembleRelease
# Output: app-release-unsigned.apk
# Optimized & minified
# Smaller file size
# Requires signing for Play Store
```

---

## 🔑 **Signing APK (For Play Store)**

### **Generate Keystore:**

```bash
keytool -genkey -v -keystore textguard.keystore \
  -alias textguard -keyalg RSA -keysize 2048 -validity 10000
```

### **Sign APK:**

```bash
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 \
  -keystore textguard.keystore \
  app-release-unsigned.apk textguard
```

---

## 📊 **Build Output**

### **APK Locations:**

```
Debug APK:
android/app/build/outputs/apk/debug/app-debug.apk

Release APK:
android/app/build/outputs/apk/release/app-release-unsigned.apk
```

### **APK Size:**

```
Debug: ~8-10 MB
Release: ~5-7 MB (after optimization)
```

---

## ✅ **Checklist**

Before distributing:

- [ ] Backend URL configured
- [ ] App tested on real device
- [ ] SMS interception working
- [ ] Notifications showing
- [ ] Background monitoring working
- [ ] Permissions granted
- [ ] No crashes or errors

---

## 🚀 **Quick Commands Reference**

```bash
# Build debug APK
./gradlew assembleDebug

# Install on device
./gradlew installDebug

# Uninstall from device
./gradlew uninstallDebug

# Clean build
./gradlew clean

# Run tests
./gradlew test

# Check for updates
./gradlew --refresh-dependencies
```

---

## 📱 **Minimum Requirements**

- **Android Version:** 8.0 (Oreo) or higher (API 26+)
- **RAM:** 2 GB minimum
- **Storage:** 50 MB free space
- **Network:** WiFi or Mobile data

---

## 🎯 **Next Steps**

1. ✅ Build APK
2. ✅ Install on phone
3. ✅ Grant permissions
4. ✅ Configure backend URL
5. ✅ Test with sample SMS
6. ✅ Share with users!

---

**Need Help?** Check ANDROID_APP_GUIDE.md for detailed documentation.
