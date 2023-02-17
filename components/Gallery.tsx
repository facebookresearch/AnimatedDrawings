const Site = require("../site.json");
import React from "react";
import { chunkArray, zipArray } from "../lib/util";

export default function Gallery({
  color,
  whiteText,
  columns = 1,
  flowVertical,
  grid,
  fullWidth,
  noteLeft,
  noteRight,
  spaceTop,
  spaceBottom,
  style,
  children,
}) {
  const bgColor = color ? `bg-${color}` : `bg-${Site.paper}`;
  const textColor = whiteText ? "text-white" : "text-gray-700";
  const padTop = spaceTop ? "pt-20" : "pt-4";
  const padBottom = spaceBottom ? "pb-20" : "pb-4";

  const itemsCount = React.Children.count(children);
  const isSingle = itemsCount < 2;
  const cols = itemsCount / columns;
  const chunks = isSingle
    ? []
    : flowVertical
    ? chunkArray(children, cols)
    : zipArray(chunkArray(children, children.length / cols));

  return (
    <div
      className={`comp_gallery flex w-screen justify-center self-stretch ${bgColor} ${textColor}`}
      style={style}
    >
      <div
        className={`max-w-screen-xl flex flex-1 flex-row items-center justify-start px-5 md:px-20 xl:px-10 ${padTop} ${padBottom}`}
      >
        {!fullWidth && (
          <div className="hidden md:flex flex-1 flex-col mr-4 pt-4 items-start justify-start h-full text-sm">
            <div className={`opacity-70 ${textColor}`}>{noteLeft || ""}</div>
          </div>
        )}

        <div
          className={`flex flex-1 flex-grow-4 self-start max-w-none ${
            fullWidth ? "" : "mx-4"
          }`}
        >
          {!isSingle &&
            chunks.map((chs, k) => (
              <div className="flex-col flex-1" key={`group${k}`}>
                {chs.map((c, i) => (
                  <div
                    className={`p-1 ${grid ? "aspect-[1/1]" : "aspect-auto"}`}
                    key={`img${i}`}
                  >
                    {c}
                  </div>
                ))}
              </div>
            ))}
          {isSingle && <div className="p-1 aspect-auto">{children}</div>}
        </div>

        {!fullWidth && (
          <div className="hidden md:flex flex-1 flex-col ml-4 pb-4 items-start justify-end h-full text-sm">
            <div className={`opacity-70 ${textColor}`}>{noteRight || ""}</div>
          </div>
        )}
      </div>
    </div>
  );
}
