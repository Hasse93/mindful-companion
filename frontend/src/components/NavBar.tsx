"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, MessageCircle, HeartPulse, BarChart3, Wind, NotebookPen, LogOut } from "lucide-react";
import { logout } from "@/lib/auth";

const links = [
  { href: "/", label: "Home", icon: Home },
  { href: "/chat", label: "Chat", icon: MessageCircle },
  { href: "/mood", label: "Mood", icon: HeartPulse },
  { href: "/journal", label: "Journal", icon: NotebookPen },
  { href: "/tools", label: "Calm", icon: Wind },
  { href: "/insights", label: "Insights", icon: BarChart3 },
];

export default function NavBar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-20 px-4 pt-4">
      <nav className="glass mx-auto flex max-w-3xl items-center justify-between rounded-2xl px-3 py-2.5">
        <Link href="/" className="flex items-center gap-2 pl-1 pr-2 font-semibold text-ink">
          <span className="grid h-7 w-7 place-items-center rounded-full brand-grad-br text-white">
            <HeartPulse size={15} />
          </span>
          <span className="hidden sm:inline">Mindful</span>
        </Link>
        <div className="flex items-center gap-0.5">
          {links.map(({ href, label, icon: Icon }) => {
            const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                aria-label={label}
                className={`flex items-center gap-1.5 rounded-xl px-2.5 py-1.5 text-sm transition ${
                  active
                    ? "bg-white/70 font-medium text-ink shadow-sm dark:bg-white/15"
                    : "text-soft hover:bg-white/40 hover:text-ink dark:hover:bg-white/10"
                }`}
              >
                <Icon size={17} />
                <span className="hidden md:inline">{label}</span>
              </Link>
            );
          })}
          <button
            onClick={logout}
            aria-label="Log out"
            className="ml-0.5 flex items-center rounded-xl px-2.5 py-1.5 text-sm text-soft transition hover:bg-white/40 hover:text-ink dark:hover:bg-white/10"
          >
            <LogOut size={17} />
          </button>
        </div>
      </nav>
    </header>
  );
}
