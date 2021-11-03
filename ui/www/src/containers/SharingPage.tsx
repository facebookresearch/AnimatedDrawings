import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { Container, Row, Col, Badge } from "react-bootstrap";
import CanvasShare from "../components/Canvas/CanvasShare";
import AboutModal from "../components/Modals/AboutModal";

const SharingPage = () => {
  const { uuid, type } = useParams<{ uuid: string; type: string }>();
  const [reported, setReported] = useState(false);
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <div className="main-content bg-share">
        <div className="navbar-title-waiver">
          <h2>
            ANIMATED <span className="text-info">DRAWINGS</span>
          </h2>
        </div>
        <div className="share-page">
          <Container fluid="md" className="mt-3 align-content-center">
            <Row className="align-items-center justify-content-center py-2 mt-1 px-lg-2">
              <Col lg={8} md={12} sm={12} className="mb-2 mx-2 pl-lg-0">
                <CanvasShare uuid={uuid} animationType={type} />
              </Col>
            </Row>
          </Container>
          <div className="home-footer-credits py-2">
            <h4>PRESENTED BY FACEBOOK AI RESEARCH</h4>
          </div>
          <div
            className="home-footer text-center py-2 mt-xs-4"
            onClick={() => setShowModal(true)}
          >
            <h3>ABOUT THIS DEMO</h3>
          </div>
          {!reported ? (
            <div
              className="footer-report-content py-2"
              onClick={() => setReported(true)}
            >
              <h4>Report something wrong</h4>
            </div>
          ) : (
            <div
              className="footer-report-content py-2"
              //onClick={() => history.push("/about")}
            >
              <h2>
                <Badge variant="success">Reported</Badge>
              </h2>
            </div>
          )}
        </div>
        <AboutModal showModal={showModal} setShowModal={setShowModal} />
      </div>
    </>
  );
};

export default SharingPage;
