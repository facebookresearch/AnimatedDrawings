import React, { useEffect, useRef } from "react";
import classnames from "classnames";
import { Row, Col } from "react-bootstrap";
import useDrawingStore from "../../hooks/useDrawingStore";
import useMaskingStore from "../../hooks/useMaskingStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import Loader from "../Loader";
import MaskStage from "./MaskStage";

const CanvasMask = () => {
  const canvasWindow = useRef<HTMLInputElement>(null);
  const { drawing, uuid, setImageUrlMask } = useDrawingStore();
  const {
    tool,
    penSize,
    lines,
    setTool,
    setPenSize,
    setLines,
  } = useMaskingStore();
  const { isLoading, getMask } = useDrawingApi((err) => {});

  /**
   * Here there are two scenarios/side effects when the CanvasDetecting component mounts
   * 1. Invokes API to get cropped image when uuid is detected from the user.
   * 2. When an cropped image is recieved, invoke API to fetch a mask.
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
            let imageDataUrl = reader.result;
            setImageUrlMask(imageDataUrl);
          };
        });
      } catch (error) {
        console.log(error);
      }
    };

    if (uuid !== "") fetchMask();

    return () => {};
  }, [uuid]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleUndo = () => {
    if (!lines.length) {
      return;
    }
    let objectLines = lines.slice(0, -1);
    setLines(objectLines);
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
                    value={4}
                    checked={penSize === 4}
                    onChange={() => setPenSize(4)}
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
            
            <button className="md-button-reset border border-dark">
              Reset mask
            </button>
          </Row>
        </Col>
      </Row>
      <div ref={canvasWindow} className="canvas-background border border-dark">
        {isLoading ? (
          <Loader drawingURL={drawing} />
        ) : (
          <div className="mask-wrapper">
            <MaskStage
              canvasWidth={canvasWindow.current?.clientWidth}
              canvasHeight={canvasWindow.current?.clientHeight}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default CanvasMask;
