import React from "react";
import ExamplesCarousel from "../ExamplesCarousel";

const Step1 = () => {

  return (
    <>
      <div className="step-actions-container">
        <h1 className="step-title">
          Upload a<br className="d-none d-lg-block" /> drawing
        </h1>
        <h5 className="bold">INSTRUCTIONS</h5>
        <ul className="d-list">
          <li>
            Upload a drawing of a single human-like character where the arms and
            legs don’t overlap the body (see examples below).{" "}
          </li>
          <li>
            Don’t include any identifiable information, offensive content (see
            our community standards), or drawings that infringe on the
            copyrights of others.{" "}
          </li>
        </ul>
        <p>For Best Results:</p>
        <ul className="d-list">
          <li>
            Make sure the character is drawn on a white piece of paper without
            lines, wrinkles, or tears.
          </li>
          <li>
            Make sure the drawing is well lit. To minimize shadows, hold the
            camera further away and zoom in on the drawing.
          </li>
        </ul>

        <ExamplesCarousel />
      </div>
    </>
  );
};

export default Step1;
