var site = require("./site.json");

const base =
  process.env.NODE_ENV === "production"
    ? `/${process.env.NEXT_PUBLIC_BASE_PATH}`
    : "";

console.info(
  `↳ Base path is '${
    base || "/"
  }'. You can edit production base-path in .env.production`
);

module.exports = {
  basePath: base,
  env: {
    basePath: base,
  },
  images: {
    loader: "custom",
    path: "/",
  },
};

/*
 * Commenting this out for now, as we'll try mdx-remote (https://github.com/hashicorp/next-mdx-remote)
 * instead of @next/mdx (https://nextjs.org/docs/advanced-features/using-mdx)

const withMDX = require("@next/mdx")({
  extension: /\.mdx?$/,
  options: {
    remarkPlugins: [],
    rehypePlugins: [],
    // If you use `MDXProvider`, uncomment the following line.
    // providerImportSource: "@mdx-js/react",
  },
});
module.exports = withMDX({
  // Append the default value with md extensions
  pageExtensions: ["ts", "tsx", "js", "jsx", "md", "mdx"],
});

*/
