import Head from "next/head";
import Link from "next/link";
import Nav from "../components/Nav";
import Site from "../site.json";

export async function getStaticProps() {
  // const sectionMetaData = getSortedMetaData();
  const sectionMetaData = {};
  return {
    props: {
      sectionMetaData,
    },
  };
}

export default function Home({ sectionMetaData }) {
  return (
    <>
      <Head>
        <meta
          http-equiv="refresh"
          content={`0; url=${process.env.basePath}/home`}
        />
      </Head>
      <p>Redirecting to homepage</p>
    </>
  );
}
