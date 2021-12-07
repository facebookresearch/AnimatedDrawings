import React from "react";
import { Spinner } from "react-bootstrap";
import example3 from "../assets/drawings_examples/example3.png";
import example4 from "../assets/drawings_examples/example4.jpg";
import example5 from "../assets/drawings_examples/example5.png";
import example6 from "../assets/drawings_examples/example6.png";
import { useDrawingApi } from "../hooks/useDrawingApi";
import useDrawingStore from "../hooks/useDrawingStore";
import useStepperStore from "../hooks/useStepperStore";

const ExamplesCarousel = () => {
  const { isLoading, setPreCannedImage } = useDrawingApi((err) => {});
  const { setUuid } = useDrawingStore();
  const { setCurrentStep } = useStepperStore();

  /**
   * Use pre canned image, invokes api to find a predefined 
   * image stored server-side given its name.
   * @param image_name 
   */
  const handlePreCannedImage = async (image_name: string) => {
    try {
      await setPreCannedImage(image_name, (data) => {
        setUuid(data as string);
        console.log(data);
      });
      setCurrentStep(2);
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="grid-precanned-imgs">
      <div className="md-grid-item">
        {isLoading ? (
          <Spinner animation="grow" variant="primary" />
        ) : (
          <img
            src={example3}
            alt=""
            onClick={() => handlePreCannedImage("example3.png")}
          />
        )}
      </div>
      <div className="md-grid-item">
        {isLoading ? (
          <Spinner animation="grow" variant="primary" />
        ) : (
          <img
            src={example4}
            alt=""
            onClick={() => handlePreCannedImage("example4.jpg")}
          />
        )}
      </div>
      <div className="md-grid-item">
        {isLoading ? (
          <Spinner animation="grow" variant="primary" />
        ) : (
          <img
            src={example5}
            alt=""
            onClick={() => handlePreCannedImage("example4.jpg")}
          />
        )}
      </div>
      <div className="md-grid-item">
        {isLoading ? (
          <Spinner animation="grow" variant="primary" />
        ) : (
          <img
            src={example6}
            alt=""
            onClick={() => handlePreCannedImage("example6.png")}
          />
        )}
      </div>
    </div>
  );
};

export default ExamplesCarousel;
