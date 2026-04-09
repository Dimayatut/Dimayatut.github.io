# AGENTS.md

## Cursor Cloud specific instructions

This is a single-file static HTML portfolio site (`index.html`). There are no build tools, package managers, or dependencies.

### Running the dev server

```bash
cd /workspace && python3 -m http.server 8080
```

The site is then available at `http://localhost:8080/`.

### Testing

- **Lint/build/unit tests:** Not applicable — there is no build system, linter, or test framework configured.
- **Manual testing:** Open `http://localhost:8080/` in a browser and verify all sections render correctly. Navigation anchor links (`#about`, `#projects`, `#contact`) should scroll to the corresponding sections.
