import React from "react";
import image_1 from "../../assets/drawings_examples/step5/image_1.png";
import image_2 from "../../assets/drawings_examples/step5/image_2.png";

const Step5 = () => {
  return (
    <>
      <div className="step-actions-container">
        <h1 className="step-title">
          Finding <span className="text-info">Character Joints</span>
        </h1>
        <p>
          Here are your character's joints! Do they fit the character? Here's an
          example of what it should look like:
        </p>
        <div className="drawing-example-wrapper mt-3">
          <img src={image_1} alt="img1_step5" />
        </div>
        <p className="bold">HINT.</p>
        <p>
          If your character doesn't have any arms, drag the elbows and wrist
          joints far away from the character and it can still be animated:
        </p>
        <div className="drawing-example-wrapper">
          <img src={image_2} alt="img2_step5" />
        </div>
        <p>
          In the next step, we’ll use the segmentation mask and these joints
          locations to animate your character with motion capture data.
        </p>
      </div>
    </>
  );
};

export default Step5;
