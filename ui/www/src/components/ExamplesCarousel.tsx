import React from "react";

import example3 from "../assets/drawings_examples/example3.png";
import example4 from "../assets/drawings_examples/example4.jpg";
import example5 from "../assets/drawings_examples/example5.png";
import example6 from "../assets/drawings_examples/example6.png";

const ExamplesCarousel = () => {
  return (
    <div className="horizontal-scrolling">
        <p>Feel free to try the demo by downloading one of the following example images.</p>
      <ul className="hs full">
        <li className="item">
          <div className="drawing-example-wrapper">
            <img alt="example 3" src={example3} />
          </div>
        </li>
        <li className="item">
          <div className="drawing-example-wrapper">
            <img alt="example 4" src={example4} />
          </div>
        </li>
        <li className="item">
          <div className="drawing-example-wrapper">
            <img alt="example 5" src={example5} />
          </div>
        </li>
        <li className="item">
          <div className="drawing-example-wrapper">
            <img alt="example 6" src={example6} />
          </div>
        </li>
      </ul>
    </div>
  );
};

export default ExamplesCarousel;
