# Maverick Workplace Device Access

Maverick has a hard access rule: the workplace must work from every Edwin device.
`127.0.0.1` and `localhost` are development details, not final user-facing
links.

## Access Order

1. **Always-on HTTPS host** - the always-on HTTPS host is required for iPhone,
   iPad, Mac, and remote access.
   Acceptable targets include Netlify, Cloudflare Pages, GitHub Pages, or an
   equivalent static HTTPS host.
2. **Folder-visible handoff** - every device path must point back to the
   `MAVERICK` folder and its top-level `WORKPLACE_INDEX.md`.
3. **PWA install** - available after any supporting web surface is served from
   HTTPS. This is optional support, not the identity of Maverick.
4. **Same-Wi-Fi fallback** - useful for testing from the iPhone while the Mac is
   awake:

   ```bash
   python3 factory/maverick_serve_devices.py --port 4181
   ```

   Then open `http://<mac-lan-ip>:4181/` from the iPhone.

## Hard Rules

- Never present `127.0.0.1` as the final answer for iPhone or multi-device use.
- Never call a LAN URL always-on unless the Mac is intentionally kept awake and
  reachable.
- Every session must leave the `MAVERICK` folder more readable or more useful.
- Any portable package or dashboard must point back to the folder-first
  workplace rule.
- Public deployment remains confirmation-gated through `github_publish` until
  the target host/repo/branch is confirmed.

## Validation

Run:

```bash
python3 factory/maverick_device_access.py
python3 factory/validate_maverick.py --phase device-access
```

The validator proves the device rule exists. The workplace rule in
`docs/maverick-workplace-folder-rule.md` defines the stronger product boundary:
Maverick is the folder first.
