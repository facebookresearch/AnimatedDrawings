import { getBasePath } from "../lib/paths";

export type VideoProps = {
  url?: string;
  youtubeId?: string;
  aspectRatio?: "wide" | "square" | "normal" | "fill";
  controls?: boolean;
  autoPlay?: boolean;
  loop?: boolean;
  muted?: boolean;
  poster?: string;
  alt?: string;
  style?: React.CSSProperties;
  className?: string;
};

export default function Video({
  url,
  youtubeId,
  aspectRatio = "wide",
  controls = true,
  autoPlay = false,
  loop = true,
  muted = true,
  poster,
  alt = "",
  style,
  className
}: VideoProps) {
  let aspect =
    aspectRatio === "wide"
      ? `aspect-w-16 aspect-h-9`
      : aspectRatio === "square"
      ? "aspect-w-9 aspect-h-9"
      : "aspect-w-4 aspect-h-3";

  let videoSize = "";

  if (aspectRatio === "fill") {
    aspect = "absolute object-cover right-0 bottom-0 min-w-full min-h-full h-full";
    videoSize = "w-full h-full object-cover object-center";
  }
  

  return youtubeId ? (
    <div className={`comp_video w-full ${aspect} ${className}`} style={style}>
      <iframe
        src={`https://www.youtube.com/embed/${youtubeId}?&autoplay=${
          autoPlay ? 1 : 0
        }&controls=${controls ? 1 : 0}&mute=${muted}`}
        frameBorder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
        title={alt}
      />
    </div>
  ) : (
    <div className={`comp_video w-full ${aspect}`} style={style}>
      <video
        controls={controls}
        autoPlay={autoPlay}
        loop={loop}
        muted={muted}
        title={alt}
        poster={poster}
        className={`m-0 ${videoSize}`}
      >
        <source src={getBasePath(url)} type="video/mp4" />
        Sorry, your browser doesn't support embedded videos.
      </video>
    </div>
  );
}
