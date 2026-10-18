import React, { useEffect, useRef } from "react"
import gsap from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"

gsap.registerPlugin(ScrollTrigger)

export const Section5WhoDecides: React.FC = () => {
  const sectionRef = useRef<HTMLElement | null>(null)
  const linesContainerRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const prefersReducedMotion =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches

    const lineElements =
      linesContainerRef.current?.querySelectorAll(".who-line")

    if (prefersReducedMotion) {
      if (lineElements) {
        gsap.set(lineElements, { yPercent: 0, opacity: 1 })
      }
      return
    }

    const ctx = gsap.context(() => {
      if (lineElements && lineElements.length > 0) {
        gsap.fromTo(lineElements, { yPercent: 110 }, {
          yPercent: 0,
          stagger: 0.12,
          duration: 0.95,
          ease: "power3.out",
          scrollTrigger: {
            trigger: linesContainerRef.current,
            start: "top 80%",
            toggleActions: "play none none none",
          },
        })
      }
    }, sectionRef)

    return () => {
      ctx.revert()
    }
  }, [])

  return (
    <section
      ref={sectionRef}
      className="w-full bg-[#C41528] text-white py-28 sm:py-44 px-6 sm:px-12 relative overflow-hidden"
      aria-label="Section 5: Who Decides"
    >
      <div className="w-full max-w-7xl mx-auto flex flex-col justify-center">
        {/* Micro Category Pill */}
        <div className="mb-8 sm:mb-12">
          <span className="inline-block text-[11px] font-sans tracking-widest uppercase text-white/80 border border-white/25 px-3.5 py-1 rounded-full backdrop-blur-xs">
            Constitutional Governance
          </span>
        </div>

        {/* ---------------- THREE HUGE WHITE LINES (MASKED REVEAL) ---------------- */}
        <div
          ref={linesContainerRef}
          className="text-white text-[clamp(2.4rem,6.2vw,5.5rem)] font-light leading-[1.08] tracking-[-0.03em] space-y-2 sm:space-y-4 select-none"
        >
          {/* Line 1 */}
          <div className="overflow-hidden py-1">
            <div className="who-line will-change-transform">
              Rules decide eligibility.
            </div>
          </div>

          {/* Line 2 */}
          <div className="overflow-hidden py-1">
            <div className="who-line will-change-transform">
              Citizens confirm the facts.
            </div>
          </div>

          {/* Line 3 with Instrument Serif Italic */}
          <div className="overflow-hidden py-1">
            <div className="who-line will-change-transform">
              AI only{" "}
              <i className="font-serif-italic font-normal italic text-white">
                explains and drafts.
              </i>
            </div>
          </div>
        </div>

        {/* Bottom Editorial Footnote Line */}
        <div className="mt-16 sm:mt-24 pt-8 border-t border-white/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-[11px] font-sans text-white/70">
          <span>No automated rejection. Zero black-box decisions.</span>
          <span className="font-mono text-white/50 text-[10px]">
            PUBLIC TRUST ARCHITECTURE • VER 2.4
          </span>
        </div>
      </div>
    </section>
  )
}

export default Section5WhoDecides
