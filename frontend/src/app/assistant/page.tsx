"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import {
  useAskAssistantMutation,
  useGetAiJobQuery,
  useGetCurrentUserQuery,
  useGetKnowledgeDocumentsQuery,
  useUploadKnowledgeDocumentMutation,
} from "@/lib/authApi";
import { getApiErrorMessage } from "@/lib/api-error";
import { useAppSelector } from "@/lib/hooks";

const fieldClass =
  "mt-2 min-h-12 w-full rounded-xl border border-ink/15 bg-white px-4 text-ink outline-none focus:border-forest focus:ring-2 focus:ring-forest/15";

export default function AssistantPage() {
  const router = useRouter();
  const token = useAppSelector((state) => state.auth.accessToken);
  const { data: user, error: userError } = useGetCurrentUserQuery(undefined, {
    skip: !token,
  });
  const { data: documents = [], refetch: refreshDocuments } = useGetKnowledgeDocumentsQuery(
    undefined,
    { skip: !token, pollingInterval: 3000 },
  );
  const [uploadDocument, uploadState] = useUploadKnowledgeDocumentMutation();
  const [ask, askState] = useAskAssistantMutation();
  const [question, setQuestion] = useState("");
  const [activeJobId, setActiveJobId] = useState("");
  const jobQuery = useGetAiJobQuery(activeJobId, {
    skip: !activeJobId,
    pollingInterval: 2000,
  });

  useEffect(() => {
    if (!token) router.replace("/login");
    if (userError && "status" in userError && userError.status === 401) {
      router.replace("/login");
    }
  }, [token, userError, router]);

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const file = data.get("document");
    if (!(file instanceof File) || !file.size) return;
    await uploadDocument(file);
    form.reset();
    await refreshDocuments();
  }

  async function handleAsk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const response = await ask(question);
    if ("data" in response && response.data) {
      setActiveJobId(response.data.id);
    }
  }

  if (!token) {
    return <main className="grid min-h-screen place-items-center text-ink/60">Mengarahkan...</main>;
  }

  return (
    <main className="mx-auto min-h-screen w-full max-w-5xl px-6 py-10">
      <header className="flex items-center justify-between border-b border-ink/10 pb-6">
        <Link className="font-semibold text-forest" href="/dashboard">
          &larr; Kembali ke dashboard
        </Link>
        <p className="text-sm text-ink/60">{user?.full_name}</p>
      </header>
      <section className="py-12">
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-forest">
          Retrieval-augmented generation
        </p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight text-ink">
          AI assistant sekolah
        </h1>
        <p className="mt-3 max-w-2xl leading-7 text-ink/60">
          Unggah panduan sekolah berformat TXT atau Markdown, lalu ajukan pertanyaan. Dokumen
          dan pencarian dipisahkan per sekolah.
        </p>
        <div className="mt-10 grid gap-6 lg:grid-cols-2">
          <motion.section
            animate={{ opacity: 1, y: 0 }}
            className="rounded-3xl border border-ink/10 bg-white p-7"
            initial={{ opacity: 0, y: 12 }}
            transition={{ duration: 0.3 }}
          >
            <h2 className="text-lg font-semibold text-ink">Basis pengetahuan</h2>
            <form className="mt-5 space-y-4" onSubmit={handleUpload}>
              <label className="block text-sm font-medium text-ink">
                Pilih dokumen (maks. 5 MiB)
                <input
                  accept=".txt,.md,text/plain,text/markdown"
                  className={fieldClass}
                  name="document"
                  required
                  type="file"
                />
              </label>
              {uploadState.error && (
                <p className="text-sm text-red-800" role="alert">
                  {getApiErrorMessage(uploadState.error)}
                </p>
              )}
              {uploadState.isSuccess && (
                <p className="text-sm text-forest" role="status">
                  Dokumen masuk antrean untuk diindeks.
                </p>
              )}
              <button
                className="min-h-11 rounded-full bg-forest px-5 text-sm font-semibold text-white disabled:opacity-60"
                disabled={uploadState.isLoading}
                type="submit"
              >
                {uploadState.isLoading ? "Mengunggah..." : "Unggah dan indeks"}
              </button>
            </form>
            <ul className="mt-6 space-y-2" aria-label="Dokumen sekolah">
              {documents.map((document) => (
                <li
                  className="flex items-center justify-between rounded-xl bg-canvas px-4 py-3 text-sm"
                  key={document.id}
                >
                  <span className="truncate text-ink/70">{document.filename}</span>
                  <span className="ml-3 shrink-0 font-medium capitalize text-forest">
                    {document.status}
                  </span>
                </li>
              ))}
              {!documents.length && (
                <li className="text-sm text-ink/50">Belum ada dokumen yang diunggah.</li>
              )}
            </ul>
          </motion.section>
          <motion.section
            animate={{ opacity: 1, y: 0 }}
            className="rounded-3xl border border-ink/10 bg-white p-7"
            initial={{ opacity: 0, y: 12 }}
            transition={{ delay: 0.08, duration: 0.3 }}
          >
            <h2 className="text-lg font-semibold text-ink">Tanyakan pada dokumen</h2>
            <form className="mt-5 space-y-4" onSubmit={handleAsk}>
              <label className="block text-sm font-medium text-ink">
                Pertanyaan
                <textarea
                  className={`${fieldClass} min-h-32 py-3`}
                  maxLength={2000}
                  minLength={3}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="Contoh: Bagaimana prosedur izin tidak masuk?"
                  required
                  value={question}
                />
              </label>
              {askState.error && (
                <p className="text-sm text-red-800" role="alert">
                  {getApiErrorMessage(askState.error)}
                </p>
              )}
              <button
                className="min-h-11 rounded-full bg-forest px-5 text-sm font-semibold text-white disabled:opacity-60"
                disabled={askState.isLoading || documents.every((item) => item.status !== "ready")}
                type="submit"
              >
                {askState.isLoading ? "Mengirim..." : "Tanyakan"}
              </button>
              {documents.every((item) => item.status !== "ready") && (
                <p className="text-xs text-ink/50">
                  Indeks setidaknya satu dokumen sebelum mengajukan pertanyaan.
                </p>
              )}
            </form>
            {jobQuery.data && (
              <div className="mt-6 rounded-2xl bg-mint/70 p-5" aria-live="polite">
                <p className="text-sm font-semibold capitalize text-forest">
                  Status: {jobQuery.data.status}
                </p>
                {jobQuery.data.answer && (
                  <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-ink">
                    {jobQuery.data.answer}
                  </p>
                )}
                {jobQuery.data.error && (
                  <p className="mt-3 text-sm text-red-800">{jobQuery.data.error}</p>
                )}
              </div>
            )}
          </motion.section>
        </div>
      </section>
    </main>
  );
}
