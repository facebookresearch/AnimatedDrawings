import React, { useState } from "react";
import { Form } from "react-bootstrap";

interface Props {
  //   loadVideoFromBlob: (data: string) => void;
  file?: File;
  setFile: (file: File) => void;
}

const UploadImage = ({ file, setFile }: Props) => {
  const [isLoading, setIsLoading] = useState(false);
  const [imgData, setImgData] = useState<string>();

  return (
    <>
      Alright! Let's get started by uploading an image of drawing!
      {imgData && <img src={imgData} alt="Preview" className="img-fluid"></img>}
      <Form className="mt-3">
        <Form.File
          id="custom-file"
          label={
            file?.name ? file.name : "Take a picture of your hand drawn figure"
          }
          custom
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
            if (e.target.files !== null && e.target.files.length > 0) {
              setIsLoading(true);
              const file = e.target.files[0];
              setFile(file);
              var reader = new FileReader();
              reader.onload = (e) => {
                const dataUrl = e.target?.result;
                if (dataUrl && typeof dataUrl === "string") {
                  console.log(dataUrl);

                  setImgData(dataUrl);
                  setIsLoading(false);
                }
              };

              reader.readAsDataURL(file);
            }
          }}
        />
      </Form>
    </>
  );
};

export default UploadImage;
