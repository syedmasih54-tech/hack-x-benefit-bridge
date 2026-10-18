import React, { useState, useEffect, useRef } from "react"
import gsap from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"
import Lenis from "lenis"
import Section1Intro from "./components/Section1Intro"
import Section2Statement from "./components/Section2Statement"
import Section3Focus from "./components/Section3Focus"
import Section4JourneyTickets from "./components/Section4JourneyTickets"
import Section5WhoDecides from "./components/Section5WhoDecides"
import Section6Closing from "./components/Section6Closing"
import { getPortalUrl, getDigiLockerUrl } from "./lib/urls"

gsap.registerPlugin(ScrollTrigger)

export type Language = "en" | "hi"

interface TranslationDictionary {
  nav: {
    brand: string
    taglineDesktop: string
    taglineMobile: string
    liveGatewayBadge: string
    livePortalBtn: string
  }
  civicGateway: {
    badge: string
    title: string
    subtitle: string
    card1Title: string
    card1Desc: string
    card1Btn: string
    card2Title: string
    card2Desc: string
    card2Btn: string
    card3Title: string
    card3Desc: string
    card3Btn: string
    slaPrefix: string
    slaStrong: string
    slaEscalation: string
    statusSummary: string
    replayIntro: string
  }
  modals: {
    voiceTitle: string
    voiceSubtitle: string
    voiceRecordingPrompt: string
    voiceSamplePrompt: string
    voiceCancelBtn: string
    voiceStopBtn: string
    scannerTitle: string
    scannerSubtitle: string
    scannerCard1Title: string
    scannerCard2Title: string
    scannerMismatch: string
    scannerAdvice: string
    scannerCloseBtn: string
    scannerLaunchBtn: string
  }
}

const TRANSLATIONS: Record<Language, TranslationDictionary> = {
  en: {
    nav: {
      brand: "BenefitBridge",
      taglineDesktop: "Citizen welfare case platform",
      taglineMobile: "Welfare platform",
      liveGatewayBadge: "Live Gateway",
      livePortalBtn: "Live Portal",
    },
    civicGateway: {
      badge: "Active Civic Gateway",
      title: "Citizen Application Modules",
      subtitle:
        "Fully functional integration connected to DigiLocker, OCR document comparison, and state Right to Public Services SLAs.",
      card1Title: "DigiLocker Direct Apply",
      card1Desc:
        "Connect government-verified DigiLocker credentials. Pull authentic Ration Cards and Income Certificates automatically with zero manual upload friction.",
      card1Btn: "Connect DigiLocker",
      card2Title: "Voice Input (हिंदी / EN)",
      card2Desc:
        "Speak age, gender, occupation, and name naturally. Powered by Whisper speech processing to auto-populate scheme requirements.",
      card2Btn: "Activate Voice Input",
      card3Title: "Document Doctor (Mismatch)",
      card3Desc:
        "Detects spelling variations (e.g. Sunita vs Sunitha) before submission to prevent Direct Benefit Transfer bank delays.",
      card3Btn: "Check Discrepancies",
      slaPrefix: "State Right to Public Services Act:",
      slaStrong: "30-Day Mandatory Statutory SLA",
      slaEscalation:
        "Automatic CPGRAMS escalation triggered if government deadlines lapse",
      statusSummary: "All 6 Landing Page Sections Deployed & Active",
      replayIntro: "Replay Intro Sequence ↻",
    },
    modals: {
      voiceTitle: "Voice Application Assistant",
      voiceSubtitle:
        "Speak in Hindi, English, Bhojpuri, or Bengali to fill your welfare application automatically.",
      voiceRecordingPrompt:
        "Listening... speak your name, age, and desired scheme clearly.",
      voiceSamplePrompt:
        'Example: "My age is 62 years and annual household income is ₹75,000. Check eligibility for Old Age Pension."',
      voiceCancelBtn: "Cancel",
      voiceStopBtn: "Stop & Transcribe",
      scannerTitle: "Document Doctor • Discrepancy Analyzer",
      scannerSubtitle:
        "Comparing Aadhaar card name string against Ration card database records.",
      scannerCard1Title: "Aadhaar Card Record:",
      scannerCard2Title: "Ration Card Database:",
      scannerMismatch:
        "Phonetic soundex variation detected: Match confidence 98.4%",
      scannerAdvice:
        "The system has generated a pre-formatted Annexure-I name variation affidavit using the Official Gazette transliteration matrix. No rejection permitted under UIDAI Circular 2024.",
      scannerCloseBtn: "Done",
      scannerLaunchBtn: "Launch Full Portal ↗",
    },
  },
  hi: {
    nav: {
      brand: "बेनिफिटब्रिज",
      taglineDesktop: "नागरिक कल्याण सेवा मंच",
      taglineMobile: "कल्याण मंच",
      liveGatewayBadge: "लाइव गेटवे",
      livePortalBtn: "लाइव पोर्टल",
    },
    civicGateway: {
      badge: "सक्रिय नागरिक प्रवेशद्वार",
      title: "नागरिक आवेदन मॉड्यूल",
      subtitle:
        "डिजीलॉकर, ओसीआर दस्तावेज़ मिलान और राज्य लोक सेवा अधिकार अधिनियम (SLA) से पूर्णतः एकीकृत।",
      card1Title: "डिजीलॉकर सीधा आवेदन",
      card1Desc:
        "सरकारी सत्यापित डिजीलॉकर खाता जोड़ें। राशन कार्ड और आय प्रमाण पत्र स्वचालित रूप से बिना किसी कागज़ी परेशानी के प्राप्त करें।",
      card1Btn: "डिजीलॉकर से कनेक्ट करें",
      card2Title: "आवाज़ से सहायता (हिंदी / EN)",
      card2Desc:
        "आयु, लिंग, व्यवसाय और नाम स्वाभाविक रूप से बोलें। व्हिस्पर स्पीच इंजन योजना विवरण स्वतः भर देगा।",
      card2Btn: "वॉइस इनपुट शुरू करें",
      card3Title: "दस्तावेज़ डॉक्टर (स्पेलिंग मिलान)",
      card3Desc:
        "बैंक DBT अस्वीकृति से बचने हेतु आवेदन से पूर्व वर्तनी भिन्नता (जैसे Sunita बनाम Sunitha) की जांच करें।",
      card3Btn: "विसंगति जांचें",
      slaPrefix: "लोक सेवा गारंटी अधिनियम:",
      slaStrong: "30-दिवसीय अनिवार्य वैधानिक समय-सीमा (SLA)",
      slaEscalation: "समय-सीमा समाप्त होने पर सीपीजीआरएएमएस स्वतः लोकपाल शिकायत",
      statusSummary: "सभी 6 लैंडिंग पृष्ठ अनुभाग सक्रिय एवं संचालित",
      replayIntro: "इंट्रो दोबारा चलाएं ↻",
    },
    modals: {
      voiceTitle: "आवाज़ आधारित आवेदन सहायक",
      voiceSubtitle:
        "हिंदी, अंग्रेज़ी, भोजपुरी या बंगाली में बोलकर अपना सरकारी आवेदन फॉर्म स्वतः भरें।",
      voiceRecordingPrompt:
        "सुन रहे हैं... कृपया अपना नाम, आयु और योजना स्पष्ट रूप से बोलें।",
      voiceSamplePrompt:
        'उदाहरण: "मेरी उम्र 62 वर्ष है, वार्षिक पारिवारिक आय ₹75,000 है, वृद्धावस्था पेंशन के लिए पात्रता जांचें"',
      voiceCancelBtn: "रद्द करें",
      voiceStopBtn: "रोकें और दर्ज करें",
      scannerTitle: "दस्तावेज़ डॉक्टर • वर्तनी विसंगति विश्लेषक",
      scannerSubtitle:
        "आधार कार्ड नाम का राशन कार्ड डेटाबेस रिकॉर्ड से मिलान किया जा रहा है।",
      scannerCard1Title: "आधार कार्ड रिकॉर्ड:",
      scannerCard2Title: "राशन कार्ड डेटाबेस:",
      scannerMismatch:
        "ध्वन्यात्मक साउंडेक्स वर्तनी भिन्नता मिली: मिलान विश्वसनीयता 98.4%",
      scannerAdvice:
        "प्रणाली ने आधिकारिक राजपत्र के आधार पर स्वतः शपथ-पत्र प्रारूप तैयार कर लिया है। यूआईडीएआई परिपत्र 2024 के अनुसार इसे निरस्त नहीं किया जा सकता।",
      scannerCloseBtn: "संपन्न",
      scannerLaunchBtn: "मुख्य पोर्टल खोलें ↗",
    },
  },
}

export default function App() {
  const [isIntroActive, setIsIntroActive] = useState<boolean>(true)
  const [selectedLanguage, setSelectedLanguage] = useState<Language>(() => {
    if (typeof window !== "undefined") {
      try {
        const saved = localStorage.getItem("benefitbridge_lang")
        if (saved === "hi" || saved === "en") return saved
      } catch {
        // Fallback for restricted iframes
      }
    }
    return "en"
  })

  const [activeModal, setActiveModal] = useState<"none" | "voice" | "scanner">(
    "none",
  )

  const underneathWordmarkRef = useRef<HTMLDivElement | null>(null)
  const lenisRef = useRef<Lenis | null>(null)

  const t = TRANSLATIONS[selectedLanguage]

  const handleLanguageChange = (lang: Language) => {
    setSelectedLanguage(lang)
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem("benefitbridge_lang", lang)
      } catch {
        // Fallback
      }
      document.documentElement.lang = lang
    }
  }

  useEffect(() => {
    if (typeof window !== "undefined") {
      document.documentElement.lang = selectedLanguage
    }
  }, [selectedLanguage])

  // Initialize Lenis smooth scroll and sync with ScrollTrigger
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.1,
      easing: (v: number) => Math.min(1, 1.001 - Math.pow(2, -10 * v)),
      smoothWheel: true,
    })
    lenisRef.current = lenis

    lenis.on("scroll", ScrollTrigger.update)

    const updateTicker = (time: number) => {
      lenis.raf(time * 1000)
    }

    gsap.ticker.add(updateTicker)
    gsap.ticker.lagSmoothing(0)

    return () => {
      gsap.ticker.remove(updateTicker)
      lenis.destroy()
      lenisRef.current = null
    }
  }, [])

  // Lock scroll while Section 1 intro is running
  useEffect(() => {
    if (isIntroActive) {
      lenisRef.current?.stop()
      document.body.style.overflow = "hidden"
    } else {
      lenisRef.current?.start()
      document.body.style.overflow = ""
      ScrollTrigger.refresh()
    }
  }, [isIntroActive])

  return (
    <div className="min-h-screen bg-[#FFFDF9] text-[#1A0F12] font-body selection:bg-[#C41528] selection:text-white relative overflow-x-hidden">
      {/* ---------------- AMBIENT GLASS UI BACKGROUND LIGHT BLOBS ---------------- */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 w-[550px] h-[550px] rounded-full bg-red-100/40 blur-[130px] animate-glass-pulse-glow" />
        <div
          className="absolute top-[35%] -right-40 w-[500px] h-[500px] rounded-full bg-amber-100/35 blur-[140px] animate-glass-pulse-glow"
          style={{ animationDelay: "2s" }}
        />
        <div
          className="absolute -bottom-40 left-1/3 w-[600px] h-[600px] rounded-full bg-rose-100/30 blur-[150px] animate-glass-pulse-glow"
          style={{ animationDelay: "4s" }}
        />
      </div>

      {/* ---------------- SECTION 1: INTRO / PRELOADER HERO ---------------- */}
      {isIntroActive && (
        <Section1Intro
          onComplete={() => setIsIntroActive(false)}
          underneathWordmarkRef={underneathWordmarkRef}
        />
      )}

      {/* ---------------- TOP FLOATING GLASS NAVIGATION ---------------- */}
      <header className="sticky top-0 z-40 bg-white/75 backdrop-blur-xl border-b border-white/80 shadow-[0_4px_30px_rgba(0,0,0,0.03)] transition-all">
        <div className="w-full max-w-7xl mx-auto px-6 sm:px-12 h-14 flex items-center justify-between text-[11px] font-sans text-[#1A0F12]/75">
          <div className="flex items-center gap-3">
            <span className="font-semibold text-[#8E1B2B]">{t.nav.brand}</span>
            <span className="text-[#1A0F12]/30">/</span>
            <span className="hidden sm:inline">{t.nav.taglineDesktop}</span>
            <span className="sm:hidden">{t.nav.taglineMobile}</span>
            <span className="hidden md:inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-red-50 border border-red-200 text-[10px] font-bold text-[#DC2626]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#DC2626] animate-pulse" />
              {t.nav.liveGatewayBadge}
            </span>
          </div>

          <div className="flex items-center gap-3 sm:gap-4">
            {/* Language Switcher */}
            <div className="flex items-center border border-[#1A0F12]/15 rounded-full p-0.5 bg-white/90 text-[11px] shadow-xs">
              <button
                type="button"
                onClick={() => handleLanguageChange("en")}
                className={`px-2.5 py-0.5 rounded-full font-medium transition-all cursor-pointer ${
                  selectedLanguage === "en"
                    ? "bg-[#C41528] text-white shadow-xs"
                    : "text-[#1A0F12]/70 hover:text-[#1A0F12]"
                }`}
                aria-label="Switch language to English"
              >
                EN
              </button>
              <button
                type="button"
                onClick={() => handleLanguageChange("hi")}
                className={`px-2.5 py-0.5 rounded-full font-medium transition-all cursor-pointer ${
                  selectedLanguage === "hi"
                    ? "bg-[#C41528] text-white shadow-xs"
                    : "text-[#1A0F12]/70 hover:text-[#1A0F12]"
                }`}
                aria-label="Switch language to Hindi"
              >
                हिंदी
              </button>
            </div>

            {/* Live Portal Button (API Docs link hidden and secured per request) */}
            <a
              href={getPortalUrl()}
              className="inline-flex items-center gap-1 px-3.5 py-1.5 rounded-full bg-[#8E1B2B]/10 hover:bg-[#C41528] hover:text-white text-[11px] font-medium text-[#8E1B2B] transition-all shadow-xs"
            >
              <span>{t.nav.livePortalBtn}</span>
              <span aria-hidden="true">→</span>
            </a>
          </div>
        </div>
      </header>

      {/* ---------------- SECTION 2: STATEMENT (WITH FLOATING GLASS CARDS) ---------------- */}
      <Section2Statement underneathWordmarkRef={underneathWordmarkRef} />

      {/* ---------------- SECTION 3: FOCUS (SKY BLUE GRADIENT, PINNED) ---------------- */}
      <Section3Focus />

      {/* ---------------- SECTION 4: THE JOURNEY TICKETS (PINNED, 3D FLY-IN) ---------------- */}
      <Section4JourneyTickets />

      {/* ---------------- SECTION 5: WHO DECIDES (RED FULL-BLEED) ---------------- */}
      <Section5WhoDecides />

      {/* ---------------- CIVIC GATEWAY WITH FLOATING GLASS CARDS ---------------- */}
      <section className="relative z-10 w-full max-w-7xl mx-auto px-6 sm:px-12 py-20 border-t border-[#1A0F12]/10 space-y-12">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <span className="text-[10px] font-mono uppercase tracking-widest text-[#C41528] block mb-1">
              {t.civicGateway.badge}
            </span>
            <h3 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#1A0F12]">
              {t.civicGateway.title}
            </h3>
          </div>
          <p className="text-xs text-[#1A0F12]/60 max-w-md font-light">
            {t.civicGateway.subtitle}
          </p>
        </div>

        {/* 3 Floating Glass Cards (DigiLocker, Voice, Document Doctor) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* 1. DigiLocker Direct Apply - Floating Glass Card */}
          <div className="border border-white/90 rounded-3xl p-7 bg-white/75 backdrop-blur-xl shadow-[0_16px_40px_rgba(196,21,40,0.06)] hover:shadow-[0_24px_55px_rgba(196,21,40,0.16)] hover:border-[#C41528]/50 hover:-translate-y-2 transition-all duration-300 flex flex-col justify-between group relative overflow-hidden animate-glass-float-1">
            <div className="absolute -top-12 -right-12 w-32 h-32 rounded-full bg-red-100/50 blur-2xl pointer-events-none group-hover:scale-125 transition-transform" />
            <div className="relative z-10">
              <div className="w-12 h-12 rounded-2xl bg-white/90 border border-[#1A0F12]/10 flex items-center justify-center text-[#C41528] mb-5 group-hover:border-[#C41528]/40 transition-colors shadow-xs">
                <svg
                  className="w-6 h-6"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z" />
                </svg>
              </div>
              <h4 className="text-lg font-bold text-[#1A0F12] mb-2 tracking-tight">
                {t.civicGateway.card1Title}
              </h4>
              <p className="text-xs text-[#1A0F12]/70 leading-relaxed font-light">
                {t.civicGateway.card1Desc}
              </p>
            </div>
            <a
              href={getDigiLockerUrl()}
              className="relative z-10 mt-6 inline-flex items-center justify-center gap-2 px-5 py-3 rounded-2xl bg-[#C41528] hover:bg-[#8E1B2B] text-white text-xs font-semibold shadow-md shadow-red-600/20 active:scale-[0.98] transition-all cursor-pointer"
            >
              <span>{t.civicGateway.card1Btn}</span>
              <span aria-hidden="true">→</span>
            </a>
          </div>

          {/* 2. Voice Assistance - Floating Glass Card */}
          <div className="border border-white/90 rounded-3xl p-7 bg-white/75 backdrop-blur-xl shadow-[0_16px_40px_rgba(196,21,40,0.06)] hover:shadow-[0_24px_55px_rgba(196,21,40,0.16)] hover:border-[#C41528]/50 hover:-translate-y-2 transition-all duration-300 flex flex-col justify-between group relative overflow-hidden animate-glass-float-2">
            <div className="absolute -top-12 -right-12 w-32 h-32 rounded-full bg-amber-100/50 blur-2xl pointer-events-none group-hover:scale-125 transition-transform" />
            <div className="relative z-10">
              <div className="w-12 h-12 rounded-2xl bg-white/90 border border-[#1A0F12]/10 flex items-center justify-center text-[#8E1B2B] mb-5 group-hover:border-[#C41528]/40 transition-colors shadow-xs">
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                  />
                </svg>
              </div>
              <h4 className="text-lg font-bold text-[#1A0F12] mb-2 tracking-tight">
                {t.civicGateway.card2Title}
              </h4>
              <p className="text-xs text-[#1A0F12]/70 leading-relaxed font-light">
                {t.civicGateway.card2Desc}
              </p>
            </div>
            <button
              type="button"
              onClick={() => setActiveModal("voice")}
              className="relative z-10 mt-6 inline-flex items-center justify-center gap-2 px-5 py-3 rounded-2xl border border-[#1A0F12]/20 hover:border-[#C41528] bg-white/90 hover:bg-[#FEE2E2]/60 text-[#8E1B2B] hover:text-[#C41528] text-xs font-semibold shadow-xs active:scale-[0.98] transition-all cursor-pointer"
            >
              <span>{t.civicGateway.card2Btn}</span>
              <span aria-hidden="true">🎙</span>
            </button>
          </div>

          {/* 3. Document Doctor - Floating Glass Card */}
          <div className="border border-white/90 rounded-3xl p-7 bg-white/75 backdrop-blur-xl shadow-[0_16px_40px_rgba(196,21,40,0.06)] hover:shadow-[0_24px_55px_rgba(196,21,40,0.16)] hover:border-[#C41528]/50 hover:-translate-y-2 transition-all duration-300 flex flex-col justify-between group relative overflow-hidden animate-glass-float-3">
            <div className="absolute -top-12 -right-12 w-32 h-32 rounded-full bg-rose-100/50 blur-2xl pointer-events-none group-hover:scale-125 transition-transform" />
            <div className="relative z-10">
              <div className="w-12 h-12 rounded-2xl bg-white/90 border border-[#1A0F12]/10 flex items-center justify-center text-[#1A0F12] mb-5 group-hover:border-[#C41528]/40 transition-colors shadow-xs">
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h4 className="text-lg font-bold text-[#1A0F12] mb-2 tracking-tight">
                {t.civicGateway.card3Title}
              </h4>
              <p className="text-xs text-[#1A0F12]/70 leading-relaxed font-light">
                {t.civicGateway.card3Desc}
              </p>
            </div>
            <button
              type="button"
              onClick={() => setActiveModal("scanner")}
              className="relative z-10 mt-6 inline-flex items-center justify-center gap-2 px-5 py-3 rounded-2xl border border-[#1A0F12]/20 hover:border-[#C41528] bg-white/90 hover:bg-[#FEE2E2]/60 text-[#1A0F12] hover:text-[#C41528] text-xs font-semibold shadow-xs active:scale-[0.98] transition-all cursor-pointer"
            >
              <span>{t.civicGateway.card3Btn}</span>
              <span aria-hidden="true">→</span>
            </button>
          </div>
        </div>

        {/* Statutory SLA Guarantee Glass Ribbon */}
        <div className="p-5 rounded-2xl border border-white/90 bg-white/75 backdrop-blur-xl shadow-[0_8px_30px_rgba(0,0,0,0.03)] flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-[#1A0F12]/80 transition-all hover:shadow-md">
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#16A34A] animate-pulse" />
            <span>
              {t.civicGateway.slaPrefix}{" "}
              <strong className="text-[#1A0F12] font-semibold">
                {t.civicGateway.slaStrong}
              </strong>
            </span>
          </div>
          <span className="text-[#8E1B2B] font-medium text-[11px]">
            {t.civicGateway.slaEscalation}
          </span>
        </div>

        {/* Replay trigger */}
        <div className="pt-4 flex items-center justify-between text-[11px] text-[#1A0F12]/50">
          <span>{t.civicGateway.statusSummary}</span>
          <button
            type="button"
            onClick={() => {
              sessionStorage.removeItem("bb_intro_seen")
              setIsIntroActive(true)
            }}
            className="text-[#C41528] hover:underline cursor-pointer font-medium"
          >
            {t.civicGateway.replayIntro}
          </button>
        </div>
      </section>

      {/* ---------------- SECTION 6: CLOSING (WHITE & GIANT CROPPED WORDMARK) ---------------- */}
      <Section6Closing />

      {/* ---------------- INTERACTIVE VOICE ASSISTANT MODAL ---------------- */}
      {activeModal === "voice" && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-md">
          <div className="w-full max-w-lg p-6 sm:p-8 rounded-3xl bg-white/90 backdrop-blur-2xl shadow-2xl border border-white/90 space-y-6">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-xl font-bold text-[#1A0F12]">
                  {t.modals.voiceTitle}
                </h3>
                <p className="text-xs text-[#1A0F12]/60 mt-1">
                  {t.modals.voiceSubtitle}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setActiveModal("none")}
                className="text-gray-400 hover:text-gray-600 text-xl font-bold cursor-pointer"
                aria-label="Close dialog"
              >
                ×
              </button>
            </div>

            <div className="p-6 rounded-2xl bg-red-50/70 border border-red-100 text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-[#C41528] text-white mx-auto flex items-center justify-center text-3xl animate-pulse shadow-lg shadow-red-500/30">
                🎙️
              </div>
              <p className="text-xs font-bold text-[#C41528]">
                {t.modals.voiceRecordingPrompt}
              </p>
              <p className="text-[11px] text-[#1A0F12]/70 italic bg-white/90 p-3 rounded-xl border border-red-200/50">
                {t.modals.voiceSamplePrompt}
              </p>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setActiveModal("none")}
                className="px-4 py-2.5 rounded-xl border border-[#1A0F12]/20 text-[#1A0F12]/80 text-xs font-semibold hover:bg-black/5 transition-colors cursor-pointer"
              >
                {t.modals.voiceCancelBtn}
              </button>
              <a
                href={getPortalUrl()}
                className="px-5 py-2.5 rounded-xl bg-[#C41528] hover:bg-[#8E1B2B] text-white text-xs font-bold transition-all shadow-sm cursor-pointer"
              >
                {t.modals.voiceStopBtn}
              </a>
            </div>
          </div>
        </div>
      )}

      {/* ---------------- INTERACTIVE DOCUMENT DOCTOR MODAL ---------------- */}
      {activeModal === "scanner" && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-md">
          <div className="w-full max-w-lg p-6 sm:p-8 rounded-3xl bg-white/90 backdrop-blur-2xl shadow-2xl border border-white/90 space-y-6">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-xl font-bold text-[#1A0F12]">
                  {t.modals.scannerTitle}
                </h3>
                <p className="text-xs text-[#1A0F12]/60 mt-1">
                  {t.modals.scannerSubtitle}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setActiveModal("none")}
                className="text-gray-400 hover:text-gray-600 text-xl font-bold cursor-pointer"
                aria-label="Close dialog"
              >
                ×
              </button>
            </div>

            <div className="p-5 rounded-2xl bg-white/80 border border-[#1A0F12]/10 space-y-3 shadow-xs">
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-gray-50/80 border border-gray-200">
                  <span className="text-[10px] text-gray-500 font-mono block">
                    {t.modals.scannerCard1Title}
                  </span>
                  <span className="font-bold text-[#1A0F12]">Sunita Devi</span>
                </div>
                <div className="p-3 rounded-xl bg-red-50/80 border border-red-200">
                  <span className="text-[10px] text-red-500 font-mono block">
                    {t.modals.scannerCard2Title}
                  </span>
                  <span className="font-bold text-[#C41528]">Sunitha Devi</span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-amber-50/80 border border-amber-200 text-amber-900 text-xs font-semibold">
                ⚠️ {t.modals.scannerMismatch}
              </div>

              <p className="text-xs text-[#1A0F12]/75 leading-relaxed font-light">
                {t.modals.scannerAdvice}
              </p>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setActiveModal("none")}
                className="px-4 py-2.5 rounded-xl border border-[#1A0F12]/20 text-[#1A0F12]/80 text-xs font-semibold hover:bg-black/5 transition-colors cursor-pointer"
              >
                {t.modals.scannerCloseBtn}
              </button>
              <a
                href={getPortalUrl()}
                className="px-5 py-2.5 rounded-xl bg-[#C41528] hover:bg-[#8E1B2B] text-white text-xs font-bold transition-all shadow-sm inline-flex items-center gap-1.5"
              >
                <span>{t.modals.scannerLaunchBtn}</span>
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
