"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, RefreshCw } from "lucide-react";
import { AFFIRMATIONS } from "@/lib/theme";

export default function Affirmation() {
  const [idx, setIdx] = useState(() => Math.floor(Math.random() * AFFIRMATIONS.length));

  function next() {
    setIdx((i) => (i + 1) % AFFIRMATIONS.length);
  }

  return (
    <div className="p-5">
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-sm font-medium text-soft">
          <Sparkles size={15} /> A gentle reminder
        </span>
        <button onClick={next} aria-label="New affirmation" className="text-soft hover:text-ink">
          <RefreshCw size={15} />
        </button>
      </div>
      <motion.p
        key={idx}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        className="mt-3 text-lg font-medium leading-relaxed"
      >
        &ldquo;{AFFIRMATIONS[idx]}&rdquo;
      </motion.p>
    </div>
  );
}
