import React from "react";
import { Button } from "react-bootstrap";
import useStepperStore from "../../hooks/useStepperStore";
import image_1 from "../../assets/step5/image_1.png";
import image_2 from "../../assets/step5/image_2.png";

const Step5 = () => {
  const { currentStep, setCurrentStep } = useStepperStore();

  return (
    <>
      <div className="step-actions-container">
        <h1 className="step-title">Finding Character Joints</h1>
        <p>
          Here are your character's joints! Do they fit the character? Here's an
          example of what it should look like:
          <div className="drawing-example-wrapper mt-3">
            <img src={image_1} alt="img1_step5" />
          </div>
        </p>

        <h4>Tip!</h4>
        <p>
          If your character doesn't have any arms, drag the elbows and wrist
          joints far away from the character and it can still be animated:
          <div className="drawing-example-wrapper">
            <img src={image_2} alt="img2_step5" />
          </div>
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

export default Step5;
