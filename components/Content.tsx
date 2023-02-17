const Site = require("../site.json");

import { getBasePath } from "../lib/paths";

export default function Content({
  color,
  whiteText,
  noteLeft,
  noteRight,
  imageLeft,
  imageRight,
  spaceTop,
  spaceBottom,
  small,
  style,
  children,
}) {
  const bgColor = color
    ? color === "theme"
      ? `bg-${Site.theme}-${Site.shade}`
      : `bg-${color}`
    : `bg-${Site.paper}`;
  const textColor = whiteText ? "text-white" : "text-gray-700";
  const padTop = spaceTop ? "pt-20" : "pt-4";
  const padBottom = spaceBottom ? "pb-20" : "pb-4";
  const textSize = small ? "prose-sm" : "prose-lg";

  return (
    <div
      className={`comp_content flex w-screen justify-center self-stretch ${bgColor} ${textColor} ${
        whiteText ? "color-flip" : ""
      }`}
      style={style}
    >
      <div
        className={`flex flex-1 flex-row box-border max-w-screen-xl items-center justify-start px-5 md:px-20 xl:px-10 ${padTop} ${padBottom}`}
      >
        <div className="hidden md:flex flex-1 flex-col mr-4 pt-2 items-start justify-start h-full text-sm">
          {imageLeft && (
            <div className="aspect-w-4 aspect-h-4">
              <img
                src={getBasePath(imageLeft)}
                alt={noteLeft || ""}
                className="object-contain"
              />
            </div>
          )}
          <div className={`opacity-70 ${textColor}`}>{noteLeft || ""}</div>
        </div>

        <div
          className={`flex-1 flex-grow-4 self-start max-w-none ${textSize} mx-4 ${textColor}`}
        >
          {children}
        </div>

        <div className="hidden md:flex flex-1 flex-col ml-4 pt-2 items-start justify-start h-full text-sm">
          {imageRight && (
            <div className="aspect-auto">
              <img
                src={getBasePath(imageRight)}
                alt={noteRight || ""}
                className="object-contain mb-2 mt-2"
              />
            </div>
          )}
          <div className={`flex opacity-70 ${textColor}`}>
            {noteRight || ""}
          </div>
        </div>
      </div>
    </div>
  );
}
