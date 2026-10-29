# Documentation

The site uses Astro and Starlight. Documentation pages live in
`src/content/docs/`; static redirects and API bookmark data live in `public/`.
From this directory:

```sh
npm ci
npm run dev
npm run build
```

The dev and build hooks generate the Python API reference from `src/plexosdb/`.
Edit pages in `src/content/docs/` and Python docstrings; generated API pages and
navigation are refreshed automatically.
