import React from "react";
import { Container, Row, Col } from "react-bootstrap";

const Navbar = () => {
  return (
    <Container fluid="md">
      <Row className="align-items-center py-2 px-1">
        <Col md={6} sm={6} xs={6} className="px-0">
          <h1 className="reg-title">Kid's Drawings Animation</h1>
        </Col>
        <Col md={6} sm={6} xs={6} className="px-0 text-right"></Col>
      </Row>
    </Container>
  );
};

export default Navbar;
