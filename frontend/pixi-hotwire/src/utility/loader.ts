import AWS from "aws-sdk";
import fileLoader from "file-loader";

const s3 = new AWS.S3({
  credentials: {
    accessKeyId: "your_access_key",
    secretAccessKey: "your_secret_key",
  },
  region: "ap-northeast-1",
});
const bucketName = "dev-60yfmd-input-drawings-bucket";
const prefix = "image_"; // ここにファイル名の接頭辞を入力してください
const suffix = ".gif"; // ここにファイル名の拡張子を入力してください

export async function loader(): Promise<void> {
  const context = require.context("./", true, /\.(gif)$/);
  const images = context.keys().map(context);
  console.log(images);

  const downloadedFiles = images.length
    ? context.keys().map((key: any) => key.match(/\/([^/]+)$/)[1])
    : [];
  console.log(downloadedFiles);

  const params: AWS.S3.ListObjectsV2Request = {
    Bucket: bucketName,
    Prefix: prefix,
  };

  s3.listObjectsV2(params, (err, data) => {
    if (err) {
      console.log(err, err.stack);
    } else {
      const objects = data.Contents || [];
      console.log(objects);
      const gifs = objects.filter((object: AWS.S3.Object) =>
        object.Key?.endsWith(suffix)
      );

      const newGifs = gifs.filter(
        (gif: AWS.S3.Object) => !downloadedFiles.includes(gif.Key!)
      );
      if (!newGifs.length) return;

      newGifs.map((g) => {
        const params: AWS.S3.GetObjectRequest = {
          Bucket: bucketName,
          Key: g.Key!,
        };

        s3.getObject(params, (err, data) => {
          if (err) {
            console.error(err);
          } else {
            const objectContent = data.Body?.toString();
            console.log("oc", typeof objectContent);
            const fileUrl = fileLoader(objectContent);
            console.log(`File downloaded and loaded from ${fileUrl}`);
          }
        });
      });
    }
  });

  setTimeout(loader, 30000); // 30秒後に再度呼び出す
}
