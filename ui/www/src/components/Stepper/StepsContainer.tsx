import React from "react";
import useStepperStore from "../../hooks/useStepperStore";
import Step1 from "./Step1";
import Step2 from "./Step2";
import Step3 from "./Step3";
import Step5 from "./Step5";
import Step6 from "./Step6";
import StepTitle from "./StepTitle";
import StepTracker from "./StepTracker";

const stepsArray = [...Array(4).keys()].map((i) => i + 1);

const StepsContainer = () => {
  const { currentStep } = useStepperStore();

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <Step1 />;
      case 2:
        return <Step2 />;
      case 3:
        return <Step3 />;
      case 4:
        return <Step5 />;
      case 5:
        return <Step6 />;
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
