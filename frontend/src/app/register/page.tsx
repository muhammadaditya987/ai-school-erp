"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { AuthFrame } from "@/components/auth-frame";
import { getApiErrorMessage } from "@/lib/api-error";
import { useRegisterSchoolMutation } from "@/lib/authApi";

const inputClassName =
  "mt-2 min-h-12 w-full rounded-xl border border-ink/15 bg-white px-4 text-ink outline-none transition focus:border-forest focus:ring-2 focus:ring-forest/15";

export default function RegisterPage() {
  const router = useRouter();
  const [registerSchool, { error, isLoading }] = useRegisterSchoolMutation();
  const [form, setForm] = useState({
    school_name: "",
    school_slug: "",
    full_name: "",
    email: "",
    password: "",
  });

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const result = await registerSchool(form);
    if ("data" in result) {
      router.push("/login?registered=1");
    }
  }

  return (
    <AuthFrame
      alternateHref="/login"
      alternateLabel="Masuk"
      alternateText="Sudah punya akun?"
      description="Buat ruang sekolah dan akun administrator untuk memulai."
      title="Daftarkan sekolah"
    >
      <form className="mt-7 space-y-4" onSubmit={handleSubmit}>
        <label className="block text-sm font-medium text-ink">
          Nama sekolah
          <input
            autoComplete="organization"
            className={inputClassName}
            maxLength={120}
            minLength={2}
            onChange={(event) =>
              setForm((current) => ({ ...current, school_name: event.target.value }))
            }
            required
            value={form.school_name}
          />
        </label>
        <label className="block text-sm font-medium text-ink">
          Alamat sekolah
          <input
            autoComplete="url"
            className={inputClassName}
            maxLength={63}
            minLength={3}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                school_slug: event.target.value.toLowerCase().replace(/[^a-z0-9-]/g, "-"),
              }))
            }
            pattern="[a-z0-9]+(-[a-z0-9]+)*"
            placeholder="contoh: sekolah-harapan"
            required
            value={form.school_slug}
          />
          <span className="mt-1 block text-xs text-ink/50">
            Gunakan huruf kecil, angka, dan tanda hubung.
          </span>
        </label>
        <label className="block text-sm font-medium text-ink">
          Nama administrator
          <input
            autoComplete="name"
            className={inputClassName}
            maxLength={120}
            minLength={2}
            onChange={(event) =>
              setForm((current) => ({ ...current, full_name: event.target.value }))
            }
            required
            value={form.full_name}
          />
        </label>
        <label className="block text-sm font-medium text-ink">
          Email
          <input
            autoComplete="email"
            className={inputClassName}
            onChange={(event) =>
              setForm((current) => ({ ...current, email: event.target.value }))
            }
            required
            type="email"
            value={form.email}
          />
        </label>
        <label className="block text-sm font-medium text-ink">
          Kata sandi
          <input
            autoComplete="new-password"
            className={inputClassName}
            minLength={12}
            onChange={(event) =>
              setForm((current) => ({ ...current, password: event.target.value }))
            }
            required
            type="password"
            value={form.password}
          />
          <span className="mt-1 block text-xs text-ink/50">Minimal 12 karakter.</span>
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
          {isLoading ? "Mendaftarkan..." : "Buat akun sekolah"}
        </button>
      </form>
    </AuthFrame>
  );
}
