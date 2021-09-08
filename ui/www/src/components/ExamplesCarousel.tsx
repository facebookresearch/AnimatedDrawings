import React from "react";
import example3 from "../assets/drawings_examples/example3.png";
import example4 from "../assets/drawings_examples/example4.jpg";
import example5 from "../assets/drawings_examples/example5.jpg";
import example6 from "../assets/drawings_examples/example6.jpg";

const ExamplesCarousel = () => {
  return (
    <div className="horizontal-scrolling">
      <h4>Examples</h4>
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
