// Shared visual config: emotion colors + mood scale (Calm Aurora palette).

export const EMOTION_COLORS: Record<string, string> = {
  joy: "#1D9E75",
  sadness: "#378ADD",
  anger: "#D85A30",
  fear: "#7F77DD",
  surprise: "#EF9F27",
  disgust: "#639922",
  neutral: "#888780",
};

export function emotionColor(label?: string | null): string {
  if (!label) return EMOTION_COLORS.neutral;
  return EMOTION_COLORS[label.toLowerCase()] ?? EMOTION_COLORS.neutral;
}

export interface MoodOption {
  score: number;
  label: string;
  icon: string; // Tabler icon name (without "ti-")
  color: string;
}

export const MOODS: MoodOption[] = [
  { score: 1, label: "Very low", icon: "mood-sad", color: "#378ADD" },
  { score: 2, label: "Low", icon: "mood-empty", color: "#7F77DD" },
  { score: 3, label: "Okay", icon: "mood-neutral", color: "#888780" },
  { score: 4, label: "Good", icon: "mood-smile", color: "#1D9E75" },
  { score: 5, label: "Great", icon: "mood-happy", color: "#EF9F27" },
];

export function moodByScore(score: number): MoodOption | undefined {
  return MOODS.find((m) => m.score === score);
}

// Day-streak: count consecutive days (ending today or yesterday) with >=1 entry.
export function computeStreak(dates: string[]): number {
  if (dates.length === 0) return 0;
  const days = new Set(dates.map((d) => new Date(d).toDateString()));
  let streak = 0;
  const cursor = new Date();
  // Allow the streak to "hold" if they haven't checked in yet today.
  if (!days.has(cursor.toDateString())) cursor.setDate(cursor.getDate() - 1);
  while (days.has(cursor.toDateString())) {
    streak += 1;
    cursor.setDate(cursor.getDate() - 1);
  }
  return streak;
}

export const AFFIRMATIONS = [
  "You are doing the best you can, and that is enough.",
  "This feeling is real, and it will also pass.",
  "You deserve the same kindness you give to others.",
  "Small steps are still steps forward.",
  "You are allowed to rest without earning it.",
  "Your worth is not measured by your productivity.",
  "It's okay to ask for help — that's strength, not weakness.",
  "You have survived every hard day so far.",
];

export const JOURNAL_PROMPTS = [
  "What is one thing that felt heavy today, and one that felt light?",
  "What would you say to a friend feeling the way you do right now?",
  "Name a moment today when you felt even slightly at ease.",
  "What is something you're looking forward to, however small?",
  "What does your body need from you right now?",
  "Describe a recent moment you felt proud of yourself.",
];
