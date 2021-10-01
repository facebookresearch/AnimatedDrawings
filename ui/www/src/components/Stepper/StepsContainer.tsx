import React from "react";
import useStepperStore from "../../hooks/useStepperStore";
import Step1 from "./Step1";
import Step3 from "./Step3";
import Step4 from "./Step4";
import Step5 from "./Step5";
import Step6 from "./Step6";

const StepsContainer = () => {
  const { currentStep } = useStepperStore();

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <Step1 />;
      case 3:
        return <Step3 />;
      case 4:
        return <Step4 />;
      case 5:
        return <Step5 />;
      case 6:
        return <Step6 />;
      default:
        return [];
    }
  };

  return (
    <>
      <div className="stepper-container-horizontal">
        <h4 className="bold">STEP {currentStep}/6</h4>
      </div>
      {renderStep()}
    </>
  );
};

export default StepsContainer;
