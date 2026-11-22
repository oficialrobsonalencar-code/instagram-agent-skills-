#!/usr/bin/env python3
"""
ig_appium.py — Core helper library for driving the Instagram Android app via Appium.

Why Appium (not uiautomator2): Instagram renders many screens (DM inbox, notes, story
viewer, the create-hub media grid, reels) with custom/SurfaceView surfaces where a plain
uiautomator2 hierarchy dump comes back EMPTY. Appium's `page_source` returns a full tree on
those screens, which is what makes the flows below possible.

Design principles distilled from real device work:
  * IG's custom buttons (action-row like/comment/repost/share, bottom-sheet options, the
    story "Add to story"/"Your story" buttons, gallery video cells) do NOT respond to
    `element.click()` OR `adb input tap`. They only fire via Appium's `mobile: clickGesture`.
    Use `gtap()` / `gesture_tap_text()` for those. Plain View buttons (Next/Share/OK, album
    picker) work with `element.click()`.
  * READS go through `page_source` (a single snapshot) so they are stale-proof; the cold-start
    UI constantly re-creates elements and `StaleObjectException` is otherwise everywhere.
  * CLICKS on standard buttons use `click_stale_safe` (re-find + retry).
  * Navigation is deterministic: force-stop + cold start, then poll for the tab bar.

Config via environment variables:
  ANDROID_SERIAL   adb serial of the target device (required)
  IG_USERNAME      your Instagram handle, used for the safe "return to my profile" deep link
  APPIUM_SERVER    Appium server URL (default http://127.0.0.1:4723)

Prereqs:
  * A physical Android device with the Instagram app installed and logged in.
  * Appium 2/3 with the uiautomator2 driver, and Appium-Python-Client.
  * `appium --address 127.0.0.1 --port 4723 --relaxed-security` running in the background.

⚠️ This drives YOUR OWN account on YOUR OWN device for personal management/automation.
   Respect Instagram's Terms of Service and rate limits. See DISCLAIMER in the README.
"""
import base64
import os
import re
import subprocess
import time

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

SERIAL = os.environ.get("ANDROID_SERIAL", "")
USERNAME = os.environ.get("IG_USERNAME", "")
SERVER = os.environ.get("APPIUM_SERVER", "http://127.0.0.1:4723")
PKG = "com.instagram.android"
MAIN_ACTIVITY = "com.instagram.mainactivity.InstagramMainActivity"
ID = f"{PKG}:id/"


# --------------------------------------------------------------------------- adb / driver
def adb(*args, timeout=30):
    cmd = ["adb"] + (["-s", SERIAL] if SERIAL else []) + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _kill_leftover_instrumentation():
    """uiautomator2 server + test instrumentation can linger and hold the single
    UiAutomation service, causing 'UiAutomation not connected'. Force-stop them."""
    for p in ("io.appium.uiautomator2.server", "io.appium.uiautomator2.server.test",
              "com.github.uiautomator", "com.github.uiautomator.test"):
        adb("shell", "am", "force-stop", p)


def driver(retries=3):
    """Return a login-preserving Appium driver for the physical device.
    Retries on 'UiAutomation not connected' after clearing leftover instrumentation."""
    last = None
    for attempt in range(retries):
        _kill_leftover_instrumentation()
        if attempt:
            time.sleep(1.5)
        adb("shell", "input", "keyevent", "KEYCODE_WAKEUP")
        o = UiAutomator2Options()
        o.platform_name = "Android"
        o.automation_name = "UiAutomator2"
        if SERIAL:
            o.udid = SERIAL
        o.no_reset = True           # keep the existing login
        o.full_reset = False        # never reinstall (that would clear the session)
        o.dont_stop_app_on_reset = True
        o.new_command_timeout = 3600
        o.set_capability("appium:skipDeviceInitialization", True)
        o.set_capability("appium:ignoreHiddenApiPolicyError", True)
        o.set_capability("appium:uiautomator2ServerLaunchTimeout", 90000)
        o.set_capability("appium:uiautomator2ServerInstallTimeout", 90000)
        try:
            return webdriver.Remote(SERVER, options=o)
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"  driver attempt {attempt + 1} failed, cleaning + retrying...")
            _kill_leftover_instrumentation()
            time.sleep(2)
    raise last


# --------------------------------------------------------------------------- finders (safe)
def by_id(d, rid):
    try:
        return d.find_element(AppiumBy.ID, ID + rid)
    except Exception:
        return None


def by_text(d, txt):
    try:
        return d.find_element(AppiumBy.XPATH, f'//*[@text="{txt}"]')
    except Exception:
        return None


def by_desc(d, desc):
    try:
        return d.find_element(AppiumBy.ACCESSIBILITY_ID, desc)
    except Exception:
        return None


def by_desc_contains(d, desc):
    try:
        return d.find_element(AppiumBy.XPATH, f'//*[contains(@content-desc,"{desc}")]')
    except Exception:
        return None


def wait_for(fn, timeout=8, poll=0.6):
    end = time.time() + timeout
    while time.time() < end:
        r = fn()
        if r:
            return r
        time.sleep(poll)
    return None


def wait_text(d, txt, timeout=8):
    return wait_for(lambda: by_text(d, txt), timeout)


def wait_desc(d, desc, timeout=8):
    return wait_for(lambda: by_desc(d, desc), timeout)


def wait_id(d, rid, timeout=8):
    return wait_for(lambda: by_id(d, rid), timeout)


# --------------------------------------------------------------------------- clicks / gestures
def click_stale_safe(finder, tries=5):
    """Re-find + click each attempt; retry on StaleObjectException. IG re-creates
    elements during cold-start/feed loads, so a cached handle goes stale immediately."""
    from selenium.common.exceptions import StaleElementReferenceException
    for _ in range(tries):
        el = finder()
        if not el:
            time.sleep(0.5)
            continue
        try:
            el.click()
            return True
        except StaleElementReferenceException:
            time.sleep(0.6)
        except Exception:
            time.sleep(0.4)
    return False


def gtap(d, x, y, settle=2.0):
    """Appium-native tap. IG's custom buttons ignore element.click() AND `adb input tap`,
    but respond to clickGesture. This is the single most important trick in this toolkit."""
    d.execute_script("mobile: clickGesture", {"x": int(x), "y": int(y)})
    time.sleep(settle)


def tap_text(d, txt, settle=2.0):
    if not wait_text(d, txt, 8):
        return False
    ok = click_stale_safe(lambda: by_text(d, txt))
    if ok:
        time.sleep(settle)
    return ok


def text_bounds(d, txt):
    """Center of an exact-text element, read from page_source (stale-proof)."""
    ps = d.page_source
    e = re.escape(txt)
    m = (re.search(rf'text="{e}"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', ps)
         or re.search(rf'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*text="{e}"', ps))
    if not m:
        return None
    x1, y1, x2, y2 = map(int, m.groups())
    return {"cx": (x1 + x2) // 2, "cy": (y1 + y2) // 2, "x": x1, "y": y1}


def gesture_tap_text(d, txt, settle=2.0):
    """Find a text element and clickGesture its center (stale-proof + IG-compatible)."""
    b = text_bounds(d, txt)
    if not b:
        return False
    gtap(d, b["cx"], b["cy"], settle)
    return True


def bounds_of(d, desc_contains):
    """Center/bounds of the first element whose content-desc contains a substring
    (read from page_source, stale-proof)."""
    ps = d.page_source
    e = re.escape(desc_contains)
    m = (re.search(rf'content-desc="[^"]*{e}[^"]*"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', ps)
         or re.search(rf'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*content-desc="[^"]*{e}[^"]*"', ps))
    if not m:
        return None
    x1, y1, x2, y2 = map(int, m.groups())
    return {"x": x1, "y": y1, "w": x2 - x1, "h": y2 - y1,
            "cx": (x1 + x2) // 2, "cy": (y1 + y2) // 2}


def dismiss(d, extra=()):
    """Best-effort dismissal of common permission / interstitial dialogs (localize as needed)."""
    for opt in ("Continue", "Not now", "Allow", "While using the app", "OK", "Got it",
                "Dismiss", "Later") + tuple(extra):
        el = by_text(d, opt)
        if el:
            try:
                el.click()
                time.sleep(1.0)
            except Exception:
                pass


def screenshot(d, path):
    """Save a screenshot via adb exec-out (does not write a file to the device gallery)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        cmd = ["adb"] + (["-s", SERIAL] if SERIAL else []) + ["exec-out", "screencap", "-p"]
        subprocess.run(cmd, stdout=f, stderr=subprocess.DEVNULL, timeout=30)
    return path


# --------------------------------------------------------------------------- navigation
def open_main():
    adb("shell", "am", "start", "-n", f"{PKG}/{MAIN_ACTIVITY}")
    time.sleep(4)


def return_to_own_profile():
    """Deep link back to your own profile — a reliable 'go home' from any screen.
    Set IG_USERNAME. This does not visit or interact with anyone else."""
    if USERNAME:
        adb("shell", "am", "start", "-a", "android.intent.action.VIEW",
            "-d", f"instagram://user?username={USERNAME}", PKG)
        time.sleep(3)


def goto_profile(d):
    """Deterministic: force-stop -> cold start -> poll for the profile tab -> stale-safe tap.
    The deep-linked profile view has NO bottom nav, hence the force-stop/cold-start."""
    for attempt in range(2):
        adb("shell", "am", "force-stop", PKG)
        time.sleep(2)
        open_main()
        prof = None
        for _ in range(20):
            prof = by_id(d, "profile_tab") or by_id(d, "tab_avatar")
            if prof:
                break
            time.sleep(1)
        if not prof:
            dismiss(d)
            prof = by_id(d, "profile_tab") or by_id(d, "tab_avatar") or by_desc(d, "Profile")
        if not prof:
            print(f"  goto_profile: profile tab not found (attempt {attempt + 1})")
            continue
        time.sleep(2.5)  # let the cold-start animation settle (reduces stale clicks)
        if not click_stale_safe(lambda: by_id(d, "profile_tab") or by_id(d, "tab_avatar")):
            continue
        time.sleep(2.5)
        for _ in range(6):
            if (by_desc(d, "New post") or by_desc(d, "Create") or by_text(d, "Edit profile") or by_text(d, "Editar perfil") or by_desc(d, "Editar perfil")):
                return True
            time.sleep(1)
    return False


# --------------------------------------------------------------------------- media into gallery
def _purge_mediastore(storage_prefix):
    """rm removes files but leaves stale MediaStore rows -> ghost cells in the picker.
    This deletes the rows under a path prefix so the album shows ONLY freshly pushed media."""
    where = f"_data LIKE '{storage_prefix}%'"
    for uri in ("content://media/external/images/media",
                "content://media/external/video/media"):
        adb("shell", f'content delete --uri {uri} --where "{where}"')


def push_images_to_album(paths, album="AppPost"):
    """Push images into a private, freshly-cleaned album so the newest = yours.
    Filename order becomes visual order in the picker (01, 02, ...)."""
    sd = f"/sdcard/Pictures/{album}"
    store = f"/storage/emulated/0/Pictures/{album}/"
    adb("shell", "rm", "-rf", sd)
    _purge_mediastore(store)
    adb("shell", "mkdir", "-p", sd)
    base = int(time.time())
    for k, p in enumerate(paths):
        t = base - k * 20
        os.utime(p, (t, t))
    for p in reversed(paths):
        dst = f"{sd}/{os.path.basename(p)}"
        adb("push", p, dst, timeout=120)
        adb("shell", "am", "broadcast", "-a",
            "android.intent.action.MEDIA_SCANNER_SCAN_FILE", "-d", f"file://{dst}")
        time.sleep(1.0)


def push_video(path, name="clip_now.mp4"):
    dst = f"/sdcard/DCIM/Camera/{name}"
    adb("shell", "rm", "-f", dst)
    adb("push", path, dst, timeout=180)
    adb("shell", "am", "broadcast", "-a",
        "android.intent.action.MEDIA_SCANNER_SCAN_FILE", "-d", f"file://{dst}")
    time.sleep(1.5)
    return dst


# --------------------------------------------------------------------------- text entry
def set_clipboard(d, text):
    """Set the device clipboard via Appium. Plain `adb input text` corrupts non-ASCII
    (Turkish, emoji); clipboard paste preserves them. Note the required contentType casing."""
    b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    d.execute_script("mobile: setClipboard", {"content": b64, "contentType": "PLAINTEXT"})


def paste_into(d, element, text):
    """Focus an EditText and paste clipboard text (unicode/emoji safe)."""
    if element is not None:
        try:
            element.click()
            time.sleep(0.5)
        except Exception:
            pass
    set_clipboard(d, text)
    time.sleep(0.4)
    adb("shell", "input", "keyevent", "279")  # KEYCODE_PASTE
    time.sleep(1)


# --------------------------------------------------------------------------- own posts
def open_first_grid_post(d):
    """Open the first (newest) post from your profile grid. The grid tile carries a
    descriptive content-desc; fall back to a coordinate inside the first tile."""
    for _ in range(3):
        tile = by_desc_contains(d, "Column") or by_desc_contains(d, "Grid")
        if tile:
            try:
                tile.click()
            except Exception:
                adb("shell", "input", "tap", "185", "1528")
        else:
            adb("shell", "input", "tap", "185", "1528")
        time.sleep(3)
        if wait_desc(d, "More options for this post", 6) or by_desc_contains(d, "options"):
            return True
        adb("shell", "input", "keyevent", "KEYCODE_BACK")
        time.sleep(1.5)
    return False


def reveal_action_row(d, tries=4, send_label="Send post"):
    """On a video/reel post opened from the grid, the like/comment/repost/share row sits
    BELOW the video, off-screen. Scroll up until the share button appears."""
    if bounds_of(d, send_label):
        return True
    for _ in range(tries):
        adb("shell", "input", "swipe", "540", "1500", "540", "750", "300")
        time.sleep(1.3)
        if bounds_of(d, send_label):
            return True
    return bool(bounds_of(d, send_label))


# --------------------------------------------------------------------------- reels feed
REELS_TAB_XY = (325, 2070)  # bottom-nav Reels icon on a 1080x2280 screen (adjust per device)


def open_reels(d):
    """Open the Reels feed from a clean tabbed home."""
    adb("shell", "am", "force-stop", PKG)
    time.sleep(2)
    open_main()
    time.sleep(3)
    adb("shell", "input", "tap", str(REELS_TAB_XY[0]), str(REELS_TAB_XY[1]))
    time.sleep(4)


def reels_next(column_x=300):
    """Swipe UP to the next reel. Swipe from a CLEAN column (default left, x~300) so the
    gesture is not absorbed by the right-side action buttons (x~1000) or, on sponsored
    reels, the centre 'Learn more' card."""
    adb("shell", "input", "swipe", str(column_x), "1600", str(column_x), "600", "250")
    time.sleep(3)


def reels_prev(column_x=300):
    """Swipe DOWN to the previous reel."""
    adb("shell", "input", "swipe", str(column_x), "600", str(column_x), "1750", "250")
    time.sleep(3)


# --------------------------------------------------------------------------- housekeeping
if __name__ == "__main__":
    d = driver()
    try:
        print("activity:", d.current_activity, "| page_source length:", len(d.page_source))
    finally:
        return_to_own_profile()
        d.quit()
