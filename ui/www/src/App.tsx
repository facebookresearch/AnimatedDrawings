import React, { useState } from "react";
import logo from "./logo.svg";
import "./App.css";
import {
  Button,
  Carousel,
  Col,
  Container,
  Form,
  Modal,
  Row,
} from "react-bootstrap";

function App() {
  const [show, setShow] = useState(false);

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  return (
    <>
      <Carousel fade>
        <Carousel.Item interval={7000}>
          <video playsInline autoPlay muted loop id="">
            <source src="demo1.mp4" type="video/mp4" />
          </video>
          <Carousel.Caption>
            <h3>First slide label</h3>
            <p>Nulla vitae elit libero, a pharetra augue mollis interdum.</p>
          </Carousel.Caption>
        </Carousel.Item>
        <Carousel.Item interval={7000}>
          <video playsInline autoPlay muted loop poster="polina.jpg" id="">
            <source src="demo2.mp4" type="video/mp4" />
          </video>

          <Carousel.Caption>
            <h3>Second slide label</h3>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
          </Carousel.Caption>
        </Carousel.Item>
      </Carousel>
      <Container fluid>
        <Row noGutters={true} className="h-100">
          <Col className="align-self-center h-100">
            <Button
              variant="primary"
              size="lg"
              onClick={handleShow}
              className="align-self-center"
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
        <Modal.Body>
          Alright! Let's get started by uploading an image of drawing!
          <Form className="mt-3">
            <Form.File
              id="custom-file"
              label="Custom file input"
              custom
              onChange={(e: React.ChangeEvent) => {
                // doSomethingWithFiles(e.target.files)
              }}
            />
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            Close
          </Button>
          <Button variant="primary" onClick={handleClose}>
            Submit
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}

export default App;
