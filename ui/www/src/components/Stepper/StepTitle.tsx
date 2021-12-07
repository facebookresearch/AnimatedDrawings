import React from "react";
import classnames from "classnames";

interface TitleProps {
  currentStep: number;
}

const titles = [
  {
    step: 1,
    title: "Upload a drawing",
  },
  {
    step: 2,
    title: "Finding the human-like character",
  },
  {
    step: 3,
    title: "Separating character",
  },
  {
    step: 4,
    title: "Finding character joints",
  },
  {
    step: 5,
    title: "Add animation",
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
      {title?.title}
    </h1>
  );
};

export default StepTitle;
