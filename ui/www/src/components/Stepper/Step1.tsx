import React from "react";
import ExamplesCarousel from "../ExamplesCarousel";

const Step1 = () => {
  return (
    <>
      <div className="step-actions-container bottom-shadow">
        <p>
          Upload a drawing of a <span className="bold">single human-like character</span>, where the
          arms and legs don’t overlap the body (see examples below).{" "}
        </p>
        <p className="bold" style={{letterSpacing: "0.2em"}}>FOR BEST RESULTS:</p>
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

        <p>
          Don’t include any identifiable information, offensive content (see our{" "}
          <a
            href="https://transparency.fb.com/policies/community-standards/"
            target="_blank"
            rel="noreferrer"
          >
            <span className="bold">community standards</span>
          </a>
          ), or drawings that infringe on the copyrights of others.
        </p>
        <p>
          Feel free to try the demo by downloading one of the following example
          images.
        </p>
        <ExamplesCarousel />
      </div>
    </>
  );
};

export default Step1;
