import React from "react";
import { Button } from "react-bootstrap";
import useStepperStore from "../../hooks/useStepperStore";

const Step5 = () => {
  const { currentStep, setCurrentStep } = useStepperStore();

  return (
    <>
      <div className="step-actions-container">
        <h1 className="step-title">Segmenting</h1>
        <p>
          Using the box, we extracted a segmentation mask to separate the
          character from the background.
        </p>
        <p>Does the mask cover the entire character?</p>
        <p>Are the arms and legs separated from each other in the mask?</p>
        <p>
          Does the mask exclude everything that isn’t part of the character?
        </p>
        <p>
          If not, you can correct this by using the drawing tools. If everything
          looks fine, simply hit next.
        </p>
      </div>
      <div className="mt-2 text-right">
        <Button
          variant="outline-dark"
          size="sm"
          disabled={false}
          onClick={() => setCurrentStep(currentStep - 1)}
        >
          Previous
        </Button>
      </div>
    </>
  );
};

export default Step5;
