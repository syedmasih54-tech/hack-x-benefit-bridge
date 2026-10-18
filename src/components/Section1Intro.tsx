import React, { useEffect, useRef, useState } from "react"
import gsap from "gsap"
import Wordmark from "./Wordmark"

interface Section1IntroProps {
  onComplete: () => void
  underneathWordmarkRef?: React.RefObject<HTMLDivElement | null>
}

export const Section1Intro: React.FC<Section1IntroProps> = ({
  onComplete,
  underneathWordmarkRef,
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const redLayerRef = useRef<HTMLDivElement | null>(null)
  const dashRef = useRef<HTMLDivElement | null>(null)
  const whiteBandRef = useRef<HTMLDivElement | null>(null)
  const middleLineRef = useRef<HTMLDivElement | null>(null)
  const dotsRef = useRef<HTMLDivElement | null>(null)
  const wordmarkWrapRef = useRef<HTMLDivElement | null>(null)

  const [hasCompleted, setHasCompleted] = useState<boolean>(false)
  const timelineRef = useRef<gsap.core.Timeline | null>(null)

  // Check if session has seen intro or user prefers reduced motion
  const [hasSeenSession] = useState<boolean>(() => {
    if (typeof window === "undefined") return false
    return sessionStorage.getItem("bb_intro_seen") === "true"
  })

  const finishIntro = () => {
    setHasCompleted(true)
    if (typeof window !== "undefined") {
      sessionStorage.setItem("bb_intro_seen", "true")
    }
    onComplete()
  }

  const handleSkip = () => {
    if (timelineRef.current) {
      // Jump to end smoothly
      timelineRef.current.progress(1)
    } else {
      finishIntro()
    }
  }

  useEffect(() => {
    if (hasCompleted) return

    // Respect prefers-reduced-motion
    if (
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {
      finishIntro()
      return
    }

    const ctx = gsap.context(
      () => {
        const redLetters = wordmarkWrapRef.current?.querySelectorAll(
          ".intro-overlay-char",
        )
        const underLetters =
          underneathWordmarkRef?.current?.querySelectorAll(".underneath-char")

        const tl = gsap.timeline({
          onComplete: () => {
            finishIntro()
          },
        })
        timelineRef.current = tl

        // Initial state
        gsap.set(redLayerRef.current, {
          clipPath: "inset(0% 0% 0% 0%)",
          opacity: 1,
        })
        gsap.set(dashRef.current, { opacity: 0, scaleX: 0 })
        gsap.set(whiteBandRef.current, { height: 0, opacity: 1 })
        gsap.set([middleLineRef.current, dotsRef.current], { opacity: 0 })

        if (redLetters && redLetters.length > 0) {
          gsap.set(redLetters, { y: "-115%" })
        }
        if (underLetters && underLetters.length > 0) {
          gsap.set(underLetters, { y: "-115%" })
        }

        // Step 1: Tiny white dash appears at top center (0.1s)
        tl.to(
          dashRef.current,
          {
            opacity: 1,
            scaleX: 1,
            duration: 0.35,
            ease: "power2.out",
          },
          0.1,
        )

        // Step 2: Letters slide down letter by letter (0.2s - 1.4s)
        // Stagger: 0.05s, 1s each, ease: expo.out
        if (redLetters && redLetters.length > 0) {
          tl.to(
            redLetters,
            {
              y: "0%",
              duration: 1.0,
              stagger: 0.05,
              ease: "expo.out",
            },
            0.2,
          )
        }

        if (underLetters && underLetters.length > 0) {
          tl.to(
            underLetters,
            {
              y: "0%",
              duration: 1.0,
              stagger: 0.05,
              ease: "expo.out",
            },
            0.2,
          )
        }

        // Middle line & dots reveal smoothly
        tl.to(
          [middleLineRef.current, dotsRef.current],
          {
            opacity: 1,
            duration: 0.5,
            ease: "power2.out",
          },
          0.5,
        )

        // Step 3: After about 2s, the line grows into a white band (height 0 to 45vh)
        tl.to(
          whiteBandRef.current,
          {
            height: "45vh",
            duration: 0.65,
            ease: "power3.inOut",
          },
          2.0,
        )

        // Step 4: Red layer wipes away from the center line outward using
        // clip-path inset(0 0 0 0) -> inset(50% 0 50% 0) (2.4s)
        tl.to(
          redLayerRef.current,
          {
            clipPath: "inset(50% 0% 50% 0%)",
            duration: 0.95,
            ease: "power4.inOut",
          },
          2.4,
        )

        // Fade out final container edge cleanly
        tl.to(
          redLayerRef.current,
          {
            opacity: 0,
            duration: 0.25,
            ease: "power1.out",
          },
          3.35,
        )
      },
      containerRef,
    )

    return () => {
      ctx.revert()
    }
  }, [hasCompleted])

  if (hasCompleted) return null

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-50 overflow-hidden pointer-events-auto"
      style={{ isolation: "isolate" }}
      aria-label="BenefitBridge preloader introduction"
    >
      {/* ---------------- RED FULL-SCREEN LAYER ---------------- */}
      <div
        ref={redLayerRef}
        className="absolute inset-0 w-full h-full bg-[#C41528] text-white flex flex-col justify-between select-none"
        style={{ clipPath: "inset(0% 0% 0% 0%)" }}
      >
        {/* 1. TOP BAR: Tiny white dash at top center & Skip Intro */}
        <header className="relative w-full max-w-7xl mx-auto px-6 sm:px-12 pt-6 flex items-center justify-between z-30">
          <div className="w-20">
            {hasSeenSession && (
              <span className="text-[10px] font-sans uppercase tracking-wider text-white/50 border border-white/20 px-2 py-0.5 rounded-full">
                Seen
              </span>
            )}
          </div>

          {/* Tiny white dash at top center */}
          <div
            ref={dashRef}
            className="w-8 h-[2.5px] bg-white rounded-full shadow-sm"
            aria-hidden="true"
          />

          {/* Skip Intro */}
          <div className="w-20 text-right">
            <button
              onClick={handleSkip}
              className="text-[11px] font-sans font-medium text-white/90 hover:text-white transition-all cursor-pointer border border-white/25 hover:border-white/60 px-3 py-1 rounded-full backdrop-blur-xs active:scale-95 inline-flex items-center gap-1"
              aria-label="Skip preloader animation"
            >
              <span>Skip intro</span>
              <span aria-hidden="true">→</span>
            </button>
          </div>
        </header>

        {/* 2. THE WORDMARK: BENEFIT OVER BRIDGE (White on red layer) */}
        <div
          ref={wordmarkWrapRef}
          className="relative w-full max-w-7xl mx-auto px-4 sm:px-8 pt-4 sm:pt-8 z-30"
        >
          <Wordmark
            colorClass="text-white"
            charClassName="intro-overlay-char"
          />
        </div>

        {/* 3. GROWING WHITE BAND (Height 0 to 45vh) */}
        <div
          ref={whiteBandRef}
          className="absolute top-1/2 left-0 right-0 -translate-y-1/2 w-full bg-white z-10 pointer-events-none"
          style={{ height: 0 }}
          aria-hidden="true"
        />

        {/* 4. 1PX WHITE HORIZONTAL LINE CROSSING MIDDLE */}
        <div
          ref={middleLineRef}
          className="absolute top-1/2 left-0 right-0 -translate-y-1/2 w-full z-20 pointer-events-none"
        >
          {/* Continuous thin 1px white line */}
          <div className="w-full h-[1px] bg-white/60" />

          {/* Overlay elements across the line */}
          <div className="w-full max-w-6xl mx-auto px-6 sm:px-12 flex items-center justify-between -translate-y-1/2 text-white text-[11px] font-medium font-sans">
            {/* Left end: tiny text "Open source" */}
            <div className="bg-[#C41528] px-2.5 py-0.5 rounded-full border border-white/30 backdrop-blur-xs flex items-center">
              <span>Open source</span>
            </div>

            {/* Center: small bridge-arch logo */}
            <div
              className="w-9 h-9 rounded-full bg-[#C41528] border border-white/70 flex items-center justify-center shadow-md -mt-0.5"
              aria-label="BenefitBridge emblem"
            >
              <svg
                className="w-5 h-5 text-white"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                {/* Clean Bridge Arch Graphic */}
                <path d="M3 18h18" />
                <path d="M4 18V9a8 8 0 0 1 16 0v9" />
                <path d="M9 18v-5a3 3 0 0 1 6 0v5" />
                <path d="M4 14h16" />
              </svg>
            </div>

            {/* Right end: tiny "Hindi-first" and three-dot menu */}
            <div className="bg-[#C41528] px-2.5 py-0.5 rounded-full border border-white/30 backdrop-blur-xs flex items-center gap-2">
              <span>Hindi-first</span>
              <span
                className="text-[14px] leading-none opacity-80"
                aria-hidden="true"
              >
                ⋯
              </span>
            </div>
          </div>
        </div>

        {/* 5. BOTTOM: ROW OF 5 SMALL DOTS (Active dot larger) */}
        <footer
          ref={dotsRef}
          className="relative w-full flex items-center justify-center gap-2 pb-8 sm:pb-12 z-30"
          aria-hidden="true"
        >
          {/* Active dot (larger) */}
          <span className="w-2.5 h-2.5 rounded-full bg-white shadow-sm ring-2 ring-white/30" />
          {/* 4 subtle companion dots */}
          <span className="w-1.5 h-1.5 rounded-full bg-white/60" />
          <span className="w-1.5 h-1.5 rounded-full bg-white/60" />
          <span className="w-1.5 h-1.5 rounded-full bg-white/60" />
          <span className="w-1.5 h-1.5 rounded-full bg-white/60" />
        </footer>
      </div>
    </div>
  )
}

export default Section1Intro
