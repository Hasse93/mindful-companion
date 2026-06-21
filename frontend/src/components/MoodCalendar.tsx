"use client";

import { moodByScore } from "@/lib/theme";
import type { MoodEntry } from "@/lib/api";

// A GitHub-style heatmap of the last 12 weeks, coloured by that day's mood.
export default function MoodCalendar({ entries }: { entries: MoodEntry[] }) {
  const WEEKS = 12;
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // Latest mood score per calendar day.
  const byDay = new Map<string, number>();
  for (const e of entries) {
    const key = new Date(e.created_at).toDateString();
    if (!byDay.has(key)) byDay.set(key, e.mood_score); // entries arrive newest-first
  }

  // Start from the Sunday WEEKS*7 days back.
  const start = new Date(today);
  start.setDate(start.getDate() - (WEEKS * 7 - 1));
  start.setDate(start.getDate() - start.getDay());

  const columns: Date[][] = [];
  const cursor = new Date(start);
  for (let w = 0; w < WEEKS + 1; w++) {
    const col: Date[] = [];
    for (let d = 0; d < 7; d++) {
      col.push(new Date(cursor));
      cursor.setDate(cursor.getDate() + 1);
    }
    columns.push(col);
  }

  return (
    <div className="p-5">
      <h2 className="text-base font-semibold">Mood calendar</h2>
      <p className="mt-0.5 text-sm text-soft">Your last 12 weeks at a glance.</p>
      <div className="mt-4 flex gap-1 overflow-x-auto pb-1">
        {columns.map((col, ci) => (
          <div key={ci} className="flex flex-col gap-1">
            {col.map((day) => {
              const future = day > today;
              const score = byDay.get(day.toDateString());
              const color = score ? moodByScore(score)?.color : undefined;
              return (
                <div
                  key={day.toISOString()}
                  title={`${day.toLocaleDateString()}${score ? ` · mood ${score}/5` : ""}`}
                  className="h-3.5 w-3.5 rounded-[4px]"
                  style={{
                    background: future
                      ? "transparent"
                      : color ?? "rgba(127,119,221,0.14)",
                  }}
                />
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}
