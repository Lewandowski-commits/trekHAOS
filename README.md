# TrekHAOS Home Assistant app repository

This repository provides a Home Assistant app for [TREK](https://github.com/liketrek/TREK), a self-hosted trip planner.

**Credits**: The original TREK app was created by [mauriceboe](https://github.com/mauriceboe). This Home Assistant integration was created by [Lewandowski-commits](https://github.com/Lewandowski-commits).

## 1. Install the Add-on (Supervisor)

Add this repository from **Settings > Apps > Install app > ⋮ > Repositories**, then paste:

```text
https://github.com/Lewandowski-commits/trekHAOS.git
```

[![Add the TrekHAOS app repository to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FLewandowski-commits%2FtrekHAOS.git)

After adding it, install **TrekHAOS** from the app store. See the app's [documentation](./apps/trek-haos/DOCS.md) for setup, access, and data storage details.

## 2. Install the Integration (HACS)

This repository also contains a Custom Integration for TREK. It provides **Calendar** events for your trips and **Sensors** for upcoming trip countdowns.

1. Go to **HACS > Integrations** in your Home Assistant.
2. Click the three dots (⋮) in the top right corner and select **Custom repositories**.
3. Add `https://github.com/Lewandowski-commits/trekHAOS.git` with the category **Integration**.
4. Click **Download** on the newly discovered TREK integration.
5. Restart Home Assistant.
6. Go to **Settings > Devices & Services > Add Integration**, search for **TREK**, and log in with your credentials!

## Remote access with a custom domain

If you want to reach the app from outside your local network without relying on Home Assistant Cloud, use a reverse proxy or tunnel in front of Home Assistant or the app itself.

A common pattern is Cloudflare Tunnel:

- Route `https://trek.example.com` to the app container on port `3000`.
- Route `https://homeassistant.example.com` to Home Assistant itself.
- Keep the app behind HTTPS and enable TREK's authentication.

Example Cloudflare tunnel ingress (generic):

```yaml
ingress:
  - hostname: homeassistant.example.com
    service: http://homeassistant:8123
  - hostname: trek.example.com
    service: http://trek:3000
  - service: http_status:404
```

When using a custom domain, set the app's public URL and origin policy to match the hostname you expose. For example in TREK:

```env
APP_URL=https://trek.example.com
ALLOWED_ORIGINS=https://trek.example.com
COOKIE_SECURE=true
```

If Home Assistant is behind the tunnel, make sure the HA `http:` config trusts the proxy that is forwarding requests. You can then keep the app accessible via a custom hostname while avoiding the Home Assistant Cloud ingress limitation.

## App image

The app uses the official multi-architecture `mauriceboe/trek` image. Its version pins the upstream image tag in [`apps/trek-haos/config.yaml`](./apps/trek-haos/config.yaml).

## License

This repository is licensed under the GNU Affero General Public License v3.0, the same license as the upstream TREK project. See [LICENSE.md](./LICENSE.md) and the [TREK source repository](https://github.com/liketrek/TREK).
