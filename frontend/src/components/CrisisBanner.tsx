"use client";

import { motion } from "framer-motion";
import { LifeBuoy } from "lucide-react";
import type { Resource } from "@/lib/api";

export default function CrisisBanner({
  level,
  resources,
}: {
  level: "elevated" | "crisis";
  resources: Resource[];
}) {
  const isCrisis = level === "crisis";
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      role="alert"
      className={`rounded-2xl border p-4 text-sm backdrop-blur-md ${
        isCrisis
          ? "border-red-300/70 bg-red-50/80 text-red-900 dark:bg-red-950/40 dark:text-red-100"
          : "border-amber-300/70 bg-amber-50/80 text-amber-900 dark:bg-amber-950/40 dark:text-amber-100"
      }`}
    >
      <p className="flex items-center gap-2 font-semibold">
        <LifeBuoy size={16} />
        {isCrisis
          ? "It sounds like you may be going through something really hard."
          : "It sounds like things feel heavy right now."}
      </p>
      <p className="mt-1.5 opacity-90">
        {isCrisis
          ? "Please reach out to a trained professional right now — you don't have to go through this alone. This app is not a crisis service."
          : "If it would help, support is always available. This app is a supportive tool, not professional care."}
      </p>
      {resources.length > 0 && (
        <ul className="mt-3 space-y-1">
          {resources.map((r) => (
            <li key={r.name}>
              <a
                href={r.url}
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium underline underline-offset-2"
              >
                {r.name}
              </a>{" "}
              — {r.contact}
            </li>
          ))}
        </ul>
      )}
    </motion.div>
  );
}
