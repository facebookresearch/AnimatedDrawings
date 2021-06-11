import React, { useState } from "react";
import logo from "./logo.svg";
import FormData from "form-data";
import axios from "axios";
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
  const [file, setFile] = useState<File>();
  const [imgData, setImgData] = useState<string>();

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  return (
    <>
      <Carousel fade>
        <Carousel.Item interval={7000}>
          <video playsInline autoPlay muted loop id="" className="min-vh-100">
            <source src="demo1.mp4" type="video/mp4" />
          </video>
          <Carousel.Caption>
            <h3>First slide label</h3>
            <p>Nulla vitae elit libero, a pharetra augue mollis interdum.</p>
          </Carousel.Caption>
        </Carousel.Item>
        <Carousel.Item interval={7000}>
          <video autoPlay muted loop id="" className="min-vh-100">
            <source src="demo2.mp4" type="video/mp4" />
          </video>

          <Carousel.Caption>
            <h3>Second slide label</h3>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
          </Carousel.Caption>
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
        <Modal.Body>
          Alright! Let's get started by uploading an image of drawing!
          {imgData && (
            <img src={imgData} alt="Preview" className="img-fluid"></img>
          )}
          <Form className="mt-3">
            <Form.File
              id="custom-file"
              label={
                file?.name
                  ? file.name
                  : "Take a picture of your hand drawn figure"
              }
              custom
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                if (e.target.files !== null && e.target.files.length > 0) {
                  const file = e.target.files[0];
                  setFile(file);
                  var reader = new FileReader();
                  reader.onload = (e) => {
                    const dataUrl = e.target?.result;
                    if (dataUrl && typeof dataUrl === "string") {
                      console.log(dataUrl);

                      setImgData(dataUrl);
                    }
                  };

                  reader.readAsDataURL(file);
                }
              }}
            />
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            Close
          </Button>
          <Button
            variant="primary"
            onClick={async (e) => {
              try {
                const form = new FormData();
                if (file !== null) {
                  form.append("file", file);
                }

                const result = await axios.post(
                  "http://localhost:5000/upload",
                  form,
                  {
                    timeout: 30000,
                    headers: {
                      "Content-Type": "multipart/form-data",
                    }, // 30s timeout
                  }
                );

                // TODO handle uploaded image
                console.log(result);
              } catch (error) {
                console.log(error);
                // onError(error);
              } finally {
                // setIsLoading(false);
              }
            }}
          >
            Submit
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}

export default App;
