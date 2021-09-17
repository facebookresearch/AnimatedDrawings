import React, { Fragment } from "react";
import classnames from "classnames";
import { Button } from "react-bootstrap";
import useStepperStore from "../../hooks/useStepperStore";
import useDrawingStore from "../../hooks/useDrawingStore";
import AnimationTypes from "../../utils/AnimationTypes";

const Step4 = () => {
  const { currentStep, setCurrentStep } = useStepperStore();
  const { animationType, setAnimationType } = useDrawingStore();

  const handleClick = async (clickType: string) => {
    try {
      if (clickType === "previous") setCurrentStep(currentStep - 1);
      else setCurrentStep(currentStep + 1);
    } catch (err) {
      console.log(err);
    }
  };

  const animationTypes = AnimationTypes.map((i: any, index: number) => {
    return (
      <Fragment key={index}>
        <div
          className={classnames("sm-grid-item", {
            "item-grid-selected": i.name === animationType,
          })}
          onClick={() => setAnimationType(i.name)}
        >
          <img src={i.gif} alt="" />
        </div>
      </Fragment>
    );
  });

  return (
    <>
      <div className="step-actions-container">
        <h4>Step 4/4</h4>
        <h1 className="reg-title">Animate</h1>
        <p>
          If anything looks off you can use the ‘fix’ button below to adjust the
          bounding box, segmentation mask, and joint positions.
          <br />
          Otherwise, choose one of the motions below to see your character
          perform it!
        </p>

        <div className="grid-container">{animationTypes}</div>
      </div>
      <div className="mt-2 text-right">
        <Button
          variant="outline-dark"
          size="sm"
          disabled={false}
          onClick={() => handleClick("previous")}
        >
          Previous
        </Button>{" "}
        <Button
          size="sm"
          className="border border-dark text-dark px-3"
          disabled={false}
          onClick={() => handleClick("next")}
        >
          Next
        </Button>
      </div>
    </>
  );
};

export default Step4;
