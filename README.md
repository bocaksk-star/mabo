# MaBo Digital website

Portfolio and services site for MaBo Digital (Marian Boledovic).

- `site/` is the published website. `site/index.html` is the whole page.
- `wrangler.jsonc` tells Cloudflare to serve `site/` as a static Worker named `mabo`.
- Deploys run on Cloudflare Pages (project `mabodigital`): every push to `main` publishes `site/` to https://mabodigital.dev.
- The Search Console figures in the page are a snapshot (data to 4 Oct 2026), stored in the `SITES` array in `site/index.html`.

## Contact form
- `worker/index.js` is the `mabo` Worker. It runs on `mabodigital.dev/api/*` (route in `wrangler.jsonc`) and handles `POST /api/contact`.
- Each enquiry is saved to the D1 database `mabo-contact` (table `enquiries`) and emailed to bocak.sk@gmail.com through Cloudflare Email Routing, with Reply-To set to the sender.
- `hello@mabodigital.dev` forwards to bocak.sk@gmail.com (Email Routing rule).

## Source of the pages
- `tools/` holds the generator scripts used to build `site/` (home page, service pages, case studies, privacy policy, sitemap). They expect the original working folders and are kept for reference.
