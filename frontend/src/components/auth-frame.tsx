"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import type { ReactNode } from "react";

export function AuthFrame({
  children,
  title,
  description,
  alternateLabel,
  alternateHref,
  alternateText,
}: {
  children: ReactNode;
  title: string;
  description: string;
  alternateLabel: string;
  alternateHref: string;
  alternateText: string;
}) {
  return (
    <main className="grid min-h-screen place-items-center px-5 py-12">
      <motion.section
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-lg rounded-3xl border border-ink/10 bg-white p-7 shadow-[0_24px_80px_-36px_rgba(16,37,30,0.3)] sm:p-10"
        initial={{ opacity: 0, y: 16 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
      >
        <Link className="text-sm font-semibold text-forest" href="/">
          School ERP
        </Link>
        <h1 className="mt-8 text-3xl font-semibold tracking-tight text-ink">{title}</h1>
        <p className="mt-3 leading-7 text-ink/60">{description}</p>
        {children}
        <p className="mt-7 text-center text-sm text-ink/60">
          {alternateText}{" "}
          <Link className="font-semibold text-forest hover:underline" href={alternateHref}>
            {alternateLabel}
          </Link>
        </p>
      </motion.section>
    </main>
  );
}
