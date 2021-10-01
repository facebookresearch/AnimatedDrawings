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
        <h1 className="step-title">Segmenting</h1>
        <p>We’ve identified the character and put a bounding box around it.</p>
        <p>
          Does the box include the entire character? If not, you can correct
          this by dragging some of the nodes.
        </p>
        <p>If everything looks fine, simply hit 'Next'.</p>
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
