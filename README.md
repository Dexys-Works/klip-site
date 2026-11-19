# klip.dexysworks.com

Static landing page for Dexys Klip, served by GitHub Pages. Plain HTML, CSS and a little JavaScript: no build service,
no third-party requests (fonts and images are self-hosted).

The Klip app itself (sign-in, dashboard, billing, legal pages) will live at **https://app.klip.dexysworks.com**.

**Early access mode (current).** Until the app is deployed, `APP_LIVE = False` in `src/build.py`: every call to action
is "Get early access", a pre-filled email to `CONTACT` (paulo.cardoso@outlook.com) in the visitor's language that
names the plan they clicked, and links into the app (sign-in, legal pages) are left out. No form service or other
third party is involved. When the app works at its URL, set `APP_LIVE = True`, rebuild and commit: "Sign in",
"Start free", plan checkout links and the legal links come back.

## Layout

| Path | What |
| --- | --- |
| `index.html`, `pt-br/index.html`, `nl/index.html` | The page in English, Brazilian Portuguese and Dutch. **Generated**, don't edit by hand. |
| `404.html`, `sitemap.xml`, `robots.txt` | Generated as well. |
| `src/build.py` | Generates the files above. Plan limits, prices and the app URL are constants at the top. |
| `src/strings.json` | All page text in the three languages. |
| `assets/` | Stylesheet, script, fonts (Manrope for the page; Poppins and Anton, the app's caption fonts, subset to Latin; all SIL Open Font License), favicon and the social-sharing image. |
| `CNAME`, `.nojekyll` | GitHub Pages custom domain; serve files as they are. |

## Change the page

```sh
python3 src/build.py                       # regenerate the pages (Python 3.9+, standard library only)
python3 -m http.server 8090                # preview at http://localhost:8090
```

Edit text in `src/strings.json` (all three languages, same keys), structure in `src/build.py`, styling in
`assets/style.css`, then rebuild and commit the generated files with your change.

Rules for the copy: claims must be true. Don't add testimonials, customer logos, usage numbers or certifications
unless they're real; GDPR/SOC 2 work is readiness only, so say "processed in the EU", "export or delete your data"
and "not used for training", not "GDPR compliant" or "SOC 2".

**Prices** (€19 Pro, €79 Business, monthly, VAT included) and plan limits are in `PLANS` in `src/build.py`. Keep them
equal to the app: limits in `worker/clipper/billing.py`, prices in `CLIPPER_PRICE_PRO_EUR` / `CLIPPER_PRICE_BUSINESS_EUR`.

## Publish (first time)

1. Create the repository `Dexys-Works/klip-site` on GitHub (public, or private on a plan with Pages), then push:
   ```sh
   git add -A && git commit -m "Publish the Dexys Klip landing page"
   git remote add origin git@github.com:Dexys-Works/klip-site.git
   git push -u origin main
   ```
2. Repository **Settings → Pages**: Source "Deploy from a branch", branch `main`, folder `/ (root)`.
3. DNS for dexysworks.com: add `CNAME  klip  dexys-works.github.io`.
4. Back in **Settings → Pages**, the custom domain shows `klip.dexysworks.com`; tick **Enforce HTTPS** once the
   certificate is issued (can take up to an hour).
5. Optional: verify `dexysworks.com` under the organization's **Settings → Pages** so nobody else can claim subdomains.

## The app moves to app.klip.dexysworks.com

Then switch off early access mode (`APP_LIVE = True`). Steps:

- Terraform (`infra/aws` or `infra/azure` in the app repo): `domain_name = "app.klip.dexysworks.com"`, apply, and add
  the DNS records Terraform outputs for that host.
- Clerk dashboard: set the production domain/allowed origins to `app.klip.dexysworks.com` (and its redirect URLs).
- Mollie: webhook and redirect URLs follow `CLIPPER_PUBLIC_APP_URL`, which Terraform derives from `domain_name`.
