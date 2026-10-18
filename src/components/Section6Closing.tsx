import React from "react"
import { getPortalUrl } from "../lib/urls"

export const Section6Closing: React.FC = () => {
  return (
    <footer
      className="w-full bg-white text-[#1A0F12] pt-24 sm:pt-36 overflow-hidden relative"
      aria-label="Section 6: Closing & Call to Action"
    >
      {/* ---------------- 1. SHORT LINE & RED "TRY THE DEMO" BUTTON ---------------- */}
      <div className="w-full max-w-7xl mx-auto px-6 sm:px-12 text-center space-y-8 mb-24 sm:mb-32">
        <div className="max-w-2xl mx-auto space-y-3">
          <span className="text-[11px] font-mono uppercase tracking-widest text-[#8E1B2B] block">
            Civic Public Infrastructure
          </span>
          <p className="text-xl sm:text-2xl font-light text-[#1A0F12] leading-snug">
            Open source. Self-hostable by NGOs, panchayats and service centres.
          </p>
        </div>

        {/* Red CTA Button (At least 44px tall, accessible focus ring) */}
        <div>
          <a
            href={getPortalUrl()}
            className="min-h-[48px] px-8 py-3.5 rounded-2xl bg-[#C41528] hover:bg-[#8E1B2B] text-white text-sm font-semibold tracking-wide transition-all shadow-[0_12px_28px_rgba(196,21,40,0.25)] hover:shadow-[0_16px_36px_rgba(196,21,40,0.35)] active:scale-[0.98] inline-flex items-center gap-2 cursor-pointer"
          >
            <span>Try the demo</span>
            <span aria-hidden="true" className="text-base font-bold">
              →
            </span>
          </a>
        </div>
      </div>

      {/* ---------------- 2. THIN LINE AND TINY FOOTER TEXT ---------------- */}
      <div className="w-full max-w-7xl mx-auto px-6 sm:px-12 border-t border-[#1A0F12]/15 pt-6 pb-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] sm:text-[12px] font-sans text-[#1A0F12]/70">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-[#8E1B2B]">BenefitBridge</span>
            <span className="text-[#1A0F12]/30">/</span>
            <span>Citizen Welfare Navigator</span>
          </div>

          <div className="flex items-center gap-6">
            <span>DigiLocker • API Setu • Citizen Charter DPI Ready</span>
          </div>

          <div className="text-right text-[#1A0F12]/50 text-[10px] font-mono">
            OPEN SOURCE CIVIC GOOD • APACHE 2.0
          </div>
        </div>
      </div>

      {/* ---------------- 3. GIANT RED WORDMARK CROPPED BY VIEWPORT EDGE ---------------- */}
      {/* Mirrors the intro: BENEFIT over BRIDGE spanning full width in heavy stencil font */}
      <div
        className="w-full overflow-hidden select-none translate-y-[12%] pointer-events-none"
        aria-hidden="true"
      >
        <div className="w-full text-center font-wordmark uppercase tracking-tight leading-[0.78] text-[#C41528]">
          {/* Line 1: BENEFIT */}
          <div className="flex justify-between items-center w-full max-w-7xl mx-auto px-2 sm:px-6 text-[clamp(3.8rem,14.5vw,11.5rem)] opacity-95">
            {["B", "E", "N", "E", "F", "I", "T"].map((c, i) => (
              <span key={`cb-${i}`} className="inline-block">
                {c}
              </span>
            ))}
          </div>

          {/* Line 2: BRIDGE (cropped at bottom edge) */}
          <div className="flex justify-between items-center w-full max-w-7xl mx-auto px-2 sm:px-6 text-[clamp(3.8rem,14.5vw,11.5rem)] mt-1 opacity-95">
            {["B", "R", "I", "D", "G", "E"].map((c, i) => (
              <span key={`cbr-${i}`} className="inline-block">
                {c}
              </span>
            ))}
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Section6Closing
