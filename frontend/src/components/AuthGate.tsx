"use client";

import { useEffect, useState } from "react";
import { getToken, onAuthChange } from "@/lib/auth";
import AuthForm from "@/components/AuthForm";

type Status = "loading" | "authed" | "anon";

// Renders the app only when a token is present; otherwise shows the auth form.
export default function AuthGate({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<Status>("loading");

  useEffect(() => {
    const sync = () => setStatus(getToken() ? "authed" : "anon");
    sync();
    return onAuthChange(sync);
  }, []);

  if (status === "loading") {
    return <div className="min-h-[60vh]" aria-hidden="true" />;
  }
  if (status === "anon") {
    return <AuthForm />;
  }
  return <>{children}</>;
}
