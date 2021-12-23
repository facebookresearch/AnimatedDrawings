import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { Container, Row, Col } from "react-bootstrap";
import CanvasShare from "../components/Canvas/CanvasShare";
import AboutModal from "../components/Modals/AboutModal";
import SharingFooter from "../components/Footers/SharingFooter";
import useLogPageView from "../hooks/useLogPageView";

const SharingPage = () => {
  const { videoId, type } = useParams<{ videoId: string; type: string }>();
  const [showModal, setShowModal] = useState(false);

  useLogPageView("View Shared Animation", "");

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
              <CanvasShare videoId={videoId} animationType={type} />
            </Col>
          </Row>
        </Container>
      </div>
      <SharingFooter setShowModal={setShowModal} />
      <AboutModal showModal={showModal} setShowModal={setShowModal} />
    </div>
  );
};

export default SharingPage;
