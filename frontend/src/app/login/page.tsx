"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { useState, type FormEvent } from "react";

import { AuthFrame } from "@/components/auth-frame";
import { getApiErrorMessage } from "@/lib/api-error";
import { useAppDispatch } from "@/lib/hooks";
import { useCreateAccessTokenMutation } from "@/lib/authApi";
import { setAccessToken } from "@/lib/authSlice";

const inputClassName =
  "mt-2 min-h-12 w-full rounded-xl border border-ink/15 bg-white px-4 text-ink outline-none transition focus:border-forest focus:ring-2 focus:ring-forest/15";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const dispatch = useAppDispatch();
  const [createAccessToken, { error, isLoading }] = useCreateAccessTokenMutation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const result = await createAccessToken({ email, password });
    if ("data" in result && result.data) {
      dispatch(setAccessToken(result.data.access_token));
      router.replace("/dashboard");
    }
  }

  return (
    <AuthFrame
      alternateHref="/register"
      alternateLabel="Daftarkan sekolah"
      alternateText="Belum punya akun?"
      description="Masuk ke ruang kerja sekolah Anda."
      title="Selamat datang kembali"
    >
      {searchParams.get("registered") === "1" && (
        <p className="mt-5 rounded-xl bg-mint px-4 py-3 text-sm text-forest" role="status">
          Sekolah berhasil didaftarkan. Silakan masuk dengan akun administrator Anda.
        </p>
      )}
      <form className="mt-7 space-y-4" onSubmit={handleSubmit}>
        <label className="block text-sm font-medium text-ink">
          Email
          <input
            autoComplete="username"
            className={inputClassName}
            onChange={(event) => setEmail(event.target.value)}
            required
            type="email"
            value={email}
          />
        </label>
        <label className="block text-sm font-medium text-ink">
          Kata sandi
          <input
            autoComplete="current-password"
            className={inputClassName}
            onChange={(event) => setPassword(event.target.value)}
            required
            type="password"
            value={password}
          />
        </label>
        {error && (
          <p className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-800" role="alert">
            {getApiErrorMessage(error)}
          </p>
        )}
        <button
          className="min-h-12 w-full rounded-full bg-forest px-5 font-semibold text-white transition hover:bg-ink disabled:cursor-wait disabled:opacity-60"
          disabled={isLoading}
          type="submit"
        >
          {isLoading ? "Memeriksa..." : "Masuk"}
        </button>
      </form>
      <p className="mt-5 text-center text-xs leading-5 text-ink/50">
        Sesi autentikasi disimpan sementara di memori browser dan berakhir ketika halaman dimuat
        ulang.
      </p>
    </AuthFrame>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<main className="grid min-h-screen place-items-center">Memuat...</main>}>
      <LoginForm />
    </Suspense>
  );
}
