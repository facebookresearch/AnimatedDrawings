import React from "react";
import { Button } from "react-bootstrap";
import useStepperStore from "../../hooks/useStepperStore";
import useDrawingStore from "../../hooks/useDrawingStore";

import image_1 from "../../assets/step3/image_1.png";
import image_2 from "../../assets/step3/image_2.png";

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
        <h1 className="step-title">Finding the Human-Like Character</h1>
        <p>We’ve identified the character and put a box around it.</p>
        <p>Is the box too small for the character? If so, adjust the box.
        <div className="drawing-example-wrapper">
          <img src={image_1} />
        </div>
        </p>
        <p>Is the box too big for the character? If so, adjust the box.
        <div className="drawing-example-wrapper">
          <img src={image_2} />
        </div>
        </p>

        <p>If everything looks fine, hit 'Next'.</p>
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
