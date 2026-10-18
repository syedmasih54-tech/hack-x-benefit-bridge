import React from "react"

interface WordmarkProps {
  colorClass: string
  containerClassName?: string
  charClassName?: string
}

export const Wordmark: React.FC<WordmarkProps> = ({
  colorClass,
  containerClassName = "",
  charClassName = "wordmark-char",
}) => {
  const line1 = ["B", "E", "N", "E", "F", "I", "T"]
  const line2 = ["B", "R", "I", "D", "G", "E"]

  return (
    <div
      className={`w-full select-none text-center font-wordmark uppercase tracking-tight leading-[0.85] ${colorClass} ${containerClassName}`}
      aria-label="BenefitBridge"
    >
      {/* Line 1: BENEFIT */}
      <div className="flex justify-between items-center w-full max-w-6xl mx-auto px-4 sm:px-8 text-[clamp(2.75rem,11.2vw,8.5rem)]">
        {line1.map((char, index) => (
          <span
            key={`l1-${index}`}
            className="overflow-hidden inline-block leading-none py-1"
          >
            <span
              className={`${charClassName} inline-block will-change-transform`}
            >
              {char}
            </span>
          </span>
        ))}
      </div>

      {/* Line 2: BRIDGE */}
      <div className="flex justify-between items-center w-full max-w-6xl mx-auto px-4 sm:px-8 text-[clamp(2.75rem,11.2vw,8.5rem)] mt-1 sm:mt-2">
        {line2.map((char, index) => (
          <span
            key={`l2-${index}`}
            className="overflow-hidden inline-block leading-none py-1"
          >
            <span
              className={`${charClassName} inline-block will-change-transform`}
            >
              {char}
            </span>
          </span>
        ))}
      </div>
    </div>
  )
}

export default Wordmark
