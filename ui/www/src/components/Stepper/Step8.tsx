import React from "react";
import { Button } from "react-bootstrap";
import useStepperStore from "../../hooks/useStepperStore";
import useDrawingStore from "../../hooks/useDrawingStore";

const Step8 = () => {
  const { uuid } = useDrawingStore();
  const { currentStep, setCurrentStep } = useStepperStore();

  const handleClick = async (clickType: string) => {
    try {
      if (null === uuid && undefined === uuid) {
        return;
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
        <h1 className="reg-title">Your Drawings</h1>
        <p>
          [Insert a description of what’s happening in this step of the process]
        </p>
      </div>
      <div className="mt-2 text-right">
        <Button
          variant="outline-dark"
          size="sm"
          className="px-4"
          onClick={() => handleClick("previous")}
        >
          Fix
        </Button>{" "}
      </div>
    </>
  );
};

export default Step8;
