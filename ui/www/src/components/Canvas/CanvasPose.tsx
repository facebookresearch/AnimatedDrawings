import React from "react";
import useDrawingStore from "../../hooks/useDrawingStore";
import useStepperStore from "../../hooks/useStepperStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import PoseEditor, { Pose } from "../PoseEditor";

const mapPoseToJoints = (pose: Pose) => {
  const entries = pose.nodes.reduce((agg, node) => {
    agg.push([node.label, node.position]);
    return agg;
  }, new Array<[string, any]>());

  return Object.fromEntries(entries);
};

const CanvasPose = () => {
  const { uuid, imageUrlPose, pose, setPose } = useDrawingStore();
  const { currentStep, setCurrentStep } = useStepperStore();
  const { isLoading, setJointLocations } = useDrawingApi((err) => {
    console.log(err);
  });

  const handleClick = async (clickType: string) => {
    try {
      if (null === uuid && undefined === uuid) {
        return;
      }

      //send new joint locations
      if (clickType === "next" && uuid) {
        const joints = mapPoseToJoints(pose);
        setJointLocations(uuid!, joints, () => {
          setCurrentStep(currentStep + 1);
        });
      }
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div className="canvas-wrapper">
      <div className="canvas-background border border-dark">
        {pose && (
          <PoseEditor imageUrl={imageUrlPose} pose={pose} setPose={setPose} />
        )}
      </div>

      <div className="mt-3">
        <button
          className="buttons large-button"
          disabled={isLoading}
          onClick={() => handleClick("next")}
        >
          Next <i className="bi bi-arrow-right" />
        </button>
      </div>
    </div>
  );
};

export default CanvasPose;
