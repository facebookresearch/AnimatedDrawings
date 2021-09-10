import React from "react";
import { useParams } from "react-router";
import { Container, Row, Col } from "react-bootstrap";
import Navbar from "../components/Navbars/Navbar";
import CanvasShare from "../components/Canvas/CanvasShare";

const SharingPage = () => {
  const { uuid, type } = useParams<{ uuid: string; type: string }>();

  return (
    <div className="main-content">
      <Navbar />
      <div className="share-page">
        <Container fluid="md" className="mt-3 align-content-center">
          <Row className="align-items-center justify-content-center py-2 mt-1 px-lg-2">
            <Col lg={12} md={12} sm={12} className="mb-2 mx-2 pl-lg-0">
              <CanvasShare uuid={uuid} animationType={type} />
            </Col>
          </Row>
        </Container>
      </div>
    </div>
  );
};

export default SharingPage;
