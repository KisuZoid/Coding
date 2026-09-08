import Link from "next/link";

import CinematicIntro from "@/components/CinematicIntro";

export default function Home() {
  return (
    <main className="bg-black">
      <header className="fixed inset-x-0 top-0 z-50 flex items-center justify-between px-6 py-5 text-white">
        <span className="text-sm font-semibold tracking-widest uppercase">
          AutoInspect<span className="text-amber-400">-X</span>
        </span>
        <Link href="/demo" className="text-sm font-medium text-white/80 hover:text-white">
          Skip to demo
        </Link>
      </header>
      <CinematicIntro />
    </main>
  );
}