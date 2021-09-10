import React from "react";
import useDrawingStore from "../../hooks/useDrawingStore";
import useStepperStore from "../../hooks/useStepperStore";
import PoseEditor from "../PoseEditor";

const CanvasPose = () => {
  const { imageUrlPose, pose, setPose } = useDrawingStore();
  const { currentStep, setCurrentStep } = useStepperStore();

  return (
    <div className="canvas-wrapper">
      <div className="canvas-background border border-dark">
        {pose && (
          <PoseEditor imageUrl={imageUrlPose} pose={pose} setPose={setPose} />
        )}
      </div>

      <div className="mt-3">
        <button
          className="large-button border border-dark"
          onClick={() => setCurrentStep(currentStep + 1)}
        >
          Preview <i className="bi bi-arrow-right" />
        </button>
      </div>
    </div>
  );
};

export default CanvasPose;
