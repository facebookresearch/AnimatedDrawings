import React from "react";
import { Button } from "react-bootstrap";
import useStepperStore from "../../hooks/useStepperStore";
import useDrawingStore from "../../hooks/useDrawingStore";
import ExamplesCarousel from "../ExamplesCarousel";

const Step1 = () => {
  const { currentStep, setCurrentStep } = useStepperStore();
  const { newCompressedDrawing } = useDrawingStore();

  const onNext = () => {
    if (currentStep > 0 && currentStep <= 4) {
      setCurrentStep(currentStep + 1);
    }
  };

  return (
    <>
      <div className="step-actions-container">
        <h4>Step 1/4</h4>
        <h1 className="reg-title">
          Upload a<br className="d-none d-lg-block" /> drawing
        </h1>
        <p>
          - Upload a drawing of a single human-like character where the arms and
          legs don’t overlap the body (see examples below). <br />
        </p>
        <p>
          - Don’t include any identifiable information, offensive content (see
          our community standards), or drawings that infringe on the copyrights
          of others.
        </p>
        <p>For Best Results:</p>
        <p>
          - Make sure the character is drawn on a white piece of paper without
          lines, wrinkles, or tears.
        </p>
        <p>
          - Make sure the drawing is well lit. To minimize shadows, hold the
          camera further away and zoom in on the drawing.
        </p>
        <ExamplesCarousel />
      </div>
      <div className="mt-2 text-right">
        <Button
          size="sm"
          className="border border-dark text-dark px-3"
          disabled={newCompressedDrawing ? false : true}
          onClick={() => onNext()}
        >
          Next
        </Button>
      </div>
    </>
  );
};

export default Step1;
