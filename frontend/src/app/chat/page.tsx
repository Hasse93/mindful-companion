"use client";

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Send, Sparkles } from "lucide-react";
import CrisisBanner from "@/components/CrisisBanner";
import { streamChat, type Resource, type TriageLevel } from "@/lib/api";

interface Msg {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [triage, setTriage] = useState<{ level: TriageLevel; resources: Resource[] } | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function send() {
    const text = input.trim();
    if (!text || sending) return;
    setInput("");
    setSending(true);
    setTriage(null);
    setMessages((m) => [...m, { role: "user", content: text }, { role: "assistant", content: "" }]);

    await streamChat(text, {
      onTriage: (level, resources) => {
        if (level !== "none") setTriage({ level, resources });
      },
      onMessage: (chunk) =>
        setMessages((m) => {
          const next = [...m];
          next[next.length - 1] = {
            role: "assistant",
            content: next[next.length - 1].content + chunk,
          };
          return next;
        }),
      onError: () =>
        setMessages((m) => {
          const next = [...m];
          next[next.length - 1] = {
            role: "assistant",
            content: "Sorry — I couldn't reach the server. Please try again.",
          };
          return next;
        }),
    });
    setSending(false);
  }

  return (
    <div className="flex h-[calc(100vh-11rem)] flex-col gap-3">
      <div className="px-1">
        <h1 className="text-xl font-semibold">Your companion</h1>
        <p className="text-sm text-soft">A warm space to think out loud.</p>
      </div>

      {triage && triage.level !== "none" && (
        <CrisisBanner level={triage.level as "elevated" | "crisis"} resources={triage.resources} />
      )}

      <div ref={scrollRef} className="glass flex-1 space-y-3 overflow-y-auto rounded-2xl p-4">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center text-center text-soft">
            <span className="grid h-12 w-12 place-items-center rounded-2xl brand-grad-br text-white">
              <Sparkles size={22} />
            </span>
            <p className="mt-3 text-sm">Hi, I&apos;m here to listen. What&apos;s on your mind today?</p>
          </div>
        )}
        {messages.map((m, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[82%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                m.role === "user"
                  ? "brand-grad-br text-white"
                  : "bg-white/70 text-ink dark:bg-white/10"
              }`}
            >
              {m.content || (sending && i === messages.length - 1 ? "…" : "")}
            </div>
          </motion.div>
        ))}
      </div>

      <div className="glass flex items-center gap-2 rounded-2xl p-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Type a message…"
          disabled={sending}
          className="flex-1 bg-transparent px-3 py-2 text-sm outline-none placeholder:text-faint"
        />
        <button
          onClick={send}
          disabled={sending || !input.trim()}
          aria-label="Send"
          className="grid h-10 w-10 place-items-center rounded-xl brand-grad text-white shadow-sm transition hover:opacity-95 disabled:opacity-40"
        >
          <Send size={17} />
        </button>
      </div>
    </div>
  );
}
