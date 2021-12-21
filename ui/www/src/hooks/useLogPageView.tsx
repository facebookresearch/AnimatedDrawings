import React, { useEffect, useLayoutEffect } from "react";
import * as ReactGA from "react-ga4";

const useLogPageView = (title: string, path: string) => {
  useLayoutEffect(() => {
    ReactGA.default.send({
      hitType: "pageview",
      page_title: title,
      page_path: path,
    });
  }, [path, title]);
};

export default useLogPageView;
