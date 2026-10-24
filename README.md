# TrekHAOS Home Assistant app repository

This repository provides a Home Assistant app for [TREK](https://github.com/liketrek/TREK), a self-hosted trip planner.

## Install

Add this repository from **Settings > Apps > Install app > ⋮ > Repositories**, then paste:

```text
https://github.com/Lewandowski-commits/trekHAOS.git
```

[![Add the TrekHAOS app repository to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FLewandowski-commits%2FtrekHAOS.git)

After adding it, install **TrekHAOS** from the app store. See the app's [documentation](./apps/trek-haos/DOCS.md) for setup, access, and data storage details.

## App image

The app uses the official multi-architecture `mauriceboe/trek` image. Its version pins the upstream image tag in [`apps/trek-haos/config.yaml`](./apps/trek-haos/config.yaml).

## License

This repository is licensed under the GNU Affero General Public License v3.0, the same license as the upstream TREK project. See [LICENSE.md](./LICENSE.md) and the [TREK source repository](https://github.com/liketrek/TREK).
