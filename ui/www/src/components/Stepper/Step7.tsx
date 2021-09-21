import React, { Fragment } from "react";
import classnames from "classnames";
import { Button } from "react-bootstrap";
import useStepperStore from "../../hooks/useStepperStore";
import useDrawingStore from "../../hooks/useDrawingStore";
import AnimationTypes from "../../utils/AnimationTypes";

const Step7 = () => {
  const { currentStep, setCurrentStep } = useStepperStore();
  const { animationType, setAnimationType } = useDrawingStore();

  const groups = AnimationTypes.reduce((r, a) => {
    r[a.group] = r[a.group] || [];
    r[a.group].push(a);
    return r;
  }, Object.create(null));

  const danceGroup = groups["dance"].map((i: any, index: number) => {
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

  const funnyGroup = groups["funny"].map((i: any, index: number) => {
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

  const jumpsGroup = groups["jumps"].map((i: any, index: number) => {
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

  const walkingGroup = groups["walks"].map((i: any, index: number) => {
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
        <h1 className="step-title">Add Animation</h1>
        <p>
          If anything looks off you can use the ‘fix’ button below to adjust the
          bounding box, segmentation mask, and joint positions.
        </p>
        <p>
          Otherwise, choose one of the motions below to see your character
          perform it!
        </p>

        <h4 className="bold">DANCE ANIMATIONS</h4>
        <div className="grid-container">{danceGroup}</div>

        <h4 className="bold">FUNNY ANIMATIONS</h4>
        <div className="grid-container">{funnyGroup}</div>

        <h4 className="bold">JUMPING ANIMATIONS</h4>
        <div className="grid-container">{jumpsGroup}</div>

        <h4 className="bold">WALKING ANIMATIONS</h4>
        <div className="grid-container">{walkingGroup}</div>
      </div>
      <div className="mt-2 text-right">
        <Button
          variant="outline-dark px-4"
          size="sm"
          disabled={false}
          onClick={() => setCurrentStep(currentStep - 1)}
        >
          Fix
        </Button>{" "}
      </div>
    </>
  );
};

export default Step7;
