import React from "react";
import { Button } from "react-bootstrap";
import useStepperStore from "../../hooks/useStepperStore";

const Step6 = () => {
  const { currentStep, setCurrentStep } = useStepperStore();

  return (
    <>
      <div className="step-actions-container">
        <h1 className="step-title">Detecting Joints</h1>
        <p>Here are the joint locations we’ve predicted.</p>
        <p>
          How do they look? They don’t need to be pixel-perfect, but they do
          need to be in roughly the correct location.
        </p>
        <p>
          If they’re not, you can correct this by dragging the nodes. Or, you
          can simply hit the ‘Next’ to continue.
        </p>
        <p>
          In the next step, we’ll use the segmentation mask and these joints
          locations to animate your character with motion capture data.
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
        </Button>{" "}
      </div>
    </>
  );
};

export default Step6;
