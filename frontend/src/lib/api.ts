// API client for the Mindful Companion FastAPI backend.
// Types here mirror backend/app/schemas.py. In a later phase, generate these
// from the backend's OpenAPI spec so they can never drift.

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function headers(): HeadersInit {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  // Read the token lazily so api.ts has no import cycle with auth.ts at load.
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("mc_token");
    if (token) h["Authorization"] = `Bearer ${token}`;
  }
  return h;
}

export type TriageLevel = "none" | "elevated" | "crisis";

export interface Resource {
  name: string;
  contact: string;
  url: string;
}

export interface MoodEntry {
  id: number;
  mood_score: number;
  note: string | null;
  sentiment_label: string | null;
  sentiment_score: number | null;
  emotion_label: string | null;
  emotion_score: number | null;
  created_at: string;
}

export interface WeeklyReport {
  period_start: string;
  period_end: string;
  entry_count: number;
  average_mood: number | null;
  positive_ratio: number | null;
  emotion_distribution: { label: string; count: number }[];
  summary: string;
}

// --- Mood ---
export async function createMood(mood_score: number, note?: string): Promise<MoodEntry> {
  const res = await fetch(`${API_URL}/mood`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({ mood_score, note: note || null }),
  });
  if (!res.ok) throw new Error(`createMood failed: ${res.status}`);
  return res.json();
}

export async function listMoods(): Promise<MoodEntry[]> {
  const res = await fetch(`${API_URL}/mood`, { headers: headers() });
  if (!res.ok) throw new Error(`listMoods failed: ${res.status}`);
  return res.json();
}

// --- Journal / gratitude ---
export interface JournalEntry {
  id: number;
  kind: "journal" | "gratitude";
  prompt: string | null;
  content: string;
  emotion_label: string | null;
  sentiment_label: string | null;
  created_at: string;
}

export async function createJournal(
  kind: "journal" | "gratitude",
  content: string,
  prompt?: string,
): Promise<JournalEntry> {
  const res = await fetch(`${API_URL}/journal`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({ kind, content, prompt: prompt ?? null }),
  });
  if (!res.ok) throw new Error(`createJournal failed: ${res.status}`);
  return res.json();
}

export async function listJournal(kind?: "journal" | "gratitude"): Promise<JournalEntry[]> {
  const qs = kind ? `?kind=${kind}` : "";
  const res = await fetch(`${API_URL}/journal${qs}`, { headers: headers() });
  if (!res.ok) throw new Error(`listJournal failed: ${res.status}`);
  return res.json();
}

// --- Weekly report ---
export async function getWeeklyReport(): Promise<WeeklyReport> {
  const res = await fetch(`${API_URL}/report/weekly`, { headers: headers() });
  if (!res.ok) throw new Error(`weekly report failed: ${res.status}`);
  return res.json();
}

// --- Chat (SSE over POST) ---
// EventSource only supports GET, so we read the stream manually and parse the
// `event:` / `data:` frames the backend emits.
export interface ChatHandlers {
  onTriage?: (level: TriageLevel, resources: Resource[]) => void;
  onMessage?: (text: string) => void;
  onDone?: () => void;
  onError?: (err: unknown) => void;
}

export async function streamChat(
  message: string,
  handlers: ChatHandlers,
  signal?: AbortSignal,
): Promise<void> {
  try {
    const res = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({ message }),
      signal,
    });
    if (!res.ok || !res.body) throw new Error(`chat failed: ${res.status}`);

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      // SSE frames are separated by a blank line.
      let sep: number;
      while ((sep = buffer.indexOf("\n\n")) !== -1) {
        const frame = buffer.slice(0, sep);
        buffer = buffer.slice(sep + 2);
        handleFrame(frame, handlers);
      }
    }
    handlers.onDone?.();
  } catch (err) {
    if ((err as Error).name !== "AbortError") handlers.onError?.(err);
  }
}

function handleFrame(frame: string, handlers: ChatHandlers): void {
  let event = "message";
  let data = "";
  for (const line of frame.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) data += line.slice(5).trim();
  }
  if (!data) return;

  try {
    const parsed = JSON.parse(data);
    if (event === "triage") {
      handlers.onTriage?.(parsed.level as TriageLevel, parsed.resources ?? []);
    } else if (event === "message") {
      handlers.onMessage?.(parsed.text ?? "");
    } else if (event === "done") {
      handlers.onDone?.();
    }
  } catch {
    // Ignore malformed frames.
  }
}
