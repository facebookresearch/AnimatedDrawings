import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { serialize } from "next-mdx-remote/serialize";
import { MDXRemote } from "next-mdx-remote";
import remarkGfm from "remark-gfm";
const rehypePrism = require("@mapbox/rehype-prism");

import Head from "next/head";
import Nav from "../components/Nav";
import Components from "../components/_export";
import {getBasePath} from "../lib/paths";

const Site = require("../site.json");

const postsDirectory = path.join(process.cwd(), "sections");

function getAllPostIds() {
  const fileNames = fs.readdirSync(postsDirectory);

  // Returns an array that looks like this:
  // [
  //   { params: { id: 'abc' } },
  //   { params: { id: 'xyz' } }, ...
  // ]
  return fileNames.map((fileName) => {
    return {
      params: {
        id: fileName.replace(/\.mdx?$/, ""),
      },
    };
  });
}

function getAllMetaData() {
  // Read all files under /sections and get their metadata
  const fileNames = fs.readdirSync(postsDirectory);
  const allMetaData:any = fileNames.map((fileName) => {
    // Remove ".md" from file name to get id
    const id = fileName.replace(/\.mdx?$/, "");

    // Read markdown file as string
    const fullPath = path.join(postsDirectory, fileName);
    const fileContents = fs.readFileSync(fullPath, "utf8");

    // Use gray-matter to parse the post metadata section
    const { data } = matter(fileContents);

    // Combine the data with the id
    return {
      id,
      ...data, // merge other frontmatter like in data:{title, date}
    };
  });

  // sort by frontmatter 'order'
  return allMetaData
    .filter(({ order }) => order >= 0)
    .sort(({ order: a }, { order: b }) => {
      if (a < b) {
        return -1;
      } else if (a > b) {
        return 1;
      } else {
        return 0;
      }
    });
}

export async function getStaticPaths() {
  const paths = getAllPostIds();
  return {
    paths,
    fallback: false,
  };
}

export const getStaticProps = async ({ params: { id } }) => {
  // Parse current MDX file
  const markdownWithMeta = fs.readFileSync(
    path.join("sections", id + ".mdx"),
    "utf-8"
  );
  const { data, content } = matter(markdownWithMeta);
  data.id = id;
  const mdxSource = await serialize(content, {
    mdxOptions: {
      remarkPlugins: [remarkGfm],
      rehypePlugins: [rehypePrism]
    },
  });
  const allMetaData = getAllMetaData();

  return {
    props: {
      id,
      mdxSource,
      currentMetaData: data,
      allMetaData,
    },
  };
};

export default function Post({ currentMetaData, allMetaData, mdxSource }) {
  const title = `${Site.title}: ${currentMetaData.title}`
  return (
    <div>
      <Head>
        <title>{title}</title>

        <meta property="og:title" content={Site.title} />
        <meta property="og:site_name" content={Site.title} />
        <meta property="og:description" content={Site.description} />
        <meta property="og:type" content="website" />
        <meta property="og:image" content={getBasePath(Site.thumbnail)} />
        <meta name="twitter:card" content="summary_large_image" />
      </Head>

      <Nav items={allMetaData} selected={currentMetaData.id} />
      <div className="prose prose-starter">
        <MDXRemote {...mdxSource} components={Components} />
      </div>
    </div>
  );
}
