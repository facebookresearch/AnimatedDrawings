import React, { useRef, useState } from "react";
import { Col, Button } from "react-bootstrap";
import imageCompression from "browser-image-compression";
import useDrawingStore from "../../hooks/useDrawingStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import WaiverModal from "../Modals/WaiverModal";

const CanvasUpload = () => {
  const inputFile = useRef() as React.MutableRefObject<HTMLInputElement>;
  const {
    drawing,
    newCompressedDrawing,
    setUuid,
    setDrawing,
    setNewCompressedDrawing,
    setOriginalDimensions,
  } = useDrawingStore();
  const { uploadImage } = useDrawingApi((err) => {});

  const [showWaiver, setShowWaiver] = useState(false);

  const upload = (e: React.MouseEvent) => {
    e.preventDefault();
    inputFile.current.click();
  };

  const compress = async (e: any) => {
    const file = e.target.files[0];
    const options = {
      maxSizeMB: 1,
      maxWidthOrHeight: 2000,
      useWebWorker: true,
    };
    try {
      const compressedFile = await imageCompression(file, options);
      const imgUrl = URL.createObjectURL(compressedFile);
      let newFile = new File([compressedFile], "animation.png", {
        type: "image/png",
        lastModified: new Date().getTime(),
      });

      const tempImage = new Image();
      if (imgUrl !== null && imgUrl !== undefined) tempImage.src = imgUrl;

      tempImage.onload = function (e) {
        setOriginalDimensions({
          width: tempImage.naturalWidth,
          height: tempImage.naturalHeight,
        });
      };

      setNewCompressedDrawing(newFile);
      setDrawing(imgUrl);
    } catch (err) {
      console.log((err as Error)?.message);
    }
  };

  /**
   * Upload image when user click on next
   * thne open the waiver modal.
   */
  const handleNext = async () => {
    try {
      await uploadImage(newCompressedDrawing, (data) => {
        setUuid(data as string);
        setShowWaiver(true);
      });
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="canvas-wrapper">
      <div className="canvas-background border border-dark">
        {drawing !== "" ? (
          <img alt="drawing" src={drawing} />
        ) : (
          <Col>
            <p>
              Drop a photo of your drawing <br /> or <br /> Select a photo from
              your device
            </p>
            <Button className="border border-dark text-dark" onClick={upload}>
              Choose File
            </Button>
          </Col>
        )}
      </div>

      <input
        type="file"
        name="file"
        ref={inputFile}
        style={{ display: "none" }}
        multiple={false}
        onChange={compress}
      />

      {drawing === "" ? (
        <div className="mt-3">
          <button className="buttons large-button" onClick={upload}>
            <i className="bi bi-camera-fill mr-2" /> Camera
          </button>
        </div>
      ) : (
        <div className="mt-3 text-center">
          <button className="buttons sm-button mr-1" onClick={upload}>
            Retake
          </button>
          <button className="buttons md-button-right ml-1" onClick={handleNext}>
            Next <i className="bi bi-arrow-right px-2" />
          </button>
        </div>
      )}

      <WaiverModal showModal={showWaiver} setShowModal={setShowWaiver} />
    </div>
  );
};

export default CanvasUpload;
