"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { HeartPulse } from "lucide-react";
import { login, register } from "@/lib/auth";

export default function AuthForm() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      if (mode === "register") await register(email, password);
      await login(email, password); // also stores the token → gate re-renders
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass w-full max-w-sm rounded-3xl p-7"
      >
        <div className="flex flex-col items-center text-center">
          <span className="grid h-12 w-12 place-items-center rounded-2xl brand-grad-br text-white">
            <HeartPulse size={22} />
          </span>
          <h1 className="mt-3 text-xl font-semibold">Mindful Companion</h1>
          <p className="mt-1 text-sm text-soft">
            {mode === "login" ? "Welcome back." : "A little space for yourself."}
          </p>
        </div>

        <form onSubmit={submit} className="mt-6 flex flex-col gap-3">
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            className="rounded-xl border border-white/50 bg-white/40 px-3 py-2.5 text-sm outline-none placeholder:text-faint focus:border-indigo-300 dark:bg-white/5"
          />
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password (min 8 characters)"
            className="rounded-xl border border-white/50 bg-white/40 px-3 py-2.5 text-sm outline-none placeholder:text-faint focus:border-indigo-300 dark:bg-white/5"
          />
          {error && <p className="text-sm text-red-600 dark:text-red-300">{error}</p>}
          <button
            type="submit"
            disabled={busy}
            className="mt-1 rounded-xl brand-grad px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:opacity-95 disabled:opacity-50"
          >
            {busy ? "Please wait…" : mode === "login" ? "Log in" : "Create account"}
          </button>
        </form>

        <p className="mt-5 text-center text-sm text-soft">
          {mode === "login" ? "New here?" : "Already have an account?"}{" "}
          <button
            onClick={() => {
              setMode(mode === "login" ? "register" : "login");
              setError(null);
            }}
            className="font-medium text-indigo-600 hover:underline dark:text-indigo-300"
          >
            {mode === "login" ? "Create an account" : "Log in"}
          </button>
        </p>
      </motion.div>
    </div>
  );
}
