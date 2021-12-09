import React from "react";
import { Spinner } from "react-bootstrap";
import example3 from "../assets/drawings_examples/example3.png";
import example4 from "../assets/drawings_examples/example4.jpg";
import example5 from "../assets/drawings_examples/example5.jpg";
import example6 from "../assets/drawings_examples/example6.png";
import { useDrawingApi } from "../hooks/useDrawingApi";
import useDrawingStore from "../hooks/useDrawingStore";
import useStepperStore from "../hooks/useStepperStore";

const ExamplesCarousel = () => {
  const { isLoading, setPreCannedImage, setConsentAnswer } = useDrawingApi((err) => {});
  const { setUuid, setDrawing, setOriginalDimensions } = useDrawingStore();
  const { setCurrentStep } = useStepperStore();

  const selectImgFile = (image_name: string) => {
    switch (image_name) {
      case "example3.png":
        return example3;
      case "example4.jpg":
        return example4;
      case "example5.jpg":
        return example5;
      case "example6.png":
        return example6;
      default:
        return example4;
    }
  };

  /**
   * Use pre canned image, invokes api to find a predefined
   * image stored server-side given its name.
   * @param image_name
   */
  const handlePreCannedImage = async (image_name: string) => {
    let img_file = selectImgFile(image_name);
    try {
      const res = await fetch(img_file);
      const blob = await res.blob();
      const imageDataUrl = URL.createObjectURL(blob);
      const tempImage = new Image();
      if (imageDataUrl !== null && imageDataUrl !== undefined)
        tempImage.src = imageDataUrl;
      // Calculate the original dimensions of img for the bouding box background.
      tempImage.onload = function (e) {
        setOriginalDimensions({
          width: tempImage.naturalWidth,
          height: tempImage.naturalHeight,
        });
      };

      await setPreCannedImage(image_name, (data) => {
        setUuid(data as string);
        setConsentAnswer(data, 0, () => {}) // here set up the consent to disagree always, as not user images are being used.
      });

      setDrawing(imageDataUrl);
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
            onClick={() => handlePreCannedImage("example5.jpg")}
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
