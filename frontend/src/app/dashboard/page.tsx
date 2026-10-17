"use client";

import Link from "next/link";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { getApiErrorMessage } from "@/lib/api-error";
import { useAppDispatch, useAppSelector } from "@/lib/hooks";
import { useGetCurrentUserQuery } from "@/lib/authApi";
import { clearAccessToken } from "@/lib/authSlice";

export default function DashboardPage() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const accessToken = useAppSelector((state) => state.auth.accessToken);
  const { data: user, error, isLoading } = useGetCurrentUserQuery(undefined, {
    skip: !accessToken,
  });

  useEffect(() => {
    if (!accessToken) {
      router.replace("/login");
    }
  }, [accessToken, router]);

  function signOut() {
    dispatch(clearAccessToken());
    router.replace("/login");
  }

  if (!accessToken || isLoading) {
    return <main className="grid min-h-screen place-items-center text-ink/60">Memuat akun...</main>;
  }

  if (error) {
    return (
      <main className="grid min-h-screen place-items-center px-6">
        <p className="text-sm text-red-800" role="alert">
          {getApiErrorMessage(error)}
        </p>
      </main>
    );
  }

  return (
    <main className="mx-auto min-h-screen w-full max-w-5xl px-6 py-10">
      <header className="flex items-center justify-between border-b border-ink/10 pb-6">
        <Link className="font-semibold text-forest" href="/">
          School ERP
        </Link>
        <button
          className="rounded-full border border-ink/15 px-4 py-2 text-sm font-medium hover:border-forest hover:text-forest"
          onClick={signOut}
          type="button"
        >
          Keluar
        </button>
      </header>
      <section className="py-12">
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-forest">
          Ruang sekolah
        </p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight text-ink">
          Halo, {user?.full_name}
        </h1>
        <p className="mt-3 text-ink/60">
          Akun Anda terhubung dengan peran{" "}
          <span className="font-medium text-ink">{user?.role.replaceAll("_", " ")}</span>.
        </p>
        <div className="mt-10 rounded-3xl border border-ink/10 bg-white p-7">
          <h2 className="text-lg font-semibold text-ink">Fondasi sekolah Anda sudah siap</h2>
          <p className="mt-2 leading-7 text-ink/60">
            Pengelolaan siswa, guru, kelas, dan jadwal akan ditambahkan sebagai modul berikutnya.
          </p>
          {user?.role === "school_admin" || user?.role === "teacher" ? (
            <Link className="mt-5 inline-flex font-semibold text-forest hover:underline" href="/assistant">
              Buka AI assistant sekolah
              <span aria-hidden="true" className="ml-2">&rarr;</span>
            </Link>
          ) : null}
        </div>
      </section>
    </main>
  );
}
