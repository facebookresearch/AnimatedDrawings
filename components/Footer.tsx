const Site = require("../site.json");
import { getBasePath } from "../lib/paths";
import React from "react";

export default function Footer({ style, columns, children }) {
  return (
    <div
      className={`comp_footer flex w-screen justify-center self-stretch bg-${Site.footerBackground} text-${Site.textColor}`}
      style={style}
    >
      <div
        className={`flex flex-1 flex-row box-border max-w-screen-xl items-start justify-start px-5 md:px-20 xl:px-10 py-20 `}
      >
        <div className="hidden md:flex flex-1 flex-col mr-4 pt-2"></div>

        {columns
          ? React.Children.map(children, (c, i) => {
              return (
                <div className="flex flex-1 box-border pr-2 item-center justify-start text-sm self-stretch">
                  {c}
                </div>
              );
            })
          : children}

        <div className="hidden md:flex flex-1 flex-col mr-4 pt-2 "></div>
      </div>
    </div>
  );
}
