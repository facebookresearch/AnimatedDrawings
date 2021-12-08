import React from "react";
import image_1 from "../../assets/drawings_examples/step5/image_1.png";
import image_2 from "../../assets/drawings_examples/step5/image_2.png";

const StepPose = () => {
  return (
    <div className="step-actions-container custom-scrollbar">
      <p>
        Here are your character's joints! Here's an example of what it should
        look like:
      </p>
      <div className="drawing-example-wrapper my-3">
        <img src={image_1} alt="img1_step5" />
      </div>
      <p className="bold" style={{ letterSpacing: "0.2em" }}>
        CHECKLIST
      </p>
      <ul className="d-list pl-2">
        <li>
          If your character doesn't have any arms, drag the elbows and wrist
          joints far away from the character and it can still be animated:
        </li>
        <li>If everything looks fine, hit 'Next'.</li>
      </ul>

      <div className="drawing-example-wrapper">
        <img src={image_2} alt="img2_step5" />
      </div>
      <p>
        In the next step, we’ll use the segmentation mask and these joints
        locations to animate your character with motion capture data.
      </p>
    </div>
  );
};

export default StepPose;
