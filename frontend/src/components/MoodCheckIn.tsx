"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Smile,
  Meh,
  Frown,
  Laugh,
  Angry,
  type LucideIcon,
} from "lucide-react";
import { createMood } from "@/lib/api";
import { MOODS } from "@/lib/theme";

const ICONS: Record<string, LucideIcon> = {
  "mood-sad": Frown,
  "mood-empty": Angry,
  "mood-neutral": Meh,
  "mood-smile": Smile,
  "mood-happy": Laugh,
};

export default function MoodCheckIn({ onSaved }: { onSaved?: () => void }) {
  const [score, setScore] = useState<number | null>(null);
  const [note, setNote] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function save() {
    if (score == null || saving) return;
    setSaving(true);
    setError(null);
    try {
      await createMood(score, note);
      setSaved(true);
      setScore(null);
      setNote("");
      onSaved?.();
      setTimeout(() => setSaved(false), 2500);
    } catch {
      setError("Couldn't save — is the API running?");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="p-5">
      <h2 className="text-base font-semibold">How are you feeling?</h2>
      <p className="mt-0.5 text-sm text-soft">There&apos;s no wrong answer.</p>

      <div className="mt-4 grid grid-cols-5 gap-2.5">
        {MOODS.map((m) => {
          const Icon = ICONS[m.icon] ?? Meh;
          const active = score === m.score;
          return (
            <motion.button
              key={m.score}
              whileTap={{ scale: 0.92 }}
              onClick={() => setScore(m.score)}
              aria-label={m.label}
              aria-pressed={active}
              className="flex flex-col items-center gap-1.5 rounded-2xl p-2 transition"
              style={{
                background: active ? `${m.color}26` : "transparent",
                outline: active ? `2px solid ${m.color}` : "none",
              }}
            >
              <span
                className="grid h-12 w-full place-items-center rounded-xl text-white"
                style={{ background: m.color }}
              >
                <Icon size={22} />
              </span>
              <span className="text-[11px] text-soft">{m.label}</span>
            </motion.button>
          );
        })}
      </div>

      <textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="Want to add a note? (optional)"
        rows={2}
        className="mt-4 w-full resize-none rounded-xl border border-white/50 bg-white/40 px-3 py-2 text-sm outline-none placeholder:text-faint focus:border-indigo-300 dark:bg-white/5"
      />

      <div className="mt-3 flex items-center gap-3">
        <button
          onClick={save}
          disabled={score == null || saving}
          className="rounded-xl brand-grad px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:opacity-95 disabled:opacity-40"
        >
          {saving ? "Saving…" : "Save check-in"}
        </button>
        {saved && <span className="text-sm text-teal-600 dark:text-teal-300">Saved ✓</span>}
        {error && <span className="text-sm text-red-600 dark:text-red-300">{error}</span>}
      </div>
    </div>
  );
}
