import React, { useEffect, useRef, useState } from "react";
import classnames from "classnames";
import { Row, Col } from "react-bootstrap";
import useDrawingStore from "../../hooks/useDrawingStore";
import useMaskingStore from "../../hooks/useMaskingStore";
import useStepperStore from "../../hooks/useStepperStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import Loader from "../Loader";
import MaskStage from "./MaskStage";
import { Position } from "../PoseEditor";
import { resizedataURL, calculateRatio } from "../../utils/Helpers";

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
  const canvasWindow = useRef<HTMLInputElement | any>(null);
  const layerRef = useRef<HTMLImageElement | any>(null);
  const {
    drawing,
    uuid,
    croppedImgDimensions,
    imageUrlPose,
    setCroppedImgDimensions,
    setImageUrlPose,
    setImageUrlMask,
    setPose,
  } = useDrawingStore();
  const {
    tool,
    penSize,
    lines,
    setMaskBase64,
    setTool,
    setPenSize,
    setLines,
  } = useMaskingStore();
  const { isLoading, getMask, getCroppedImage, getJointLocations, setMask } = useDrawingApi((err) => {});
  const { currentStep, setCurrentStep } = useStepperStore();
  const [imgScale, setImgScale] = useState(1);

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
          canvasWindow.current?.offsetWidth -20,
          canvasWindow.current?.offsetHeight -20,
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
    } catch (err) {
      console.log(err);
    }
  };

  const handleReset = () => {
    if (!lines.length) {
      return;
    }
    setLines([]);
  };

  const handleUndo = () => {
    if (!lines.length) {
      return;
    }
    let newLines = lines.slice(0, -1);
    setLines(newLines);
  };

  return (
    <div className="canvas-wrapper">
      <Row className="justify-content-between px-3 mb-3">
        <Col>
          <Row>
            <button
              className={classnames("sm-button-icon border border-dark mr-2", {
                "bg-primary": tool === "pen",
              })}
              onClick={() => setTool("pen")}
            >
              <i className="bi bi-pencil-fill" />
            </button>
            <button
              className={classnames("sm-button-icon border border-dark mr-2", {
                "bg-primary": tool === "eraser",
              })}
              onClick={() => setTool("eraser")}
            >
              <i className="bi bi-eraser-fill" />
            </button>
            <div className="pens-wrapper">
              <form className="pens">
                <label className="label1">
                  <input
                    type="radio"
                    name="radio"
                    value={3}
                    checked={penSize === 3}
                    onChange={() => setPenSize(3)}
                  />
                  <span></span>
                </label>
                <label className="label2">
                  <input
                    type="radio"
                    name="radio"
                    value={10}
                    checked={penSize === 10}
                    onChange={() => setPenSize(10)}
                  />
                  <span></span>
                </label>
                <label className="label3">
                  <input
                    type="radio"
                    name="radio"
                    value={20}
                    checked={penSize === 20}
                    onChange={() => setPenSize(20)}
                  />
                  <span></span>
                </label>
              </form>
            </div>
          </Row>
        </Col>
        <Col>
          <Row className="justify-content-end">
            <button
              className="sm-button-icon border border-dark mr-2"
              onClick={handleUndo}
            >
              <i className="bi bi-arrow-90deg-left" />
            </button>

            <button
              className="md-button-reset border border-dark"
              onClick={handleReset}
            >
              Reset mask
            </button>
          </Row>
        </Col>
      </Row>
      <div ref={canvasWindow} className="canvas-background border border-dark">
        {isLoading ? (
          <Loader drawingURL={drawing} />
        ) : (
          <MaskStage
            scale={imgScale}
            canvasWidth={croppedImgDimensions.width}
            canvasHeight={croppedImgDimensions.height}
            ref={layerRef}
          />
        )}
      </div>
      <div className="mt-3">
        <button
          className="buttons large-button"
          disabled={isLoading}
          onClick={() => handleClick("next")}
        >
          Next <i className="bi bi-arrow-right ml-1" />
        </button>
      </div>
    </div>
  );
};

export default CanvasMask;
