import React from "react";
import image_1 from "../../assets/drawings_examples/step4/image_1.png";
import image_2 from "../../assets/drawings_examples/step4/image_2.png";
import image_3 from "../../assets/drawings_examples/step4/image_3.png";

const Step3 = () => {
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
        <li>If the arms or legs are stuck together, use the eraser tool to separate them</li>
        <li>If everything looks fine, hit 'Next'.</li>
      </ul>
      <div className="drawing-example-wrapper mt-1">
        <img src={image_1} alt="img1_step4" />
      </div>
      <div className="drawing-example-wrapper">
        <img src={image_2} alt="img2_step4" />
      </div>
      <div className="drawing-example-wrapper mt-2">
        <img src={image_3} alt="img3_step4" />
      </div>
    </div>
  );
};

export default Step3;
