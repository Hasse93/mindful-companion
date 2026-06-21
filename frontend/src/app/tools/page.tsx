"use client";

import GlassCard from "@/components/ui/GlassCard";
import BreathingExercise from "@/components/BreathingExercise";
import GroundingExercise from "@/components/GroundingExercise";
import Affirmation from "@/components/Affirmation";

export default function ToolsPage() {
  return (
    <div className="flex flex-col gap-4">
      <div className="px-1 pt-2">
        <h1 className="text-2xl font-semibold">Find calm</h1>
        <p className="mt-1 text-sm text-soft">A few small practices to steady yourself.</p>
      </div>

      <GlassCard delay={0.05}>
        <BreathingExercise />
      </GlassCard>

      <GlassCard delay={0.1}>
        <GroundingExercise />
      </GlassCard>

      <GlassCard delay={0.15}>
        <Affirmation />
      </GlassCard>
    </div>
  );
}
