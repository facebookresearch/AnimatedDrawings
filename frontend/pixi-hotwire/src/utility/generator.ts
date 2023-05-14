import { Character } from "../scenes/Character";

export function generator(): Character[] {
  const context = require.context("./", true, /\.gif$/);
  const gifFiles = context.keys();
  return gifFiles.map((g) => new Character(g));
}
