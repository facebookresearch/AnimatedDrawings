import React, { useEffect, useRef, useState } from "react";
import { Row, Col, Button, Spinner } from "react-bootstrap";
import { resizedataURL, calculateRatio } from "../../utils/Helpers";
import useDrawingStore from "../../hooks/useDrawingStore";
import useMaskingStore from "../../hooks/useMaskingStore";
import useStepperStore from "../../hooks/useStepperStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import { EmptyLoader } from "../Loader";
import MaskStage from "./MaskStage";
import { Position } from "./PoseEditor";
import MaskingToolbar from "./MaskingToolbar";
import useLogPageView from "../../hooks/useLogPageView";

const mapJointsToPose = (joints: object) => {
  return {
    nodes: Object.entries(joints).map((arr) => {
      return { id: arr[0], label: arr[0], position: arr[1] as Position };
    }),
    edges: [
      // Right side
      {
        from: "right_shoulder",
        to: "right_elbow",
      },
      {
        from: "right_elbow",
        to: "right_wrist",
      },
      {
        from: "right_shoulder",
        to: "right_hip",
      },
      {
        from: "right_hip",
        to: "right_knee",
      },
      {
        from: "right_knee",
        to: "right_ankle",
      },
      // Left side
      {
        from: "left_shoulder",
        to: "left_elbow",
      },
      {
        from: "left_elbow",
        to: "left_wrist",
      },
      {
        from: "left_shoulder",
        to: "left_hip",
      },
      {
        from: "left_hip",
        to: "left_knee",
      },
      {
        from: "left_knee",
        to: "left_ankle",
      },
      // Shoulders and hips
      {
        from: "left_shoulder",
        to: "right_shoulder",
      },
      {
        from: "left_hip",
        to: "right_hip",
      },
      // face
      {
        from: "nose",
        to: "left_eye",
      },
      {
        from: "nose",
        to: "right_eye",
      },
      {
        from: "nose",
        to: "left_ear",
      },
      {
        from: "nose",
        to: "right_ear",
      },
      {
        from: "nose",
        to: "left_shoulder",
      },
      {
        from: "nose",
        to: "right_shoulder",
      },
    ],
  };
};

const CanvasMask = () => {
  useLogPageView("Mask", "#mask");
  const canvasWindow = useRef<HTMLInputElement | any>(null);
  const layerRef = useRef<HTMLImageElement | any>(null);
  const {
    uuid,
    croppedImgDimensions,
    imageUrlPose,
    setCroppedImgDimensions,
    setPose,
  } = useDrawingStore();
  const { setMaskBase64, setLines } = useMaskingStore();
  const { isLoading, getJointLocations, setMask } = useDrawingApi((err) => {});
  const { currentStep, setCurrentStep } = useStepperStore();
  const [imgScale, setImgScale] = useState(1);
  const [isFetching, setIsFetching] = useState(false);

  /**
   * When cropped image is updated, recalculate the dimensions,
   * which are provided to the mask/segmentation canvas.
   */
  useEffect(() => {
    const tempImage = new Image();
    if (imageUrlPose !== null && imageUrlPose !== undefined)
      tempImage.src = imageUrlPose; // cropped image base64

    tempImage.onload = (e) => {
      if (canvasWindow.current) {
        setCroppedImgDimensions({
          width: tempImage.naturalWidth,
          height: tempImage.naturalHeight,
        });

        const ratio = calculateRatio(
          canvasWindow.current?.offsetWidth - 45, // Toolbar Offset
          canvasWindow.current?.offsetHeight - 45, // Toolbar Offset
          tempImage.naturalWidth,
          tempImage.naturalHeight
        );
        setImgScale(ratio);
      }
    };

    return () => {};
  }, [imageUrlPose]); // eslint-disable-line react-hooks/exhaustive-deps

  /**
   * Handles Next and Previous buttons logic.
   * @param clickType a string with a type of action "next" or "previous"
   * @returns
   */
  const handleClick = async (clickType: string) => {
    try {
      if (null === uuid && undefined === uuid) {
        return;
      }

      if (clickType === "next" && uuid) {
        setIsFetching(true);
        const uri = layerRef.current?.toDataURL();
        const newDataUri = await resizedataURL(
          uri,
          croppedImgDimensions.width,
          croppedImgDimensions.height
        );
        setMaskBase64(newDataUri); // base64

        const response = await fetch(newDataUri || uri);
        const blob = await response.blob();
        const file = new File([blob], "mask.png", {
          type: "image/png",
          lastModified: Date.now(),
        });

        // Send new mask to server.
        await setMask(uuid!, file, () => {
          console.log("New mask loaded.");
        });

        // Get joint locations for next step.
        await getJointLocations(uuid!, (data) => {
          const mappedPose = mapJointsToPose(data);
          setPose(mappedPose);
        });

        // Finally move to next step
        setIsFetching(false);
        setCurrentStep(currentStep + 1);
      }
      if (clickType === "previous") {
        setLines([]);
        setCurrentStep(currentStep - 1);
      }
    } catch (err) {
      setIsFetching(false);
      console.log(err);
    }
  };

  return (
    <>
      <div className="canvas-wrapper">
        <div className="blue-box d-none d-lg-block" />
        <div
          ref={canvasWindow}
          className="canvas-background-p-0 canvas-mask loader"
        >
          <div className="mask-tool-wrapper">
            <MaskStage
              scale={imgScale}
              canvasWidth={croppedImgDimensions.width}
              canvasHeight={croppedImgDimensions.height}
              ref={layerRef}
            />
            <MaskingToolbar />
          </div>
          {isFetching && <EmptyLoader />}
        </div>
        <Row className="justify-content-center mt-3 pb-1">
          <Col lg={6} md={6} xs={12} className="order-md-2 text-center">
            <Button
              block
              size="lg"
              className="py-lg-3 mt-lg-3 my-1 shadow-button"
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
            </Button>
          </Col>
          <Col lg={6} md={6} xs={12} className="order-md-1">
            <Button
              block
              size="lg"
              variant="outline-primary"
              className="py-lg-3 mt-lg-3 my-1"
              disabled={isLoading}
              onClick={() => handleClick("previous")}
            >
              Previous
            </Button>
          </Col>
        </Row>
      </div>
    </>
  );
};

export default CanvasMask;
