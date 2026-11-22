# Instagram Android Automation with Appium 📱

**Automate the Instagram app on a real Android phone — in Python, through the actual UI.**

This open-source **Instagram automation** toolkit (and Claude skill) uses [Appium](https://appium.io/)
and `adb` to drive the **Instagram Android app** on a **physical device**. It lets you
**publish posts, reels and stories, repost your own content, delete posts, unsend messages, and
browse the reels feed** — by operating the real app the way a person would, with no private or
HTTP API and no third-party service.

Unlike headless "Instagram API bot" projects, it works the on-screen UI with `uiautomator2`
under Appium, which is the only reliable way to reach Instagram's custom-rendered Android
screens (DM inbox, notes, story viewer, the media-picker grid, the reels feed). The heart of the
project is a [techniques guide](docs/TECHNIQUES.md) that documents the non-obvious tricks which
make **Android Instagram UI automation** actually work.

### ✨ What you can do
- 📸 **Publish carousel & photo posts** — full aspect ratio (no forced 1:1 crop), unicode/emoji captions.
- 🎬 **Publish reels** from a local video, keeping the original audio.
- 📖 **Publish & share stories** — post a fresh image to your story, or add an existing post/reel to it.
- 🔁 **Repost your own posts and reels.**
- 🗑️ **Delete posts** and **unsend accidental DMs**.
- 🎞️ **Browse the reels feed** for content research — observation only (no likes, comments or follows).

### 🚀 Why real-device UI automation (Appium) instead of an API?
Instagram has no public publishing API for personal accounts, and private/HTTP clients get
flagged fast. Driving the **real app on a real Android device** looks like ordinary human
traffic, keeps your existing login (`noReset`), and reaches every screen the app can show.
The trade-off is that Instagram's custom rendering breaks naive tooling — which is exactly what
this project solves. See the [techniques guide](docs/TECHNIQUES.md): native `clickGesture` for
buttons that ignore normal taps, stale-proof reads from `page_source`, MediaStore cleanup for
the media picker, the full-aspect crop toggle, reel-cell selection, and reels scrolling.

**Keywords:** Instagram automation · Instagram Android automation · Appium · uiautomator2 · adb ·
mobile UI automation · Android device automation · publish Instagram posts / reels / stories with
Python · auto post to Instagram · open source.

---

## 🇹🇷 Türkçe — Bu proje ne işe yarar?

**Instagram uygulamasını gerçek bir Android telefonda, Python ile, arayüz üzerinden otomatikleştir.**

Bu açık kaynak **Instagram otomasyon** araç seti (ve Claude skill'i), [Appium](https://appium.io/)
ve `adb` kullanarak **Instagram Android uygulamasını fiziksel bir cihazda** sürer. Böylece
**gönderi, reels ve hikaye paylaşma; kendi içeriğini repost etme; gönderi silme; mesaj geri alma;
reels akışında gezinme** işlemlerini — gizli/HTTP API veya üçüncü taraf servis olmadan,
uygulamayı bir insan gibi kullanarak — yapabilirsin.

Headless "Instagram API botu" projelerinin aksine, Appium altında `uiautomator2` ile ekran
arayüzünü sürer; bu, Instagram'ın özel render edilen Android ekranlarına (DM kutusu, notlar,
hikaye görüntüleyici, medya seçici grid, reels akışı) ulaşmanın **tek güvenilir yolu**. Projenin
kalbi, Android'de **Instagram arayüz otomasyonunu** gerçekten çalıştıran ipuçlarını belgeleyen
[teknikler rehberi](docs/TECHNIQUES.md).

### ✨ Neler yapabilirsin
- 📸 **Carousel & fotoğraf gönderisi paylaş** — tam en-boy oranı (zorunlu 1:1 kırpma yok), Türkçe/emoji açıklama.
- 🎬 **Reels paylaş** (yerel videodan, orijinal ses korunur).
- 📖 **Hikaye paylaş** — taze görseli hikayene koy ya da mevcut gönderiyi/reel'i hikayene ekle.
- 🔁 **Kendi gönderi ve reels'ini repost et.**
- 🗑️ **Gönderileri sil**, **kazara atılan DM'leri geri al**.
- 🎞️ **Reels akışında gezin** — içerik araştırması için, salt-gözlem (beğeni/yorum/takip yok).

### 🚀 Neden gerçek-cihaz arayüz otomasyonu (Appium)?
Instagram'ın kişisel hesaplar için genel bir yayın API'si yok ve gizli/HTTP istemciler hızla
işaretleniyor. **Gerçek uygulamayı gerçek bir Android cihazda** sürmek, normal insan trafiğine
benzer, mevcut oturumunu korur (`noReset`) ve uygulamanın gösterebildiği her ekrana ulaşır.
Bedeli: Instagram'ın özel render'ı basit araçları bozar — bu projenin çözdüğü sorun tam da bu.
Detay için [teknikler rehberi](docs/TECHNIQUES.md): normal dokunuşa yanıt vermeyen butonlar için
native `clickGesture`, `page_source`'tan stale-proof okuma, medya seçici için MediaStore
temizliği, tam-oran kırpma anahtarı, reel hücre seçimi ve reels kaydırma.

**Anahtar kelimeler:** Instagram otomasyonu · Instagram Android otomasyon · Appium · uiautomator2 ·
adb · mobil arayüz otomasyonu · Android cihaz otomasyonu · Python ile Instagram gönderi / reels /
hikaye paylaşma · otomatik Instagram paylaşımı · açık kaynak.

---

## Requirements
- A physical Android phone with the Instagram app installed and **already logged in**.
- `adb` (Android platform-tools) and the device connected/authorised.
- Appium 2/3 with the `uiautomator2` driver, plus `Appium-Python-Client` (see `requirements.txt`).
- Java + Android SDK (for the Appium uiautomator2 driver).

## Setup
```bash
pip install -r requirements.txt
# start the Appium server (keep it running):
appium --address 127.0.0.1 --port 4723 --relaxed-security

# configure the target (never reinstalls / never logs out):
export ANDROID_SERIAL="<your adb serial>"    # from: adb devices
export IG_USERNAME="<your_instagram_handle>" # used only for the 'return to my profile' deep link
# optional: export APPIUM_SERVER="http://127.0.0.1:4723"
```
The driver uses `noReset=true` / `full_reset=false`, so your login is preserved.

## Usage
Every publishing example supports `--dry-run` (drives up to the Share screen without posting).
```bash
python examples/publish_carousel.py --images a.jpg b.jpg --caption "hello" --dry-run
python examples/publish_reel.py     --video clip.mp4 --caption "hello" --dry-run
python examples/post_to_story.py    --dry-run
python examples/repost.py           --dry-run
python examples/browse_reels.py     --count 5
python examples/delete_all_posts.py --yes            # destructive; recoverable ~30 days
```
`ig_appium.py` is the reusable helper library; the `examples/` scripts show how to compose it.

## Notes on reliability
Instagram's UI shifts between app versions and device languages. Text selectors in the examples
are English placeholders — adjust them to your app language. Hard-coded coordinates assume a
**1080×2280** screen; prefer reading positions from `page_source`. Cold-start navigation is slow
but deterministic (force-stop → cold start → poll for the tab bar).

## ⚠️ Disclaimer
This is for **personal management of your own account on your own device**, and for learning how
Android UI automation works. Automating Instagram may violate its
[Terms of Use](https://help.instagram.com/581066165581870); use it thoughtfully, keep volumes
human, and accept the risk to your own account. Do **not** use it to spam, mass-message, scrape,
impersonate, or interact with other people's accounts. The reels-browsing example is
observation-only. No warranty; you are responsible for how you use it.

## License
[PolyForm Noncommercial License 1.0.0](LICENSE) — free to use, modify and share for any
**non-commercial** purpose. **Commercial use (including selling it or a service built on it) is
not permitted.**
