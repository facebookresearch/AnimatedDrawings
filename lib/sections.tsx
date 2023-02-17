/* This file was based on Next.js tutorial. It's been mostly refactored into [id].js. To be removed */

// import fs from "fs";
// import path from "path";
// import matter from "gray-matter";
// import { remark } from "remark";
// import html from "remark-html";

// const postsDirectory = path.join(process.cwd(), "sections");

// /**
//  * Get all the ids (filenames) in the `postsDirectory`
//  */
// export function getAllPostIds() {
//   const fileNames = fs.readdirSync(postsDirectory);

//   // Returns an array that looks like this:
//   // [
//   //   { params: { id: 'abc' } },
//   //   { params: { id: 'xyz' } }, ...
//   // ]
//   return fileNames.map((fileName) => {
//     return {
//       params: {
//         id: fileName.replace(/\.mdx?$/, ""),
//       },
//     };
//   });
// }

// /**
//  * Read the mdx files in the `postsDirectory`, and sort the contents by the `order` property in frontmatter
//  * @returns
//  */
// export function getSortedMetaData() {
//   // Get file names under /posts
//   const fileNames = fs.readdirSync(postsDirectory);
//   const allPostsData = fileNames.map((fileName) => {
//     // Remove ".md" from file name to get id
//     const id = fileName.replace(/\.mdx?$/, "");

//     // Read markdown file as string
//     const fullPath = path.join(postsDirectory, fileName);
//     const fileContents = fs.readFileSync(fullPath, "utf8");

//     // Use gray-matter to parse the post metadata section
//     const matterResult = matter(fileContents);

//     // Combine the data with the id
//     return {
//       id,
//       ...matterResult.data, // .id and other frontmatter like {title, date}
//     };
//   });

//   // Sort posts by date
//   return allPostsData.sort(({ order: a }, { order: b }) => {
//     if (a < b) {
//       return -1;
//     } else if (a > b) {
//       return 1;
//     } else {
//       return 0;
//     }
//   });
// }

// /**
//  * Get the content by its id
//  * @param {*} id mdx filename (without extension)
//  * @returns {id, contentHtml. ...matterResult.data}
//  */
// export async function getPostData(id) {
//   const fullPath = path.join(postsDirectory, `${id}.mdx`);
//   const fileContents = fs.readFileSync(fullPath, "utf8");

//   // Use gray-matter to parse the post metadata section
//   const matterResult = matter(fileContents);

//   // Use remark to convert markdown into HTML string
//   const processedContent = await remark()
//     .use(html)
//     .process(matterResult.content);
//   const contentHtml = processedContent.toString();

//   // Combine the data with the id and contentHtml
//   return {
//     id,
//     contentHtml,
//     ...matterResult.data, // .id and other frontmatter like {title, date}
//   };
// }

// export async function getPath(id) {
//   return path.join(postsDirectory, `${id}.mdx`);
// }


export {}