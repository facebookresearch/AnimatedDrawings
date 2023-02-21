const Site = require("../site.json");
import React from "react";
import { chunkArray, zipArray } from "../lib/util";
import { useBreakpoint } from "./useBreakPoint";

export type GalleryProps = {
  color?: "theme" | "white" | "gray" | "blue" | "red" | "yellow" | "green";
  whiteText?: boolean;
  columns?: number | number[];
  layout?: "vertical" | "grid" | "horizontal";
  fullWidth?: boolean;
  noteLeft?: string;
  noteRight?: string;
  spaceTop?: boolean;
  spaceBottom?: boolean;
  style?: React.CSSProperties;
  className?: string;
  children: React.ReactNode;
};

export default function Gallery({
  color,
  whiteText,
  columns = 1,
  layout = 'grid',
  fullWidth,
  noteLeft,
  noteRight,
  spaceTop,
  spaceBottom,
  style,
  className='',
  children,
}: GalleryProps ) {
  const bgColor = color ? `bg-${color}` : `bg-${Site.paper}`;
  const textColor = whiteText ? "text-white" : "text-gray-700";
  const padTop = spaceTop ? "pt-20" : "pt-4";
  const padBottom = spaceBottom ? "pb-20" : "pb-4";

  // Makes the gallery responsive to the screen size (mobile 'md' or desktop)
  const breakpoints:any = useBreakpoint();
  const responsiveCols:boolean = Array.isArray(columns) && columns.length > 1;
  const totalCols:number = responsiveCols ? ( breakpoints['md'] ? columns[1] : columns[0] ) : columns as number;

  const itemsCount = React.Children.count(children);
  const isSingle = itemsCount < 2;
  const cols = itemsCount / totalCols;
  const chunks = isSingle
    ? []
    : layout === "vertical"
    ? chunkArray(children, cols)
    : zipArray(chunkArray(children, React.Children.count(children) / cols));

  return (
    <div
      className={`comp_gallery flex w-screen justify-center self-stretch ${bgColor} ${textColor} ${className}`}
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
          {!isSingle && layout !== "horizontal" && 
            chunks.map((chs, k) => (
              <div className="flex-col flex-1" key={`group${k}`}>
                {chs.map((c:React.ReactNode, i:number) => (
                  <div
                    className={`p-1 ${layout==='grid' ? "aspect-[1/1]" : "aspect-auto"}`}
                    key={`img${i}`}
                  >
                    {c}
                  </div>
                ))}
              </div>
            ))}

          {!isSingle && layout === "horizontal" && 
            <div>
              {React.Children.map(children, (c:React.ReactNode, i:number) => (
                <div className="inline-block mr-2" key={`img${i}`}>{c}</div>
              ))}
            </div>
          }
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
