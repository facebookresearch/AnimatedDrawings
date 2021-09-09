import React, { useState } from "react";
import { Button, Card, Form, Spinner } from "react-bootstrap";
import { useDrawingApi } from "../hooks/useDrawingApi";

interface StepProps {
  onClose: () => void;
  onImageUploadSuccess: (data: any) => void;
}
interface Props {
  file: File | undefined;
  setFile: (file: File) => void;
}

interface FooterProps {
  file: File | undefined;
  onClose: () => void;
  isLoading: boolean;
  uploadImage: (file: File, onResult: (result: any) => void) => void;
  onImageUploadSuccess: (data: any) => void;
}

export const UploadImageStep = ({
  onClose,
  onImageUploadSuccess,
}: StepProps) => {
  const { isLoading, uploadImage } = useDrawingApi((err) => {});
  const [file, setFile] = useState<File>();

  return (
    <Card className="border-0">
      <Card.Body>
        <Card.Title>Upload Image</Card.Title>
        <Card.Text>
          Alright! Let's get started by uploading an image of drawing!
        </Card.Text>
        <UploadImageBody file={file} setFile={setFile} />
      </Card.Body>
      <Card.Footer className="text-muted d-flex justify-content-end">
        <UploadImageFooter
          isLoading={isLoading}
          file={file}
          onClose={onClose}
          uploadImage={uploadImage}
          onImageUploadSuccess={onImageUploadSuccess}
        />
      </Card.Footer>
    </Card>
  );
};

const UploadImageBody = ({ file, setFile }: Props) => {
  const [imgData, setImgData] = useState<string>();

  return (
    <>
      {file && !imgData && (
        <Spinner animation="border" role="status" aria-hidden="true" />
      )}
      {imgData && <img src={imgData} alt="Preview" className="img-fluid"></img>}
      <Form className="m-0">
        <Form.File
          id="custom-file"
          label={
            file?.name ? file.name : "Take a picture of your hand drawn figure"
          }
          custom
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
            if (e.target.files !== null && e.target.files.length > 0) {
              const file = e.target.files[0];
              setFile(file);
              var reader = new FileReader();
              reader.onload = (e) => {
                const dataUrl = e.target?.result;
                if (dataUrl && typeof dataUrl === "string") {

                  setImgData(dataUrl);
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

const UploadImageFooter = ({
  file,
  isLoading,
  onClose,
  uploadImage,
  onImageUploadSuccess,
}: FooterProps) => {
  return (
    <>
      <Button
        className="mr-3"
        variant="secondary"
        onClick={onClose}
        disabled={isLoading}
      >
        Close
      </Button>
      <Button
        variant="primary"
        // disabled={isLoading}
        onClick={async (e) => {
          if (file !== null && file !== undefined) {
            await uploadImage(file, (data) =>
              onImageUploadSuccess(data as string)
            );
          }
        }}
      >
        {!isLoading && "Submit"}
        {isLoading && (
          <Spinner
            as="span"
            animation="border"
            size="sm"
            role="status"
            aria-hidden="true"
          />
        )}
      </Button>
    </>
  );
};

export default UploadImageBody;
