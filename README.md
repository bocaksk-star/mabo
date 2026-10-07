# MaBo Digital website

Portfolio and services site for MaBo Digital (Marian Boledovic).

- `site/` is the published website. `site/index.html` is the whole page.
- `wrangler.jsonc` tells Cloudflare to serve `site/` as a static Worker named `mabo-digital`.
- Deploys run on Cloudflare: the repository is connected to the Worker (Workers Builds), so every push to `main` publishes the site. Deploy command: `npx wrangler deploy`.
- The Search Console figures in the page are a snapshot (data to 4 Oct 2026), stored in the `SITES` array in `site/index.html`.
