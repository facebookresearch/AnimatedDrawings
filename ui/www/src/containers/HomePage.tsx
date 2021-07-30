import React, { useCallback, useReducer, useState } from "react";
import axios from "axios";
import "./HomePage.css";
import {
  Button,
  Carousel,
  Col,
  Container,
  Modal,
  Row,
  Spinner,
} from "react-bootstrap";
import UploadImageBody, {
  UploadImageStep,
} from "../components/UploadImageStep";
import PoseStep from "../components/PoseStep";

enum CreateAnimationStep {
  Upload = "upload",
  Pose = "pose",
}

interface Props {}

const HomePage = (props: Props) => {
  const [show, setShow] = useState(false);

  const [uuid, setUuid] = useState<string>();

  const [step, setStep] = useState<CreateAnimationStep>(
    CreateAnimationStep.Upload
  );
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  return (
    <>
      <Carousel fade>
        <Carousel.Item interval={7000}>
          <video playsInline autoPlay muted loop id="" className="min-vh-100">
            <source src="demo1.mp4" type="video/mp4" />
          </video>
        </Carousel.Item>
        <Carousel.Item interval={7000}>
          <video playsInline autoPlay muted loop id="" className="min-vh-100">
            <source src="demo2.mp4" type="video/mp4" />
          </video>
        </Carousel.Item>
      </Carousel>

      <Container fluid>
        <Row noGutters={true} className="vh-100">
          <Col className="d-flex flex-column justify-content-end vh-100">
            <Button
              variant="primary"
              size="lg"
              onClick={handleShow}
              className="align-self-end m-5"
            >
              Create your own Animations
            </Button>
          </Col>
        </Row>
      </Container>
      <Modal show={show} onHide={handleClose} centered>
        <Modal.Header closeButton>
          <Modal.Title>Create your own animation</Modal.Title>
        </Modal.Header>
        <Modal.Body className="p-0">
          {step === CreateAnimationStep.Upload && (
            <UploadImageStep
              onClose={handleClose}
              onImageUploadSuccess={(data) => {
                setUuid(data as string);
                setStep(CreateAnimationStep.Pose);
              }}
            />
          )}
          {step === CreateAnimationStep.Pose && <PoseStep uuid={uuid} />}
        </Modal.Body>
      </Modal>
    </>
  );
};

export default HomePage;
