import React, { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { getPortalUrl } from "../lib/urls";

gsap.registerPlugin(ScrollTrigger);

// Seeded bar widths for stable, deterministic barcode rendering
const BARCODE_SEEDS = [
  [2, 1, 3, 1, 2, 4, 1, 2, 3, 1, 1, 4, 2, 1, 3, 2, 1, 4, 1, 2, 3],
  [3, 1, 2, 4, 1, 1, 3, 2, 1, 4, 2, 1, 2, 3, 1, 4, 1, 2, 1, 3, 2],
  [1, 4, 2, 1, 3, 2, 1, 3, 4, 1, 2, 1, 4, 2, 3, 1, 1, 2, 4, 1, 2],
];

interface BarcodeProps {
  seed: number[];
  isFlickering: boolean;
}

const Barcode: React.FC<BarcodeProps> = ({ seed, isFlickering }) => {
  let currentX = 2;
  const rects = seed.map((width, idx) => {
    const x = currentX;
    currentX += width * 2.1 + 1.8;
    return (
      <rect
        key={idx}
        x={x}
        y="0"
        width={width * 1.7}
        height="22"
        fill="#C41528"
      />
    );
  });

  return (
    <svg
      width={currentX + 4}
      height="22"
      className={`mx-auto transition-opacity duration-150 ${
        isFlickering ? "opacity-25" : "opacity-100"
      }`}
      aria-hidden="true"
    >
      {rects}
    </svg>
  );
};

export const Section4JourneyTickets: React.FC = () => {
  const sectionRef = useRef<HTMLElement | null>(null);
  const pinContainerRef = useRef<HTMLDivElement | null>(null);
  const cardsWrapRef = useRef<HTMLDivElement | null>(null);

  const card1Ref = useRef<HTMLDivElement | null>(null);
  const card2Ref = useRef<HTMLDivElement | null>(null);
  const card3Ref = useRef<HTMLDivElement | null>(null);

  const [flickeringCard, setFlickeringCard] = useState<number | null>(null);
  const [isThirdStubTorn, setIsThirdStubTorn] = useState<boolean>(false);

  // Hover 3D cursor tilt (desktop only)
  const handleCardMouseMove = (
    e: React.MouseEvent<HTMLDivElement>,
    cardEl: HTMLDivElement | null
  ) => {
    if (!cardEl || window.innerWidth < 768) return;
    const rect = cardEl.getBoundingClientRect();
    const relX = (e.clientX - rect.left) / rect.width - 0.5;
    const relY = (e.clientY - rect.top) / rect.height - 0.5;

    gsap.to(cardEl, {
      rotateY: relX * 12, // -6deg to +6deg
      rotateX: -relY * 12, // -6deg to +6deg
      duration: 0.25,
      ease: "power2.out",
      overwrite: "auto",
    });
  };

  const handleCardMouseLeave = (cardEl: HTMLDivElement | null) => {
    if (!cardEl || window.innerWidth < 768) return;
    gsap.to(cardEl, {
      rotateY: 0,
      rotateX: 0,
      duration: 0.45,
      ease: "power2.out",
      overwrite: "auto",
    });
  };

  const triggerFlicker = (cardIdx: number) => {
    setFlickeringCard(cardIdx);
    setTimeout(() => {
      setFlickeringCard(null);
    }, 220);
  };

  useEffect(() => {
    const prefersReducedMotion =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (prefersReducedMotion) {
      if (card1Ref.current && card2Ref.current && card3Ref.current) {
        gsap.set([card1Ref.current, card2Ref.current, card3Ref.current], {
          y: 0,
          x: 0,
          rotateX: 0,
          rotateY: 0,
          rotateZ: 0,
          scale: 1,
          opacity: 1,
        });
      }
      return;
    }

    const ctx = gsap.context(() => {
      const isMobile = window.innerWidth < 768;

      if (isMobile) {
        // Mobile stack animation without 3D tilt
        const cards = [card1Ref.current, card2Ref.current, card3Ref.current];
        cards.forEach((card) => {
          if (!card) return;
          gsap.fromTo(
            card,
            { y: 80, opacity: 0 },
            {
              y: 0,
              opacity: 1,
              duration: 0.8,
              ease: "power3.out",
              scrollTrigger: {
                trigger: card,
                start: "top 85%",
                toggleActions: "play none none none",
              },
            }
          );
        });
        return;
      }

      // Desktop: Pinned 250vh with 3D flying entry
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top top",
          end: "+=250%",
          pin: pinContainerRef.current,
          scrub: 1.2,
          anticipatePin: 1,
        },
      });

      // Start positions from specification:
      gsap.set(card1Ref.current, {
        y: "120vh",
        x: "-30vw",
        rotateX: 60,
        rotateY: -35,
        rotateZ: -12,
        scale: 0.8,
        transformOrigin: "center center",
      });

      gsap.set(card2Ref.current, {
        y: "120vh",
        x: "0vw",
        rotateX: 60,
        rotateY: 0,
        rotateZ: 6,
        scale: 0.8,
        transformOrigin: "center center",
      });

      gsap.set(card3Ref.current, {
        y: "120vh",
        x: "30vw",
        rotateX: 60,
        rotateY: 35,
        rotateZ: 12,
        scale: 0.8,
        transformOrigin: "center center",
      });

      // Fly into row with power3.out, stagger 0.15, scrubbed to scroll
      tl.to(
        card1Ref.current,
        {
          y: "0vh",
          x: "0vw",
          rotateX: 0,
          rotateY: 0,
          rotateZ: 0,
          scale: 1,
          ease: "power3.out",
          duration: 0.75,
        },
        0
      );

      tl.to(
        card2Ref.current,
        {
          y: "0vh",
          x: "0vw",
          rotateX: 0,
          rotateY: 0,
          rotateZ: 0,
          scale: 1,
          ease: "power3.out",
          duration: 0.75,
        },
        0.15
      );

      tl.to(
        card3Ref.current,
        {
          y: "0vh",
          x: "0vw",
          rotateX: 0,
          rotateY: 0,
          rotateZ: 0,
          scale: 1,
          ease: "power3.out",
          duration: 0.75,
        },
        0.3
      );

      // Overshoot tilt on the third ticket at the end
      tl.to(
        card3Ref.current,
        {
          rotateZ: 3.5,
          rotateY: -3,
          duration: 0.2,
          ease: "power2.out",
        },
        0.85
      );

      tl.to(
        card3Ref.current,
        {
          rotateZ: 0,
          rotateY: 0,
          duration: 0.15,
          ease: "power2.inOut",
        },
        1.05
      );
    }, sectionRef);

    return () => {
      ctx.revert();
    };
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative w-full min-h-[350vh] bg-gradient-to-b from-white via-[#FFF8F8] to-white overflow-hidden border-t border-b border-[#1A0F12]/10"
      aria-label="Section 4: The Journey Tickets"
    >
      {/* Soft warm red bottom glow */}
      <div
        className="absolute inset-x-0 bottom-0 h-[50vh] pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse 110% 85% at 50% 100%, #FECACA 0%, rgba(254, 226, 226, 0.4) 50%, transparent 80%)",
        }}
        aria-hidden="true"
      />

      {/* ---------------- PINNED VIEWPORT CONTAINER ---------------- */}
      <div
        ref={pinContainerRef}
        className="w-full h-screen relative flex flex-col justify-between items-center py-8 sm:py-12 px-4 sm:px-8 overflow-hidden"
      >
        {/* 1. TOP PILL LABEL IN WHITE & RED */}
        <div className="z-20 text-center">
          <div className="inline-flex items-center gap-2 px-5 py-1.5 rounded-full border border-[#C41528]/35 bg-white shadow-xs">
            <span className="font-serif-italic italic text-[#C41528] text-base tracking-wide font-normal">
              The journey
            </span>
          </div>
        </div>

        {/* 2. THREE TICKET CARDS CONTAINER (Perspective 1200px) */}
        <div
          ref={cardsWrapRef}
          className="w-full max-w-6xl mx-auto z-20 my-auto"
          style={{ perspective: "1200px" }}
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 items-stretch">
            {/* ---------------- TICKET 1: ELIGIBILITY ---------------- */}
            <div
              ref={card1Ref}
              onMouseMove={(e) => handleCardMouseMove(e, card1Ref.current)}
              onMouseEnter={() => triggerFlicker(0)}
              onMouseLeave={() => handleCardMouseLeave(card1Ref.current)}
              className="bg-white rounded-3xl shadow-[0_20px_50px_rgba(0,0,0,0.10)] border border-[#1A0F12]/12 flex flex-col justify-between overflow-hidden transition-all duration-300 hover:border-[#C41528]/40 hover:shadow-[0_25px_60px_rgba(196,21,40,0.12)] will-change-transform"
              style={{ transformStyle: "preserve-3d" }}
            >
              {/* Top part */}
              <div className="p-6 sm:p-7 flex-1 flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-mono text-[#C41528] tracking-widest uppercase block mb-1">
                    Stage 01
                  </span>
                  <h3 className="font-serif-italic italic text-[28px] text-[#C41528] leading-tight font-normal">
                    Eligibility
                  </h3>
                  <p className="text-xs text-[#1A0F12]/75 font-light leading-relaxed mt-2.5 mb-6">
                    Fixed, source-linked rules tell Sunita if she may qualify, and show why.
                  </p>
                </div>

                {/* Bullets with small red arrows */}
                <ul className="space-y-3 text-xs text-[#1A0F12]/85">
                  <li className="flex items-start gap-2.5">
                    <span className="text-[#C41528] font-bold text-sm leading-none mt-0.5">
                      →
                    </span>
                    <span>Hindi voice or tap input</span>
                  </li>
                  <li className="flex items-start gap-2.5">
                    <span className="text-[#C41528] font-bold text-sm leading-none mt-0.5">
                      →
                    </span>
                    <span>Why? panel with the official source</span>
                  </li>
                  <li className="flex items-start gap-2.5">
                    <span className="text-[#C41528] font-bold text-sm leading-none mt-0.5">
                      →
                    </span>
                    <span>Never says "approved"</span>
                  </li>
                </ul>
              </div>

              {/* Dashed perforation line with semicircle notches */}
              <div className="relative flex items-center w-full my-1">
                <div className="w-5 h-5 rounded-full bg-[#FFF5F5] border-r border-[#1A0F12]/15 -ml-2.5" />
                <div className="flex-1 border-t-2 border-dashed border-[#C41528]/30 mx-1" />
                <div className="w-5 h-5 rounded-full bg-[#FFF5F5] border-l border-[#1A0F12]/15 -mr-2.5" />
              </div>

              {/* Bottom Stub */}
              <div className="p-5 sm:p-6 bg-[#FFFDFC] border-t border-[#1A0F12]/5 text-center space-y-2">
                <span className="text-[10px] font-mono text-[#8E1B2B] uppercase tracking-wider block font-semibold">
                  Next step: check eligibility
                </span>
                <Barcode seed={BARCODE_SEEDS[0]} isFlickering={flickeringCard === 0} />
                <p className="text-[9px] font-sans text-[#1A0F12]/60 tracking-tight pt-1">
                  Rules decide. AI only explains.
                </p>
              </div>
            </div>

            {/* ---------------- TICKET 2: DOCUMENT DOCTOR ---------------- */}
            <div
              ref={card2Ref}
              onMouseMove={(e) => handleCardMouseMove(e, card2Ref.current)}
              onMouseEnter={() => triggerFlicker(1)}
              onMouseLeave={() => handleCardMouseLeave(card2Ref.current)}
              className="bg-white rounded-3xl shadow-[0_20px_50px_rgba(0,0,0,0.10)] border border-[#1A0F12]/12 flex flex-col justify-between overflow-hidden transition-all duration-300 hover:border-[#C41528]/40 hover:shadow-[0_25px_60px_rgba(196,21,40,0.12)] will-change-transform"
              style={{ transformStyle: "preserve-3d" }}
            >
              {/* Top part */}
              <div className="p-6 sm:p-7 flex-1 flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-mono text-[#C41528] tracking-widest uppercase block mb-1">
                    Stage 02
                  </span>
                  <h3 className="font-serif-italic italic text-[28px] text-[#C41528] leading-tight font-normal">
                    Document Doctor
                  </h3>
                  <p className="text-xs text-[#1A0F12]/75 font-light leading-relaxed mt-2.5 mb-6">
                    Reads the name on her documents and flags possible mismatches.
                  </p>
                </div>

                {/* Bullets with small red arrows */}
                <ul className="space-y-3 text-xs text-[#1A0F12]/85">
                  <li className="flex items-start gap-2.5">
                    <span className="text-[#C41528] font-bold text-sm leading-none mt-0.5">
                      →
                    </span>
                    <span>Reads ration card and passbook</span>
                  </li>
                  <li className="flex items-start gap-2.5">
                    <span className="text-[#C41528] font-bold text-sm leading-none mt-0.5">
                      →
                    </span>
                    <span>She confirms every detail</span>
                  </li>
                  <li className="flex items-start gap-2.5">
                    <span className="text-[#C41528] font-bold text-sm leading-none mt-0.5">
                      →
                    </span>
                    <span>Never called fraud</span>
                  </li>
                </ul>
              </div>

              {/* Dashed perforation line with semicircle notches */}
              <div className="relative flex items-center w-full my-1">
                <div className="w-5 h-5 rounded-full bg-[#FFF5F5] border-r border-[#1A0F12]/15 -ml-2.5" />
                <div className="flex-1 border-t-2 border-dashed border-[#C41528]/30 mx-1" />
                <div className="w-5 h-5 rounded-full bg-[#FFF5F5] border-l border-[#1A0F12]/15 -mr-2.5" />
              </div>

              {/* Bottom Stub */}
              <div className="p-5 sm:p-6 bg-[#FFFDFC] border-t border-[#1A0F12]/5 text-center space-y-2">
                <span className="text-[10px] font-mono text-[#8E1B2B] uppercase tracking-wider block font-semibold">
                  Next step: fix the name
                </span>
                <Barcode seed={BARCODE_SEEDS[1]} isFlickering={flickeringCard === 1} />
                <p className="text-[9px] font-sans text-[#1A0F12]/60 tracking-tight pt-1">
                  Rules decide. AI only explains.
                </p>
              </div>
            </div>

            {/* ---------------- TICKET 3: COMPLAINT (WITH TEAR-OFF STUB) ---------------- */}
            <div
              ref={card3Ref}
              onMouseMove={(e) => handleCardMouseMove(e, card3Ref.current)}
              onMouseEnter={() => triggerFlicker(2)}
              onMouseLeave={() => handleCardMouseLeave(card3Ref.current)}
              className="bg-white rounded-3xl shadow-[0_20px_50px_rgba(0,0,0,0.10)] border border-[#1A0F12]/12 flex flex-col justify-between overflow-hidden transition-all duration-300 hover:border-[#C41528]/40 hover:shadow-[0_25px_60px_rgba(196,21,40,0.12)] will-change-transform relative"
              style={{ transformStyle: "preserve-3d" }}
            >
              {/* Top part */}
              <div className="p-6 sm:p-7 flex-1 flex flex-col justify-between">
                <div>
                  <span className="text-[10px] font-mono text-[#C41528] tracking-widest uppercase block mb-1">
                    Stage 03
                  </span>
                  <h3 className="font-serif-italic italic text-[28px] text-[#C41528] leading-tight font-normal">
                    Complaint
                  </h3>
                  <p className="text-xs text-[#1A0F12]/75 font-light leading-relaxed mt-2.5 mb-6">
                    A Hindi draft from verified facts, filed by her, never automatically.
                  </p>
                </div>

                {/* Bullets with small red arrows */}
                <ul className="space-y-3 text-xs text-[#1A0F12]/85">
                  <li className="flex items-start gap-2.5">
                    <span className="text-[#C41528] font-bold text-sm leading-none mt-0.5">
                      →
                    </span>
                    <span>She reads and approves</span>
                  </li>
                  <li className="flex items-start gap-2.5">
                    <span className="text-[#C41528] font-bold text-sm leading-none mt-0.5">
                      →
                    </span>
                    <span>Opens the official portal</span>
                  </li>
                  <li className="flex items-start gap-2.5">
                    <span className="text-[#C41528] font-bold text-sm leading-none mt-0.5">
                      →
                    </span>
                    <span>21-day follow-up reminder</span>
                  </li>
                </ul>
              </div>

              {/* Dashed perforation line with semicircle notches */}
              <div className="relative flex items-center w-full my-1">
                <div className="w-5 h-5 rounded-full bg-[#FFF5F5] border-r border-[#1A0F12]/15 -ml-2.5" />
                <div className="flex-1 border-t-2 border-dashed border-[#C41528]/30 mx-1" />
                <div className="w-5 h-5 rounded-full bg-[#FFF5F5] border-l border-[#1A0F12]/15 -mr-2.5" />
              </div>

              {/* Bottom Stub with Tear-Off Interaction */}
              <div
                onClick={() => setIsThirdStubTorn((prev) => !prev)}
                className={`p-5 sm:p-6 bg-[#FFFDFC] border-t border-[#1A0F12]/5 text-center space-y-2 cursor-pointer transition-all duration-300 origin-top-left ${
                  isThirdStubTorn
                    ? "rotate-8 translate-y-3 bg-[#FFF5F4] shadow-md border-[#C41528]/30"
                    : "hover:bg-[#FFF9F8]"
                }`}
                title="Click to tear off stub"
              >
                <div className="flex items-center justify-between px-1">
                  <span className="text-[10px] font-mono text-[#8E1B2B] uppercase tracking-wider font-semibold">
                    Next step: escalate
                  </span>
                  <span className="text-[9px] text-[#C41528] font-mono underline font-medium">
                    {isThirdStubTorn ? "Torn" : "Click to tear ✂"}
                  </span>
                </div>

                <Barcode seed={BARCODE_SEEDS[2]} isFlickering={flickeringCard === 2} />

                {/* Exposed Red Demo Button when stub tears off */}
                {isThirdStubTorn ? (
                  <div className="pt-2 animate-fadeIn">
                    <a
                      href={getPortalUrl()}
                      onClick={(e) => e.stopPropagation()}
                      className="min-h-[44px] w-full px-4 py-2.5 rounded-xl bg-[#C41528] hover:bg-[#8E1B2B] text-white text-xs font-bold transition-all shadow-md inline-flex items-center justify-center gap-1.5 cursor-pointer active:scale-98"
                    >
                      <span>Try the demo</span>
                      <span aria-hidden="true">→</span>
                    </a>
                  </div>
                ) : (
                  <p className="text-[9px] font-sans text-[#1A0F12]/60 tracking-tight pt-1">
                    Rules decide. AI only explains.
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* 3. FOOTER LINE UNDER THE CARDS */}
        <div className="z-20 text-center">
          <p className="font-serif-italic italic text-[#8E1B2B]/75 text-xs sm:text-sm tracking-wide select-none">
            Prototype with dummy data.
          </p>
        </div>
      </div>
    </section>
  );
};

export default Section4JourneyTickets;
