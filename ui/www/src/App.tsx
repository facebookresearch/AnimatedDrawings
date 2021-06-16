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
  Spinner,
} from "react-bootstrap";

function App() {
  const [show, setShow] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [file, setFile] = useState<File>();
  const [imgData, setImgData] = useState<string>();
  const [responseData, setResponseData] = useState<string>();
  const [videoData, setVideoData] = useState<string>();

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  function loadVideoBlob(data: string) {
    var reader = new FileReader();

    if (data !== null && data !== undefined) {
      reader.onload = (e) => {
        const dataUrl = e.target?.result;
        if (dataUrl && typeof dataUrl === "string") {
          console.log(dataUrl);

          const videoPlayer = document.getElementById("videoPlayer");

          if (videoPlayer && videoPlayer instanceof HTMLVideoElement) {
            videoPlayer.onerror = (e) => {
              debugger;
              console.log("Error in Video Player", e, videoPlayer.error);
              // TODO Show Error.
              throw e;
            };
            videoPlayer.src = dataUrl;
            videoPlayer.loop = true;
            videoPlayer.load();
            videoPlayer.onloadeddata = function () {
              videoPlayer.play();
              setIsLoading(false);
              handleClose();
            };
          }
        }
      };

      var blob = new Blob([data], { type: "video/mp4" });
      reader.readAsDataURL(blob);
    }
  }

  return (
    <>
      {!videoData && (
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
      )}

      <div>
        <video
          id="videoPlayer"
          className="min-vh-100 position-absolute"
        ></video>
      </div>
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
                  setIsLoading(true);
                  const file = e.target.files[0];
                  setFile(file);
                  var reader = new FileReader();
                  reader.onload = (e) => {
                    const dataUrl = e.target?.result;
                    if (dataUrl && typeof dataUrl === "string") {
                      console.log(dataUrl);

                      setImgData(dataUrl);
                      setIsLoading(false);
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
            disabled={isLoading}
            onClick={async (e) => {
              try {
                setIsLoading(true);
                const form = new FormData();
                if (file !== null) {
                  form.append("file", file);
                }

                const result = await axios.post(
                  "http://localhost:5000/upload",
                  form,
                  {
                    responseType: "arraybuffer",
                    timeout: 60000,
                    headers: {
                      "Content-Type": "multipart/form-data",
                    }, // 30s timeout
                  }
                );

                setResponseData(result.data);
                loadVideoBlob(result.data);

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
            {!isLoading && "Submit"}
            {isLoading && (
              <Spinner
                as="span"
                animation="border"
                size="sm"
                role="status"
                aria-hidden="true"
              />
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}

export default App;
