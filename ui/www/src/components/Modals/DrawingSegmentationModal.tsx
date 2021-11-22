import React, { useRef, useState, Fragment } from "react";
import classnames from "classnames";
import UndoIcon from "../../assets/customIcons/undo.svg";
import { Modal, Row, Col, Button } from "react-bootstrap";

import useMaskingStore from "../../hooks/useMaskingStore";

import MaskStage from "../Canvas/MaskStage";
import SegmentationHelpModal from "./SegmentationHelpModal";

interface props {
  showModal: boolean;
  croppedImgDimensions: { width: number; height: number };
  imgScale: number;
  handleModal: () => void;
}

const DrawingSegmentationModal = ({
  showModal,
  croppedImgDimensions,
  imgScale,
  handleModal,
}: props) => {
  const canvasWindow = useRef<HTMLInputElement | any>(null);
  const layerRef = useRef<HTMLImageElement | any>(null);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const {
    tool,
    penSize,
    lines,
    setTool,
    setPenSize,
    setLines,
  } = useMaskingStore();

  const handleReset = () => {
    if (!lines.length) {
      return;
    }
    setLines([]);
  };

  const handleUndo = () => {
    if (!lines.length) {
      return;
    }
    let newLines = lines.slice(0, -1);
    setLines(newLines);
  };

  return (
    <Fragment>
      <Modal
        centered
        size="lg"
        animation={false}
        show={showModal}
        onHide={handleModal}
      >
        <Modal.Header closeButton className="bg-secondary mt-lg-2">
          <h2 className="ml-lg-4 modal-title">FIX SEGMENTATION </h2>
          <span onClick={() => setShowHelpModal(true)}>
            <i className="bi bi-question-circle-fill ml-3" />
          </span>
        </Modal.Header>
        <Modal.Body className="bg-secondary px-0">
          <div className="canvas-wrapper">
            <Row className="mb-3 mx-0 tools-wrapper">
              <Col>
                <Row>
                  <button
                    className={classnames(
                      "sm-button-icon border border-dark mr-2",
                      {
                        "bg-primary text-white": tool === "pen",
                      }
                    )}
                    onClick={() => setTool("pen")}
                  >
                    <i className="bi bi-pencil-fill" />
                  </button>
                  <button
                    className={classnames(
                      "sm-button-icon border border-dark mr-2",
                      {
                        "bg-primary text-white": tool === "eraser",
                      }
                    )}
                    onClick={() => setTool("eraser")}
                  >
                    <i className="bi bi-eraser-fill" />
                  </button>
                  <div className="pens-wrapper border border-dark">
                    <form className="pens">
                      <label className="label0 d-none d-lg-block">
                        <input
                          type="radio"
                          name="radio"
                          value={3}
                          checked={penSize === 3}
                          onChange={() => setPenSize(3)}
                        />
                        <span></span>
                      </label>
                      <label className="label1">
                        <input
                          type="radio"
                          name="radio"
                          value={5}
                          checked={penSize === 5}
                          onChange={() => setPenSize(5)}
                        />
                        <span></span>
                      </label>
                      <label className="label2">
                        <input
                          type="radio"
                          name="radio"
                          value={15}
                          checked={penSize === 15}
                          onChange={() => setPenSize(15)}
                        />
                        <span></span>
                      </label>
                      <label className="label3">
                        <input
                          type="radio"
                          name="radio"
                          value={26}
                          checked={penSize === 26}
                          onChange={() => setPenSize(26)}
                        />
                        <span></span>
                      </label>
                    </form>
                  </div>
                </Row>
              </Col>
              <Col>
                <Row className="justify-content-end">
                  <button
                    className="sm-button-icon border border-dark mr-2"
                    onClick={handleUndo}
                  >
                    <img src={UndoIcon} alt="icon" />
                  </button>

                  <button
                    className="md-button-reset border border-dark p-0"
                    onClick={handleReset}
                  >
                    Reset mask
                  </button>
                </Row>
              </Col>
            </Row>
            <div ref={canvasWindow} className="canvas-background loader">
              <MaskStage
                scale={imgScale}
                canvasWidth={croppedImgDimensions.width}
                canvasHeight={croppedImgDimensions.height}
                ref={layerRef}
              />
            </div>
          </div>
        </Modal.Body>
        <Modal.Footer className="bg-secondary">
          <Button variant="default" onClick={handleModal}>Close</Button>
        </Modal.Footer>
      </Modal>
      <SegmentationHelpModal
        showModal={showHelpModal}
        handleModal={() => setShowHelpModal(!showHelpModal)}
        title={"HOW TO FIX"}
      />
    </Fragment>
  );
};

export default DrawingSegmentationModal;
