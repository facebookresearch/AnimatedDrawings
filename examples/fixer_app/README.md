# Fixer App (Developer notes)

This folder produces two HTML Jinja template files that are used by the Flask server launched via `../fix_annotations.py`.

The files here that are used by the server are `submit.html` and `dist/index.html`.

### Build process

If you make any changes to `index.html` (or any of the React app components sourced by it), you will need to rebuild the generated output file at `dist/index.html`.

To run this build process, you can run:

```
cd fixer_app
npm install
npm run build
```

This invokes [Parcel](https://parceljs.org/) to build the React app, inlines all JS and CSS code within the output HTML file, and uses [`shx sed`](https://github.com/shelljs/shx#sed) to insert in Jinja template variables post-build.

Note that no build process is required for `submit.html`.



