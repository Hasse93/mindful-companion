"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Eye, Hand, Ear, Wind, Soup, RotateCcw, type LucideIcon } from "lucide-react";

interface Step {
  count: number;
  sense: string;
  prompt: string;
  icon: LucideIcon;
}

// The 5-4-3-2-1 grounding technique.
const STEPS: Step[] = [
  { count: 5, sense: "see", prompt: "Name 5 things you can see around you.", icon: Eye },
  { count: 4, sense: "feel", prompt: "Notice 4 things you can physically feel.", icon: Hand },
  { count: 3, sense: "hear", prompt: "Listen for 3 sounds, near or far.", icon: Ear },
  { count: 2, sense: "smell", prompt: "Find 2 things you can smell.", icon: Wind },
  { count: 1, sense: "taste", prompt: "Notice 1 thing you can taste.", icon: Soup },
];

export default function GroundingExercise() {
  const [idx, setIdx] = useState(0);
  const [done, setDone] = useState(false);
  const step = STEPS[idx];

  function next() {
    if (idx + 1 >= STEPS.length) setDone(true);
    else setIdx(idx + 1);
  }
  function restart() {
    setIdx(0);
    setDone(false);
  }

  return (
    <div className="p-6">
      <h2 className="text-base font-semibold">5-4-3-2-1 grounding</h2>
      <p className="mt-0.5 text-sm text-soft">Come back to the present, one sense at a time.</p>

      <div className="mt-5 min-h-[150px]">
        <AnimatePresence mode="wait">
          {done ? (
            <motion.div
              key="done"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center py-6 text-center"
            >
              <p className="text-lg font-medium">Nicely done.</p>
              <p className="mt-1 text-sm text-soft">Notice how your body feels now.</p>
              <button
                onClick={restart}
                className="mt-4 flex items-center gap-1.5 rounded-xl border border-white/50 bg-white/40 px-4 py-2 text-sm transition hover:bg-white/60 dark:bg-white/5"
              >
                <RotateCcw size={15} /> Start again
              </button>
            </motion.div>
          ) : (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: 24 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -24 }}
              transition={{ duration: 0.3 }}
              className="flex flex-col items-center py-3 text-center"
            >
              <span
                className="grid h-16 w-16 place-items-center rounded-2xl text-white"
                style={{ background: "linear-gradient(135deg,#5dcaa5,#7f77dd)" }}
              >
                <step.icon size={28} />
              </span>
              <p className="mt-3 text-3xl font-semibold">{step.count}</p>
              <p className="mt-1 max-w-xs text-sm text-soft">{step.prompt}</p>
              <button
                onClick={next}
                className="mt-4 rounded-xl brand-grad px-5 py-2 text-sm font-medium text-white shadow-sm transition hover:opacity-95"
              >
                {idx + 1 >= STEPS.length ? "Finish" : "Next"}
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="mt-2 flex justify-center gap-1.5">
        {STEPS.map((s, i) => (
          <span
            key={s.sense}
            className="h-1.5 rounded-full transition-all"
            style={{
              width: i === idx && !done ? 20 : 8,
              background: i < idx || done ? "#1D9E75" : "rgba(127,119,221,0.35)",
            }}
          />
        ))}
      </div>
    </div>
  );
}
