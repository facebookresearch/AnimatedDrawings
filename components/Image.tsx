import { getBasePath } from "../lib/paths";

export type ImageProps = {
  url: string;
  caption?: string;
  captionType?: "default" | "overlay";
  showCaption?: boolean;
  contain?: boolean;
  style?: React.CSSProperties;
  className?: string;
};

export default function Image({ url, caption, captionType, showCaption, contain, style, className='' }:ImageProps) {
  const resize = contain ? "object-contain" : "object-cover w-full h-full";
  return (
    <div className="relative">
      <img
        src={getBasePath(url)}
        alt={caption}
        className={`comp_image ${resize} m-0 ${className}`}
        style={style}
      />
      {caption && showCaption && captionType === 'overlay' && (
        <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs p-2 md:p-2">
          {caption}
        </div>
      )}

      {caption && showCaption && captionType !== 'overlay' && (
        <div className="text-gray-600 text-xs mt-1 mb-3">
          {caption}
        </div>
      )}
    </div>
  );
}
