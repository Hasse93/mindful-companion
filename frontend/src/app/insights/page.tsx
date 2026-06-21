"use client";

import { useEffect, useState } from "react";
import { Quote } from "lucide-react";
import GlassCard from "@/components/ui/GlassCard";
import { getWeeklyReport, type WeeklyReport } from "@/lib/api";
import { emotionColor } from "@/lib/theme";

export default function InsightsPage() {
  const [report, setReport] = useState<WeeklyReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getWeeklyReport()
      .then(setReport)
      .catch(() => setError("Couldn't load your weekly report. Is the API running?"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="px-1 pt-6 text-sm text-soft">Preparing your week…</p>;
  if (error) return <p className="px-1 pt-6 text-sm text-red-600 dark:text-red-300">{error}</p>;
  if (!report) return null;

  const maxCount = Math.max(1, ...report.emotion_distribution.map((e) => e.count));

  return (
    <div className="flex flex-col gap-4">
      <div className="px-1 pt-2">
        <h1 className="text-2xl font-semibold">Your week</h1>
        <p className="mt-1 text-sm text-soft">A gentle look back at the last 7 days.</p>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Check-ins", value: String(report.entry_count) },
          { label: "Avg mood", value: report.average_mood != null ? `${report.average_mood} / 5` : "—" },
          {
            label: "Positive",
            value: report.positive_ratio != null ? `${Math.round(report.positive_ratio * 100)}%` : "—",
          },
        ].map((s, i) => (
          <GlassCard key={s.label} delay={0.05 + i * 0.05} soft className="p-4">
            <p className="text-xs text-soft">{s.label}</p>
            <p className="mt-1 text-2xl font-semibold">{s.value}</p>
          </GlassCard>
        ))}
      </div>

      {report.emotion_distribution.length > 0 && (
        <GlassCard delay={0.2}>
          <div className="p-5">
            <h2 className="text-base font-semibold">Emotions this week</h2>
            <div className="mt-4 space-y-2.5">
              {report.emotion_distribution.map((e) => (
                <div key={e.label} className="flex items-center gap-3 text-sm">
                  <span className="w-20 shrink-0 capitalize text-soft">{e.label}</span>
                  <div className="h-2.5 flex-1 rounded-full bg-white/40 dark:bg-white/10">
                    <div
                      className="h-2.5 rounded-full"
                      style={{
                        width: `${(e.count / maxCount) * 100}%`,
                        background: emotionColor(e.label),
                      }}
                    />
                  </div>
                  <span className="w-6 text-right text-faint">{e.count}</span>
                </div>
              ))}
            </div>
          </div>
        </GlassCard>
      )}

      <GlassCard delay={0.3}>
        <div className="p-5">
          <h2 className="flex items-center gap-2 text-base font-semibold">
            <Quote size={16} /> A reflection
          </h2>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">{report.summary}</p>
        </div>
      </GlassCard>
    </div>
  );
}
