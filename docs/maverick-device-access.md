# Maverick Device Access

Maverick has a hard access rule: the cockpit must work from every Edwin device.
`127.0.0.1` and `localhost` are development details, not final user-facing
links.

## Access Order

1. **Always-on HTTPS host** - the always-on HTTPS host is required for iPhone,
   iPad, Mac, and remote access.
   Acceptable targets include Netlify, Cloudflare Pages, GitHub Pages, or an
   equivalent static HTTPS host.
2. **PWA install** - available after the cockpit is served from HTTPS. The
   dashboard ships `manifest.webmanifest` and `service-worker.js` so the device
   can keep a cached cockpit shell.
3. **Same-Wi-Fi fallback** - useful for testing from the iPhone while the Mac is
   awake:

   ```bash
   python3 factory/maverick_serve_devices.py --port 4181
   ```

   Then open `http://<mac-lan-ip>:4181/` from the iPhone.

## Hard Rules

- Never present `127.0.0.1` as the final answer for iPhone or multi-device use.
- Never call a LAN URL always-on unless the Mac is intentionally kept awake and
  reachable.
- Every portable package must include the cockpit HTML, CSS, JavaScript,
  manifest, service worker, and dashboard data.
- Public deployment remains confirmation-gated through `github_publish` until
  the target host/repo/branch is confirmed.

## Validation

Run:

```bash
python3 factory/maverick_device_access.py
python3 factory/validate_maverick.py --phase device-access
```

The validator proves the hard rule exists, the PWA files are present, and the
dashboard data exposes the same device-access contract.
