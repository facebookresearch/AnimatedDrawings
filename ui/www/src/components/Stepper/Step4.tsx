import React, { Fragment } from "react";
import classnames from "classnames";
import { Button } from "react-bootstrap";
import useStepperStore from "../../hooks/useStepperStore";
import useDrawingStore from "../../hooks/useDrawingStore";
import example4 from "../../assets/drawings_examples/example4.jpg";

const Step4 = () => {
  const { currentStep, setCurrentStep } = useStepperStore();
  const { animationType, setAnimationType } = useDrawingStore();

  const handleClick = async (clickType: string) => {
    try {
      if (clickType === "previous") {
        setCurrentStep(currentStep - 1);
      }
    } catch (err) {
      console.log(err);
    }
  };

  /**
   * This is temporary hardcoded array.
   */
  const types = [
    { name: "run_jump", gif: example4 },
    { name: "wave", gif: example4 },
    { name: "dance", gif: example4 },
    { name: "run_jump", gif: example4 },
    { name: "wave", gif: example4 },
    { name: "dance", gif: example4 },
    { name: "run_jump", gif: example4 },
    { name: "wave", gif: example4 },
    { name: "dance", gif: example4 },
  ];

  const animationTypes = types.map((i: any, index: number) => {
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
          [Insert a description of what’s happening in this step of the process]
        </p>

        <div className="grid-container">{animationTypes}</div>
      </div>
      <div className="mt-2 text-right">
        <Button
          variant="outline-dark"
          className="px-3"
          size="sm"
          disabled={false}
          onClick={() => handleClick("previous")}
        >
          Fix
        </Button>
      </div>
    </>
  );
};

export default Step4;
