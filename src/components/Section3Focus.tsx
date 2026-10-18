import React, { useEffect, useRef } from "react"
import gsap from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"

gsap.registerPlugin(ScrollTrigger)

export const Section3Focus: React.FC = () => {
  const sectionRef = useRef<HTMLElement | null>(null)
  const pinContainerRef = useRef<HTMLDivElement | null>(null)
  const redBgRef = useRef<HTMLDivElement | null>(null)
  const redGlowRef = useRef<HTMLDivElement | null>(null)
  const textRef = useRef<HTMLHeadingElement | null>(null)

  const words = [
    { text: "We", isItalic: false },
    { text: "keep", isItalic: false },
    { text: "our", isItalic: false },
    { text: "focus", isItalic: false },
    { text: "on", isItalic: false },
    { text: "the", isItalic: true },
    { text: "last", isItalic: true },
    { text: "mile", isItalic: true },
  ]

  useEffect(() => {
    const prefersReducedMotion =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches

    const wordElements = textRef.current?.querySelectorAll(".focus-word")

    if (prefersReducedMotion) {
      if (wordElements) {
        gsap.set(wordElements, { opacity: 1, filter: "blur(0px)" })
      }
      if (redBgRef.current) {
        gsap.set(redBgRef.current, { opacity: 1 })
      }
      if (redGlowRef.current) {
        gsap.set(redGlowRef.current, { opacity: 1, scaleY: 1 })
      }
      return
    }

    const ctx = gsap.context(() => {
      // Create master scrub timeline pinned for 150vh
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top top",
          end: "+=150%",
          pin: pinContainerRef.current,
          scrub: 0.9,
          anticipatePin: 1,
        },
      })

      // 1. Clean white & soft rose gradient fades in
      tl.fromTo(
        redBgRef.current,
        { opacity: 0 },
        { opacity: 1, duration: 0.35, ease: "power2.out" },
        0,
      )

      // 2. Soft red glow rises from bottom edge via scaleY & opacity
      tl.fromTo(
        redGlowRef.current,
        {
          opacity: 0.2,
          scaleY: 0.2,
          transformOrigin: "bottom center",
        },
        {
          opacity: 1,
          scaleY: 1.15,
          duration: 0.5,
          ease: "power2.out",
        },
        0.05,
      )

      // 3. Split words animate: opacity 0.15 -> 1 and blur 8px -> 0
      if (wordElements && wordElements.length > 0) {
        tl.fromTo(
          wordElements,
          {
            opacity: 0.15,
            filter: "blur(8px)",
          },
          {
            opacity: 1,
            filter: "blur(0px)",
            stagger: 0.09,
            duration: 0.45,
            ease: "power2.out",
          },
          0.1,
        )
      }
    }, sectionRef)

    return () => {
      ctx.revert()
    }
  }, [])

  return (
    <section
      ref={sectionRef}
      className="relative w-full h-[250vh] bg-white overflow-hidden"
      aria-label="Section 3: Focus on the last mile"
    >
      {/* ---------------- PINNED VIEWPORT CONTAINER ---------------- */}
      <div
        ref={pinContainerRef}
        className="w-full h-screen relative flex items-center justify-center overflow-hidden bg-white"
      >
        {/* 1. CLEAN WHITE TO SOFT RED GRADIENT LAYER */}
        <div
          ref={redBgRef}
          className="absolute inset-0 w-full h-full pointer-events-none will-change-transform"
          style={{
            background:
              "linear-gradient(180deg, #FFFFFF 0%, #FFF5F5 35%, #FEE2E2 100%)",
          }}
          aria-hidden="true"
        />

        {/* 2. SOFT RED GLOW RISING FROM BOTTOM EDGE */}
        <div
          ref={redGlowRef}
          className="absolute inset-x-0 bottom-0 h-[65vh] pointer-events-none will-change-transform"
          style={{
            background:
              "radial-gradient(ellipse 110% 85% at 50% 100%, #FECACA 0%, rgba(254, 226, 226, 0.55) 45%, rgba(255, 255, 255, 0) 80%)",
          }}
          aria-hidden="true"
        />

        {/* Subtle decorative micro indicators in red and white */}
        <div className="absolute top-8 left-0 right-0 max-w-7xl mx-auto px-6 sm:px-12 flex items-center justify-between text-[11px] font-sans text-[#1A0F12]/70 z-10 pointer-events-none">
          <span className="bg-white/80 backdrop-blur-xs px-3 py-1 rounded-full border border-[#C41528]/25 text-[#8E1B2B] font-medium">
            Civic charter focus
          </span>
          <span className="font-mono text-[10px] text-[#C41528]/80 font-semibold">
            SEC. 03 // RESOLUTION
          </span>
        </div>

        {/* ---------------- 3. CENTERED WORD-BY-WORD SCRUBBED HEADLINE ---------------- */}
        <div className="relative z-10 max-w-5xl mx-auto px-6 sm:px-12 text-center select-none">
          <h2
            ref={textRef}
            className="text-[clamp(2.4rem,5.6vw,4.25rem)] leading-[1.18] tracking-tight"
            aria-label="We keep our focus on the last mile"
          >
            {words.map((item, index) => (
              <span
                key={index}
                className={`focus-word inline-block mx-[0.14em] will-change-[opacity,filter] ${
                  item.isItalic
                    ? "font-serif-italic italic font-normal text-[#C41528]"
                    : "font-sans font-light text-[#1A0F12]"
                }`}
              >
                {item.text}
              </span>
            ))}
          </h2>

          {/* Micro subline below */}
          <p className="mt-6 text-xs sm:text-sm font-light text-[#1A0F12]/75 max-w-lg mx-auto tracking-normal">
            Where applications stall, names get misspelled, and rights go
            unclaimed.
          </p>
        </div>
      </div>
    </section>
  )
}

export default Section3Focus
