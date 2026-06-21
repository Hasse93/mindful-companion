"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Flame, MessageCircle, Wind, NotebookPen, ArrowRight } from "lucide-react";
import GlassCard from "@/components/ui/GlassCard";
import MoodCheckIn from "@/components/MoodCheckIn";
import Affirmation from "@/components/Affirmation";
import { listMoods, type MoodEntry } from "@/lib/api";
import { computeStreak } from "@/lib/theme";

function greeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

export default function Home() {
  const [entries, setEntries] = useState<MoodEntry[]>([]);

  const refresh = useCallback(() => {
    listMoods().then(setEntries).catch(() => setEntries([]));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const streak = computeStreak(entries.map((e) => e.created_at));
  const avg =
    entries.length > 0
      ? (entries.reduce((s, e) => s + e.mood_score, 0) / entries.length).toFixed(1)
      : "—";
  const sentiments = entries.filter((e) => e.sentiment_label);
  const positive =
    sentiments.length > 0
      ? Math.round(
          (sentiments.filter((e) => e.sentiment_label === "POSITIVE").length /
            sentiments.length) *
            100,
        )
      : null;

  const tools = [
    { href: "/chat", label: "Talk it through", icon: MessageCircle, from: "#7f77dd", to: "#5dcaa5" },
    { href: "/tools", label: "Find calm", icon: Wind, from: "#5dcaa5", to: "#378add" },
    { href: "/journal", label: "Journal", icon: NotebookPen, from: "#afa9ec", to: "#7f77dd" },
  ];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-end justify-between px-1 pt-2">
        <div>
          <h1 className="text-2xl font-semibold">{greeting()}.</h1>
          <p className="mt-1 text-sm text-soft">How are you arriving today?</p>
        </div>
        <span className="flex items-center gap-1.5 rounded-full bg-amber-100/80 px-3 py-1.5 text-sm font-medium text-amber-800 backdrop-blur dark:bg-amber-900/40 dark:text-amber-200">
          <Flame size={15} /> {streak}-day streak
        </span>
      </div>

      <GlassCard delay={0.05}>
        <MoodCheckIn onSaved={refresh} />
      </GlassCard>

      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Avg mood", value: `${avg}${avg !== "—" ? " / 5" : ""}` },
          { label: "Positive", value: positive != null ? `${positive}%` : "—" },
          { label: "Check-ins", value: String(entries.length) },
        ].map((s, i) => (
          <GlassCard key={s.label} delay={0.1 + i * 0.05} soft className="p-4">
            <p className="text-xs text-soft">{s.label}</p>
            <p className="mt-1 text-2xl font-semibold">{s.value}</p>
          </GlassCard>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {tools.map((t, i) => (
          <GlassCard key={t.href} delay={0.2 + i * 0.05} className="overflow-hidden">
            <Link href={t.href} className="flex items-center justify-between p-4">
              <span className="flex items-center gap-3">
                <span
                  className="grid h-10 w-10 place-items-center rounded-xl text-white"
                  style={{ background: `linear-gradient(135deg, ${t.from}, ${t.to})` }}
                >
                  <t.icon size={18} />
                </span>
                <span className="text-sm font-medium">{t.label}</span>
              </span>
              <ArrowRight size={16} className="text-faint" />
            </Link>
          </GlassCard>
        ))}
      </div>

      <GlassCard delay={0.35}>
        <Affirmation />
      </GlassCard>
    </div>
  );
}
