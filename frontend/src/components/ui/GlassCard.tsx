"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";

export default function GlassCard({
  children,
  className = "",
  delay = 0,
  soft = false,
}: {
  children: ReactNode;
  className?: string;
  delay?: number;
  soft?: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: "easeOut" }}
      className={`${soft ? "glass-soft" : "glass"} rounded-2xl ${className}`}
    >
      {children}
    </motion.div>
  );
}
