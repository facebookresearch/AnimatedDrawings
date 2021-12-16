import React, { useEffect, useRef, useState } from "react";
import { Row, Col, Button, Spinner } from "react-bootstrap";
import useDrawingStore from "../../hooks/useDrawingStore";
import useStepperStore from "../../hooks/useStepperStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import PoseEditor, { Pose } from "./PoseEditor";
import { calculateRatio } from "../../utils/Helpers";

const mapPoseToJoints = (pose: Pose) => {
  const entries = pose.nodes.reduce((agg, node) => {
    agg.push([node.label, node.position]);
    return agg;
  }, new Array<[string, any]>());

  return Object.fromEntries(entries);
};

const CanvasPose = () => {
  const canvasWindow = useRef<HTMLDivElement | any>(null);
  const {
    uuid,
    croppedImgDimensions,
    imageUrlPose,
    imageUrlMask,
    pose,
    setPose,
    setImageUrlMask,
    setAnimationType,
  } = useDrawingStore();
  const { currentStep, setCurrentStep } = useStepperStore();
  const { isLoading, getMask, setJointLocations } = useDrawingApi((err) => {
    console.log(err);
  });
  const [imgScale, setImgScale] = useState(1);

  /**
   * 1. When canvas mounts, calculate the ratio between canvas
   * and cropped image to make the drawing fit the canvas, substract canvas padding 20. 
   * 2. Get the mask from previous state to use in the background.
   * The component will only rerender when the uuid and croppedImg dimensions 
   * dependencies change. Exhaustive-deps eslint warning was diable as 
   * no more dependencies are really necesary as side effects
   */
  useEffect(() => {
    const fetchMask = async () => {
      try {
        const ratio = calculateRatio(
          canvasWindow.current?.offsetWidth - 40,
          canvasWindow.current?.offsetHeight - 40,
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
      } catch (error) {
        console.log(error);
      }
    };

    if (uuid !== "") fetchMask();

    return () => {};
  }, [uuid, croppedImgDimensions]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleClick = async (clickType: string) => {
    try {
      if (null === uuid && undefined === uuid) {
        return;
      }

      //send new joint locations to the server
      if (clickType === "next" && uuid) {
        const joints = mapPoseToJoints(pose);
        await setJointLocations(uuid!, joints, () => {
          console.log("New joints location set.");
        });
        setAnimationType("running_jump");
        setCurrentStep(currentStep + 1);
      }
      if (clickType === "previous") {
        setCurrentStep(currentStep - 1);
      }
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div className="canvas-wrapper">
      <div className="blue-box d-none d-lg-block"></div>
      <div ref={canvasWindow} className="canvas-background canvas-pose">
        {pose && (
          <PoseEditor
            imageUrl={imageUrlPose}
            maskUrl={imageUrlMask}
            pose={pose}
            scale={imgScale}
            setPose={setPose}
          />
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
  );
};

export default CanvasPose;
