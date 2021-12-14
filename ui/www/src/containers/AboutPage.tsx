import React from "react";
import { Navbar, Nav, Container, Row, Col } from "react-bootstrap";

const AboutPage = () => {
  return (
    <div className="main-content bg-about">
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
        <Container>
          <Row className="justify-content-center mt-2">
            <Col lg={7} md={10} xs={12} className="about-single-page">
              <h2 className="mb-4 text-center">ABOUT THIS DEMO</h2>
              <p>
                Children’s drawings have a wonderful inventiveness,
                energy, and variety. We focus on the consequence of all
                that variety in their drawings of human figures as we develop an
                algorithm to bring them to life through automatic
                animation.
              </p>
              <br />
              <p> This demo builds upon <a href="https://github.com/facebookresearch/detectron2" target="_blank" rel="noreferrer" className="bold"> Detectron2</a> and 
                <a href="https://github.com/MVIG-SJTU/AlphaPose" target="_blank" rel="noreferrer"> AlphaPose</a>. Motion capture data comes from the{" "}
                <a href="http://mocap.cs.cmu.edu/" target="_blank" rel="noreferrer">CMU Graphics Motion Capture Lab</a> and
                <a href="https://www.mixamo.com/" target="_blank" rel="noreferrer"> Mixamo</a>.
              </p>
              <br />
              <p>
                Built by Jesse Smith, Jessica Hodgins, Somya Jain, Sahir
                Gomez, Somayan Chakrabarti, Clarence Edmondson III, Christopher Gustave, 
                Kristin Cooke, Qingyuan Zheng, and friends at Meta AI Research.
              </p>
              <hr />
              <p>
                The “Animated Drawings” Demo allows parents and guardians
                to convert two-dimensional children’s’ drawings into fun
                animations.
              </p>
              <p>
                To use the Demo, you’ll need to upload an image of your or
                your child’s drawing. Later, you’ll have the option to
                contribute the image to a public dataset, but you can use
                the Demo without contributing the image. In order to use
                the Demo, you don’t need a Facebook account and we don’t
                collect any information that identifies you or your child.
                We collect technical information about your browser or
                device, including through the use of cookies, but we use
                that information only to provide the tool and for
                analytics purposes to see how individuals interact with
                our website.
              </p>
              <p>
                When you upload an image of your or your child’s drawing,
                we will retain the image for a short period of time, after
                which it will be permanently deleted if you do not agree
                to contribute it to a public dataset
              </p>
              <p>
                After an animation is created from a drawing by you or
                your child, you will have the option to download or share
                the generated animation to Facebook and certain other
                social media platforms. If you choose to share your
                generated animation on social media, then the privacy
                policy of the operator(s) of the applicable social media
                platform(s) will apply to your sharing of the animation
              </p>
              <p>
                If you choose to provide us with feedback about the Demo,
                we will have access to the email address from which you
                provide the feedback, as well as any other personal
                information that you provide in the feedback itself.
              </p>
              <p>
                If you choose to contribute your or your child’s drawing
                to our public data set, the image will not be stored with
                any personal information
                <span className="bold">
                  {" "}
                  We will not associate contributed drawings with your
                  name, your child’s name, photo metadata, or any other
                  personally identifiable information
                </span>
                . This means that you won’t be able to request deletion of
                the image after you have consented to contributing it.
                Please be sure you are okay with how we’ll use the
                drawings as specified below before you consent to
                contributing to research.
              </p>
              <p>
                If you consent to contributing your or your child’s
                drawing and your interactions with the demo to further
                research, the drawing and interactions may be used,
                released, or published for any of the following purposes:
              </p>
              <ul className="d-list pl-2">
                <li>
                  To train a model to better identify, segment, and place
                  joints on hand drawn characters;
                </li>
                <li>To ensure quality annotations by human viewers;</li>
                <li>As part of an academic research paper or video;</li>
                <li>
                  As part of a publicly available database for researchers
                  to develop creativity tools for children; and/or
                </li>
                <li>
                  As part of future initiatives to encourage additional
                  image collection.
                </li>
              </ul>
              <p>
                If you consent to contributing your or your child’s
                drawing for further research, the purposes set forth above
                are the only research-related purposes for which we will
                use the contributed drawing.
              </p>
            </Col>
          </Row>
        </Container>
      </div>
      <Navbar expand="sm" bg="transparent" className="align-items-start">
        <Nav className="mr-auto">
          <Nav.Link
            href={`https://docs.google.com/forms/d/e/1FAIpQLSfynXUEVc0YvSYGXN3BCFjl7uNthyEkxqibsNHn3pqA_Wt8Hg/viewform?entry.1387562397=Preload Step [No ID]`}
            target="_blank"
            rel="noreferrer"
            className="text-primary"
          >
            Feedback
            <i className="bi bi-info-circle-fill ml-2 h3"></i>
          </Nav.Link>
        </Nav>
        <Nav className="text-right">
          <Nav.Link
            href="https://www.facebook.com/about/privacy/"
            target="_blank"
            rel="noreferrer"
            className="text-primary"
          >
            Privacy Policy
          </Nav.Link>
          <Nav.Link
            href="/terms"
            target="_blank"
            rel="noreferrer"
            className="text-primary"
          >
            Terms
          </Nav.Link>
          <Nav.Link
            href="https://www.facebook.com/policies/cookies/"
            target="_blank"
            rel="noreferrer"
            className="text-primary"
          >
            Cookies
          </Nav.Link>
        </Nav>
      </Navbar>
    </div>
  );
};

export default AboutPage;
