import { useState } from "react";
import { useNavigate, Navigate } from "react-router-dom";
import { ScanSearch, CheckCircle2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { DEMO_EMAIL, DEMO_PASSWORD } from "../constants";

const FEATURES = [
  "Parse resumes and score every candidate against your job description",
  "Rank candidates automatically, with a plain-language reason for every score",
  "Filter and search a live recruiter dashboard — no spreadsheets required",
];

export default function LoginPage() {
  const { isAuthenticated, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState(DEMO_EMAIL);
  const [password, setPassword] = useState(DEMO_PASSWORD);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (isAuthenticated) return <Navigate to="/dashboard" replace />;

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    const result = await login(email, password);
    setSubmitting(false);
    if (result.ok) {
      navigate("/dashboard");
    } else {
      setError(result.error);
    }
  }

  return (
    <div className="flex min-h-screen">
      <div className="hidden w-1/2 flex-col justify-between bg-navy px-12 py-12 text-white lg:flex">
        <div className="flex items-center gap-2.5">
          <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-mint/20 text-mint">
            <ScanSearch size={22} />
          </span>
          <span className="font-display text-lg font-semibold">IRSCS</span>
        </div>

        <div className="max-w-md">
          <h1 className="font-display text-4xl font-semibold leading-tight">
            Screen resumes against the job, not a hunch.
          </h1>
          <p className="mt-4 text-white/70">
            An AI-assisted recruitment dashboard that parses resumes, scores candidates against your
            job description, and explains every ranking in plain language.
          </p>
          <ul className="mt-8 space-y-3">
            {FEATURES.map((f) => (
              <li key={f} className="flex items-start gap-2.5 text-sm text-white/80">
                <CheckCircle2 size={16} className="mt-0.5 shrink-0 text-mint" />
                {f}
              </li>
            ))}
          </ul>
        </div>

        <p className="text-xs text-white/40">
          Automated job-description matching — intended to assist, not replace, human recruitment decisions.
        </p>
      </div>

      <div className="flex w-full flex-col justify-center px-6 py-12 sm:px-12 lg:w-1/2">
        <div className="mx-auto w-full max-w-sm">
          <div className="mb-8 lg:hidden">
            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-deepblue/10 text-deepblue">
              <ScanSearch size={22} />
            </span>
          </div>

          <h2 className="font-display text-2xl font-semibold text-ink">Recruiter sign in</h2>
          <p className="mt-1.5 text-sm text-muted">Sign in to view jobs and ranked candidates.</p>

          <form onSubmit={handleSubmit} className="mt-7 space-y-4">
            {error && (
              <div className="rounded-lg border border-bad/30 bg-bad-bg px-3.5 py-2.5 text-sm text-bad">
                {error}
              </div>
            )}
            <div>
              <label className="mb-1.5 block text-sm font-medium text-ink">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-lg border border-border px-3 py-2.5 text-sm outline-none focus:border-teal"
                required
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-ink">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border border-border px-3 py-2.5 text-sm outline-none focus:border-teal"
                required
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-lg bg-deepblue py-2.5 text-sm font-semibold text-white transition-colors hover:bg-navy disabled:opacity-50"
            >
              {submitting ? "Signing in…" : "Sign in"}
            </button>
          </form>

          <div className="mt-6 rounded-lg border border-border bg-surface px-4 py-3 text-xs text-muted">
            <p className="font-medium text-ink">Demo credentials (prefilled)</p>
            <p className="mt-1">Email: {DEMO_EMAIL}</p>
            <p>Password: {DEMO_PASSWORD}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
