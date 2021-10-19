import React from "react";
import { Modal, Row, Col } from "react-bootstrap";
import VideoExample from "../../assets/video_assets/segmentationExample.mp4";

interface modalProps {
  showModal: boolean;
  title: string;
  handleModal: () => void;
}

const SegmentationHelpModal = ({ showModal, title, handleModal }: modalProps) => {
  return (
    <Modal centered animation={false} show={showModal} onHide={handleModal}>
      <Modal.Header closeButton className="bg-secondary mt-lg-2">
        <h2 className="ml-lg-4 modal-title">{title}</h2>
      </Modal.Header>
      <Modal.Body className="bg-secondary modal-share">
        <Row className="px-lg-4 mt-2 mb-1">
          <Col>
            <video autoPlay muted loop playsInline width="100%" height="auto">
              <source src={VideoExample} type="video/mp4" />
            </video>
          </Col>
        </Row>
      </Modal.Body>
      <Modal.Footer className="bg-secondary pb-0"></Modal.Footer>
    </Modal>
  );
};

export default SegmentationHelpModal;
