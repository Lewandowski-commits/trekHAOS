# TrekHAOS

TrekHAOS runs the official multi-architecture TREK container image on Home Assistant OS.

## Install

Add `https://github.com/Lewandowski-commits/trekHAOS.git` under **Settings > Apps > Install app > ⋮ > Repositories**, then install **TrekHAOS** from the app store.

## First run and sign-in

Start the app and open **Open Web UI** on its app page. TREK's first-run flow creates the initial account.

Before the first start, set both the required `ADMIN_EMAIL` and `ADMIN_PASSWORD` fields in the app's Configuration tab. The app passes these values to TREK as environment variables. TREK uses them only when it creates the first account in an empty database; if either is missing, TREK generates a password instead. Once the database has a user, changing these options will not change that account.

The password option is stored by Home Assistant as an app setting. You can use Home Assistant's `!secret` syntax when setting it in YAML. If TREK has already initialized its database, use the password reset/recovery instructions in the [TREK troubleshooting guide](https://github.com/liketrek/TREK/wiki/Troubleshooting); do not delete the app's data unless you intend to erase its trips and uploads.

`COOKIE_SECURE` defaults to `false`. Keep it set to `false` when accessing TREK over plain HTTP; set it to `true` only when TREK is served over HTTPS.

## Environment variables

The Configuration tab exposes TREK's documented environment variables. Optional fields can be left blank to use TREK's own defaults; Home Assistant passes configured values to the container. Secret values, including passwords, API keys, and `ENCRYPTION_KEY`, use password fields. For details on each variable and its behavior, see the [TREK environment variables reference](https://github.com/liketrek/TREK/wiki/Environment-Variables).

`PORT` is fixed to `3000` inside the container to match the app's port mapping; change the host-side port in Network settings instead. `HOST` is intentionally not exposed because TREK documents it as source/Proxmox-only and says not to set it in container deployments.

## Network access

The app exposes container port `3000` on host port `3000` by default. Use the **Open Web UI** button, or visit `http://<HOME_ASSISTANT_IP>:3000`.

If port 3000 is already in use, change the host port in the app's Network settings. TREK has its own user authentication; use that authentication if you expose the service beyond your trusted local network.

For remote access beyond your local network, use a trusted reverse proxy or tunnel in front of Home Assistant or the app itself. A common setup is Cloudflare Tunnel with separate hostnames for Home Assistant and the TREK app:

```yaml
ingress:
  - hostname: homeassistant.example.com
    service: http://homeassistant:8123
  - hostname: trek.example.com
    service: http://trek:3000
  - service: http_status:404
```

When exposing TREK publicly, keep HTTPS enabled and set the app URL to the public hostname. Example:

```env
APP_URL=https://trek.example.com
ALLOWED_ORIGINS=https://trek.example.com
COOKIE_SECURE=true
```

If Home Assistant itself is behind the tunnel, configure `http:` to trust the proxy that forwards traffic to Home Assistant. This is different from the app-level config above, and it is required to avoid 400 responses from Home Assistant when the domain is served through the tunnel.

Nabu Casa remote access is not currently supported by this app. The Web UI button connects directly to port 3000, which works on the local network but is not proxied by the Home Assistant Cloud URL. Making it available there requires Home Assistant ingress, but TREK's current web client assumes it is served from the root URL and does not support ingress's changing subpath. Enabling ingress without upstream base-path support would break page assets, API requests, and navigation.

## Persistent data

The app maps TREK's `/app/data` and `/app/uploads` directories to Home Assistant's private app storage. Home Assistant includes these files in app backups.

## Support

- [TREK documentation and releases](https://github.com/liketrek/TREK)
- [TrekHAOS issues](https://github.com/Lewandowski-commits/trekHAOS/issues)

## Updating the app version

The `version` in `config.yaml` selects the tag pulled from `mauriceboe/trek`. A scheduled GitHub Actions workflow checks weekly for a newer stable image tag available for both supported architectures and opens a pull request when one is found. Review and merge the pull request to update the app. If pull request creation is blocked, allow GitHub Actions to create pull requests under **Settings > Actions > General**.
