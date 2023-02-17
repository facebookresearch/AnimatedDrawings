/*
 * Since `next export` currently have issues with image loader and paths,
 * here we define a custom function to resolve path.
 * Caveat: Images are not automatically optimized like, as they would be if deployed with Next.js
 *
 * The base path for development is always "/"
 * For production, you can define the basePath in .env.production
 *
 * You can also access the current base path via process.env.basePath
 */

export function assetLoader({ src }) {
  return `${process.env.basePath}/assets/${src}`;
}

export function getBasePath(src) {
  // When basePath is "", Next.js automatically prepend "/" but not when basePath is "/xyz".
  // Here we account for this condition
  return !process.env.basePath ? `${src}` : `${process.env.basePath}${src}`;
}
