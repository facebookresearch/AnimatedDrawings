import React from "react";
import image_1 from "../../assets/drawings_examples/step3/image_1.png";
import image_2 from "../../assets/drawings_examples/step3/image_2.png";

const StepBoundingBox = () => {
  return (
    <div className="step-actions-container custom-scrollbar">
      <p>
        We’ve identified the character and put a box around it. Is the box too
        small for the character? If so, adjust the box.
      </p>
      <p className="bold" style={{ letterSpacing: "0.2em" }}>
        CHECKLIST
      </p>
      <ul className="d-list pl-2">
        <li>Resize the box to ensure it tightly fits one character.</li>
        <li>If everything looks fine, hit 'Next'.</li>
      </ul>
      <div className="drawing-example-wrapper">
        <img src={image_1} alt="Img1" />
      </div>
      <div className="drawing-example-wrapper">
        <img src={image_2} alt="Img2" />
      </div>
    </div>
  );
};

export default StepBoundingBox;
