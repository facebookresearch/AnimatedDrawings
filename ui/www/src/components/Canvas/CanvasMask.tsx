import React, { useEffect, useRef, useState } from "react";
import { Row, Col, Button, Spinner } from "react-bootstrap";
import { resizedataURL, calculateRatio } from "../../utils/Helpers";
import useDrawingStore from "../../hooks/useDrawingStore";
import useMaskingStore from "../../hooks/useMaskingStore";
import useStepperStore from "../../hooks/useStepperStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import { EmptyLoader } from "../Loader";
import BoundingBoxStage from "./BoundingBoxStage";
import MaskStage from "./MaskStage";
import { Position } from "./PoseEditor";
import MaskingToolbar from "./MaskingToolbar";

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

const bbRatio = (
  canvasWidth: number,
  canvasHeight: number,
  oW: number,  //Original image width
  oH: number,  //Original image height
) => {
  if (oH >= oW && canvasHeight >= canvasWidth) {
    return canvasHeight / oH < 1 ? canvasHeight / oH : 1;
  } else if (oH < oW && canvasHeight >= canvasWidth) {
    return canvasHeight / oW < 1 ? canvasHeight / oW : 1
  } else if (oH >= oW && canvasHeight < canvasWidth) {
    return canvasWidth / oH < 1 ? canvasWidth / oH : 1;
  } else {
    return canvasWidth / oW < 1 ? canvasWidth / oW : 1;
  }
};

const CanvasMask = () => {
  const canvasWindow = useRef<HTMLInputElement | any>(null);
  const layerRef = useRef<HTMLImageElement | any>(null);
  const {
    uuid,
    croppedImgDimensions,
    imageUrlPose,
    originalDimension,
    setBox,
    setCroppedImgDimensions,
    setImageUrlPose,
    setImageUrlMask,
    setPose,
  } = useDrawingStore();
  const {
    setMaskBase64,
    setLines,
  } = useMaskingStore();
  const { isLoading,   getBoundingBox, getMask, getCroppedImage, getJointLocations, setMask } = useDrawingApi((err) => {});
  const { currentStep, setCurrentStep } = useStepperStore();
  const [ imgScale, setImgScale ] = useState(1);
  const [ isFetching, setIsFetching ] = useState(true)
  const [ iWidth, setImageWidth ] = useState(0);
  const [ iHeight, setImageHeight ] = useState(0);

  /**
   * When the components mounts, invokes API to fetch json bounding box coordinates.
   * The component will only render once while waitng for the mask to finish fetching.
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
          }
        };

        const ratio = bbRatio(
          canvasWindow.current?.offsetWidth -20,
          canvasWindow.current?.offsetHeight -20,
          originalDimension.width,
          originalDimension.height
        );
        
        const calculatedWidth = originalDimension.width * ratio;
        const calculatedHeight = originalDimension.height * ratio;
        setImageWidth(calculatedWidth);
        setImageHeight(calculatedHeight);

        await getBoundingBox(uuid!, (data) => {
          setBox({
            x:
              data.x1 * ratio +
              (canvasWindow.current?.offsetWidth / 2 - calculatedWidth / 2),
            width: data.x2 * ratio - data.x1 * ratio,
            y:
              data.y1 * ratio +
              (canvasWindow.current?.offsetHeight / 2 - calculatedHeight / 2),
            height: data.y2 * ratio - data.y1 * ratio,
            id: "1",
          });
        });
      } catch (error) {
        console.log(error);
      }
    };

    const timeout = setTimeout(() => {
      setIsFetching(false);
    }, 2000);

    if (uuid !== "") fetchBB();

    return () => {clearTimeout(timeout)};
  }, []); // eslint-disable-line react-hooks/exhaustive-deps


  /**
   * Here there is one scenarios/side effect when the CanvasMask component mounts
   * this hook invokes API to fetch a mask given uuid as parameter.
   * The component will only rerender when the uuid and croppedImg dimensions dependencies change.
   * exhaustive-deps eslint warning was diable as no more dependencies are really necesary as side effects.
   * Contrary to this, including other function dependencies will trigger infinite loop rendereing.
   */
  useEffect(() => {
    const fetchMask = async () => {
      try {
        const ratio = calculateRatio(
          canvasWindow.current?.offsetWidth - 45, // Toolbar Offset
          canvasWindow.current?.offsetHeight - 45, // Toolbar Offset
          croppedImgDimensions.width,
          croppedImgDimensions.height
        );  
        setImgScale(ratio);

        await getMask(uuid!, (data) => {
          let reader = new window.FileReader();
          reader.readAsDataURL(data);
          reader.onload = function () {
            let imageDataUrl = reader.result; // base64
            setImageUrlMask(imageDataUrl);
          };
        });
        await getCroppedImage(uuid!, (data) => {
          let reader = new window.FileReader();
          reader.readAsDataURL(data);
          reader.onload = function () {
            let imageDataUrl = reader.result;
            setImageUrlPose(imageDataUrl);
          };
        });
        getJointLocations(uuid!, (data) => {
          const mappedPose = mapJointsToPose(data);
          setPose(mappedPose);
        });
      } catch (error) {
        console.log(error);
      }
    };

    if (uuid !== "") fetchMask();

    return () => {};
  }, [uuid, croppedImgDimensions ]); // eslint-disable-line react-hooks/exhaustive-deps


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
        await setMask(uuid!, file, () => {
          console.log("New mask loaded.");
        });
        setCurrentStep(currentStep + 1);
      }
      if (clickType === "previous") {
        setLines([]);
        setCurrentStep(currentStep - 1);
      }
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <>
      <div className="canvas-wrapper">
        <div className="blue-box d-none d-lg-block" />
        <div ref={canvasWindow} className="canvas-background-p-0 canvas-mask loader">
          {isFetching ? (
            <>
              <BoundingBoxStage
                canvasWidth={canvasWindow.current?.offsetWidth}
                canvasHeight={canvasWindow.current?.offsetHeight}
                imageWidth={iWidth}
                imageHeight={iHeight}
              />
              <EmptyLoader />
            </>
          ) : (
            <>
              <div className="mask-tool-wrapper">
                <MaskStage
                  scale={imgScale}
                  canvasWidth={croppedImgDimensions.width}
                  canvasHeight={croppedImgDimensions.height}
                  ref={layerRef}
                />
                <MaskingToolbar />
              </div>
              {isLoading && <EmptyLoader />}
            </>
          )}
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
