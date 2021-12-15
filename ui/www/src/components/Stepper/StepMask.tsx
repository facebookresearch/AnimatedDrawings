import React from "react";
import image_1 from "../../assets/drawings_examples/step3/Step3GIF1.gif";
import image_2 from "../../assets/drawings_examples/step3/Step3GIF2.gif";

const StepMask = () => {
  return (
    <div className="step-actions-container custom-scrollbar">
      <p>
        We’ve separated the character from the background, and highlighted it.
      </p>
      <p className="bold" style={{ letterSpacing: "0.2em" }}>
        CHECKLIST
      </p>
      <ul className="d-list pl-2">
        <li>If the body parts of your character are not highlighted, use the pen and eraser tools to fix it.</li>
      </ul>
      <div className="drawing-example-wrapper mt-1">
        <img src={image_1} alt="img1_step3" />
      </div>
      <ul className="d-list pl-2">
        <li>If the arms or legs are stuck together, use the eraser tool to separate them</li>
      </ul>
      <div className="drawing-example-wrapper">
        <img src={image_2} alt="img2_step3" />
      </div>
    </div>
  );
};

export default StepMask;
