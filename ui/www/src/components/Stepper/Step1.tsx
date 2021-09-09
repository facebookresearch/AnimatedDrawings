import React from "react";
import { Button } from "react-bootstrap";
import useStepperStore from "../../hooks/useStepperStore";
import useDrawingStore from "../../hooks/useDrawingStore";
import ExamplesCarousel from "../ExamplesCarousel";

const Step1 = () => {
  const { currentStep, setCurrentStep } = useStepperStore();
  const { newCompressedDrawing } = useDrawingStore();

  const onNext = () => {
    if (currentStep > 0 && currentStep <= 4) {
      setCurrentStep(currentStep + 1);
    }
  };

  return (
    <>
      <div className="step-actions-container">
        <h4>Step 1/4</h4>
        <h1 className="reg-title">
          Upload a<br className="d-none d-lg-block" /> drawing
        </h1>
        <p>
          Insert description of spc #1 <br />
          Insert description of spc #2
        </p>
        <ExamplesCarousel />
      </div>
      <div className="mt-2 text-right">
        <Button
          size="sm"
          className="border border-dark text-dark px-3"
          disabled={newCompressedDrawing ? false : true}
          onClick={() => onNext()}
        >
          Next
        </Button>
      </div>
    </>
  );
};

export default Step1;
