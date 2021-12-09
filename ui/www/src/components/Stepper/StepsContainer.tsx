import React from "react";
import useStepperStore from "../../hooks/useStepperStore";
import StepUpload from "./StepUpload";
import StepBoundingBox from "./StepBoundingBox";
import StepMask from "./StepMask";
import StepPose from "./StepPose";
import StepAnimation from "./StepAnimation";
import StepTitle from "./StepTitle";
import StepTracker from "./StepTracker";

const stepsArray = [...Array(4).keys()].map((i) => i + 1);

const StepsContainer = () => {
  const { currentStep } = useStepperStore();

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <StepUpload />;
      case 2:
        return <StepBoundingBox />;
      case 3:
        return <StepMask />;
      case 4:
        return <StepPose />;
      case 5:
        return <StepAnimation />;
      default:
        return [];
    }
  };

  return (
    <div className="stepper-wrapper bg-white">
      {currentStep !== 5 ? (
        <div className="stepper-container-horizontal">
          <h3 className="step-counter">STEP {currentStep}/4</h3>
          <StepTracker currentStepNumber={currentStep - 1} steps={stepsArray} />
          <StepTitle currentStep={currentStep} />
        </div>
      ) : (
        <div className="stepper-container-horizontal">
          <StepTitle currentStep={currentStep} />
        </div>
      )}
      {renderStep()}
    </div>
  );
};

export default StepsContainer;
