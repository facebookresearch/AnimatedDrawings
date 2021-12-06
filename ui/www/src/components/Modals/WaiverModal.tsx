import React, { Fragment } from "react";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import useStepperStore from "../../hooks/useStepperStore";
import useDrawingStore from "../../hooks/useDrawingStore";
import WaiverStep from "../Stepper/WaiverStep";

interface modalProps {
  showModal: boolean;
  setShowModal: (show: boolean) => void;
}

const WaiverModal = ({ showModal, setShowModal }: modalProps) => {
  const { setAgreeTerms, setCurrentStep } = useStepperStore();
  const { uuid } = useDrawingStore();
  const { isLoading, setConsentAnswer } = useDrawingApi((err) => {});

  /**
   * Send waiver response to server.
   * 1 as aggree, and 0 as disagree
   * @param res boolean response.
   */
  const handleNext = async (res: boolean) => {
    let response = res ? 1 : 0;
    try {
      setAgreeTerms(res);
      await setConsentAnswer(uuid, response, () => {
        setShowModal(false);
      });
      setCurrentStep(2);
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <Fragment>
      {showModal ? (
        <div className="waiver-step-container-wrap">
          <div className="main-content bg-waiver">
            <div className="navbar-title-waiver">
              <h2>
                ANIMATED <span className="text-info">DRAWINGS</span>
              </h2>
            </div>
            <div className="share-page">
              <WaiverStep
                showModal={showModal}
                isLoading={isLoading}
                setShowModal={setShowModal}
                handleNext={handleNext}
              />
            </div>
          </div>
        </div>
      ) : null}
    </Fragment>
  );
};

export default WaiverModal;
