import React from "react";
import useStepperStore from "../../hooks/useStepperStore";
import StepTracker from "./StepTracker";
import Step1 from "./Step1";
import Step2 from "./Step2";
import Step3 from "./Step3";
import Step4 from "./Step4";
import Step5 from "./Step5";
import Step3A from "./Step3A";

const stepsArray = ["1", "2", "3", "4"];

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
        return <Step3A />;
      case 5:
        return <Step4 />;
      case 6:
        return <Step5 />;
      default:
        return [];
    }
  };

  return (
    <>
      <div className="stepper-container-horizontal">
        <StepTracker
          currentStepNumber={currentStep - 1}
          steps={stepsArray}
          stepColor="black"
        />
      </div>
      {renderStep()}
    </>
  );
};

export default StepsContainer;
