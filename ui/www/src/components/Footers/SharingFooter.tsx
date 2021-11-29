import React from "react";
import { Navbar, Nav } from "react-bootstrap";

interface props {
  setShowModal: (res: boolean) => void;
}

export default function SharingFooter({ setShowModal }: props) {
  return (
    <Navbar
      expand="sm"
      bg="transparent"
      className="align-items-start"
    >
      <Nav className="mr-auto feedback-wrapper">
        <Nav.Link href="https://ai.facebook.com/" className="text-primary">
          PRESENTED BY FACEBOOK AI RESEARCH
        </Nav.Link>
      </Nav>

      <Nav className="text-center feedback-wrapper">
        <Nav.Link
          href={`https://docs.google.com/forms/d/e/1FAIpQLSeKewkuKtcePdGLAbzkjF6apnLHpfswMyjgt7hKBNH0m02W3Q/viewform?usp=pp_url&entry.1352936659=${window.location.href}`}
          target="_blank"
          rel="noreferrer"
          className="text-primary"
        >
          REPORT SOMETHING WRONG
        </Nav.Link>
      </Nav>
    </Navbar>
  );
}
