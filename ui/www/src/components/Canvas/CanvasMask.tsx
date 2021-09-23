import React, { useEffect, useRef } from "react";
import classnames from "classnames";
import { Row, Col } from "react-bootstrap";
import useDrawingStore from "../../hooks/useDrawingStore";
import useMaskingStore from "../../hooks/useMaskingStore";
import useStepperStore from "../../hooks/useStepperStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import Loader from "../Loader";
import MaskStage from "./MaskStage";

const CanvasMask = () => {
  const canvasWindow = useRef<HTMLInputElement>(null);
  const layerRef = useRef<HTMLImageElement | any>(null);
  const {
    drawing,
    uuid,
    croppedImgDimensions,
    setImageUrlPose,
    setImageUrlMask,
  } = useDrawingStore();
  const {
    tool,
    penSize,
    lines,
    blackLines,
    setMaskBase64,
    setTool,
    setPenSize,
    setLines,
    setBlackLines,
  } = useMaskingStore();
  const { isLoading, getMask, getCroppedImage, setMask } = useDrawingApi((err) => {});
  const { currentStep, setCurrentStep } = useStepperStore();

  /**
   * Here there is one scenarios/side effect when the CanvasMask component mounts
   * this hook invokes API to fetch a mask given uuid as parameter.
   * The component will only rerender when the uuid dependency changes.
   * exhaustive-deps eslint warning was diable as no more dependencies are really necesary as side effects.
   * Contrary to this, including other function dependencies will trigger infinite loop rendereing.
   */
  useEffect(() => {
    const fetchMask = async () => {
      try {
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
      } catch (error) {
        console.log(error);
      }
    };

    if (uuid !== "") fetchMask();

    return () => {};
  }, [uuid]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleClick = async (clickType: string) => {
    try {
      if (null === uuid && undefined === uuid) {
        return;
      }

      if (clickType === "next" && uuid) {
        const uri = layerRef.current?.toDataURL();
        setMaskBase64(uri); // base64
        const response = await fetch(uri);
        const blob = await response.blob();
        const file = new File([blob], "mask.png", {
          type: "image/png",
          lastModified: Date.now(),
        });
        await setMask(uuid!, file, () => {
          console.log("New mask loaded.");
          setCurrentStep(currentStep + 1);
        });
      }
    } catch (err) {
      console.log(err);
    }
  };

  const handleReset = () => {
    if (!lines.length && !blackLines.length) {
      return;
    }
    setLines([]);
    setBlackLines([]);
  };

  const handleUndo = () => {
    if (!lines.length && !blackLines.length) {
      return;
    }
    let objectLines = lines.slice(0, -1);
    let backgroundLines = blackLines.slice(0, -1);
    setLines(objectLines);
    setBlackLines(backgroundLines);
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
