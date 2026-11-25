# Skyline Residences — Private Homes Above Brickell Bay

A standalone, pixel-perfect 1:1 clone of [Skyline Residences](https://skyline-estate.framer.website/).

## Features
- **100% Localized Assets**: All web fonts (`.woff2`), high-resolution photography, interactive scroll-sequence frames, and UI assets stored locally in `assets/`.
- **Self-Hosted Framer Runtime & CMS**: Complete `.mjs` modules and `.framercms` binary databases with static byte-range slicer patches for LiteSpeed/Apache.
- **Interactive Scroll Sequence & Floor Explorer**: Full 96-frame WebGL/Canvas scroll film and interactive floor/residence selector preserved 1:1.
- **Clean URLs**: Server-side URL rewriting via `.htaccess` (`/residences`, `/residences/penthouse`, `/contact`, `/privacy`, `/terms`).
- **Telemetry & Watermark Free**: Removed Framer analytics, editor overlays, and badge containers.

## Structure
```
skyline-estate/
├── index.html
├── residences.html
├── contact.html
├── privacy.html
├── terms.html
├── 404.html
├── residences/
│   ├── index.html
│   ├── bay-residence.html
│   ├── corner-residence.html
│   ├── sky-residence.html
│   └── penthouse.html
└── assets/
    ├── cms/
    ├── css/
    ├── fonts/
    ├── framer/
    └── images/
```
