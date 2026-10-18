import React, { useEffect, useRef } from "react"
import gsap from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"
import Wordmark from "./Wordmark"
import { getPortalUrl } from "../lib/urls"

gsap.registerPlugin(ScrollTrigger)

interface Section2StatementProps {
  underneathWordmarkRef?: React.RefObject<HTMLDivElement | null>
}

export const Section2Statement: React.FC<Section2StatementProps> = ({
  underneathWordmarkRef,
}) => {
  const sectionRef = useRef<HTMLElement | null>(null)
  const headlineRef = useRef<HTMLDivElement | null>(null)
  const cardsContainerRef = useRef<HTMLDivElement | null>(null)

  const card1Ref = useRef<HTMLDivElement | null>(null)
  const card2Ref = useRef<HTMLDivElement | null>(null)
  const card3Ref = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    // Check reduced motion preference
    const prefersReducedMotion =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches

    const ctx = gsap.context(() => {
      // 1. Headline lines reveal upward with a mask
      const headlineLines =
        headlineRef.current?.querySelectorAll(".headline-line")

      if (headlineLines && headlineLines.length > 0) {
        if (prefersReducedMotion) {
          gsap.set(headlineLines, { yPercent: 0, opacity: 1 })
        } else {
          gsap.fromTo(headlineLines, { yPercent: 105 }, {
            yPercent: 0,
            stagger: 0.08,
            duration: 0.95,
            ease: "power3.out",
            scrollTrigger: {
              trigger: headlineRef.current,
              start: "top 85%",
              toggleActions: "play none none none",
            },
          })
        }
      }

      // 2. Three document cards rise with parallax scrub at different speeds
      if (
        !prefersReducedMotion &&
        card1Ref.current &&
        card2Ref.current &&
        card3Ref.current &&
        cardsContainerRef.current
      ) {
        const isMobile = window.innerWidth < 768

        // Card 1: Ration Card (Speed 1, slightly rotated -3deg)
        gsap.fromTo(
          card1Ref.current,
          {
            y: isMobile ? 30 : 70,
            rotate: isMobile ? 0 : -3,
          },
          {
            y: isMobile ? -10 : -45,
            rotate: isMobile ? 0 : -1,
            ease: "none",
            scrollTrigger: {
              trigger: cardsContainerRef.current,
              start: "top 95%",
              end: "bottom 15%",
              scrub: 1,
            },
          },
        )

        // Card 2: Bank Passbook (Speed 2 - faster scrub, rotated +2.5deg)
        gsap.fromTo(
          card2Ref.current,
          {
            y: isMobile ? 50 : 130,
            rotate: isMobile ? 0 : 2.5,
          },
          {
            y: isMobile ? -20 : -90,
            rotate: isMobile ? 0 : 0.8,
            ease: "none",
            scrollTrigger: {
              trigger: cardsContainerRef.current,
              start: "top 95%",
              end: "bottom 15%",
              scrub: 1.6,
            },
          },
        )

        // Card 3: Readiness 60% (Speed 3 - medium scrub, rotated -1.5deg)
        gsap.fromTo(
          card3Ref.current,
          {
            y: isMobile ? 40 : 100,
            rotate: isMobile ? 0 : -1.8,
          },
          {
            y: isMobile ? -15 : -65,
            rotate: isMobile ? 0 : -0.2,
            ease: "none",
            scrollTrigger: {
              trigger: cardsContainerRef.current,
              start: "top 95%",
              end: "bottom 15%",
              scrub: 1.25,
            },
          },
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
      className="w-full bg-[#FFFDF9] text-[#1A0F12] relative overflow-hidden"
      aria-label="BenefitBridge Statement & Document Verification"
    >
      {/* Ambient Glass UI Background Light Blobs */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-20 -left-32 w-80 h-80 rounded-full bg-red-100/40 blur-[120px]" />
        <div className="absolute top-1/2 -right-32 w-96 h-96 rounded-full bg-amber-100/35 blur-[130px]" />
        <div className="absolute bottom-10 left-1/4 w-80 h-80 rounded-full bg-rose-100/30 blur-[120px]" />
      </div>

      {/* ---------------- 1. TOP WORDMARK IN RED (#C41528) ---------------- */}
      <div
        ref={underneathWordmarkRef}
        className="relative w-full max-w-7xl mx-auto px-4 sm:px-8 pt-4 sm:pt-8 text-center z-10"
      >
        <Wordmark colorClass="text-[#C41528]" charClassName="underneath-char" />

        {/* BIG LIVE PORTAL BUTTON DIRECTLY BELOW BENEFIT BRIDGE */}
        <div className="mt-8 sm:mt-10 mb-2 flex justify-center items-center z-20">
          <a
            href={getPortalUrl()}
            className="min-h-[56px] sm:min-h-[64px] px-8 sm:px-14 py-4 rounded-2xl bg-[#C41528] hover:bg-[#8E1B2B] !text-white text-base sm:text-xl font-bold tracking-tight shadow-[0_16px_36px_rgba(196,21,40,0.28)] hover:shadow-[0_20px_48px_rgba(196,21,40,0.42)] hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-3.5 group cursor-pointer border border-[#C41528]"
          >
            <span className="w-3 h-3 rounded-full bg-white animate-pulse" />
            <span className="!text-white font-bold tracking-normal">
              Launch Citizen Welfare Portal
            </span>
            <span className="!text-white text-xl sm:text-2xl transition-transform group-hover:translate-x-1.5 font-bold">
              →
            </span>
          </a>
        </div>
      </div>

      {/* ---------------- 2. CAPTIONS BELOW WORDMARK ---------------- */}
      <div className="relative z-10 w-full max-w-7xl mx-auto px-6 sm:px-12 pt-4 pb-12 sm:pb-16 flex items-center justify-between border-b border-[#1A0F12]/15 text-[11px] sm:text-[12px] font-sans text-[#1A0F12]/75">
        <span className="tracking-normal font-normal">
          Welfare, made reachable
        </span>
        <span className="tracking-normal font-normal text-right">
          Voice-assisted case platform
        </span>
      </div>

      {/* ---------------- 3. RIGHT-ALIGNED HEADLINE IN DEEP RED ---------------- */}
      <div className="relative z-10 w-full max-w-7xl mx-auto px-6 sm:px-12 pt-16 sm:pt-24 pb-16">
        <div
          ref={headlineRef}
          className="text-right ml-auto max-w-4xl text-[#8E1B2B] text-[clamp(2.1rem,4.8vw,3.5rem)] font-light leading-[1.14] tracking-[-0.02em] select-none"
        >
          {/* Masked Line 1 */}
          <div className="overflow-hidden py-1">
            <div className="headline-line will-change-transform">
              {"Welfare isn't failing"}
            </div>
          </div>

          {/* Masked Line 2 */}
          <div className="overflow-hidden py-1">
            <div className="headline-line will-change-transform">
              for lack of money.
            </div>
          </div>

          {/* Masked Line 3 with Instrument Serif Italic */}
          <div className="overflow-hidden py-1">
            <div className="headline-line will-change-transform">
              {"It's failing at the"}{" "}
              <i className="font-serif-italic font-normal italic text-[#C41528] tracking-normal inline-block ml-1">
                last mile of paperwork.
              </i>
            </div>
          </div>
        </div>
      </div>

      {/* ---------------- 4. THREE FLOATING PARALLAX GLASS DOCUMENT CARDS ---------------- */}
      <div
        ref={cardsContainerRef}
        className="relative z-10 w-full max-w-7xl mx-auto px-6 sm:px-12 pt-8 pb-28 sm:pb-36"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 items-start">
          {/* CARD 1: Ration Card (NFSA) - Floating Glass Card */}
          <div
            ref={card1Ref}
            className="w-full bg-white/75 backdrop-blur-xl rounded-3xl border border-white/90 p-6 sm:p-7 shadow-[0_16px_40px_rgba(26,15,18,0.06)] hover:shadow-[0_24px_55px_rgba(196,21,40,0.16)] hover:border-[#C41528]/50 transition-all flex flex-col justify-between min-h-[390px] will-change-transform relative overflow-hidden group animate-glass-float-1"
          >
            <div className="absolute -top-12 -right-12 w-32 h-32 rounded-full bg-red-100/50 blur-2xl pointer-events-none group-hover:scale-125 transition-transform" />
            <div>
              {/* Card Header & Issuer Stamp */}
              <div className="flex items-center justify-between pb-4 border-b border-[#1A0F12]/10 mb-5">
                <div>
                  <span className="text-[10px] font-sans font-semibold tracking-wider text-[#C41528] uppercase block">
                    Govt of NCT Delhi • Food Dept
                  </span>
                  <h4 className="text-sm font-bold text-[#1A0F12] tracking-tight">
                    Ration Card (NFSA)
                  </h4>
                </div>
                <div className="w-8 h-8 rounded-full bg-white/90 border border-[#1A0F12]/15 flex items-center justify-center text-[10px] font-mono text-[#8E1B2B] shadow-xs">
                  PHH
                </div>
              </div>

              {/* Beneficiary Details */}
              <div className="space-y-3 text-xs">
                <div>
                  <span className="text-[10px] text-[#1A0F12]/50 block">
                    Head of Household
                  </span>
                  <p className="font-semibold text-sm text-[#1A0F12]">
                    Sunita Devi
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-1">
                  <div>
                    <span className="text-[10px] text-[#1A0F12]/50 block">
                      Card Number
                    </span>
                    <span className="font-mono text-xs text-[#1A0F12]">
                      0710 •••• 4912
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-[#1A0F12]/50 block">
                      Family Members
                    </span>
                    <span className="font-semibold text-xs text-[#1A0F12]">
                      03 Units
                    </span>
                  </div>
                </div>

                <div className="pt-2">
                  <span className="text-[10px] text-[#1A0F12]/50 block">
                    FPS Shop ID
                  </span>
                  <span className="font-mono text-xs text-[#1A0F12]/75">
                    FPS-DL-CENTRAL-094
                  </span>
                </div>
              </div>
            </div>

            {/* Bottom Authenticity Strip */}
            <div className="pt-5 border-t border-[#1A0F12]/10 flex items-center justify-between text-[11px] text-[#1A0F12]/60">
              <span className="inline-flex items-center gap-1.5 font-medium text-[#8E1B2B]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#C41528]" />
                NFSA Direct Verified
              </span>
              <span className="font-mono text-[10px]">VER: 2026.04</span>
            </div>
          </div>

          {/* CARD 2: Bank Passbook with Spelling Variance Flag - Floating Glass Card */}
          <div
            ref={card2Ref}
            className="w-full bg-white/75 backdrop-blur-xl rounded-3xl border border-white/90 p-6 sm:p-7 shadow-[0_16px_40px_rgba(26,15,18,0.06)] hover:shadow-[0_24px_55px_rgba(196,21,40,0.16)] hover:border-[#C41528]/50 transition-all flex flex-col justify-between min-h-[390px] will-change-transform relative overflow-hidden group animate-glass-float-2"
          >
            <div className="absolute -top-12 -right-12 w-32 h-32 rounded-full bg-amber-100/50 blur-2xl pointer-events-none group-hover:scale-125 transition-transform" />
            <div>
              {/* Bank Header */}
              <div className="flex items-center justify-between pb-4 border-b border-[#1A0F12]/10 mb-5">
                <div>
                  <span className="text-[10px] font-sans font-semibold tracking-wider text-[#8E1B2B] uppercase block">
                    State Bank of India • Savings
                  </span>
                  <h4 className="text-sm font-bold text-[#1A0F12] tracking-tight">
                    Primary Savings Passbook
                  </h4>
                </div>
                <div className="w-8 h-8 rounded-full bg-white/90 border border-[#8E1B2B]/20 flex items-center justify-center text-[#8E1B2B] shadow-xs">
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
                    />
                  </svg>
                </div>
              </div>

              {/* Account Data & Discrepancy Highlight */}
              <div className="space-y-3 text-xs">
                <div>
                  <span className="text-[10px] text-[#1A0F12]/50 block">
                    Account Name (Passbook)
                  </span>
                  <p className="font-semibold text-sm text-[#1A0F12]">
                    Sunitha Devi
                  </p>
                </div>

                {/* Soft Document Doctor Callout */}
                <div className="p-2.5 rounded-xl bg-white/80 border border-[#C41528]/25 text-[11px] text-[#8E1B2B] space-y-0.5 shadow-xs">
                  <div className="font-semibold flex items-center gap-1">
                    <span>⚠ Phonetic Spelling Variation</span>
                  </div>
                  <p className="text-[10px] text-[#8E1B2B]/85 leading-relaxed font-light">
                    {"\"Sunitha\" vs \"Sunita\" on Ration Card. Correcting now guarantees immediate Direct Benefit Transfer (DBT)."}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-1">
                  <div>
                    <span className="text-[10px] text-[#1A0F12]/50 block">
                      Account No
                    </span>
                    <span className="font-mono text-xs text-[#1A0F12]">
                      •••• •••• 0981
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-[#1A0F12]/50 block">
                      IFSC Code
                    </span>
                    <span className="font-mono text-xs text-[#1A0F12]">
                      SBIN0001234
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom Status */}
            <div className="pt-5 border-t border-[#1A0F12]/10 flex items-center justify-between text-[11px] text-[#1A0F12]/60">
              <span className="inline-flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#EAB308]" />
                DBT Ready with Confirmation
              </span>
              <span className="font-mono text-[10px]">NPCI Seeded</span>
            </div>
          </div>

          {/* CARD 3: Citizen Readiness 60% - Floating Glass Card */}
          <div
            ref={card3Ref}
            className="w-full bg-white/75 backdrop-blur-xl rounded-3xl border border-white/90 p-6 sm:p-7 shadow-[0_16px_40px_rgba(26,15,18,0.06)] hover:shadow-[0_24px_55px_rgba(196,21,40,0.16)] hover:border-[#C41528]/50 transition-all flex flex-col justify-between min-h-[390px] will-change-transform relative overflow-hidden group animate-glass-float-3"
          >
            <div className="absolute -top-12 -right-12 w-32 h-32 rounded-full bg-rose-100/50 blur-2xl pointer-events-none group-hover:scale-125 transition-transform" />
            <div>
              {/* Readiness Header */}
              <div className="flex items-center justify-between pb-4 border-b border-[#1A0F12]/10 mb-5">
                <div>
                  <span className="text-[10px] font-sans font-semibold tracking-wider text-[#C41528] uppercase block">
                    NSAP Citizen Charter
                  </span>
                  <h4 className="text-sm font-bold text-[#1A0F12] tracking-tight">
                    IGNWPS Readiness Index
                  </h4>
                </div>
                <div className="px-2.5 py-1 rounded-full bg-[#C41528]/10 text-[#C41528] text-xs font-mono font-bold">
                  60%
                </div>
              </div>

              {/* Progress & Checklist */}
              <div className="space-y-3.5 text-xs">
                {/* 60% Bar */}
                <div>
                  <div className="flex justify-between text-[11px] text-[#1A0F12]/65 mb-1.5">
                    <span>Application Completeness</span>
                    <span className="font-mono font-semibold text-[#1A0F12]">
                      3 of 5 Verified
                    </span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-[#1A0F12]/10 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-[#C41528] to-[#8E1B2B] rounded-full"
                      style={{ width: "60%" }}
                    />
                  </div>
                </div>

                {/* Micro Checklist */}
                <ul className="space-y-2 pt-1 text-[11px]">
                  <li className="flex items-center gap-2 text-[#C41528]">
                    <span>✓</span>
                    <span className="text-[#1A0F12]">
                      Age verified (65 years ≥ 40 threshold)
                    </span>
                  </li>
                  <li className="flex items-center gap-2 text-[#C41528]">
                    <span>✓</span>
                    <span className="text-[#1A0F12]">
                      NFSA BPL Ration status matched
                    </span>
                  </li>
                  <li className="flex items-center gap-2 text-[#8E1B2B]">
                    <span>⚠</span>
                    <span className="text-[#1A0F12]">
                      Passbook name variance to confirm
                    </span>
                  </li>
                  <li className="flex items-center gap-2 text-[#1A0F12]/40">
                    <span>○</span>
                    <span>Self-declaration income statement pending</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Bottom Statutory SLA Guarantee */}
            <div className="pt-5 border-t border-[#1A0F12]/10 flex items-center justify-between text-[11px] text-[#1A0F12]/60">
              <span className="inline-flex items-center gap-1.5 font-medium text-[#8E1B2B]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#C41528]" />
                30-Day Mandatory SLA
              </span>
              <span className="font-mono text-[10px]">Sec. 4 Charters</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Section2Statement
