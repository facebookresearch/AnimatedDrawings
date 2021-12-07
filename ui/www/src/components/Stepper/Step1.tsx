import React from "react";
import ExamplesCarousel from "../ExamplesCarousel";

const Step1 = () => {
  return (
    <div className="step-actions-container custom-scrollbar">
      <p>
        Upload a drawing of a <span className="bold">ONE</span> character, where
        the arms and legs don’t overlap the body (see examples below).{" "}
      </p>
      <p className="bold" style={{ letterSpacing: "0.2em" }}>
        CHECKLIST
      </p>
      <ul className="d-list pl-2">
        <li>
          Make sure the character is drawn on a white piece of paper without
          lines, wrinkles, or tears.
        </li>
        <li>
          Make sure the drawing is well lit. To minimize shadows, hold the
          camera further away and zoom in on the drawing.
        </li>
        <li>
          Don’t include any identifiable information, offensive content (see our{" "}
          <a
            href="https://transparency.fb.com/policies/community-standards/"
            target="_blank"
            rel="noreferrer"
          >
            <span className="bold">community standards</span>
          </a>
          ), or drawings that infringe on the copyrights of others.
        </li>
      </ul>
      <p>
        Feel free to try the demo by clicking on one of the following example
        images.
      </p>
      <ExamplesCarousel />
    </div>
  );
};

export default Step1;
