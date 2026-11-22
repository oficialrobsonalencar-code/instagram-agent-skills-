---
name: instagram-android-automation
description: >-
  Drive the Instagram Android app on a physical device via Appium + adb to manage your own
  account: publish carousel/photo posts, reels and stories, share a post to your story, repost
  your own content, delete posts, unsend an accidental DM, and browse the reels feed
  (observation only). Use when a task needs to operate the real Instagram app UI (not an HTTP
  API) on a connected Android phone. Requires ANDROID_SERIAL and a running Appium server.
---

# Instagram Android Automation (Appium)

Operate the Instagram Android app through its real UI. This skill exists because Instagram's
custom-rendered screens defeat naive automation; the working approach and its non-obvious tricks
are captured here and in `docs/TECHNIQUES.md`.

## When to use
- Publishing to / managing **your own** Instagram account from a connected Android device.
- Any flow that must go through the actual app UI (DM inbox, notes, story viewer, create-hub
  media grid, reels feed) where an HTTP/private API is not available or not wanted.

## Prerequisites
1. A physical Android phone with Instagram installed and **logged in**; `adb devices` shows it.
2. Appium 2/3 + uiautomator2 driver + `Appium-Python-Client` (`pip install -r requirements.txt`).
3. Appium server running: `appium --address 127.0.0.1 --port 4723 --relaxed-security`.
4. Environment: `export ANDROID_SERIAL=<serial>` and `export IG_USERNAME=<your_handle>`.

## How to use
`ig_appium.py` is the helper library. `examples/*.py` are runnable flows, each with `--dry-run`:

| Task | Command |
|------|---------|
| Publish carousel/photo (full aspect) | `python examples/publish_carousel.py --images a.jpg b.jpg --caption "..."` |
| Publish reel | `python examples/publish_reel.py --video clip.mp4 --caption "..."` |
| Share your post to story | `python examples/post_to_story.py` |
| Repost your own post | `python examples/repost.py` |
| Delete all posts (destructive) | `python examples/delete_all_posts.py --yes` |
| Browse reels (observation) | `python examples/browse_reels.py --count 5` |

## Key rules (see docs/TECHNIQUES.md for the why)
- IG's custom buttons ignore `element.click()` and `adb tap`; use Appium `mobile: clickGesture`
  (`gtap` / `gesture_tap_text`). Standard buttons (Next/Share/OK) use `element.click()`.
- Read state from `page_source` (stale-proof); click standard buttons with `click_stale_safe`.
- Navigate with force-stop → cold start → poll for the profile tab; end on your own profile.
- Push media into a private, MediaStore-purged album; captions via clipboard paste (unicode-safe).
- Verify every step with a screenshot; text selectors are English placeholders — localize them.

## Safety
Personal use, your own account, your own device. Respect Instagram's Terms. Never spam,
mass-message, scrape, impersonate, or interact with other people's accounts. In the DM area,
never blind-tap the compose bar or reaction bar (that sends content). See the README disclaimer.
