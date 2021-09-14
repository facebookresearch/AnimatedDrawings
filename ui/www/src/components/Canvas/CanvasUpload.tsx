import React, { useRef } from "react";
import classnames from "classnames";
import { Col, Button } from "react-bootstrap";
import imageCompression from "browser-image-compression";
import useDrawingStore from "../../hooks/useDrawingStore";
import useStepperStore from "../../hooks/useStepperStore";

const CanvasUpload = () => {
  const inputFile = useRef() as React.MutableRefObject<HTMLInputElement>;
  const { drawing, setDrawing, setNewCompressedDrawing } = useDrawingStore();
  const { currentStep, agreeTerms, setAgreeTerms } = useStepperStore();

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

      setNewCompressedDrawing(newFile);
      setDrawing(imgUrl);
    } catch (err) {
      console.log((err as Error)?.message);
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

      {currentStep === 1 ? (
        <div className="mt-3">
          <button className="large-button border border-dark" onClick={upload}>
            <i className="bi bi-camera-fill mr-2" /> Camera
          </button>
          <input
            type="file"
            name="file"
            ref={inputFile}
            style={{ display: "none" }}
            multiple={false}
            onChange={compress}
          />
        </div>
      ) : (
        <div className="mt-3 text-center">
          <button
            className="md-button-2 border border-dark"
            onClick={() => setAgreeTerms(false)}
          >
            Disagree
          </button>
          <button
            className={classnames(
              "border border-dark",
              { "md-button-success text-white": agreeTerms },
              { "md-button-2": !agreeTerms }
            )}
            onClick={() => setAgreeTerms(true)}
          >
            Agree
          </button>
        </div>
      )}
    </div>
  );
};

export default CanvasUpload;
