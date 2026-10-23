<div align="center">
  <img src="assets/terry-banner.png" alt="Terry — Your Terra Companion" width="100%">

  # Terry — Your Terra Companion

  **A fox on your desktop to help you keep your Hackatime goals on track.**
</div>

Terry checks your coding time on [Hackatime](https://hackatime.hackclub.com) and lets you know how you’re doing against your daily and weekly goals. Whether you’re on track or need a little nudge, Terry’s got you.

<div align="center">
  <img src="assets/terry-mascot.png" alt="Terry the fox" width="240">
</div>

## What Terry does

- Shows your coding time for today and this week.
- Tracks your daily and weekly goals.
- Gives you a status update to help you stay on track.

## Get started

1. Sign in to [Hackatime](https://hackatime.hackclub.com).
2. Open **Settings** and then **Setup**.
3. Copy your Hackatime API key.
4. Launch Terry. The first run creates `~/.terry_companion/config.json`.
5. Open that file, paste your API key into the `api_key` field, save, and launch Terry again.

For example:

```json
{
  "api_key": "YOUR_HACKATIME_API_KEY"
}
```

Terry starts with a daily goal of **1.5 hours** and a weekly goal of **10 hours**. You can adjust `daily_goal` and `goal_hours` in the same config file.

## Keep your API key private

Your API key is sensitive. Don’t share it or post it publicly.
