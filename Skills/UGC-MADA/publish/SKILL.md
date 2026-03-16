# Skill: publish

## Purpose
Publish generated video content to Instagram Reels and TikTok for a given influencer account. Uses official APIs as primary channel, Playwright + lightpanda browser as fallback.

---

## Input
```json
{
  "influencer_id": "inf_01",
  "platform": "instagram" | "tiktok" | "both",
  "video_path": "forge/output/inf_01_brand_20260315.mp4",
  "caption": "string (max 2200 chars for IG, 2200 for TT)",
  "hashtags": ["#martinique", "#creole"],
  "cover_time_ms": 1000,
  "schedule_at": null  // ISO 8601 or null for immediate
}
```

## Output
```json
{
  "influencer_id": "inf_01",
  "instagram": {"status": "published" | "scheduled" | "failed", "post_id": "...", "method": "api" | "browser"},
  "tiktok":    {"status": "published" | "scheduled" | "failed", "post_id": "...", "method": "api" | "browser"},
  "errors": []
}
```

---

## Credential Model

All credentials are stored in `.env` on the VPS, namespaced by influencer ID:

```env
# Per influencer — repeat for inf_01 through inf_06
INF_01_IG_ACCESS_TOKEN=...
INF_01_IG_ACCOUNT_ID=...
INF_01_TT_ACCESS_TOKEN=...
INF_01_TT_OPEN_ID=...

# Browser fallback session cookies (exported from browser after manual login)
INF_01_IG_COOKIES_PATH=/opt/ugc_mada/sessions/inf_01_ig_cookies.json
INF_01_TT_COOKIES_PATH=/opt/ugc_mada/sessions/inf_01_tt_cookies.json
```

Thomas creates the accounts and exports session cookies after first login. Tokens are generated via OAuth flows for each platform.

---

## Layer 1 — Instagram (Meta Graph API)

### Flow
```
1. Upload video → POST /v19.0/{ig-account-id}/media
   - media_type=REELS
   - video_url=<presigned S3 or public URL>
   - caption, cover_url, share_to_feed=true

2. Poll upload status → GET /v19.0/{container-id}?fields=status_code
   - Wait until status_code=FINISHED (up to 5 min)

3. Publish → POST /v19.0/{ig-account-id}/media_publish
   - creation_id={container-id}
```

### Rate Limits
- 50 API calls per user per hour
- 25 posts per 24h per account
- Reels: max 15 min, min 3s, MP4/MOV

### Python implementation
```python
import httpx, time, os

async def publish_instagram(influencer_id: str, video_url: str, caption: str) -> dict:
    token = os.environ[f"{influencer_id.upper()}_IG_ACCESS_TOKEN"]
    account_id = os.environ[f"{influencer_id.upper()}_IG_ACCOUNT_ID"]
    base = "https://graph.instagram.com/v19.0"

    async with httpx.AsyncClient() as client:
        # Step 1: create container
        r = await client.post(f"{base}/{account_id}/media", params={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": "true",
            "access_token": token,
        })
        r.raise_for_status()
        container_id = r.json()["id"]

        # Step 2: poll until ready
        for _ in range(30):  # max 5 min
            r = await client.get(f"{base}/{container_id}", params={
                "fields": "status_code",
                "access_token": token,
            })
            if r.json().get("status_code") == "FINISHED":
                break
            await asyncio.sleep(10)
        else:
            raise TimeoutError("Instagram upload timed out")

        # Step 3: publish
        r = await client.post(f"{base}/{account_id}/media_publish", params={
            "creation_id": container_id,
            "access_token": token,
        })
        r.raise_for_status()
        return {"status": "published", "post_id": r.json()["id"], "method": "api"}
```

---

## Layer 1 — TikTok (Content Posting API v2)

### Flow
```
1. Init upload → POST /v2/post/publish/video/init/
   - publish_type=DIRECT_POST
   - video source: FILE_UPLOAD or PULL_FROM_URL

2. Upload video chunks to upload_url

3. Poll status → GET /v2/post/publish/status/fetch/
   - Wait until status=PUBLISH_COMPLETE
```

### Requirements
- TikTok for Developers app approved for Content Posting API
- Scope: video.upload, video.publish
- Token refresh: access tokens expire in 24h, refresh tokens in 365d

### Python implementation
```python
async def publish_tiktok(influencer_id: str, video_path: str, caption: str, hashtags: list) -> dict:
    token = os.environ[f"{influencer_id.upper()}_TT_ACCESS_TOKEN"]
    open_id = os.environ[f"{influencer_id.upper()}_TT_OPEN_ID"]
    base = "https://open.tiktokapis.com"

    async with httpx.AsyncClient() as client:
        # Step 1: init
        r = await client.post(f"{base}/v2/post/publish/video/init/",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8"},
            json={
                "post_info": {
                    "title": caption[:150],
                    "privacy_level": "PUBLIC_TO_EVERYONE",
                    "disable_duet": False,
                    "disable_comment": False,
                    "video_cover_timestamp_ms": 1000,
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": os.path.getsize(video_path),
                    "chunk_size": 10_000_000,
                    "total_chunk_count": 1,
                },
            }
        )
        r.raise_for_status()
        data = r.json()["data"]
        publish_id = data["publish_id"]
        upload_url = data["upload_url"]

        # Step 2: upload
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        await client.put(upload_url,
            headers={"Content-Range": f"bytes 0-{len(video_bytes)-1}/{len(video_bytes)}",
                     "Content-Type": "video/mp4"},
            content=video_bytes,
        )

        # Step 3: poll
        for _ in range(30):
            r = await client.post(f"{base}/v2/post/publish/status/fetch/",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8"},
                json={"publish_id": publish_id},
            )
            if r.json()["data"]["status"] == "PUBLISH_COMPLETE":
                break
            await asyncio.sleep(10)

        return {"status": "published", "post_id": publish_id, "method": "api"}
```

---

## Layer 2 — Browser Fallback (Playwright + lightpanda)

### When fallback triggers
- API returns 4xx/5xx after 2 retries
- TikTok API not yet approved (pending app review)
- Token expired and refresh failed
- Rate limit hit (>25 posts/24h on Instagram)

### lightpanda setup (Docker, VPS)
```bash
# Run lightpanda CDP server
docker run -d --name lightpanda \
  -p 9222:9222 \
  --restart unless-stopped \
  lightpanda/browser:nightly
```

### Playwright connection
```python
from playwright.async_api import async_playwright

async def get_browser():
    """
    Connect to lightpanda CDP. Falls back to system Chromium if lightpanda down.
    """
    p = await async_playwright().start()
    try:
        browser = await p.chromium.connect_over_cdp("ws://127.0.0.1:9222")
        return browser, p
    except Exception:
        # Fallback to Chromium if lightpanda unreachable
        browser = await p.chromium.launch(headless=True)
        return browser, p
```

### Instagram browser flow
```python
async def publish_instagram_browser(influencer_id: str, video_path: str, caption: str) -> dict:
    cookies_path = os.environ[f"{influencer_id.upper()}_IG_COOKIES_PATH"]
    browser, p = await get_browser()
    try:
        context = await browser.new_context()
        await context.add_cookies(json.loads(open(cookies_path).read()))
        page = await context.new_page()

        await page.goto("https://www.instagram.com/")
        # Click Create
        await page.click("[aria-label='New post']", timeout=10000)
        # Upload file
        async with page.expect_file_chooser() as fc_info:
            await page.click("text=Select from computer")
        file_chooser = await fc_info.value
        await file_chooser.set_files(video_path)
        # Navigate steps: crop → filters → caption
        await page.click("text=Next"); await page.wait_for_timeout(1000)
        await page.click("text=Next"); await page.wait_for_timeout(1000)
        await page.fill("[aria-label='Write a caption...']", caption)
        await page.click("text=Share")
        await page.wait_for_selector("text=Your reel has been shared", timeout=120000)
        return {"status": "published", "post_id": None, "method": "browser"}
    finally:
        await browser.close()
        await p.stop()
```

### TikTok browser flow
```python
async def publish_tiktok_browser(influencer_id: str, video_path: str, caption: str) -> dict:
    cookies_path = os.environ[f"{influencer_id.upper()}_TT_COOKIES_PATH"]
    browser, p = await get_browser()
    try:
        context = await browser.new_context()
        await context.add_cookies(json.loads(open(cookies_path).read()))
        page = await context.new_page()

        await page.goto("https://www.tiktok.com/upload")
        await page.wait_for_selector("input[type=file]", timeout=15000)
        await page.set_input_files("input[type=file]", video_path)
        await page.wait_for_selector(".upload-progress-done", timeout=120000)
        await page.fill("[data-e2e='video-desc-input']", caption)
        await page.click("[data-e2e='post-button']")
        await page.wait_for_selector("text=Your video is being uploaded", timeout=30000)
        return {"status": "published", "post_id": None, "method": "browser"}
    finally:
        await browser.close()
        await p.stop()
```

---

## Orchestration Logic

```python
async def publish(influencer_id: str, platform: str, video_path: str,
                  video_url: str, caption: str, hashtags: list) -> dict:
    results = {}

    platforms = ["instagram", "tiktok"] if platform == "both" else [platform]

    for plat in platforms:
        try:
            if plat == "instagram":
                result = await publish_instagram(influencer_id, video_url, caption)
            else:
                result = await publish_tiktok(influencer_id, video_path, caption, hashtags)
        except Exception as api_error:
            # Fallback to browser
            try:
                if plat == "instagram":
                    result = await publish_instagram_browser(influencer_id, video_path, caption)
                else:
                    result = await publish_tiktok_browser(influencer_id, video_path, caption)
                result["fallback_reason"] = str(api_error)
            except Exception as browser_error:
                result = {"status": "failed", "error": str(browser_error), "method": "browser"}

        results[plat] = result

    return {"influencer_id": influencer_id, **results}
```

---

## Scheduling

When `schedule_at` is set, do NOT call publish immediately. Instead write to the n8n schedule queue:

```python
# POST to n8n webhook
await httpx.post(
    f"{N8N_BASE_URL}/webhook/ugc-schedule",
    json={"influencer_id": influencer_id, "platform": platform,
          "video_path": video_path, "caption": caption,
          "publish_at": schedule_at},
    headers={"Authorization": f"Bearer {N8N_API_KEY}"}
)
```

n8n workflow polls the queue and calls `publish()` at the right time.

---

## Notes

- lightpanda is Beta — monitor for regressions after nightly updates
- Instagram selector strings change frequently — pin to tested selectors, add fallback XPath
- Session cookies expire — Thomas should re-export cookies monthly or when browser flow fails
- Never store cookies or tokens in this repo or any git-tracked file
- TikTok API review can take 1-4 weeks — browser fallback is the default until approval
