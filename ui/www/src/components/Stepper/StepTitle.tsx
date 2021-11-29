import React from "react";
import classnames from "classnames";

interface TitleProps {
  currentStep: number;
}

const titles = [
  {
    step: 1,
    firstLine: "Upload a",
    secondLine: "drawing",
  },
  {
    step: 2,
    firstLine: "Finding the",
    secondLine: "human-like ",
    thirdLine: "character",
  },
  {
    step: 3,
    firstLine: "Separating",
    secondLine: "character",
  },
  {
    step: 4,
    firstLine: "Finding",
    secondLine: "character joints",
  },
  {
    step: 5,
    firstLine: "Add",
    secondLine: "animation",
  },
];

const StepTitle = ({ currentStep }: TitleProps) => {
  const title = titles.find((i) => i.step === currentStep);
  return (
    <h1
      className={classnames("step-title", {
        "ml-2": currentStep === 5,
      })}
    >
      {title?.firstLine} <span className="text-info">{title?.secondLine}</span>
      {title?.thirdLine}
    </h1>
  );
};

export default StepTitle;
