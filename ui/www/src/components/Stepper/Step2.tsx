import React from "react";
import { Button, Spinner } from "react-bootstrap";
import useStepperStore from "../../hooks/useStepperStore";
import useDrawingStore from "../../hooks/useDrawingStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";

const Step2 = () => {
  const { agreeTerms, currentStep, setCurrentStep } = useStepperStore();
  const { newCompressedDrawing } = useDrawingStore();
  const { isLoading } = useDrawingApi((err) => {});

  const handleClick = async (clickType: string) => {
    try {
      if (
        clickType === "next" &&
        newCompressedDrawing !== null &&
        newCompressedDrawing !== undefined
      ) {
        setCurrentStep(currentStep + 1);
      }

      if (clickType === "previous") {
        setCurrentStep(currentStep - 1);
      }
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <>
      <div className="step-actions-container">
        <h4>Step 2/4</h4>
        <h1 className="reg-title">
          Would you like
          <br className="d-none d-lg-block" /> to help our research?
        </h1>
        <p>Granting permission is totally optional.</p>
        <p>
          Thanks for giving our demo a try. It is still a work in progress and,
          to make it more robust, we need to collect additional drawings and
          annotations for training. We’d like to use the drawing you’ve
          uploaded, but first we’d like to make sure you’re okay with how we’ll
          use it. If you aren’t, you can opt out and still use the demo.
        </p>
        <p>In plain English, here is our request:</p>
        <p>
          1. Are you willing to let us use your child’s drawings to help make
          the tool better? We will not associate the drawing with your name,
          your child’s name, photo metadata or any other personally identifiable
          information. The drawing will be used to train a model to better
          identify, segment, and place joints on hand drawn characters. The
          deidentified drawing may also be sent to human viewers to ensure
          quality annotations.
        </p>
        <p>
          2. The drawings also may be used as part of an academic research paper
          or video and may be used in future initiatives to encourage additional
          image collection. Are you willing to let us publish your child’s
          drawing for these research purposes? Again no personal information
          would be included with the drawing.
        </p>
        <p>
          3. Releasing a public dataset is a useful way to encourage research
          within that area. Are you willing to let us include your child’s
          drawings in a publicly available database so that other researchers
          can work on creativity tools for children? Again, we will not
          associate any personal information with the drawing. The only thing
          that will be included in the database is a photograph of the drawing
          and the annotations (e.g. the separation from the background, and the
          bone structure for the character).
        </p>
        <p>Here are a couple more things to be aware of:</p>
        <p>
          1. As a large company, Facebook needs to be very careful about
          copyright infringement. We would appreciate it if you would avoid
          uploading any content that infringes on the copyright of others (no
          drawings of Mickey Mouse, please) or content that might be regarded as
          offensive.
        </p>
        <p>
          2. Because we are removing all personal information from the drawings,
          we will not be able to remove them from the dataset at a future date,
          should you request it. Please be sure you are okay with how we’ll use
          the drawings before granting us permission.
        </p>
        <p>And here is the legal version of our request:</p>
        <p>
          You submitted original images drawn or otherwise developed by You
          and/or Your child (“Materials”) and interacted with the demo (“User
          Input”). You grant Facebook, Inc. and its agents, affiliated
          companies, and licensees, a perpetual, irrevocable, nonexclusive,
          royalty-free license to use, create derivative works of, publicly use,
          distribute, reproduce, and perform/display the Materials and User
          Input to improve the model, and to publicly use, distribute,
          reproduce, and perform/display the Materials and User Input for the
          purposes of (1) having professional annotators or crowdsourced workers
          annotate or clean the Materials and User Input, and (2) publicly
          releasing the Materials and User Input as part of an open source
          dataset.
        </p>
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
          disabled={!agreeTerms || isLoading}
          onClick={() => handleClick("next")}
        >
          {isLoading ? (
            <Spinner
              as="span"
              animation="border"
              size="sm"
              role="status"
              aria-hidden="true"
            />
          ) : (
            "Next"
          )}
        </Button>
      </div>
    </>
  );
};

export default Step2;
