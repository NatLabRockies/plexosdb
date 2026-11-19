# Documentation

The site uses Astro and Starlight. Documentation pages live in
`src/content/docs/`; static redirects and API bookmark data live in `public/`.
From this directory:

```sh
npm ci
npm run dev
npm run build
```

Generated API references are checked into the repository. Routine dev and build
commands do not rewrite them. After changing public Python APIs or their
docstrings, run `npm run generate:api` and review the generated changes.
