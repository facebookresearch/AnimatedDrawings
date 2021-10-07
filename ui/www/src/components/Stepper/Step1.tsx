import React from "react";
import ExamplesCarousel from "../ExamplesCarousel";

const Step1 = () => {

  return (
    <>
      <div className="step-actions-container">
        <h1 className="step-title">
          Upload a<br className="d-none d-lg-block" /> drawing
        </h1>
        <p>Upload a drawing of a <b>single human-like character</b>, where the arms and
            legs don’t overlap the body (see examples below). </p>
        <p>For Best Results:</p>
        <ul className="d-list">
          <li>
            Make sure the character is drawn on a blank piece of paper without
            lines, wrinkles, or tears.
          </li>
          <li>
            Make sure the drawing is well lit. To minimize shadows, hold the
            camera further away and zoom in on the drawing.
          </li>
        </ul>

        <h5 className="bold">NOTE</h5>
        <p>Don’t include any identifiable information, offensive content
          (see our <a href="https://transparency.fb.com/policies/community-standards/" target="_blank" rel="noreferrer">community standards</a>),
          or drawings that infringe on the copyrights of others.</p>

        <ExamplesCarousel />
      </div>
    </>
  );
};

export default Step1;
