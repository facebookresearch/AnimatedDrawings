import { getTextColors } from "../lib/metaTheme";

export type FeatureSummaryProps = {
  label?: string;
  action?: string;
  actionUrl?: string;
  darkMode?: boolean;
  centerAlign?: boolean;
  small?: boolean;
  style?: React.CSSProperties;
  children: React.ReactNode;
  className?: string;
};

export default function FeatureSummary({
  label,
  action,
  actionUrl,
  darkMode,
  centerAlign,
  small,
  style,
  children,
  className,
}: FeatureSummaryProps) {
  const { primary, secondary } = getTextColors(darkMode);
  const uiColor = darkMode ? "bg-gray-800" : "bg-white";

  return (
    <div className={`${darkMode ? 'dark-mode' : ''} ${centerAlign ? 'text-center' : 'text-left'}`}>
      {label && (small 
        ? <p className={`${secondary} mb-0`}>{label}</p> 
        : <h6 className={`${secondary} mb-2`}>{label}</h6>
      )}
      
      <div>{children}</div>

      <div className={`flex flex-col ${centerAlign ? 'items-center' : 'items-start'}`}>
        {/* This button should be refactored as its own component */}
        {actionUrl && action && (
          <a
            href={actionUrl}
            className="group flex gap-2 items-center no-underline py-2 mt-4"
          >
            <button className={`btn btn-circle btn-outline btn-xs ${ darkMode ? 'border-white group-hover:border-blue-200' : 'border-gray-600 group-hover:border-primary' }  group-hover:bg-transparent group`}>
              <svg
                width="10"
                height="8"
                viewBox="0 0 10 8"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  className={`${ darkMode ? 'fill-white group-hover:fill-blue-200' : 'fill-gray-600 group-hover:fill-primary' }`}
                  d="M6.32142 0L10 4L6.32142 8L5.67114 7.30677L8.25215 4.5L0 4.5V3.5L8.23964 3.5L5.67114 0.707107L6.32142 0Z"
                  fill="#1C2B33"
                />
              </svg>
            </button>
            <span className={`font-bold ${primary} ${darkMode ? 'group-hover:text-blue-200' : 'group-hover:text-primary'}`}>
              {action}
            </span>
          </a>
        )}
      </div>
    </div>
  );
}
