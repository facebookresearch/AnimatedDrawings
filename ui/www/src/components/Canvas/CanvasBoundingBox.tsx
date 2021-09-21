import React, { useRef, useEffect, useState } from "react";
import { Spinner } from "react-bootstrap";
import useDrawingStore from "../../hooks/useDrawingStore";
import useStepperStore from "../../hooks/useStepperStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import BoundingBoxStage from "./BoundingBoxStage";

export interface BoundingBox {
  x: number;
  width: number;
  y: number;
  height: number;
  id: string;
}

const CanvasBoundingBox = () => {
  const canvasWindow = useRef<HTMLDivElement | any>(null);
  const { currentStep, setCurrentStep } = useStepperStore();
  const {
    uuid,
    imageUrlPose,
    originalDimension,
    boundingBox,
    setCroppedImgDimensions,
    setBox,
  } = useDrawingStore();
  const {
    isLoading,
    getBoundingBox,
    setBoundingBox,
  } = useDrawingApi((err) => {});

  const [imgWidth, setImgWidth] = useState(0);
  const [imgHeight, setImgHeight] = useState(0);

  /**
   * When the components mounts, invokes API to fetch json bounding box coordinates.
   * The component will only rerender when the uuid dependency changes.
   * exhaustive-deps eslint warning was diable as no more dependencies are really necesary as side effects.
   * Contrary to this, including other function dependencies will trigger infinite loop rendereing.
   */
  useEffect(() => {
    const fetchBB = async () => {
      try {
        const tempImage = new Image();
        if (imageUrlPose !== null && imageUrlPose !== undefined)
          tempImage.src = imageUrlPose; // cropped image base64

        tempImage.onload = (e) => {
          if (canvasWindow.current) {
            setCroppedImgDimensions({
              width: tempImage.naturalWidth,
              height: tempImage.naturalHeight,
            });
            setImgWidth(tempImage.naturalWidth);
            setImgHeight(tempImage.naturalHeight);
          }
        };

        await getBoundingBox(uuid!, (data) => {
          setBox({
            x:
              (data.x1 * tempImage.naturalWidth) / originalDimension.width +
              (canvasWindow.current?.offsetWidth / 2 -
                tempImage.naturalWidth / 2),
            width: (data.x2 * tempImage.naturalWidth) / originalDimension.width,
            y:
              (data.y1 * tempImage.naturalHeight) / originalDimension.height +
              (canvasWindow.current?.offsetHeight / 2 -
                tempImage.naturalHeight / 2),
            height:
              (data.y2 * tempImage.naturalHeight) / originalDimension.height,
            id: "1",
          });
        });
      } catch (error) {
        console.log(error);
      }
    };

    if (uuid !== "") fetchBB();

    return () => {};
  }, [uuid]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleClick = async (clickType: string) => {
    try {
      if (null === uuid && undefined === uuid) {
        return;
      }
      //Send new bounding box attributes.
      if (clickType === "next") {
        let xOffset = canvasWindow.current?.offsetWidth / 2 - imgWidth / 2;
        let yOffset = canvasWindow.current?.offsetHeight / 2 - imgHeight / 2;
        const coordinates = {
          x1: Math.round(
            (boundingBox.x - xOffset) * (originalDimension.width / imgWidth) >=
              0
              ? (boundingBox.x - xOffset) * (originalDimension.width / imgWidth)
              : 0
          ),
          x2: Math.round(
            boundingBox.width * (originalDimension.width / imgWidth)
          ),
          y1: Math.round(
            (boundingBox.y - yOffset) *
              (originalDimension.height / imgHeight) >=
              0
              ? (boundingBox.y - yOffset) *
                  (originalDimension.height / imgHeight)
              : 0
          ),
          y2: Math.round(
            boundingBox.height * (originalDimension.height / imgHeight)
          ),
        };
        console.log("New Coordinates: ", coordinates);
        await setBoundingBox(uuid!, coordinates, () => {
          setCurrentStep(currentStep + 1);
        });
      }
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div className="canvas-wrapper">
      <div ref={canvasWindow} className="canvas-background border border-dark">
        <BoundingBoxStage
          canvasWidth={canvasWindow.current?.offsetWidth}
          canvasHeight={canvasWindow.current?.offsetHeight}
        />
      </div>

      <div className="mt-3">
        <button
          className="buttons large-button"
          disabled={isLoading}
          onClick={() => handleClick("next")}
        >
          {isLoading ? (
            <Spinner
              as="span"
              animation="border"
              size="sm"
              role="status"
              aria-hidden="true"
            />
          ) : (
            <>
              Next <i className="bi bi-arrow-right ml-1" />{" "}
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default CanvasBoundingBox;
