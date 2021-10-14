import React, { useRef, useState } from "react";
import { Spinner } from "react-bootstrap";
import imageCompression from "browser-image-compression";
import heic2any from "heic2any";
import useDrawingStore from "../../hooks/useDrawingStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import WaiverModal from "../Modals/WaiverModal";
import Loader from "../Loader";
import CanvasPlaceholder from "../../assets/backgrounds/canvas_placeholder.gif";

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
  const { isLoading, uploadImage } = useDrawingApi((err) => {});

  const [showWaiver, setShowWaiver] = useState(false);
  const [converting, setConvertingHeic] = useState(false);
  const [compressing, setCompressing] = useState(false)

  const upload = (e: React.MouseEvent) => {
    e.preventDefault();
    inputFile.current.click();
  };

  const compress = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const file = e.target.files[0];
    const options = {
      maxSizeMB: 1,
      maxWidthOrHeight: 2000,
      useWebWorker: true,
    };
    try {
      // Check if the file is in HEIC format.
      if (file.type === "image/heic") {
        const heicURL = URL.createObjectURL(file);
        convertHeicformat(heicURL);
      } else {
        setCompressing(true);
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
        setCompressing(false)
      }
    } catch (err) {
      console.log((err as Error)?.message);
    }
  };

  const convertHeicformat = async (heicURL: string) => {
    try {
      setConvertingHeic(true);
      const res = await fetch(heicURL);
      const blob = await res.blob();
      const conversionResult: any = await heic2any({
        blob,
        toType: "image/jpeg",
        quality: 0.1,
      });
      const imgUrl = URL.createObjectURL(conversionResult);
      let newFile = new File([conversionResult], "animation.png", {
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
      setConvertingHeic(false);
    } catch (err) {
      console.log(err);
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
      <div className="blue-box d-none d-lg-block"></div>
      <div className="canvas-background-p-0">
        {converting ? (
          <Spinner animation="border" role="status" aria-hidden="true" />
        ) : (
          <>
            {drawing !== "" ? (
              <>
                {" "}
                {isLoading ? (
                  <Loader drawingURL={drawing} />
                ) : (
                  <img alt="drawing" src={drawing} />
                )}
              </>
            ) : (
              <img
                alt="placeholder"
                src={CanvasPlaceholder}
                className="placeholder"
              />
            )}
          </>
        )}
      </div>

      <input
        ref={inputFile}
        type="file"
        name="file"
        accept=".jpg, .png, .heic"
        style={{ display: "none" }}
        multiple={false}
        onChange={compress}
      />

      {drawing === "" ? (
        <div className="mt-4">
          {compressing ? (
            <button className="buttons large-button">
              <Spinner
                as="span"
                animation="border"
                size="sm"
                role="status"
                aria-hidden="true"
              />
            </button>
          ) : (
            <button className="buttons large-button" onClick={upload}>
              <i className="bi bi-image-fill mr-2" /> Upload
            </button>
          )}
        </div>
      ) : (
        <div className="mt-4 text-center">
          <button className="buttons sm-button mr-1 text-dark" onClick={upload}>
            Retake
          </button>
          <button
            className="buttons md-button-right ml-1"
            disabled={isLoading || compressing}
            onClick={() => handleNext()}
          >
            {isLoading || compressing ? (
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                />
            ) : (
              <>
                Next <i className="bi bi-arrow-right px-2" />
              </>
            )}
          </button>
        </div>
      )}

      <WaiverModal showModal={showWaiver} setShowModal={setShowWaiver} />
    </div>
  );
};

export default CanvasUpload;
