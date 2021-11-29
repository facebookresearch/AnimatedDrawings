import React from "react";
import { useHistory } from "react-router-dom";
import { Container, Row, Col, Button } from "react-bootstrap";
import AboutModal from "../components/Modals/AboutModal";
import SplashVideo from "../assets/video_assets/splashVideo.mp4";
import HomeFooter from "../components/Footers/HomeFooter";

const HomePage = () => {
  const history = useHistory();
  const [showModal, setShowModal] = React.useState(false);
  return (
    <>
      <div className="main-content bg-home" id="home">
        <div className="home-page">
          <Container className="align-content-center home-info">
            <Row className="justify-content-center">
              <Col lg={6} md={6} sm={6} className="text-center mb-4">
                <h2 className="mb-3">
                  ANIMATED <span className="text-info">DRAWINGS</span>
                </h2>

                <h4 className="subtitle">PRESENTED BY FACEBOOK AI RESEARCH</h4>
              </Col>
            </Row>
            <Row className="justify-content-center">
              <Col lg={5} md={6} sm={6} className="text-center mb-4">
                <h3>
                  Bring children's drawings to life, by animating characters to
                  move around!
                </h3>
              </Col>
            </Row>
            <Row className="justify-content-center">
              <Col
                lg={6}
                md={10}
                xs={12}
                className="mb-4 justify-content-center"
              >
                <div className="ml-auto mr-auto gif-wrapper">
                  <div className="gif-div">
                    <div className="video-contain">
                      <video
                        autoPlay
                        muted
                        loop
                        playsInline
                        width="100%"
                        height="auto"
                      >
                        <source src={SplashVideo} type="video/mp4" />
                      </video>
                    </div>
                  </div>
                  <div className="gif-shadow-div"></div>
                </div>
              </Col>
            </Row>
            <Row className="justify-content-center">
              <Col lg={3} md={4} className="text-center">
                <Button
                  block
                  size="lg"
                  className="px-4 py-2 py-lg-3"
                  onClick={() => history.push("/canvas")}
                >
                  Get Started
                </Button>
              </Col>
            </Row>
          </Container>
        </div>
        <HomeFooter uuid={'[No ID] - Preload feedback'} setShowModal={setShowModal} />
        <AboutModal showModal={showModal} setShowModal={setShowModal} />
      </div>
    </>
  );
};

export default HomePage;
