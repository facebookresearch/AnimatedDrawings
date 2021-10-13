import React from "react";
import image_1 from "../../assets/drawings_examples/step4/image_1.png";
import image_2 from "../../assets/drawings_examples/step4/image_2.png";
import image_3 from "../../assets/drawings_examples/step4/image_3.png";

const Step4 = () => {
  return (
    <>
      <div className="step-actions-container">
        <h1 className="step-title">
          Separating <span className="text-info">Character</span>
        </h1>
        <p>
          We’ve separated the character from the background, and highlighted it.
          Did we get the entire character? Did we include things that aren’t
          part of the character? If so, use the tools to fix it.
        </p>
        <div className="drawing-example-wrapper mt-1">
          <img src={image_1} alt="img1_step4" />
        </div>
        <br />
        <div className="drawing-example-wrapper">
          <img src={image_2} alt="img2_step4" />
        </div>
        <p>
          If the limbs are stuck together, please erase the mask to separate
          them. See the example below:
        </p>
        <div className="drawing-example-wrapper mt-2">
          <img src={image_3} alt="img3_step4" />
        </div>
      </div>
    </>
  );
};

export default Step4;
