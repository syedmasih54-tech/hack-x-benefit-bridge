import React, { useState, useEffect } from "react"

interface SplashScreenProps {
  onComplete: () => void
}

export const SplashScreen: React.FC<SplashScreenProps> = ({ onComplete }) => {
  // Phase 1: 0.0s - 0.8s (The Singularity / Glow Pulse)
  // Phase 2: 0.8s - 1.8s (Identity Stagger Reveal)
  // Phase 3: 1.8s - 2.6s (System Verification Scan)
  // Phase 4: 2.6s - 3.2s (Smooth Cinematic Exit)
  const [phase, setPhase] = useState<number>(1)
  const [isExiting, setIsExiting] = useState<boolean>(false)
  const [dpiReady, setDpiReady] = useState<boolean>(false)

  useEffect(() => {
    // Phase 2 starts at 800ms
    const tPhase2 = setTimeout(() => {
      setPhase(2)
    }, 800)

    // Phase 3 starts at 1800ms
    const tPhase3 = setTimeout(() => {
      setPhase(3)
    }, 1800)

    // DPI ready tick at 2200ms
    const tDpiReady = setTimeout(() => {
      setDpiReady(true)
    }, 2200)

    // Phase 4 starts at 2600ms (scale-105, opacity-0)
    const tPhase4 = setTimeout(() => {
      setPhase(4)
      setIsExiting(true)
    }, 2600)

    // Completion at 3200ms
    const tComplete = setTimeout(() => {
      onComplete()
    }, 3200)

    return () => {
      clearTimeout(tPhase2)
      clearTimeout(tPhase3)
      clearTimeout(tDpiReady)
      clearTimeout(tPhase4)
      clearTimeout(tComplete)
    }
  }, [onComplete])

  return (
    <div
      className={`fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#0B0F19] cyber-grid overflow-hidden transition-all duration-700 ease-in-out ${
        isExiting
          ? "scale-105 opacity-0 pointer-events-none"
          : "scale-100 opacity-100"
      }`}
      aria-label="BenefitBridge Cinematic Startup"
    >
      {/* Background Ambient Glows */}
      <div className="absolute top-1/4 -left-20 w-96 h-96 ambient-glow-blue blur-3xl opacity-60 pointer-events-none" />
      <div className="absolute top-1/3 -right-20 w-96 h-96 ambient-glow-saffron blur-3xl opacity-50 pointer-events-none" />
      <div className="absolute bottom-10 left-1/3 w-80 h-80 ambient-glow-green blur-3xl opacity-40 pointer-events-none" />

      {/* Cyber Grid Overlay Mask */}
      <div className="absolute inset-0 bg-radial from-transparent via-[#0B0F19]/60 to-[#0B0F19] pointer-events-none" />

      {/* Center Cinematic Container */}
      <div className="relative z-10 flex flex-col items-center justify-center max-w-xl w-full px-6 text-center space-y-6">
        {/* Phase 1 & 2: Center Shield / Emblem with Radial Glow & Expanding Ripple */}
        <div className="relative flex items-center justify-center">
          {/* Expanding Luminous Ripple (Phase 2+) */}
          {phase >= 2 && (
            <>
              <div className="absolute w-32 h-32 rounded-full border border-blue-500/40 animate-ripple pointer-events-none" />
              <div
                className="absolute w-32 h-32 rounded-full border border-amber-500/30 animate-ripple pointer-events-none"
                style={{ animationDelay: "0.4s" }}
              />
            </>
          )}

          {/* Glowing Radial Rings (Phase 1+) */}
          <div className="absolute w-40 h-40 rounded-full border border-blue-500/20 animate-pulse-ring pointer-events-none" />
          <div className="absolute w-32 h-32 rounded-full border border-[#FB923C]/30 animate-pulse-ring pointer-events-none" />

          {/* Central Shield Emblem */}
          <div
            className={`w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-gradient-to-br from-[#161F30] via-[#111827] to-[#0B0F19] border border-[#1F2937] shadow-2xl flex items-center justify-center relative z-10 transition-all duration-700 ${
              phase >= 2
                ? "scale-110 shadow-blue-500/25 border-blue-500/50"
                : "scale-100"
            }`}
          >
            {/* Luminous Core Glow */}
            <div className="absolute inset-0 bg-gradient-to-tr from-blue-600/20 via-transparent to-amber-500/20 rounded-2xl" />

            {/* Emblem SVG: Gov Shield with Bridge Arch */}
            <svg
              className="w-10 h-10 sm:w-12 sm:h-12 text-[#2563EB] drop-shadow-[0_0_12px_rgba(37,99,235,0.6)]"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.75"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              <path
                d="M7 11c1.5 3 8.5 3 10 0"
                stroke="#FB923C"
                strokeWidth="2"
              />
              <circle cx="12" cy="8" r="1.5" fill="#10B981" stroke="#10B981" />
            </svg>
          </div>
        </div>

        {/* Phase 2: Title & Bilingual Subtext Stagger Reveal */}
        <div
          className={`space-y-2 transition-all duration-700 transform ${
            phase >= 2 ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          }`}
        >
          {/* Main Title with Gradient Fill */}
          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-[#F9FAFB] via-blue-100 to-cyan-300 bg-clip-text text-transparent drop-shadow-sm">
            BenefitBridge
          </h1>

          {/* Hindi / English Subtext */}
          <p className="text-xs sm:text-sm font-semibold tracking-wide text-slate-400 flex items-center justify-center gap-2">
            <span className="text-slate-300">Citizen Welfare Navigator</span>
            <span className="text-[#FB923C]">•</span>
            <span className="text-[#FB923C] font-hindi">
              सेतु नागरिक सशक्तिकरण
            </span>
          </p>
        </div>

        {/* Phase 3: System Verification Laser Scan & DPI Badge */}
        <div
          className={`w-full max-w-md transition-all duration-700 transform ${
            phase >= 3 ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          }`}
        >
          <div className="relative bg-[#111827]/80 backdrop-blur-md border border-[#1F2937] p-4 rounded-xl shadow-2xl overflow-hidden space-y-3">
            {/* Sweeping Laser Line (0 to 100% Sweep) */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
              <div className="h-full w-24 bg-gradient-to-r from-transparent via-cyan-400/30 to-transparent animate-laser" />
            </div>

            {/* DPI Connection Text */}
            <div className="text-[11px] font-mono text-slate-400 text-left flex items-center justify-between">
              <span className="truncate">
                Connecting to Digital Public Infrastructure...
              </span>
              <span className="text-cyan-400 font-bold shrink-0 ml-2">
                [DPI v2.0]
              </span>
            </div>

            {/* Sub-Badges: DigiLocker | API Setu | Citizen Charter */}
            <div className="flex items-center justify-between gap-1.5 text-[10px] font-mono text-slate-500 pt-1 border-t border-slate-800">
              <span className="px-2 py-0.5 rounded bg-blue-950/60 border border-blue-900/40 text-blue-300">
                DigiLocker
              </span>
              <span className="text-slate-600">|</span>
              <span className="px-2 py-0.5 rounded bg-indigo-950/60 border border-indigo-900/40 text-indigo-300">
                API Setu OIDC
              </span>
              <span className="text-slate-600">|</span>
              <span className="px-2 py-0.5 rounded bg-amber-950/60 border border-amber-900/40 text-amber-300">
                Citizen Charter
              </span>
            </div>

            {/* Status Tick Indicator */}
            <div className="flex items-center justify-center gap-2 pt-1 text-xs">
              {dpiReady ? (
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-[#10B981] font-semibold text-[11px] shadow-sm animate-fade-in">
                  <span className="w-2 h-2 rounded-full bg-[#10B981] animate-ping" />
                  <span>✓ DPI Secure Pipeline Ready</span>
                </div>
              ) : (
                <div className="inline-flex items-center gap-1.5 text-slate-500 text-[11px]">
                  <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
                  <span>Verifying Cryptographic Handshake...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Discrete Skip Intro Button */}
      <button
        type="button"
        onClick={onComplete}
        className="absolute bottom-6 right-6 z-50 text-xs font-medium text-slate-400 hover:text-white bg-white/[0.04] hover:bg-white/[0.1] px-4 py-2 rounded-full border border-white/10 backdrop-blur-md transition-all flex items-center gap-1.5 cursor-pointer shadow-lg active:scale-95"
      >
        <span>Skip Intro</span>
        <span className="text-slate-300">→</span>
      </button>

      {/* Bottom Legal / Govt Security Footnote */}
      <div className="absolute bottom-6 left-6 hidden sm:flex items-center gap-2 text-[10px] text-slate-500 font-mono">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
        <span>MeitY • API Setu Partner Verified • Citizen Charter 2026</span>
      </div>
    </div>
  )
}
export default SplashScreen
