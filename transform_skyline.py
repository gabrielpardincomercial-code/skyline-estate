import os
import re
import glob

BASE_DIR = "/Users/gabrielalvespardin/Projetos/skyline-estate"
RAW_PAGES_DIR = "/tmp/skyline_raw_pages"
RAW_FRAMER_DIR = "/tmp/skyline_raw_framer"
OUT_FRAMER_DIR = os.path.join(BASE_DIR, "assets", "framer")

os.makedirs(OUT_FRAMER_DIR, exist_ok=True)

SITE_ID = "757vc66RuZzKa944RVNfCn"

def localize_asset_urls(text):
    # 1. CMS binary database URLs inside .mjs modules
    text = re.sub(
        r'new URL\([\"\x27`]\./([^\"\x27`]+\.framercms)[\"\x27`]\s*,\s*[\"\x27`]https://framerusercontent\.com/modules/[^\"\x27`]+[\"\x27`]\)\.href\.replace\([\"\x27`]/modules/[\"\x27`]\s*,\s*[\"\x27`]/cms/[\"\x27`]\)',
        r'new URL("/assets/cms/\1",location.origin).href',
        text
    )

    # 2. Framer site bundle URLs (.mjs, .json)
    text = text.replace(
        f"https://framerusercontent.com/sites/{SITE_ID}/",
        "/assets/framer/"
    )

    # 3. Videos (.mp4)
    text = re.sub(
        r'https?://framerusercontent\.com/(?:assets|images)/([a-zA-Z0-9_\-]+\.mp4)',
        r'/assets/videos/\1',
        text
    )

    # 4. Fonts (.woff2 from framerusercontent/assets or fonts.gstatic.com)
    text = re.sub(
        r'https?://framerusercontent\.com/assets/([a-zA-Z0-9_\-]+\.woff2)',
        r'/assets/fonts/\1',
        text
    )
    text = re.sub(
        r'https?://fonts\.gstatic\.com/[^\s\"\x27`<>\\)]+/([a-zA-Z0-9_\-]+\.woff2)',
        r'/assets/fonts/\1',
        text
    )

    # 5. Images under /assets/
    text = re.sub(
        r'https?://framerusercontent\.com/assets/([a-zA-Z0-9_\-]+\.(?:png|jpg|jpeg|svg|webp|gif|avif))',
        r'/assets/images/\1',
        text
    )

    # 6. Images under /images/ (with or without query parameters)
    text = re.sub(
        r'https?://framerusercontent\.com/images/([a-zA-Z0-9_\-]+\.[a-zA-Z0-9]+)(?:\?[^\s\"\x27`<>\\)]*)?',
        r'/assets/images/\1',
        text
    )

    return text

print("--- 1. Transforming Framer Runtime Modules (.mjs & .json) ---")
for src_path in sorted(glob.glob(os.path.join(RAW_FRAMER_DIR, "*"))):
    fname = os.path.basename(src_path)
    dest_path = os.path.join(OUT_FRAMER_DIR, fname)
    with open(src_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    content = localize_asset_urls(content)

    # Patch static .framercms range reader so full-file HTTP 200 responses slice cleanly
    if "Unexpected response length" in content:
        content = content.replace(
            "if(l.length!==i)throw Error(`Request failed: Unexpected response length`);",
            "if(l.length!==i)return t.map(e=>l.slice(e.from,e.to));"
        )
        print(f"  [PATCHED] {fname} (static .framercms byte-range slicer)")

    # Specific runtime patches for framer.BkV6hVyt.mjs
    if fname == "framer.BkV6hVyt.mjs":
        old_Ya = "function Ya(e,t){try{let n=new URL(e);return t?n.searchParams.set(`scale-down-to`,`${t}`):n.searchParams.delete(`scale-down-to`),n.toString()}catch{return e}}"
        new_Ya = 'function Ya(e,t){return typeof e=="string"?e.replace(/^https?:\\/\\/framerusercontent\\.com\\/images\\/([^?#]+).*$/,"/assets/images/$1"):e}'
        assert old_Ya in content, "old_Ya not found in framer.BkV6hVyt.mjs"
        content = content.replace(old_Ya, new_Ya)

        old_Qa = "function Qa(e,t,n){if(![`auto`,`lossless`].includes(t.preferredSize??``))return{src:n,srcSet:void 0};if(e){let r=Za(n,t,e);if(!r?.length)return{src:n,srcSet:void 0};let[i,...a]=r;return{src:i?.src,srcSet:a.map(({src:e,scale:t})=>`${e} ${t}x`).join(`, `)}}else return{src:n,srcSet:Xa(n,t,Ja(t.pixelWidth,t.pixelHeight))}}"
        new_Qa = "function Qa(e,t,n){return{src:Ya(n),srcSet:void 0}}"
        assert old_Qa in content, "old_Qa not found in framer.BkV6hVyt.mjs"
        content = content.replace(old_Qa, new_Qa)

        old_Ch = "function Ch(e,t){if(!e||!t?.src)return t;let n=new URL(t.src);return n.searchParams.delete(`scale-down-to`),n.searchParams.delete(`lossless`),{...t,sizes:`min(100vw, ${e.maxWidth-Sh(e)}px)`,srcSet:Qa(t.nodeFixedSize,t,t.src).srcSet}}"
        new_Ch = "function Ch(e,t){if(!e||!t?.src)return t;let s=Ya(t.src);return{...t,src:s,sizes:`min(100vw, ${e.maxWidth-Sh(e)}px)`,srcSet:void 0}}"
        assert old_Ch in content, "old_Ch not found in framer.BkV6hVyt.mjs"
        content = content.replace(old_Ch, new_Ch)

        assert "try{new URL(e);let r=new Image;" in content, "Preloader pattern not found in framer.BkV6hVyt.mjs"
        content = content.replace("try{new URL(e);let r=new Image;", "try{new URL(e,location.origin);let r=new Image;")
        print("  [PATCHED] framer.BkV6hVyt.mjs (local image resolver + CMS binary URL mapper)")

    # Specific patch for script_main.DRH-7Rg6.mjs: disable Framer badge mount
    if fname == "script_main.DRH-7Rg6.mjs":
        old_badge = "(function(){Ar&&s(()=>{T(document.getElementById(`__framer-badge-container`),h(_,{},h(g(()=>import(`./PX9hIOIVM._KE8Wdf_.mjs`)))))})})()"
        assert old_badge in content, "old_badge not found in script_main.DRH-7Rg6.mjs"
        content = content.replace(old_badge, "/* badge disabled */")
        print("  [PATCHED] script_main.DRH-7Rg6.mjs (disabled Framer watermark badge)")

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(content)

ROUTE_MAP = {
    "index.html": "index.html",
    "residences.html": "residences.html",
    "contact.html": "contact.html",
    "404.html": "404.html",
    "privacy.html": "privacy.html",
    "terms.html": "terms.html",
    "residences_bay-residence.html": "residences/bay-residence.html",
    "residences_corner-residence.html": "residences/corner-residence.html",
    "residences_sky-residence.html": "residences/sky-residence.html",
    "residences_penthouse.html": "residences/penthouse.html",
}

print(f"\n--- 2. Transforming {len(ROUTE_MAP)} HTML Pages ---")
for src_name, dest_rel in ROUTE_MAP.items():
    src_path = os.path.join(RAW_PAGES_DIR, src_name)
    dest_path = os.path.join(BASE_DIR, dest_rel)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(src_path, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()

    # Localize all URLs to root-relative /assets/...
    html = localize_asset_urls(html)

    # Strip srcset attributes from SSR <img> tags so browser uses crisp local src
    html = re.sub(r'\ssrcset=[\'"][^\'"]*[\'"]', '', html)

    # Strip ONLY Framer telemetry & editorbar injection scripts + gstatic preconnect
    html = re.sub(
        r'<link\b[^>]*href=[\'"]https://fonts\.gstatic\.com[\'"][^>]*>',
        '',
        html,
        flags=re.IGNORECASE
    )
    html = re.sub(
        r'<script\b[^>]*\bsrc=[\'"][^\'"]*events\.framer\.com[^\'"]*[\'"][^>]*>[\s\S]*?<\/script>',
        '',
        html,
        flags=re.IGNORECASE
    )
    html = re.sub(
        r'<script>try\{if\(localStorage\.getItem\("__framer_force_showing_editorbar_since"\)\)[\s\S]*?<\/script>',
        '',
        html
    )

    # Update canonical and og:url to https://skyline-estate.landingprofile.com
    html = html.replace("https://skyline-estate.framer.website", "https://skyline-estate.landingprofile.com")

    # Normalize all internal relative hrefs (./foo, ../foo, ./) to root-relative (/foo, /)
    depth = dest_rel.count("/")
    if depth == 1:
        folder = dest_rel.split("/")[0]
        html = re.sub(r'href=[\'"]\./([^\'"#]+)(#[^\'"<>]*)?[\'"]', rf'href="/{folder}/\1\2"', html)
        html = re.sub(r'href=[\'"]\.\./([^\'"]*)[\'"]', r'href="/\1"', html)
    else:
        html = re.sub(r'href=[\'"]\./([^\'"]*)[\'"]', r'href="/\1"', html)

    # Inject inline styles and link for main.css
    inline_css = (
        '<style>'
        '#__framer-badge-container, #__framer-editorbar, #__framer-editorbar-container, #template-overlay '
        '{ display: none !important; visibility: hidden !important; opacity: 0 !important; pointer-events: none !important; }'
        '</style>\n'
        '<link rel="stylesheet" href="/assets/css/main.css?v=1">'
    )
    if '</head>' in html:
        html = html.replace('</head>', f'{inline_css}\n</head>')

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Also write index.html inside residences/ so trailing-slash URLs (/residences/) return 200 natively
    if dest_rel == "residences.html":
        folder_index = os.path.join(BASE_DIR, "residences", "index.html")
        os.makedirs(os.path.dirname(folder_index), exist_ok=True)
        with open(folder_index, "w", encoding="utf-8") as f:
            f.write(html)
        print("  [OK] residences/index.html (trailing-slash fallback)")

    print(f"  [OK] {dest_rel}")

print("\n--- Transformation Complete! ---")
