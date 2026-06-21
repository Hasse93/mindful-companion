"use client";

import { useCallback, useEffect, useState } from "react";
import GlassCard from "@/components/ui/GlassCard";
import MoodCheckIn from "@/components/MoodCheckIn";
import MoodCalendar from "@/components/MoodCalendar";
import MoodTrendChart from "@/components/MoodTrendChart";
import { listMoods, type MoodEntry } from "@/lib/api";
import { emotionColor, moodByScore } from "@/lib/theme";

export default function MoodPage() {
  const [entries, setEntries] = useState<MoodEntry[]>([]);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    listMoods()
      .then(setEntries)
      .catch(() => setError("Couldn't load your check-ins. Is the API running?"));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <div className="flex flex-col gap-4">
      <div className="px-1 pt-2">
        <h1 className="text-2xl font-semibold">Mood</h1>
        <p className="mt-1 text-sm text-soft">Check in and watch your patterns unfold.</p>
      </div>

      {error && <p className="px-1 text-sm text-red-600 dark:text-red-300">{error}</p>}

      <GlassCard delay={0.05}>
        <MoodCheckIn onSaved={refresh} />
      </GlassCard>

      <GlassCard delay={0.1}>
        <MoodTrendChart entries={entries} />
      </GlassCard>

      <GlassCard delay={0.15}>
        <MoodCalendar entries={entries} />
      </GlassCard>

      <GlassCard delay={0.2}>
        <div className="p-5">
          <h2 className="text-base font-semibold">Recent check-ins</h2>
          <ul className="mt-3 space-y-2">
            {entries.slice(0, 8).map((e) => {
              const mood = moodByScore(e.mood_score);
              return (
                <li
                  key={e.id}
                  className="flex items-center gap-3 rounded-xl bg-white/40 px-3 py-2.5 text-sm dark:bg-white/5"
                >
                  <span
                    className="h-2.5 w-2.5 shrink-0 rounded-full"
                    style={{ background: mood?.color }}
                  />
                  <div className="min-w-0 flex-1">
                    {e.note && <p className="truncate">{e.note}</p>}
                    <p className="text-xs text-faint">
                      {new Date(e.created_at).toLocaleString()} · {mood?.label}
                    </p>
                  </div>
                  {e.emotion_label && (
                    <span
                      className="shrink-0 rounded-full px-2 py-0.5 text-xs"
                      style={{
                        background: `${emotionColor(e.emotion_label)}22`,
                        color: emotionColor(e.emotion_label),
                      }}
                    >
                      {e.emotion_label}
                    </span>
                  )}
                </li>
              );
            })}
            {entries.length === 0 && <li className="text-sm text-faint">No check-ins yet.</li>}
          </ul>
        </div>
      </GlassCard>
    </div>
  );
}
