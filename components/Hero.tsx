const Site = require("../site.json");
import { getBasePath } from "../lib/paths";
import Video from "./Video";
import Image from "./Image";
import FeatureSummary from "./FeatureSummary";

export type HeroLayout = "default" | "vertical";

export type HeroProps = {
  layout?: HeroLayout;
  image?: string;
  video?: string;
  overlay?: boolean;
  bgColor?: string;
  fullHeight?: boolean;
  style?: React.CSSProperties;
  children: React.ReactNode;
  className?: string;
};

export default function Hero({
  layout,
  image,
  video,
  overlay,
  fullHeight,
  bgColor,
  style = {},
  children,
  className = ''
}: HeroProps) {

  const bg = bgColor ? `bg-${bgColor}` : `bg-${Site.theme}-${Site.shade}`;
  const split = (image || video) && !overlay;

  const height = fullHeight ? `h-[calc(100vh-64px)] ${ split || overlay ? "" : "md:min-h-[1000px]" }` : "";

  const contentFlow = layout === "vertical" ? "flex-col" : `flex-col-reverse lg:flex-row`;
  const contentMargin = `${fullHeight ? "my-0" : ""} ${split ? 'mt-0 mb-10 px-6 lg:px-0' : 'px-0 my-20'}`;

  const contentAlign = `${ fullHeight ? `${ split ? "justify-start-only" : "justify-center" }` : 'justify-center'} lg:justify-start`;
  const summaryMargin = layout === "vertical" ? "mt-20" : (split ? "lg:my-[140px]" : "lg:my-20");
  const imageW = layout === 'vertical' ?    "md:w-[70vw] md:max-w-[850px] w-full px-0" : "w-[100vw] lg:w-full p-0 lg:p-4";
  const imageH = layout === 'vertical' ? "md:h-[39vw] md:max-h-[478px] h-[40vh] mb-20" : "h-[100vw] max-h-[500px] lg:h-[500px]";
  // const imageSize = layout === 'vertical' ? "md:w-[70vw] md:max-w-[850px] w-full px-0 md:h-[39vw] md:max-h-[478px] mb-20" : "w-[100vw] lg:w-full h-[100vw] max-h-[500px] lg:h-[500px] p-0 lg:p-4";
  const equalSize = layout === 'vertical' ? "" : `${ split ? "lg:flex-1" : "lg:w-[50%]" }`;

  const imageOverlay = overlay ? "bg-cover bg-center bg-no-repeat" : "";

  const containerStyle = {
    backgroundImage: (overlay && image && !video) ? `url(${getBasePath(image)})` : false,
    ...style
  }


  return (
    <div
      className={`relative flex flex-col w-screen justify-center items-center ${bg} ${imageOverlay} ${height} px-10 xl:px-0 ${className}`}
      //style={containerStyle}
    >
      { overlay && video &&
        <div className="absolute inset-0 z-0 overflow-hidden">
          <Video url={video} autoPlay loop muted poster={image || undefined} controls={false} aspectRatio="fill" />
          <div className="absolute inset-0 bg-pink-300 opacity-80" />
        </div>
      }

      <div className={`relative z-1 flex ${contentFlow} gap-10 h-full lg:w-full max-w-screen-xl ${contentAlign} items-center `}>        
        <div className={`md:w-[50%] lg:ml-8 ${equalSize} ${contentMargin} ${summaryMargin}`}>
          {children}
        </div>

        {split &&
          <div className={`flex ${imageW} ${imageH} ${equalSize} items-center relative`}>
            { image && !video && 
              <div 
                style={{backgroundImage: `url(${getBasePath(image)})`}} 
                className="h-full w-full bg-cover bg-center bg-no-repeat"
              />
            }

            { video &&
              <Video url={video} autoPlay loop muted poster={image || undefined} controls={false} aspectRatio="fill" />
            }
          </div>
        }


      </div>
    </div>
  );
}
