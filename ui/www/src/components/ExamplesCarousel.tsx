import React from "react";

import example3 from "../assets/drawings_examples/example3.png";
import example4 from "../assets/drawings_examples/example4.jpg";
import example5 from "../assets/drawings_examples/example5.png";
import example6 from "../assets/drawings_examples/example6.png";

const ExamplesCarousel = () => {
  return (
    <>
      <div className="grid-precanned-imgs">
        <div className="md-grid-item" onClick={() => {}}>
          <img src={example3} alt="" />
        </div>
        <div className="md-grid-item" onClick={() => {}}>
          <img src={example4} alt="" />
        </div>
        <div className="md-grid-item" onClick={() => {}}>
          <img src={example5} alt="" />
        </div>
        <div className="md-grid-item" onClick={() => {}}>
          <img src={example6} alt="" />
        </div>
      </div>
    </>
  );
};

export default ExamplesCarousel;
