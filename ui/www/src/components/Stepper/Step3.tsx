import React from "react";
import { Button } from "react-bootstrap";
import useStepperStore from "../../hooks/useStepperStore";
import useDrawingStore from "../../hooks/useDrawingStore";

const Step3 = () => {
  const { uuid } = useDrawingStore();
  const { setCurrentStep } = useStepperStore();

  const handleClick = async (clickType: string) => {
    try {
      if (null === uuid && undefined === uuid) {
        return;
      }
      if (clickType === "previous") {
        setCurrentStep(1);
      }
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <>
      <div className="step-actions-container">
        <h1 className="step-title">Detecting</h1>
        <p>
          We’re currently scanning the figure to identify the human figure
          within it.
        </p>
        <p>Click on 'Next' when the detection finalizes.</p>
      </div>
      <div className="mt-2 text-right">
        <Button
          variant="outline-dark"
          size="sm"
          disabled={false}
          onClick={() => handleClick("previous")}
        >
          Previous
        </Button>{" "}
      </div>
    </>
  );
};

export default Step3;
