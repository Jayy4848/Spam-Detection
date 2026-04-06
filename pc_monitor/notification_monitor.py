"""
TextGuard AI — PC Notification Monitor
Monitors Windows notifications and clipboard, analyzes via TextGuard API.

Install:
    pip install requests pywin32

Run:
    python notification_monitor.py
"""

import sys
import time
import threading
import subprocess
import requests
from datetime import datetime

# ─── CONFIG ────────────────────────────────────────────────────────────────────
API_URL       = "http://localhost:8000/api/predict/"
POLL_INTERVAL = 1.5   # seconds
MIN_TEXT_LEN  = 10

# ─── TERMINAL COLORS ───────────────────────────────────────────────────────────
RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"


def analyze(text: str) -> dict:
    """Send text to TextGuard API."""
    try:
        resp = requests.post(
            API_URL,
            json={"message": text, "language": "en"},
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
    except requests.exceptions.ConnectionError:
        print(f"{YELLOW}⚠  Backend not reachable at {API_URL}{RESET}")
    except Exception as e:
        print(f"{YELLOW}⚠  API error: {e}{RESET}")
    return None


def print_result(source: str, text: str, result: dict):
    """Pretty-print analysis result."""
    if not result:
        return

    category    = result.get("category", "unknown")
    confidence  = result.get("confidence", 0)
    is_phishing = result.get("is_phishing", False)
    risk_level  = result.get("risk_level", "low")
    risk_score  = result.get("risk_score", 0)
    keywords    = result.get("suspicious_keywords", [])
    urgency     = result.get("urgency_analysis", {}).get("level", "low")

    if is_phishing or category == "spam" or risk_level == "high":
        color = RED;    badge = "🚨 HIGH RISK"
    elif risk_level == "medium" or category in ("promotion", "important"):
        color = YELLOW; badge = "⚠️  MEDIUM RISK"
    else:
        color = GREEN;  badge = "✅ SAFE"

    ts = datetime.now().strftime("%H:%M:%S")
    preview = text[:100] + "..." if len(text) > 100 else text

    print(f"\n{'─'*62}")
    print(f"  {BOLD}{color}{badge}{RESET}  {DIM}[{ts}]{RESET}  📳 {source}")
    print(f"  Category   : {BOLD}{category.upper()}{RESET}  |  Confidence: {confidence*100:.0f}%")
    print(f"  Risk Score : {color}{int(risk_score*100)}/100{RESET}  |  Urgency: {urgency}")
    if is_phishing:
        print(f"  {RED}🎣 PHISHING — do NOT click any links in this message{RESET}")
    if keywords:
        print(f"  Flagged    : {', '.join(keywords[:5])}")
    print(f"  {DIM}{preview}{RESET}")
    print(f"{'─'*62}")


# ─── CLIPBOARD MONITOR ─────────────────────────────────────────────────────────
class ClipboardMonitor:
    """
    Monitors clipboard for new text.
    When you copy a notification/SMS text, it auto-analyzes it.
    """

    def __init__(self):
        self.last_text = ""
        self.running   = False

    def get_clipboard(self) -> str:
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
                capture_output=True, text=True, timeout=3
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def start(self):
        self.running = True
        print(f"{CYAN}📋 Clipboard monitor active — copy any notification text to analyze it{RESET}\n")

        while self.running:
            text = self.get_clipboard()
            if text and text != self.last_text and len(text) >= MIN_TEXT_LEN:
                self.last_text = text
                print(f"\n{CYAN}📋 New clipboard text detected — analyzing...{RESET}")
                result = analyze(text)
                print_result("Clipboard", text, result)
            time.sleep(POLL_INTERVAL)

    def stop(self):
        self.running = False


# ─── WINDOWS TOAST MONITOR ─────────────────────────────────────────────────────
class WindowsToastMonitor:
    """
    Reads Windows Action Center notifications using PowerShell.
    Works on Windows 10/11 without any native SDK compilation.
    """

    POWERSHELL_SCRIPT = r"""
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]

function Await($WinRtTask, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}

[Windows.UI.Notifications.Management.UserNotificationListener, Windows.UI.Notifications.Management, ContentType = WindowsRuntime] | Out-Null
[Windows.UI.Notifications.KnownNotificationBindings, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null

$listener = [Windows.UI.Notifications.Management.UserNotificationListener]::Current
$accessTask = $listener.RequestAccessAsync()
$access = Await $accessTask ([Windows.UI.Notifications.Management.UserNotificationListenerAccessStatus])

if ($access -ne "Allowed") {
    Write-Output "ACCESS_DENIED"
    exit
}

$notifTask = $listener.GetNotificationsAsync([Windows.UI.Notifications.NotificationKinds]::Toast)
$notifs = Await $notifTask ([System.Collections.Generic.IReadOnlyList[Windows.UI.Notifications.UserNotification]])

foreach ($notif in $notifs) {
    try {
        $appName = $notif.AppInfo.DisplayInfo.DisplayName
        $binding = $notif.Notification.Visual.GetBinding([Windows.UI.Notifications.KnownNotificationBindings]::ToastGeneric)
        if ($binding -eq $null) { continue }
        $textElements = $binding.GetTextElements()
        $text = ($textElements | ForEach-Object { $_.Text }) -join " "
        if ($text.Length -gt 5) {
            Write-Output "NOTIF|$($notif.Id)|$appName|$text"
        }
    } catch {}
}
"""

    def __init__(self):
        self.seen_ids = set()
        self.running  = False

    def get_notifications(self) -> list:
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", self.POWERSHELL_SCRIPT],
                capture_output=True, text=True, timeout=8
            )
            lines = result.stdout.strip().split("\n")
            notifications = []

            for line in lines:
                line = line.strip()
                if line == "ACCESS_DENIED":
                    return None  # Signal access denied
                if line.startswith("NOTIF|"):
                    parts = line.split("|", 3)
                    if len(parts) == 4:
                        _, notif_id, app_name, text = parts
                        notifications.append({
                            "id": notif_id.strip(),
                            "app": app_name.strip(),
                            "text": text.strip()
                        })

            return notifications
        except Exception:
            return []

    def start(self):
        self.running = True
        print(f"{CYAN}🔔 Windows notification monitor active{RESET}\n")

        access_warned = False

        while self.running:
            notifications = self.get_notifications()

            if notifications is None:
                if not access_warned:
                    print(f"{YELLOW}⚠  Notification access denied.")
                    print(f"   Go to: Settings → Privacy → Notifications → Allow apps to access notifications{RESET}")
                    access_warned = True
            elif notifications:
                for notif in notifications:
                    nid = notif["id"]
                    if nid in self.seen_ids:
                        continue
                    self.seen_ids.add(nid)

                    app  = notif["app"]
                    text = notif["text"]

                    # Skip system noise
                    if any(skip in app.lower() for skip in ["textguard", "windows", "microsoft store"]):
                        continue

                    print(f"\n{CYAN}🔔 Notification from: {app}{RESET}")
                    threading.Thread(
                        target=lambda a=app, t=text: print_result(a, t, analyze(t)),
                        daemon=True
                    ).start()

            time.sleep(POLL_INTERVAL)

    def stop(self):
        self.running = False


# ─── MAIN ──────────────────────────────────────────────────────────────────────
def check_backend() -> bool:
    try:
        resp = requests.get(API_URL.replace("/predict/", "/health/"), timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


def main():
    print(f"""
{BOLD}{CYAN}╔══════════════════════════════════════════════╗
║   TextGuard AI — PC Notification Monitor     ║
║   Analyzes notifications & clipboard text    ║
╚══════════════════════════════════════════════╝{RESET}

  Backend : {API_URL}
  Press Ctrl+C to stop
""")

    # Check backend
    if check_backend():
        print(f"{GREEN}✅ Backend connected{RESET}\n")
    else:
        print(f"{RED}❌ Backend not reachable — start Django server first:{RESET}")
        print(f"   cd backend && python manage.py runserver\n")

    # Start both monitors in parallel threads
    toast_monitor     = WindowsToastMonitor()
    clipboard_monitor = ClipboardMonitor()

    t1 = threading.Thread(target=toast_monitor.start,     daemon=True)
    t2 = threading.Thread(target=clipboard_monitor.start, daemon=True)

    t1.start()
    t2.start()

    print(f"{DIM}Both monitors running. Waiting for notifications...{RESET}\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        toast_monitor.stop()
        clipboard_monitor.stop()
        print(f"\n{YELLOW}TextGuard PC Monitor stopped.{RESET}")


if __name__ == "__main__":
    main()
