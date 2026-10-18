import React, { useState } from "react"
import SplashScreen from "./SplashScreen"

type Language = "en" | "hi"

interface TrackedApplication {
  id: string
  applicant: string
  scheme: string
  status: "Submitted" | "Under Review" | "Verified" | "Dispatched"
  slaDaysTotal: number
  slaDaysRemaining: number
  targetDate: string
  dbtStatus: "Linked" | "Pending" | "Variation Detected"
}

export const App: React.FC = () => {
  // Splash Screen State
  const [showSplash, setShowSplash] = useState<boolean>(true)

  // App State
  const [lang, setLang] = useState<Language>("en")
  const [searchToken, setSearchToken] = useState<string>("")
  const [activeModal, setActiveModal] =
    useState<"none" | "digilocker" | "voice" | "docDoctor" | "tracker">("none")
  const [copiedToken, setCopiedToken] = useState<boolean>(false)

  // Voice Interaction Simulated States
  const [isRecording, setIsRecording] = useState<boolean>(false)
  const [voiceStep, setVoiceStep] =
    useState<"idle" | "listening" | "processed">("idle")
  const [activeAudioPrompt, setActiveAudioPrompt] =
    useState<"widow" | "scholarship" | "kisan">("widow")

  // Sample Tracked Applications
  const sampleApps: Record<string, TrackedApplication> = {
    "APP-82403435": {
      id: "APP-82403435",
      applicant: "Sunita Devi",
      scheme: "Indira Gandhi National Widow Pension Scheme (IGNWPS)",
      status: "Under Review",
      slaDaysTotal: 30,
      slaDaysRemaining: 9,
      targetDate: "23-Oct-2026",
      dbtStatus: "Linked",
    },
    "APP-SUNITA-ACTIVE-01": {
      id: "APP-SUNITA-ACTIVE-01",
      applicant: "Sunita Devi",
      scheme: "Indira Gandhi National Widow Pension Scheme (IGNWPS)",
      status: "Submitted",
      slaDaysTotal: 30,
      slaDaysRemaining: 21,
      targetDate: "04-Nov-2026",
      dbtStatus: "Variation Detected",
    },
    "APP-SCHOLAR-2026": {
      id: "APP-SCHOLAR-2026",
      applicant: "Amit Kumar",
      scheme: "Post-Matric Scholarship for SC/ST/OBC Students",
      status: "Verified",
      slaDaysTotal: 21,
      slaDaysRemaining: 4,
      targetDate: "18-Oct-2026",
      dbtStatus: "Linked",
    },
  }

  const [activeTrackedApp, setActiveTrackedApp] =
    useState<TrackedApplication | null>(null)

  const handleTrackSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const cleanId = searchToken.trim().toUpperCase()
    if (!cleanId) return

    if (sampleApps[cleanId]) {
      setActiveTrackedApp(sampleApps[cleanId])
    } else {
      setActiveTrackedApp({
        id: cleanId,
        applicant: "Citizen Applicant",
        scheme: "Statutory Public Welfare Scheme",
        status: "Submitted",
        slaDaysTotal: 30,
        slaDaysRemaining: 18,
        targetDate: "31-Oct-2026",
        dbtStatus: "Linked",
      })
    }
    setActiveModal("tracker")
  }

  const handleCopyToken = (token: string) => {
    navigator.clipboard.writeText(token)
    setCopiedToken(true)
    setTimeout(() => setCopiedToken(false), 2200)
  }

  const t = {
    en: {
      navLive: "NIC / DPI Connected",
      refCitizen: "Citizen ID: DL-IND-8829103",
      trackPlaceholder: "Enter Token (e.g. APP-82403435)",
      trackBtn: "Track",
      heroBadge: "Statutory Rights & Public Service Guarantee Act 2026",
      heroHeadline: "India's Direct Welfare & Statutory Benefit Navigator",
      heroSubtitle:
        "Pre-screen eligibility, prevent bank DBT rejection, and apply directly via DigiLocker with guaranteed 30-day Citizen Charter disposal.",
      trustPill1: "100% Paperless DigiLocker OIDC",
      trustPill2: "Statutory 30-Day SLA Guarantee",
      trustPill3: "DBT Name Mismatch Prevention",
      card1Title: "DigiLocker Direct Apply",
      card1Sub: "Instant Paperless Submission",
      card1Desc:
        "Pull authentic digital certificates directly from Govt issuers. No document scanning or photo upload required. Submits with cryptographic proof.",
      card1Btn: "Log in with DigiLocker (One-Click Apply)",
      card1Badge: "API Setu v2.0 Partner",
      card2Title: "Voice Assistance",
      card2Sub: "Hindi & English Voice Intake",
      card2Desc:
        "Bolein aur Aavedan Karein. Speak naturally in your native language. Our AI extracts family criteria, validates scheme rules, and confirms over audio.",
      card2Btn: "Bolein aur Aavedan Karein / Speak to Apply",
      card2Badge: "Aadhaar Masked Whisper",
      card3Title: "Document Doctor & Matcher",
      card3Sub: "PFMS / DBT Pre-Verification",
      card3Desc:
        "Catches critical spelling differences like 'Sunita Devi vs Sunitha Devi' between your Ration Card and Bank Passbook to prevent DBT transfer failure.",
      card3Btn: "Scan & Resolve Name Mismatches",
      card3Badge: "95% Phonetic Match Detected",
      tickerText:
        "Guaranteed statutory disposal: 30 days under Citizen Charters • 100% CPGRAMS escalation ready • Zero Aadhaar storage • Direct Benefit Transfer (DBT) verification enabled",
      replaySplash: "Replay Cinematic Intro",
    },
    hi: {
      navLive: "एनआईसी / डीपीआई कनेक्टेड",
      refCitizen: "नागरिक पहचान: DL-IND-8829103",
      trackPlaceholder: "टोकन दर्ज करें (उदा. APP-82403435)",
      trackBtn: "ट्रैक करें",
      heroBadge: "लोक सेवा गारंटी एवं नागरिक अधिकार पत्र अधिनियम 2026",
      heroHeadline: "भारत का प्रत्यक्ष कल्याण एवं वैधानिक लाभ नेविगेटर",
      heroSubtitle:
        "पात्रता की पूर्व-जांच करें, बैंक डीबीटी अस्वीकृति रोकें, और नागरिक अधिकार पत्र के तहत 30-दिवसीय गारंटी के साथ डिजीलॉकर से सीधे आवेदन करें।",
      trustPill1: "१००% पेपरलेस डिजीलॉकर OIDC",
      trustPill2: "वैधानिक ३०-दिवसीय निवारण गारंटी",
      trustPill3: "डीबीटी नाम विसंगति निवारण",
      card1Title: "डिजीलॉकर प्रत्यक्ष आवेदन",
      card1Sub: "तत्काल पेपरलेस सत्यापन",
      card1Desc:
        "सरकारी जारीकर्ताओं से सीधे प्रामाणिक डिजिटल प्रमाण पत्र प्राप्त करें। दस्तावेज़ स्कैन या फ़ोटो अपलोड की आवश्यकता नहीं है।",
      card1Btn: "डिजीलॉकर से लॉगिन करें (एक-क्लिक आवेदन)",
      card1Badge: "एपीआई सेतु पार्टनर",
      card2Title: "द्विभाषी वॉइस सहायता",
      card2Sub: "हिंदी एवं अंग्रेजी वॉइस आवेदन",
      card2Desc:
        "बोलें और आवेदन करें। अपनी सहज भाषा में बात करें। हमारा सिस्टम जनसांख्यिकीय डेटा निकालकर योजना नियमों की स्वतः जांच करता है।",
      card2Btn: "बोलें और आवेदन करें / Speak to Apply",
      card2Badge: "आधार संरक्षित वॉइस इंजन",
      card3Title: "दस्तावेज़ डॉक्टर एवं वर्तनी मिलान",
      card3Sub: "पीएफएमएस / डीबीटी पूर्व-सत्यापन",
      card3Desc:
        "राशन कार्ड और बैंक पासबुक के बीच 'सुनीता देवी बनाम सुनीथा देवी' जैसी वर्तनी विसंगतियों को समय रहते पकड़कर बैंक डीबीटी विफलता को रोकता है।",
      card3Btn: "नाम विसंगति का समाधान करें",
      card3Badge: "९५% ध्वन्यात्मक मिलान",
      tickerText:
        "नागरिक अधिकार पत्र के तहत गारंटीकृत वैधानिक निवारण: ३० दिन • १००% सीपीग्राम्स (CPGRAMS) अपीलीय निगरानी • शून्य आधार भंडारण • प्रत्यक्ष लाभ अंतरण (DBT) सक्रिय",
      replaySplash: "सिनेमैटिक इंट्रो पुनः देखें",
    },
  }[lang]

  return (
    <div className="min-h-screen bg-[#0B0F19] text-[#F9FAFB] flex flex-col font-sans selection:bg-[#2563EB] selection:text-white relative">
      {/* Starting Intro Animation Component */}
      {showSplash && <SplashScreen onComplete={() => setShowSplash(false)} />}

      {/* Background Ambient Glows */}
      <div className="fixed top-0 left-1/4 w-[500px] h-[500px] ambient-glow-blue blur-3xl opacity-30 pointer-events-none z-0" />
      <div className="fixed top-1/3 right-10 w-[450px] h-[450px] ambient-glow-saffron blur-3xl opacity-20 pointer-events-none z-0" />
      <div className="fixed bottom-10 left-1/3 w-[450px] h-[450px] ambient-glow-green blur-3xl opacity-20 pointer-events-none z-0" />

      {/* 1. TOP NAVIGATION BAR */}
      <header className="sticky top-0 z-40 bg-[#0B0F19]/80 backdrop-blur-md border-b border-[#1F2937] px-4 sm:px-8 py-3.5">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          {/* Left: Logo & Live Connection Pill */}
          <div className="flex items-center gap-3 w-full sm:w-auto justify-between sm:justify-start">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#161F30] to-[#111827] border border-[#2563EB]/40 flex items-center justify-center shadow-md shadow-blue-500/10">
                <svg
                  className="w-5 h-5 text-[#2563EB]"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  <path
                    d="M7 11c1.5 3 8.5 3 10 0"
                    stroke="#FB923C"
                    strokeWidth="2"
                  />
                </svg>
              </div>
              <div>
                <span className="font-extrabold text-base tracking-tight text-white flex items-center gap-1.5">
                  BenefitBridge
                  <span className="text-[10px] font-mono text-[#FB923C] bg-[#FB923C]/10 px-1.5 py-0.2 rounded border border-[#FB923C]/20">
                    GOV
                  </span>
                </span>
                <span className="text-[10px] text-slate-400 block -mt-0.5">
                  Citizen Welfare Navigator
                </span>
              </div>
            </div>

            {/* Live NIC / DPI status pill */}
            <div className="inline-flex items-center gap-1.5 bg-[#111827] border border-[#1F2937] px-2.5 py-1 rounded-full text-[11px] text-slate-300">
              <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
              <span className="font-medium text-emerald-400">{t.navLive}</span>
            </div>
          </div>

          {/* Center: Language Toggle Pill */}
          <div className="inline-flex items-center bg-[#111827] p-1 rounded-full border border-[#1F2937] text-xs font-semibold">
            <button
              type="button"
              onClick={() => setLang("en")}
              className={`px-3.5 py-1 rounded-full transition-all cursor-pointer ${
                lang === "en"
                  ? "bg-[#2563EB] text-white shadow-sm font-bold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              English
            </button>
            <button
              type="button"
              onClick={() => setLang("hi")}
              className={`px-3.5 py-1 rounded-full transition-all cursor-pointer ${
                lang === "hi"
                  ? "bg-[#2563EB] text-white shadow-sm font-bold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              हिंदी
            </button>
          </div>

          {/* Right: Quick Track Status Input & Citizen Badge */}
          <div className="flex items-center gap-2.5 w-full sm:w-auto">
            <form
              onSubmit={handleTrackSubmit}
              className="relative flex items-center w-full sm:w-64"
            >
              <input
                type="text"
                value={searchToken}
                onChange={(e) => setSearchToken(e.target.value)}
                placeholder={t.trackPlaceholder}
                className="w-full bg-[#111827] border border-[#1F2937] focus:border-[#2563EB] text-xs text-white placeholder-slate-500 rounded-xl pl-3 pr-14 py-2 transition-all shadow-inner"
              />
              <button
                type="submit"
                className="absolute right-1 top-1 bottom-1 bg-[#2563EB] hover:bg-blue-600 text-white text-[11px] font-bold px-2.5 rounded-lg transition-all cursor-pointer flex items-center justify-center"
              >
                {t.trackBtn}
              </button>
            </form>

            <span className="hidden xl:inline-block font-mono text-[11px] text-slate-400 bg-[#111827] px-2.5 py-1.5 rounded-xl border border-[#1F2937]">
              {t.refCitizen}
            </span>
          </div>
        </div>
      </header>

      {/* 2. HERO SECTION */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-8 py-8 sm:py-12 space-y-12 relative z-10">
        <section className="text-center max-w-3xl mx-auto space-y-4">
          {/* Statutory Badge */}
          <div className="inline-flex items-center gap-2 bg-[#161F30]/80 border border-[#2563EB]/40 px-3.5 py-1.5 rounded-full text-xs font-semibold text-blue-200 backdrop-blur-md shadow-sm">
            <span className="w-2 h-2 rounded-full bg-[#FB923C]" />
            <span>{t.heroBadge}</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.1] text-white">
            {lang === "en" ? (
              <>
                India's Direct Welfare &amp;{" "}
                <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-[#FB923C] bg-clip-text text-transparent">
                  Statutory Benefit
                </span>{" "}
                Navigator
              </>
            ) : (
              <>
                भारत का प्रत्यक्ष कल्याण एवं{" "}
                <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-[#FB923C] bg-clip-text text-transparent">
                  वैधानिक लाभ
                </span>{" "}
                नेविगेटर
              </>
            )}
          </h1>

          {/* Subtitle */}
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed max-w-2xl mx-auto">
            {t.heroSubtitle}
          </p>

          {/* Trust Metric Badges */}
          <div className="pt-2 flex flex-wrap items-center justify-center gap-2.5 text-xs text-slate-300">
            <span className="inline-flex items-center gap-1.5 bg-[#111827] border border-[#1F2937] px-3 py-1 rounded-full text-blue-300">
              <span className="text-emerald-400">✓</span> {t.trustPill1}
            </span>
            <span className="inline-flex items-center gap-1.5 bg-[#111827] border border-[#1F2937] px-3 py-1 rounded-full text-amber-300">
              <span className="text-amber-400">⚖️</span> {t.trustPill2}
            </span>
            <span className="inline-flex items-center gap-1.5 bg-[#111827] border border-[#1F2937] px-3 py-1 rounded-full text-emerald-300">
              <span className="text-emerald-400">🛡️</span> {t.trustPill3}
            </span>
          </div>
        </section>

        {/* 3. ACTION HUB (3 Interactive Cards in Dark Glassmorphism) */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* CARD 1: DigiLocker Direct Apply */}
          <div className="group relative bg-[#111827]/80 backdrop-blur-md border border-[#1F2937] hover:border-[#2563EB]/60 rounded-2xl p-6 flex flex-col justify-between shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
            {/* Top Royal Blue Glow Border */}
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#2563EB] to-cyan-400" />

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                {/* Official DigiLocker Cloud & Shield Icon */}
                <div className="w-12 h-12 rounded-xl bg-blue-950/80 border border-blue-800/50 flex items-center justify-center text-blue-400 shadow-inner group-hover:scale-105 transition-transform">
                  <svg
                    className="w-6 h-6"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z" />
                    <rect
                      x="10"
                      y="11"
                      width="4"
                      height="4"
                      rx="1"
                      fill="#2563EB"
                      stroke="#2563EB"
                    />
                  </svg>
                </div>
                <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-blue-400 bg-blue-950/80 px-2.5 py-1 rounded-full border border-blue-900/50">
                  {t.card1Badge}
                </span>
              </div>

              <div>
                <h3 className="text-lg font-bold text-white group-hover:text-blue-300 transition-colors">
                  {t.card1Title}
                </h3>
                <span className="text-xs font-semibold text-slate-400 block mb-2">
                  {t.card1Sub}
                </span>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {t.card1Desc}
                </p>
              </div>

              <div className="space-y-1.5 pt-2 text-[11px] text-slate-400 font-mono">
                <div className="flex items-center gap-1.5 text-emerald-400">
                  <span>✓</span>
                  <span>Ration Card (NFSA / BPL) Pulled</span>
                </div>
                <div className="flex items-center gap-1.5 text-emerald-400">
                  <span>✓</span>
                  <span>Annual Income Certificate Verified</span>
                </div>
              </div>
            </div>

            <div className="pt-6">
              <button
                type="button"
                onClick={() => setActiveModal("digilocker")}
                className="w-full bg-[#2563EB] hover:bg-blue-600 text-white font-bold text-xs py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-600/20 active:scale-[0.98] cursor-pointer"
              >
                <svg
                  className="w-4 h-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
                <span>{t.card1Btn}</span>
              </button>
            </div>
          </div>

          {/* CARD 2: Voice Assistance in Hindi & English */}
          <div className="group relative bg-[#111827]/80 backdrop-blur-md border border-[#1F2937] hover:border-[#FB923C]/60 rounded-2xl p-6 flex flex-col justify-between shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
            {/* Top Saffron / Amber Glow Border */}
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#F97316] to-[#FB923C]" />

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                {/* Microphone Icon with Animated Soundwave Visualizer */}
                <div className="w-12 h-12 rounded-xl bg-amber-950/80 border border-amber-800/50 flex items-center justify-center text-[#FB923C] shadow-inner group-hover:scale-105 transition-transform">
                  <svg
                    className="w-6 h-6"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                    <line x1="12" x2="12" y1="19" y2="22" />
                  </svg>
                </div>

                {/* Animated Soundwave Visualizer */}
                <div className="flex items-center gap-1 h-6 px-2.5 py-1 bg-[#161F30] rounded-full border border-slate-700">
                  <span className="w-1 bg-[#FB923C] rounded-full soundwave-bar-1" />
                  <span className="w-1 bg-amber-400 rounded-full soundwave-bar-2" />
                  <span className="w-1 bg-emerald-400 rounded-full soundwave-bar-3" />
                  <span className="w-1 bg-[#FB923C] rounded-full soundwave-bar-4" />
                  <span className="w-1 bg-amber-300 rounded-full soundwave-bar-5" />
                </div>
              </div>

              <div>
                <h3 className="text-lg font-bold text-white group-hover:text-amber-300 transition-colors">
                  {t.card2Title}
                </h3>
                <span className="text-xs font-semibold text-slate-400 block mb-2">
                  {t.card2Sub}
                </span>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {t.card2Desc}
                </p>
              </div>

              <div className="bg-[#161F30]/90 border border-slate-700/60 p-2.5 rounded-xl text-[11px] text-slate-300 font-mono flex items-center justify-between">
                <span className="truncate">
                  "मैं सुनीता देवी, 65 वर्ष, विधवा पेंशन..."
                </span>
                <span className="text-[#FB923C] text-[10px] shrink-0 font-bold ml-2">
                  DEVNAGARI
                </span>
              </div>
            </div>

            <div className="pt-6">
              <button
                type="button"
                onClick={() => setActiveModal("voice")}
                className="w-full bg-gradient-to-r from-[#F97316] to-[#FB923C] hover:from-amber-600 hover:to-amber-500 text-slate-950 font-bold text-xs py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg shadow-orange-500/20 active:scale-[0.98] cursor-pointer"
              >
                <svg
                  className="w-4 h-4 text-slate-950"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                >
                  <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                </svg>
                <span>{t.card2Btn}</span>
              </button>
            </div>
          </div>

          {/* CARD 3: Document Doctor & Spelling Matcher */}
          <div className="group relative bg-[#111827]/80 backdrop-blur-md border border-[#1F2937] hover:border-[#10B981]/60 rounded-2xl p-6 flex flex-col justify-between shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
            {/* Top Emerald Green Glow Border */}
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#10B981] to-teal-400" />

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                {/* Document Doctor Icon */}
                <div className="w-12 h-12 rounded-xl bg-emerald-950/80 border border-emerald-800/50 flex items-center justify-center text-[#10B981] shadow-inner group-hover:scale-105 transition-transform">
                  <svg
                    className="w-6 h-6"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                    <line x1="9" y1="15" x2="15" y2="15" />
                    <line x1="12" y1="12" x2="12" y2="18" />
                  </svg>
                </div>

                <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-emerald-400 bg-emerald-950/80 px-2.5 py-1 rounded-full border border-emerald-900/50">
                  {t.card3Badge}
                </span>
              </div>

              <div>
                <h3 className="text-lg font-bold text-white group-hover:text-emerald-300 transition-colors">
                  {t.card3Title}
                </h3>
                <span className="text-xs font-semibold text-slate-400 block mb-2">
                  {t.card3Sub}
                </span>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {t.card3Desc}
                </p>
              </div>

              {/* Visual Matcher Demonstration Pill */}
              <div className="p-3 bg-[#161F30] border border-slate-700 rounded-xl space-y-1.5 text-xs">
                <div className="flex items-center justify-between text-slate-300">
                  <span className="text-slate-400 text-[10px]">
                    Ration Card:
                  </span>
                  <strong className="text-white font-mono">Sunita Devi</strong>
                </div>
                <div className="flex items-center justify-between text-slate-300">
                  <span className="text-slate-400 text-[10px]">
                    Bank Passbook:
                  </span>
                  <strong className="text-amber-300 font-mono">
                    Sunitha Devi
                  </strong>
                </div>
                <div className="pt-1 border-t border-slate-800 flex items-center justify-between text-[10px] text-emerald-400 font-semibold">
                  <span>Match Score: 95%</span>
                  <span className="text-slate-400">Auto-Correction Ready</span>
                </div>
              </div>
            </div>

            <div className="pt-6">
              <button
                type="button"
                onClick={() => setActiveModal("docDoctor")}
                className="w-full bg-[#10B981] hover:bg-emerald-600 text-slate-950 font-bold text-xs py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg shadow-emerald-500/20 active:scale-[0.98] cursor-pointer"
              >
                <svg
                  className="w-4 h-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
                <span>{t.card3Btn}</span>
              </button>
            </div>
          </div>
        </section>

        {/* 4. REPLAY SPLASH & FOOTER HELPER */}
        <section className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 pt-4 border-t border-[#1F2937]">
          <div>
            <span>
              BenefitBridge Gov-Tech Engine v2.4 • MeitY &amp; API Setu Verified
              Pipeline
            </span>
          </div>
          <button
            type="button"
            onClick={() => setShowSplash(true)}
            className="text-slate-400 hover:text-white flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <svg
              className="w-3.5 h-3.5 text-blue-400"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
            <span>{t.replaySplash}</span>
          </button>
        </section>
      </main>

      {/* 5. STATUTORY CITIZEN SLA GUARANTEE TICKER (Bottom Status Ribbon) */}
      <footer className="sticky bottom-0 z-30 bg-[#0B0F19]/90 backdrop-blur-md border-t border-[#1F2937] py-2.5 overflow-hidden">
        <div className="ticker-track flex items-center gap-8 text-xs font-mono text-slate-400">
          <div className="flex items-center gap-6 whitespace-nowrap">
            <span className="flex items-center gap-1.5 text-amber-300 font-bold">
              <span className="w-2 h-2 rounded-full bg-[#FB923C] animate-pulse" />
              <span>
                GUARANTEED STATUTORY DISPOSAL: 30 DAYS UNDER CITIZEN CHARTERS
              </span>
            </span>
            <span>•</span>
            <span className="text-emerald-400">
              100% CPGRAMS ESCALATION READY
            </span>
            <span>•</span>
            <span>ZERO AADHAAR NUMBERS STORED</span>
            <span>•</span>
            <span className="text-blue-400">
              DIRECT BENEFIT TRANSFER (DBT) PRE-VERIFIED
            </span>
            <span>•</span>
            <span className="text-slate-300">
              RIGHT TO PUBLIC SERVICES ACT SEC 4 COMPLIANT
            </span>
          </div>
          <div className="flex items-center gap-6 whitespace-nowrap">
            <span className="flex items-center gap-1.5 text-amber-300 font-bold">
              <span className="w-2 h-2 rounded-full bg-[#FB923C] animate-pulse" />
              <span>
                GUARANTEED STATUTORY DISPOSAL: 30 DAYS UNDER CITIZEN CHARTERS
              </span>
            </span>
            <span>•</span>
            <span className="text-emerald-400">
              100% CPGRAMS ESCALATION READY
            </span>
            <span>•</span>
            <span>ZERO AADHAAR NUMBERS STORED</span>
            <span>•</span>
            <span className="text-blue-400">
              DIRECT BENEFIT TRANSFER (DBT) PRE-VERIFIED
            </span>
            <span>•</span>
            <span className="text-slate-300">
              RIGHT TO PUBLIC SERVICES ACT SEC 4 COMPLIANT
            </span>
          </div>
        </div>
      </footer>

      {/* =====================================================================
          INTERACTIVE MODAL 1: DIGILOCKER DIRECT APPLY
          ===================================================================== */}
      {activeModal === "digilocker" && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
          <div className="bg-[#111827] border border-[#2563EB]/50 rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl relative">
            <button
              type="button"
              onClick={() => setActiveModal("none")}
              className="absolute top-4 right-4 text-slate-400 hover:text-white text-lg font-bold p-1 cursor-pointer"
            >
              &times;
            </button>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-900/60 border border-blue-600 flex items-center justify-center text-blue-300">
                <svg
                  className="w-5 h-5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z" />
                </svg>
              </div>
              <div>
                <h3 className="font-bold text-white text-base">
                  DigiLocker Authenticated Profile
                </h3>
                <span className="text-xs text-emerald-400 font-medium">
                  ✓ Cryptographic Digital Signature Verified
                </span>
              </div>
            </div>

            <div className="bg-[#161F30] p-4 rounded-xl border border-slate-700 space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Citizen Full Name:</span>
                <strong className="text-white">Sunita Devi</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">National SSO ID:</span>
                <span className="font-mono text-blue-300">DL-IND-8829103</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Welfare Scheme:</span>
                <strong className="text-amber-300">
                  Indira Gandhi National Widow Pension (IGNWPS)
                </strong>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Statutory SLA Timeline:</span>
                <span className="text-emerald-400 font-bold">
                  30 Days Guaranteed
                </span>
              </div>
            </div>

            {/* Pulled Documents */}
            <div className="space-y-2 text-xs">
              <span className="font-semibold text-slate-300 uppercase tracking-wider text-[10px]">
                Pulled Government Credentials:
              </span>
              <div className="p-3 bg-[#0B0F19] border border-slate-800 rounded-xl flex items-center justify-between">
                <div>
                  <div className="font-bold text-white">
                    Ration Card (NFSA / BPL)
                  </div>
                  <span className="text-[10px] text-slate-500">
                    Dept of Food &amp; Civil Supplies •
                    in.gov.dord.ration:10928374
                  </span>
                </div>
                <span className="text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded font-bold">
                  Pre-Verified
                </span>
              </div>
              <div className="p-3 bg-[#0B0F19] border border-slate-800 rounded-xl flex items-center justify-between">
                <div>
                  <div className="font-bold text-white">Income Certificate</div>
                  <span className="text-[10px] text-slate-500">
                    Revenue Dept • Annual Income: ₹0 (BPL / Eligible)
                  </span>
                </div>
                <span className="text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded font-bold">
                  Pre-Verified
                </span>
              </div>
            </div>

            <div className="pt-2 flex gap-3">
              <button
                type="button"
                onClick={() => {
                  setActiveTrackedApp({
                    id: "APP-DL-WIDOW-9214",
                    applicant: "Sunita Devi",
                    scheme:
                      "Indira Gandhi National Widow Pension Scheme (IGNWPS)",
                    status: "Submitted",
                    slaDaysTotal: 30,
                    slaDaysRemaining: 30,
                    targetDate: "13-Nov-2026",
                    dbtStatus: "Linked",
                  })
                  setActiveModal("tracker")
                }}
                className="w-full bg-[#2563EB] hover:bg-blue-600 text-white font-bold text-xs py-3 rounded-xl transition cursor-pointer"
              >
                Confirm &amp; Generate Tracked Application
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =====================================================================
          INTERACTIVE MODAL 2: BILINGUAL VOICE NAVIGATOR
          ===================================================================== */}
      {activeModal === "voice" && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
          <div className="bg-[#111827] border border-[#FB923C]/50 rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl relative">
            <button
              type="button"
              onClick={() => setActiveModal("none")}
              className="absolute top-4 right-4 text-slate-400 hover:text-white text-lg font-bold p-1 cursor-pointer"
            >
              &times;
            </button>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-950 border border-amber-600 flex items-center justify-center text-[#FB923C]">
                <svg
                  className="w-5 h-5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                </svg>
              </div>
              <div>
                <h3 className="font-bold text-white text-base">
                  Bilingual Voice Intake Engine
                </h3>
                <span className="text-xs text-amber-400 font-medium">
                  Whisper Model • Aadhaar Scrubbed Real-Time
                </span>
              </div>
            </div>

            {/* Microphone Visualizer Circle */}
            <div className="py-6 flex flex-col items-center justify-center space-y-3">
              <button
                type="button"
                onClick={() => {
                  setIsRecording(!isRecording)
                  setVoiceStep("listening")
                  setTimeout(() => setVoiceStep("processed"), 1800)
                }}
                className={`w-20 h-20 rounded-full flex items-center justify-center transition-all cursor-pointer ${
                  isRecording
                    ? "bg-rose-600 animate-pulse ring-8 ring-rose-500/30 text-white"
                    : "bg-[#FB923C] hover:bg-amber-500 text-slate-950 ring-4 ring-[#FB923C]/20"
                }`}
              >
                <svg
                  className="w-8 h-8"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                >
                  <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                </svg>
              </button>
              <span className="text-xs font-mono text-slate-400">
                {isRecording
                  ? "Listening... (Speaking in Hindi / English)"
                  : "Click mic to speak or select a sample"}
              </span>
            </div>

            {/* Quick Sample Prompts */}
            <div className="space-y-2 text-xs">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">
                Try Sample Voice Recitation:
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setActiveAudioPrompt("widow")
                    setVoiceStep("processed")
                  }}
                  className={`p-2.5 rounded-xl border text-left cursor-pointer transition ${
                    activeAudioPrompt === "widow"
                      ? "bg-amber-950/60 border-[#FB923C] text-amber-200"
                      : "bg-[#161F30] border-slate-700 text-slate-300"
                  }`}
                >
                  <div className="font-bold text-[11px]">
                    Hindi: Sunita Devi (65y)
                  </div>
                  <div className="text-[10px] text-slate-400">
                    "मैं सुनीता देवी, 65 वर्ष, विधवा पेंशन..."
                  </div>
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setActiveAudioPrompt("scholarship")
                    setVoiceStep("processed")
                  }}
                  className={`p-2.5 rounded-xl border text-left cursor-pointer transition ${
                    activeAudioPrompt === "scholarship"
                      ? "bg-amber-950/60 border-[#FB923C] text-amber-200"
                      : "bg-[#161F30] border-slate-700 text-slate-300"
                  }`}
                >
                  <div className="font-bold text-[11px]">
                    English: SC Scholarship
                  </div>
                  <div className="text-[10px] text-slate-400">
                    "I am SC student Amit, income 80k..."
                  </div>
                </button>
              </div>
            </div>

            {/* Extracted Entity Preview */}
            {voiceStep === "processed" && (
              <div className="p-3.5 bg-[#0B0F19] border border-emerald-500/40 rounded-xl space-y-1.5 text-xs animate-fade-in">
                <div className="text-[10px] font-bold text-emerald-400 uppercase flex items-center justify-between">
                  <span>✓ Extracted Demographic Profile</span>
                  <span className="text-slate-400">Confidence: 99.2%</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-slate-300 pt-1">
                  <div>
                    Age:{" "}
                    <strong className="text-white">
                      {activeAudioPrompt === "widow" ? "65 Years" : "20 Years"}
                    </strong>
                  </div>
                  <div>
                    Gender:{" "}
                    <strong className="text-white">
                      {activeAudioPrompt === "widow" ? "Female" : "Male"}
                    </strong>
                  </div>
                  <div>
                    Marital:{" "}
                    <strong className="text-white">
                      {activeAudioPrompt === "widow" ? "Widow" : "Single"}
                    </strong>
                  </div>
                  <div>
                    Income:{" "}
                    <strong className="text-white">
                      {activeAudioPrompt === "widow" ? "₹0 (Nil)" : "₹80,000"}
                    </strong>
                  </div>
                </div>
                <div className="pt-2 text-[11px] text-amber-300 font-semibold border-t border-slate-800">
                  Target Scheme:{" "}
                  {activeAudioPrompt === "widow"
                    ? "Indira Gandhi National Widow Pension (IGNWPS)"
                    : "Post-Matric Scholarship"}
                </div>
              </div>
            )}

            <div className="pt-2 flex gap-3">
              <button
                type="button"
                onClick={() => {
                  setActiveTrackedApp({
                    id: "APP-VOICE-8819",
                    applicant:
                      activeAudioPrompt === "widow"
                        ? "Sunita Devi"
                        : "Amit Kumar",
                    scheme:
                      activeAudioPrompt === "widow"
                        ? "Indira Gandhi National Widow Pension Scheme"
                        : "Post-Matric Scholarship",
                    status: "Submitted",
                    slaDaysTotal: 30,
                    slaDaysRemaining: 30,
                    targetDate: "13-Nov-2026",
                    dbtStatus: "Linked",
                  })
                  setActiveModal("tracker")
                }}
                className="w-full bg-[#FB923C] hover:bg-amber-500 text-slate-950 font-bold text-xs py-3 rounded-xl transition cursor-pointer"
              >
                Submit Voice Application Under Citizen Charter
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =====================================================================
          INTERACTIVE MODAL 3: DOCUMENT DOCTOR & SPELLING MATCHER
          ===================================================================== */}
      {activeModal === "docDoctor" && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
          <div className="bg-[#111827] border border-[#10B981]/50 rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl relative">
            <button
              type="button"
              onClick={() => setActiveModal("none")}
              className="absolute top-4 right-4 text-slate-400 hover:text-white text-lg font-bold p-1 cursor-pointer"
            >
              &times;
            </button>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-950 border border-emerald-600 flex items-center justify-center text-[#10B981]">
                <svg
                  className="w-5 h-5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
              </div>
              <div>
                <h3 className="font-bold text-white text-base">
                  Document Doctor Mismatch Analyzer
                </h3>
                <span className="text-xs text-emerald-400 font-medium">
                  PFMS / DBT Bank Discrepancy Prevention
                </span>
              </div>
            </div>

            {/* Comparison Table */}
            <div className="bg-[#161F30] p-4 rounded-xl border border-slate-700 space-y-3 text-xs">
              <div className="flex items-center justify-between pb-2 border-b border-slate-700">
                <span className="text-slate-400">Identity Source:</span>
                <span className="text-slate-400">Extracted Name String:</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-semibold text-white">
                  Ration Card (NFSA)
                </span>
                <span className="font-mono bg-slate-900 px-2 py-0.5 rounded text-blue-300">
                  Sunita Devi
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-semibold text-white">
                  SBI Bank Passbook
                </span>
                <span className="font-mono bg-slate-900 px-2 py-0.5 rounded text-amber-300">
                  Sunitha Devi
                </span>
              </div>
              <div className="pt-2 border-t border-slate-700 flex items-center justify-between">
                <span className="text-slate-400">Levenshtein Distance:</span>
                <span className="text-emerald-400 font-bold">
                  1 character ('h' variation)
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Soundex Phonetic Code:</span>
                <span className="text-emerald-400 font-bold">
                  S530 (Exact Match)
                </span>
              </div>
            </div>

            {/* Warning Note */}
            <div className="p-3 bg-amber-950/40 border border-amber-600/40 rounded-xl text-xs text-amber-200 leading-relaxed">
              <strong>BenefitBridge Assessment:</strong> Minor spelling
              variation noted. BenefitBridge does NOT reject your application,
              but resolving this difference now will prevent direct benefit
              transfer (DBT) bank delays later.
            </div>

            <div className="pt-2 flex gap-3">
              <button
                type="button"
                onClick={() => setActiveModal("none")}
                className="w-full bg-[#10B981] hover:bg-emerald-600 text-slate-950 font-bold text-xs py-3 rounded-xl transition cursor-pointer"
              >
                Attach Auto-Generated Name Variation Affidavit &rarr;
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =====================================================================
          INTERACTIVE MODAL 4: APPLICATION TRACKER & SLA DRAWER
          ===================================================================== */}
      {activeModal === "tracker" && activeTrackedApp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
          <div className="bg-[#111827] border border-[#2563EB]/50 rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl relative">
            <button
              type="button"
              onClick={() => setActiveModal("none")}
              className="absolute top-4 right-4 text-slate-400 hover:text-white text-lg font-bold p-1 cursor-pointer"
            >
              &times;
            </button>

            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase">
                  Application Reference
                </span>
                <div className="font-mono text-lg font-black text-white flex items-center gap-2">
                  <span>{activeTrackedApp.id}</span>
                  <button
                    type="button"
                    onClick={() => handleCopyToken(activeTrackedApp.id)}
                    className="text-xs bg-slate-800 hover:bg-slate-700 px-2 py-0.5 rounded text-slate-300 cursor-pointer"
                  >
                    {copiedToken ? "✓ Copied" : "Copy"}
                  </button>
                </div>
              </div>
              <span className="bg-blue-950 text-blue-300 border border-blue-800 text-xs font-bold px-3 py-1 rounded-full">
                {activeTrackedApp.status}
              </span>
            </div>

            <div className="bg-[#161F30] p-4 rounded-xl border border-slate-700 space-y-2.5 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Applicant Name:</span>
                <strong className="text-white">
                  {activeTrackedApp.applicant}
                </strong>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Welfare Scheme:</span>
                <span className="text-slate-200 text-right max-w-xs">
                  {activeTrackedApp.scheme}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Statutory SLA Window:</span>
                <span className="text-blue-300 font-bold">
                  {activeTrackedApp.slaDaysTotal} Days Guaranteed
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Resolution Deadline:</span>
                <span className="text-emerald-400 font-bold">
                  {activeTrackedApp.targetDate}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Bank DBT Status:</span>
                <span
                  className={
                    activeTrackedApp.dbtStatus === "Linked"
                      ? "text-emerald-400 font-bold"
                      : "text-amber-400 font-bold"
                  }
                >
                  {activeTrackedApp.dbtStatus}
                </span>
              </div>
            </div>

            {/* SLA Progress Bar */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400 font-semibold">
                  Statutory SLA Progress:
                </span>
                <span className="text-emerald-400 font-bold">
                  {activeTrackedApp.slaDaysRemaining} Days Left
                </span>
              </div>
              <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-emerald-500 to-blue-500 rounded-full"
                  style={{
                    width: `${Math.round(
                      ((activeTrackedApp.slaDaysTotal -
                        activeTrackedApp.slaDaysRemaining) /
                        activeTrackedApp.slaDaysTotal) *
                        100,
                    )}%`,
                  }}
                />
              </div>
            </div>

            <div className="pt-2 flex gap-3">
              <button
                type="button"
                onClick={() => setActiveModal("none")}
                className="w-full bg-[#111827] hover:bg-[#161F30] border border-slate-700 text-slate-300 font-bold text-xs py-3 rounded-xl transition cursor-pointer"
              >
                Close Tracker
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
export default App
