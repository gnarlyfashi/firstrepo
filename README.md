# firstrepo

Static landing page ready for GitHub Pages. The site uses a single `index.html` with embedded styles, so you can publish it instantly without any build tools.

## Preview locally
Open `index.html` in your browser:

```bash
# from the repository root
python -m http.server 8000
# then visit http://localhost:8000
```

## Publish on GitHub Pages
1. Push this repository to GitHub.
2. In your repo, go to **Settings → Pages**.
3. Choose your default branch and select the root folder, then click **Save**.
4. Your site will be available at `https://<username>.github.io/<repository>/`.

## Customize
- Update the text in `index.html` to match your project.
- Tweak the accent colors at the top of the CSS variables block.
- Add more sections by duplicating the existing cards or callout panel.
