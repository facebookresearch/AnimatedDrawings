import React from "react";
import image_1 from "../../assets/drawings_examples/step2/Step2GIF1.gif";
import image_2 from "../../assets/drawings_examples/step2/Step2GIF2.gif";

const StepBoundingBox = () => {
  return (
    <div className="step-actions-container custom-scrollbar">
      <p>We’ve identified the character, and put a box around it.</p>
      <p className="bold" style={{ letterSpacing: "0.2em" }}>
        CHECKLIST
      </p>
      <ul className="d-list pl-2">
        <li>Resize the box to ensure it tightly fits one character.</li>
      </ul>
      <div className="bb-samples-wrapper">
        <div>
          <img src={image_1} alt="Img1" />
        </div>
        <div>
          <img src={image_2} alt="Img2" />
        </div>
      </div>
    </div>
  );
};

export default StepBoundingBox;
