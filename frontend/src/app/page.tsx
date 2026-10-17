import Link from "next/link";

const capabilities = [
  {
    number: "01",
    title: "One trusted workspace",
    description:
      "Bring everyday school operations together behind clear access controls and reliable records.",
  },
  {
    number: "02",
    title: "Built for the school community",
    description:
      "Give educators, administrators, families, and learners a foundation for working in sync.",
  },
  {
    number: "03",
    title: "Ready for responsible AI",
    description:
      "Add helpful AI workflows on top of governed school data, with privacy and accountability in mind.",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen overflow-hidden">
      <header className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-6 lg:px-10">
        <Link aria-label="School ERP home" className="flex items-center gap-3" href="/">
          <span aria-hidden="true" className="grid size-10 place-items-center rounded-2xl bg-forest text-lg font-bold text-white">
            S
          </span>
          <span className="text-base font-semibold tracking-tight text-ink">School ERP</span>
        </Link>
        <span className="hidden rounded-full border border-ink/10 px-4 py-2 text-sm text-ink/65 sm:inline-flex">
          A better-connected school day
        </span>
      </header>

      <section className="mx-auto grid w-full max-w-7xl gap-14 px-6 pb-20 pt-14 lg:grid-cols-[1.1fr_0.9fr] lg:items-center lg:px-10 lg:pb-28 lg:pt-20">
        <div className="max-w-2xl">
          <p className="mb-6 inline-flex items-center gap-2 rounded-full bg-mint px-4 py-2 text-sm font-medium text-forest">
            <span aria-hidden="true" className="size-2 rounded-full bg-forest" />
            The foundation for what comes next
          </p>
          <h1 className="text-balance text-5xl font-semibold leading-[1.08] tracking-[-0.045em] text-ink sm:text-6xl lg:text-7xl">
            Make room for a
            {" "}
            <span className="text-forest">brighter school day.</span>
          </h1>
          <p className="mt-7 max-w-xl text-lg leading-8 text-ink/65">
            A thoughtful home for school operations, designed to bring people and
            information together as your community grows.
          </p>
          <a
            className="mt-9 inline-flex min-h-12 items-center justify-center rounded-full bg-forest px-6 text-sm font-semibold text-white transition hover:bg-ink focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-forest"
            href="#approach"
          >
            Explore the approach
            <span aria-hidden="true" className="ml-2">
              &rarr;
            </span>
          </a>
        </div>

        <div aria-label="A connected school community" className="relative mx-auto w-full max-w-lg">
          <div className="absolute inset-8 rounded-full bg-[#e9f2e5] blur-3xl" />
          <div className="relative rounded-[2rem] border border-ink/10 bg-white/80 p-5 shadow-[0_24px_80px_-36px_rgba(16,37,30,0.3)] sm:p-8">
            <div className="flex items-center justify-between border-b border-ink/10 pb-5">
              <div>
                <p className="text-sm font-medium text-ink/55">Your school, in sync</p>
                <p className="mt-1 text-lg font-semibold text-ink">A shared foundation</p>
              </div>
              <span aria-hidden="true" className="grid size-11 place-items-center rounded-2xl bg-mint text-xl text-forest">
                ✳
              </span>
            </div>
            <div className="space-y-3 py-6">
              {[
                ["Learning", "Space to focus on what matters"],
                ["Community", "A clearer way to stay connected"],
                ["Insight", "Information you can act on"],
              ].map(([title, detail], index) => (
                <div
                  className="flex items-center gap-4 rounded-2xl bg-canvas p-4"
                  key={title}
                >
                  <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-white text-sm font-semibold text-forest">
                    0{index + 1}
                  </span>
                  <div>
                    <p className="font-semibold text-ink">{title}</p>
                    <p className="mt-0.5 text-sm text-ink/55">{detail}</p>
                  </div>
                </div>
              ))}
            </div>
            <p className="rounded-xl bg-mint/70 px-4 py-3 text-sm leading-6 text-forest">
              Designed to grow with your school, one useful step at a time.
            </p>
          </div>
        </div>
      </section>

      <section className="border-y border-ink/10 bg-white/65" id="approach">
        <div className="mx-auto w-full max-w-7xl px-6 py-16 lg:px-10 lg:py-20">
          <div className="mb-10 max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-[0.16em] text-forest">
              A considered beginning
            </p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
              Built around the people who make a school.
            </h2>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            {capabilities.map((capability) => (
              <article
                className="rounded-3xl border border-ink/10 bg-white p-6 sm:p-7"
                key={capability.number}
              >
                <p className="text-sm font-semibold text-forest">{capability.number}</p>
                <h3 className="mt-8 text-lg font-semibold text-ink">{capability.title}</h3>
                <p className="mt-3 leading-7 text-ink/60">{capability.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <footer className="mx-auto flex w-full max-w-7xl flex-col gap-3 px-6 py-7 text-sm text-ink/50 sm:flex-row sm:items-center sm:justify-between lg:px-10">
        <p>School ERP</p>
        <p>Secure foundations. Better-connected schools.</p>
      </footer>
    </main>
  );
}
