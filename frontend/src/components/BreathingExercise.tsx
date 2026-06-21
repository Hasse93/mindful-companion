"use client";

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

type Phase = { label: string; seconds: number; scale: number };

// Box-breathing: inhale 4 · hold 4 · exhale 4 · hold 4.
const PHASES: Phase[] = [
  { label: "Breathe in", seconds: 4, scale: 1.35 },
  { label: "Hold", seconds: 4, scale: 1.35 },
  { label: "Breathe out", seconds: 4, scale: 1 },
  { label: "Hold", seconds: 4, scale: 1 },
];

export default function BreathingExercise() {
  const [running, setRunning] = useState(false);
  const [phaseIdx, setPhaseIdx] = useState(0);
  const [cycles, setCycles] = useState(0);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!running) return;
    const phase = PHASES[phaseIdx];
    timer.current = setTimeout(() => {
      const next = (phaseIdx + 1) % PHASES.length;
      setPhaseIdx(next);
      if (next === 0) setCycles((c) => c + 1);
    }, phase.seconds * 1000);
    return () => {
      if (timer.current) clearTimeout(timer.current);
    };
  }, [running, phaseIdx]);

  function toggle() {
    if (running) {
      setRunning(false);
      setPhaseIdx(0);
    } else {
      setCycles(0);
      setPhaseIdx(0);
      setRunning(true);
    }
  }

  const phase = PHASES[phaseIdx];

  return (
    <div className="flex flex-col items-center p-6">
      <h2 className="text-base font-semibold">Box breathing</h2>
      <p className="mt-0.5 text-sm text-soft">Follow the orb to settle your breath.</p>

      <div className="relative my-7 grid h-48 w-48 place-items-center">
        <motion.div
          className="absolute h-40 w-40 rounded-full"
          style={{ background: "radial-gradient(circle at 35% 30%, #7ee0c1, #7f77dd)" }}
          animate={{ scale: running ? phase.scale : 1, opacity: running ? 0.95 : 0.7 }}
          transition={{ duration: running ? phase.seconds : 0.6, ease: "easeInOut" }}
        />
        <div className="z-10 text-center">
          <p className="text-lg font-medium text-white drop-shadow">
            {running ? phase.label : "Ready?"}
          </p>
          {running && <p className="text-sm text-white/80">{cycles} cycles</p>}
        </div>
      </div>

      <button
        onClick={toggle}
        className="rounded-xl brand-grad px-5 py-2 text-sm font-medium text-white shadow-sm transition hover:opacity-95"
      >
        {running ? "Stop" : "Begin"}
      </button>
    </div>
  );
}
