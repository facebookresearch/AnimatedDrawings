import React from "react";
import { Navbar, Container, Row, Col } from "react-bootstrap";
import HomeFooter from "../components/Footers/HomeFooter";
import AboutModal from "../components/Modals/AboutModal";

export default function TermsPage() {
  const [showModal, setShowModal] = React.useState(false);
  return (
    <div className="main-content bg-main">
      <Navbar bg="transparent">
        <Navbar.Brand href="/">
          <div className="ad-logo-title">
            <h2 className="mb-3">
              ANIMATED <span className="text-info">DRAWINGS</span>
            </h2>
          </div>
        </Navbar.Brand>
      </Navbar>
      <div className="terms-page mb-2">
        <Container className="">
          <Row className="justify-content-center mt-2">
            <Col lg={10} md={10} xs={12}>
              <h2 className="mb-4 text-center">Terms of use</h2>
              <h3>Animated Drawings Demo Supplemental Terms of Service</h3>
              <br />
              <p>
                By using this Animated Drawings demo (the “Demo”), you agree to
                be bound by Meta Platform Inc.’s Terms of Service (available at
                <a href="https://www.facebook.com/terms.php">
                  {" "}
                  https://www.facebook.com/terms.php
                </a>
                ) (as may be updated from time to time, the “Terms of Service”),
                as supplemented by these Animated Drawing Demo Supplemental
                Terms of Service (these “Supplemental Terms”). You acknowledge
                and agree that:
              </p>
              <p>
                1. As part of your use of the Demo, and subject to the terms of
                these Supplemental Terms and the Terms of Service, you may
                submit drawings created by you or your child (“Materials”) to
                the Demo. Once such Materials are submitted, you will have the
                opportunity to correct the Demo’s identification, segmentation,
                and placement of joints on the hand drawn characters
                (“Modifications”). After the Materials are submitted and
                Modifications (if any) are made, the Demo can be used to create
                animated renderings of such Materials (the “Animations”).
              </p>
              <p>
                2. By submitting Materials to the Demo, you represent that: (a)
                you are at least 18 years old (or the age of majority in the
                jurisdiction from which you are accessing the Demo); (b) each
                item of Materials submitted to the Demo is an original
                two-dimensional static drawing and does not include or otherwise
                incorporate any other form of artwork or media (including
                photographs, videos or music); (c) with respect to each item of
                Materials submitted to the Demo, you are the creator of, or the
                parent or guardian of the child that created, such item; (d) you
                will not allow a child to use the Demo; and (e) the Materials do
                not contain any information that could be used to identify you
                or a child who created such Materials (such as your or the
                child’s name, address or age)
              </p>
              <p>
                3. You grant to Meta and its affiliated companies, licensees and
                representatives, on behalf of you and any child who created any
                item of Materials that you submit to the Demo, a perpetual,
                irrevocable, nonexclusive, royalty-free license to reproduce,
                distribute, perform and display (publicly or otherwise), modify,
                create derivative works of, host and otherwise use the
                Materials, Animations and Modifications in connection with the
                Demo.
              </p>
              <p>
                4. As a large company, Meta needs to be very careful about
                intellectual property infringement. You may not submit any
                content to the Demo that infringes the intellectual property
                rights of others (e.g., no drawings of Mickey Mouse, please).
                Also, do not submit content that might be regarded as offensive.
              </p>
              <p>
                5. Because we will not associate Materials or Animations
                (including any Modifications) with your name, your child’s name,
                photo metadata, or any other personally identifiable
                information, you won’t be able to request deletion of submitted
                Materials or Animations generated from such Materials. Please
                make sure that you are okay with how we will use the Materials
                and Animations before you agree to these Supplemental Terms and
                grant to us the permissions included in these Supplemental
                Terms.
              </p>
              <p>
                6. The Demo allows you to share Animations generated from your
                submitted Materials, including your Modifications to such
                Animations, on Facebook and certain other social media
                platforms. If you elect to share the Animation on any such
                social media platforms, your use of the Animation is subject to
                any additional terms, conditions and policies applicable to such
                platforms
              </p>
            </Col>
          </Row>
        </Container>
      </div>
      <HomeFooter
        uuid={"[No ID] - Preload feedback"}
        setShowModal={setShowModal}
      />
      <AboutModal showModal={showModal} setShowModal={setShowModal} />
    </div>
  );
}
