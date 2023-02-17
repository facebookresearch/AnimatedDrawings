import { getBasePath } from "../lib/paths";

export type ImageProps = {
  url: string;
  caption?: string;
  contain?: boolean;
  style?: React.CSSProperties;
  showCaption?: boolean;
};

export default function Image({ url, caption, contain, style, showCaption }:ImageProps) {
  const resize = contain ? "object-contain" : "object-cover w-full h-full";
  return (
    <div className="relative">
      <img
        src={getBasePath(url)}
        alt={caption}
        className={`comp_image ${resize} m-0`}
        style={style}
      />
      {caption && showCaption && (
        <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs p-3 md:p-4">
          {caption}
        </div>
      )}
    </div>
  );
}
