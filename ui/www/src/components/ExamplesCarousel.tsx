import React from "react";

const ExamplesCarousel = () => {
  return (
    <div className="horizontal-scrolling">
      <h4>Examples</h4>
      <ul className="hs full">
        <li className="item">
          <div className="drawing-example-wrapper">
            <img alt="example 3" src="/assets/example3.png"/>
          </div>
        </li>
        <li className="item">
          <div className="drawing-example-wrapper">
            <img alt="example 4" src="/assets/example4.jpg" />
          </div>
        </li>
        <li className="item">
          <div className="drawing-example-wrapper">
            <img alt="example 5" src="/assets/example5.jpg" />
          </div>
        </li>
        <li className="item">
          <div className="drawing-example-wrapper">
            <img alt="example 6" src="/assets/example6.jpg" />
          </div>
        </li>
      </ul>
    </div>
  );
};

export default ExamplesCarousel;
