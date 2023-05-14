import AWS from "aws-sdk";
import * as PIXI from "pixi.js";
import { Character } from "../scenes/Character";
const region = "ap-northeast-1";
const s3 = new AWS.S3({
  credentials: {
    accessKeyId: "your_access_key",
    secretAccessKey: "your_secret_key",
  },
  region,
});
const bucketName = "dev-60yfmd-input-drawings-bucket";
const prefix = "image_"; // ここにファイル名の接頭辞を入力してください
const suffix = ".gif"; // ここにファイル名の拡張子を入力してください

export async function loader(): Promise<Character[]> {
  const context = require.context("./", true, /\.(gif)$/);
  const images = context.keys().map(context);

  const downloadedFiles = images.length
    ? context.keys().map((key: any) => key.match(/\/([^/]+)$/)[1])
    : [];
  console.log(downloadedFiles);

  const params: AWS.S3.ListObjectsV2Request = {
    Bucket: bucketName,
    Prefix: prefix,
  };

  const chars: Character[] = [];

  const data = await s3.listObjectsV2(params).promise();
  const objects = data.Contents || [];
  const gifs = objects.filter((object: AWS.S3.Object) =>
    object.Key?.endsWith(suffix)
  );
  const newGifs = gifs.filter(
    (gif: AWS.S3.Object) => !downloadedFiles.includes(gif.Key!)
  );
  if (!newGifs.length) return chars;

  return await Promise.all(
    newGifs.map(async (g) => {
      const appLoader = PIXI.Assets.loader;
      try {
        const char = await appLoader.load(
          `https://${bucketName}.s3.${region}.amazonaws.com/${g.Key!}`
        );
        return new Character(g.Key!, char);
      } catch (e) {
        console.log(e);
        return new Character(`garlic1.gif`); //失敗したらガーリックが増えることにしよう
      }
    })
  );

  // setTimeout(loader, 30000); // 30秒後に再度呼び出す
}
