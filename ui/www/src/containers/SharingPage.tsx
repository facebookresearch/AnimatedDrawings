import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { Container, Row, Col } from "react-bootstrap";
import CanvasShare from "../components/Canvas/CanvasShare";
import AboutModal from "../components/Modals/AboutModal";
import SharingFooter from "../components/Footers/SharingFooter";

const SharingPage = () => {
  const { uuid, type } = useParams<{ uuid: string; type: string }>();
  const [showModal, setShowModal] = useState(false);

  return (
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
        <div
          className="home-footer-credits text-center py-2"
          onClick={() => setShowModal(true)}
        >
          <h4>ABOUT THIS DEMO</h4>
        </div>
      </div>
      <SharingFooter setShowModal={setShowModal} />
      <AboutModal showModal={showModal} setShowModal={setShowModal} />
    </div>
  );
};

export default SharingPage;
