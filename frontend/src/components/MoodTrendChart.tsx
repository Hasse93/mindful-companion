"use client";

import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { MoodEntry } from "@/lib/api";

export default function MoodTrendChart({ entries }: { entries: MoodEntry[] }) {
  // Oldest -> newest for a left-to-right trend.
  const data = [...entries]
    .reverse()
    .map((e) => ({
      date: new Date(e.created_at).toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
      }),
      mood: e.mood_score,
    }));

  return (
    <div className="p-5">
      <h2 className="text-base font-semibold">Mood over time</h2>
      <p className="mt-0.5 text-sm text-soft">How your check-ins have trended.</p>
      <div className="mt-4 h-48 w-full">
        {data.length === 0 ? (
          <p className="pt-12 text-center text-sm text-faint">No check-ins yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 6, right: 6, left: -24, bottom: 0 }}>
              <defs>
                <linearGradient id="moodFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#7f77dd" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="#5dcaa5" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="date"
                tick={{ fontSize: 11, fill: "var(--ink-soft)" }}
                tickLine={false}
                axisLine={false}
                minTickGap={20}
              />
              <YAxis
                domain={[1, 5]}
                ticks={[1, 2, 3, 4, 5]}
                tick={{ fontSize: 11, fill: "var(--ink-soft)" }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                contentStyle={{
                  borderRadius: 12,
                  border: "1px solid rgba(255,255,255,0.5)",
                  background: "rgba(255,255,255,0.9)",
                  fontSize: 12,
                }}
              />
              <Area
                type="monotone"
                dataKey="mood"
                stroke="#7f77dd"
                strokeWidth={2.5}
                fill="url(#moodFill)"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
