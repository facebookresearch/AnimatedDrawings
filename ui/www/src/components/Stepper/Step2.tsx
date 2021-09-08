import React from "react";
import { Button, Spinner } from "react-bootstrap";
import useStepperStore from "../../hooks/useStepperStore";
import useDrawingStore from "../../hooks/useDrawingStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";

const Step2 = () => {
  const {
    agreeTerms,
    currentStep,
    setCurrentStep,
  } = useStepperStore();
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
        <p>This is totally optional!</p>
        <p>
          This is totally optional! Thanks for trying out our demo! We’re
          working hard to make our system robust to everyone’s drawing styles.
          To do this, we’d like to use the drawing you uploaded to train future
          models and will need you to agree to these terms.
        </p>
        <p>
          This Materials Release (“Release”) is between the undersigned (“You”)
          and Facebook, Inc. and its agents, affiliated companies, and licensees
          (“Facebook”), and is effective as of the date written below
          (“Effective Date”). You have submitted original images drawn or
          otherwise developed by You and/or Your child, with the understanding
          that such images (“Materials”) and Your user input (You may have been
          asked to correct bounding boxes, segmentation masks, and joint
          positions, after submitting the Materials and viewing the animation to
          improve the animation, or to select one of several motions to apply to
          the drawing, or to specify the character’s ‘up’ or ‘forward’ vector,
          etc.). We are requesting that these Materials and User Input be used
          in one or more of the following ways by Facebook: - The Materials and
          User Input may be included in model training data. - The Materials and
          animations derived from the images may be included in one or more
          research papers , accompanying video, or any other research-related
          release materials (such as a website). - Some of the animations may
          also be used in future Facebook initiatives to encourage additional
          image collection. - The entire collection of Materials and User Input
          (or a subset of each) may be publicly released as a dataset for use by
          the research community. - Materials may be crowdsourced for annotation
          collection purposes. 1. Training License. You grant Facebook a
          perpetual, nonexclusive, royalty-free license to use and create
          derivative works of the Materials and User Input to improve the model,
          and to publicly use, distribute, reproduce, and perform/display the
          Materials and User Input for the purpose of having professional
          annotators or crowdsourced workers annotate or clean the Materials and
          User Input. 2. Release. You release Facebook from any and all claims
          that might arise out of direct or indirect use of the Materials and
          User Input. You will not make any claims against Facebook for our use
          of this data. Or, you are giving this data to Facebook for no
          compensation or other claims. (Essentially, a more limited
          indemnification clause that people won’t be wary to sign.). 3. Reps
          and Warranties; Indemnification. Facebook is not obligated to use the
          Materials. You will not attempt to enjoin or otherwise impair
          Facebook’s use of the Materials that is in accordance with this
          Release. You represent and warrant that (i) You have all necessary
          rights to grant these licenses (including on behalf of Your child as
          necessary), (ii) the Materials will not infringe any copyright, trade
          secret, trademark, or right of publicity/privacy of any third party.
          You agree to indemnify and hold Facebook harmless from and against all
          third-party claims arising out of Your breach of these representations
          and warranties, but solely with respect to use of the Materials as
          authorized under this Release. 4. Limitation of Liability. EXCEPT FOR
          AN INDEMNIFICATION CLAIM, NEITHER PARTY WILL BE LIABLE FOR ANY
          CONSEQUENTIAL, INCIDENTAL, INDIRECT, SPECIAL, OR PUNITIVE DAMAGES,
          ARISING OUT OF OR RELATED TO THIS RELEASE, EVEN IF THE PARTY HAS BEEN
          ADVISED OF THE POSSIBILITY OF SUCH DAMAGES, AND NOTWITHSTANDING THE
          FAILURE OF ESSENTIAL PURPOSE OF ANY LIMITED REMEDY STATED HEREIN. 5.
          Release Termination. Aside from the licenses granted under this
          Release, all other provisions will survive its termination, if any,
          and Facebook will have no obligation to remove or recall any prior use
          or distribution of the Materials that is in accordance with this
          Release. 6. Miscellaneous. This Release will be binding upon and will
          inure to the benefit of the parties’ successors, and will be governed
          by the laws of the State of California.
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
