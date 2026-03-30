import { useEffect, useRef } from "react";

const CAR_COLOR = "#F97316";
const TRACK_RADIUS = 80;
const ANIMATION_DURATION = 2.5; // seconds per lap

function SportsCarSVG({ color }) {
  return (
    <g>
      {/* Body */}
      <rect x="-22" y="-8" width="44" height="13" rx="4" fill={color} />
      {/* Cabin */}
      <path d="M-8,-8 L-14,-18 L8,-18 L14,-8 Z" fill={color} />
      {/* Windshield */}
      <path d="M-6,-9 L-11,-17 L6,-17 L11,-9 Z" fill="#1e293b" opacity="0.7" />
      {/* Front bumper */}
      <rect x="18" y="-4" width="6" height="8" rx="2" fill={color} />
      {/* Rear bumper */}
      <rect x="-24" y="-4" width="4" height="8" rx="2" fill={color} />
      {/* Spoiler */}
      <rect x="-22" y="-12" width="8" height="2" rx="1" fill={color} />
      <rect x="-20" y="-16" width="12" height="2" rx="1" fill={color} />
      {/* Front wheel */}
      <circle cx="14" cy="6" r="5" fill="#1e293b" />
      <circle cx="14" cy="6" r="2.5" fill="#94a3b8" />
      {/* Rear wheel */}
      <circle cx="-12" cy="6" r="5" fill="#1e293b" />
      <circle cx="-12" cy="6" r="2.5" fill="#94a3b8" />
      {/* Headlight */}
      <rect x="22" y="-3" width="3" height="4" rx="1" fill="#fef08a" />
      {/* Tail light */}
      <rect x="-24" y="-3" width="2" height="4" rx="1" fill="#ef4444" />
      {/* Speed lines */}
      <line x1="-26" y1="-2" x2="-34" y2="-2" stroke="#94a3b8" strokeWidth="1.5" strokeLinecap="round" opacity="0.5" />
      <line x1="-26" y1="2" x2="-32" y2="2" stroke="#94a3b8" strokeWidth="1" strokeLinecap="round" opacity="0.4" />
      <line x1="-26" y1="-5" x2="-30" y2="-5" stroke="#94a3b8" strokeWidth="1" strokeLinecap="round" opacity="0.3" />
    </g>
  );
}

export default function SportsCarLoader({ size = 240 }) {
  const carGroupRef = useRef(null);
  const trailRef = useRef(null);
  const startTimeRef = useRef(null);
  const frameRef = useRef(null);

  const cx = size / 2;
  const cy = size / 2;
  const r = TRACK_RADIUS;

  useEffect(() => {
    const duration = ANIMATION_DURATION * 1000;

    function animate(timestamp) {
      if (!startTimeRef.current) startTimeRef.current = timestamp;
      const elapsed = timestamp - startTimeRef.current;
      const progress = (elapsed % duration) / duration; // 0 to 1
      const angle = progress * 2 * Math.PI - Math.PI / 2; // start at top

      const x = cx + r * Math.cos(angle);
      const y = cy + r * Math.sin(angle);
      const rotateDeg = (angle * 180) / Math.PI + 90; // car faces tangent direction

      if (carGroupRef.current) {
        carGroupRef.current.setAttribute(
          "transform",
          `translate(${x}, ${y}) rotate(${rotateDeg})`
        );
      }

      // Update dashed arc trail: strokeDashoffset goes from full circumference to 0
      if (trailRef.current) {
        const circumference = 2 * Math.PI * r;
        const trailLength = progress * circumference;
        trailRef.current.setAttribute("stroke-dasharray", `${trailLength} ${circumference}`);
        // rotate so the trail starts at the top
        trailRef.current.setAttribute(
          "transform",
          `rotate(-90, ${cx}, ${cy})`
        );
      }

      frameRef.current = requestAnimationFrame(animate);
    }

    frameRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frameRef.current);
  }, [cx, cy, r]);

  const circumference = 2 * Math.PI * r;

  return (
    <div
      style={{
        display: "inline-flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 12,
      }}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Background track */}
        <circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth="6"
        />

        {/* Trail arc */}
        <circle
          ref={trailRef}
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke={CAR_COLOR}
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={`0 ${circumference}`}
          opacity="0.35"
        />

        {/* Car */}
        <g ref={carGroupRef}>
          <SportsCarSVG color={CAR_COLOR} />
        </g>
      </svg>
      <span
        style={{
          fontFamily: "system-ui, sans-serif",
          fontSize: 14,
          fontWeight: 600,
          color: CAR_COLOR,
          letterSpacing: "0.1em",
          textTransform: "uppercase",
        }}
      >
        Loading...
      </span>
    </div>
  );
}
