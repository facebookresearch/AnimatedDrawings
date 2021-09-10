import React from "react";
import { Button, Spinner } from "react-bootstrap";
import useStepperStore from "../../hooks/useStepperStore";
import useDrawingStore from "../../hooks/useDrawingStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";

import { Pose } from "../PoseEditor";

const mapPoseToJoints = (pose: Pose) => {
  const entries = pose.nodes.reduce((agg, node) => {
    agg.push([node.label, node.position]);
    return agg;
  }, new Array<[string, any]>());
  console.log(entries);

  return Object.fromEntries(entries);
};

const Step3 = () => {
  const { uuid, pose } = useDrawingStore();
  const { currentStep, setCurrentStep } = useStepperStore();  
  const { isLoading, setJointLocations } = useDrawingApi((err) => {
    console.log(err);
  });

  const handleClick = async (clickType: string) => {
    try {
      if (null === uuid && undefined === uuid) {
        return;
      }

      if (clickType === "next" && uuid) {
        const joints = mapPoseToJoints(pose);
        console.log(joints);
        setJointLocations(uuid!, joints, () => {
          //history.push(`/result/${uuid}`);
          setCurrentStep(currentStep + 1);
        });
      }
      if (clickType === "previous") {
        setCurrentStep(currentStep - 1);
      }
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <>
      <div className="step-actions-container">
        <h4>Step 3/4</h4>
        <h1 className="reg-title">Detecting</h1>
        <p>
          [Insert a description of what’s happening in this step of the process]
        </p>
      </div>
      <div className="mt-2 text-right">
        <Button
          variant="outline-dark"
          size="sm"
          disabled={false}
          onClick={() => handleClick("previous")}
        >
          Previous
        </Button>{" "}
        <Button
          size="sm"
          className="border border-dark text-dark px-3"
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
            "Next"
          )}
        </Button>
      </div>
    </>
  );
};

export default Step3;
