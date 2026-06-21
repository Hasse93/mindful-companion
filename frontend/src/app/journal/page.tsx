"use client";

import { useCallback, useEffect, useState } from "react";
import { RefreshCw, Heart, PenLine } from "lucide-react";
import GlassCard from "@/components/ui/GlassCard";
import { createJournal, listJournal, type JournalEntry } from "@/lib/api";
import { JOURNAL_PROMPTS, emotionColor } from "@/lib/theme";

type Kind = "journal" | "gratitude";

export default function JournalPage() {
  const [kind, setKind] = useState<Kind>("journal");
  const [content, setContent] = useState("");
  const [promptIdx, setPromptIdx] = useState(0);
  const [saving, setSaving] = useState(false);
  const [entries, setEntries] = useState<JournalEntry[]>([]);

  const refresh = useCallback(() => {
    listJournal().then(setEntries).catch(() => setEntries([]));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const prompt = kind === "journal" ? JOURNAL_PROMPTS[promptIdx] : "What are you grateful for today?";

  async function save() {
    if (!content.trim() || saving) return;
    setSaving(true);
    try {
      await createJournal(kind, content, prompt);
      setContent("");
      refresh();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="px-1 pt-2">
        <h1 className="text-2xl font-semibold">Journal</h1>
        <p className="mt-1 text-sm text-soft">Put your thoughts somewhere safe.</p>
      </div>

      <div className="flex gap-2">
        {(["journal", "gratitude"] as Kind[]).map((k) => (
          <button
            key={k}
            onClick={() => setKind(k)}
            className={`flex items-center gap-1.5 rounded-xl px-4 py-2 text-sm font-medium transition ${
              kind === k
                ? "brand-grad text-white shadow-sm"
                : "glass-soft text-soft hover:text-ink"
            }`}
          >
            {k === "journal" ? <PenLine size={15} /> : <Heart size={15} />}
            {k === "journal" ? "Journal" : "Gratitude"}
          </button>
        ))}
      </div>

      <GlassCard delay={0.05}>
        <div className="p-5">
          <div className="flex items-start justify-between gap-3">
            <p className="text-sm font-medium text-soft">{prompt}</p>
            {kind === "journal" && (
              <button
                onClick={() => setPromptIdx((i) => (i + 1) % JOURNAL_PROMPTS.length)}
                aria-label="New prompt"
                className="shrink-0 text-soft hover:text-ink"
              >
                <RefreshCw size={15} />
              </button>
            )}
          </div>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Start writing…"
            rows={5}
            className="mt-3 w-full resize-none rounded-xl border border-white/50 bg-white/40 px-3 py-2.5 text-sm leading-relaxed outline-none placeholder:text-faint focus:border-indigo-300 dark:bg-white/5"
          />
          <button
            onClick={save}
            disabled={!content.trim() || saving}
            className="mt-3 rounded-xl brand-grad px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:opacity-95 disabled:opacity-40"
          >
            {saving ? "Saving…" : "Save entry"}
          </button>
        </div>
      </GlassCard>

      <div className="flex flex-col gap-3">
        {entries.map((e, i) => (
          <GlassCard key={e.id} delay={Math.min(i * 0.04, 0.3)} soft>
            <div className="p-4">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-xs font-medium text-soft">
                  {e.kind === "gratitude" ? <Heart size={13} /> : <PenLine size={13} />}
                  {e.kind === "gratitude" ? "Gratitude" : "Journal"}
                </span>
                <span className="text-xs text-faint">
                  {new Date(e.created_at).toLocaleDateString()}
                </span>
              </div>
              {e.prompt && <p className="mt-1.5 text-xs italic text-faint">{e.prompt}</p>}
              <p className="mt-1.5 whitespace-pre-wrap text-sm leading-relaxed">{e.content}</p>
              {e.emotion_label && (
                <span
                  className="mt-2 inline-block rounded-full px-2 py-0.5 text-xs"
                  style={{
                    background: `${emotionColor(e.emotion_label)}22`,
                    color: emotionColor(e.emotion_label),
                  }}
                >
                  {e.emotion_label}
                </span>
              )}
            </div>
          </GlassCard>
        ))}
        {entries.length === 0 && (
          <p className="px-1 text-sm text-faint">Your entries will appear here.</p>
        )}
      </div>
    </div>
  );
}
