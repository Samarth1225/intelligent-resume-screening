import { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Mail, Phone, GraduationCap, Briefcase, RefreshCcw } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import Layout from "../components/Layout";
import ScoreBadge from "../components/ScoreBadge";
import ScoreBar from "../components/ScoreBar";
import SkillPill from "../components/SkillPill";
import ExplanationList from "../components/ExplanationList";
import LoadingSpinner from "../components/LoadingSpinner";
import { candidatesApi, apiErrorMessage } from "../api/client";
import { scoreBand } from "../utils/scoreBand";

export default function CandidateDetailPage() {
  const { candidateId } = useParams();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [error, setError] = useState("");
  const [reanalyzing, setReanalyzing] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await candidatesApi.get(candidateId);
      setCandidate(data);
    } catch (err) {
      setError(apiErrorMessage(err, "Could not load this candidate."));
    }
  }, [candidateId]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleReanalyze() {
    setReanalyzing(true);
    try {
      const data = await candidatesApi.analyze(candidateId);
      setCandidate(data);
    } catch (err) {
      setError(apiErrorMessage(err, "Could not re-analyze this candidate."));
    } finally {
      setReanalyzing(false);
    }
  }

  const chartData = candidate
    ? [
        { name: "Skill", value: candidate.score.skill_score },
        { name: "Experience", value: candidate.score.experience_score },
        { name: "Education", value: candidate.score.education_score },
        { name: "Project", value: candidate.score.project_score },
        { name: "Semantic", value: candidate.score.semantic_score },
      ]
    : [];

  return (
    <Layout
      title="Candidate Profile"
      actions={
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-muted hover:bg-surface"
        >
          <ArrowLeft size={16} /> Back
        </button>
      }
    >
      {error && <p className="mb-4 text-sm text-bad">{error}</p>}

      {!candidate ? (
        <LoadingSpinner label="Loading candidate…" />
      ) : (
        <div className="grid gap-5 lg:grid-cols-3">
          {/* Left: identity + facts */}
          <div className="space-y-5 lg:col-span-1">
            <div className="rounded-xl border border-border bg-white p-5">
              <h2 className="font-display text-xl font-semibold text-ink">{candidate.name}</h2>
              <div className="mt-3 space-y-2 text-sm text-muted">
                <p className="flex items-center gap-2"><Mail size={14} /> {candidate.email}</p>
                <p className="flex items-center gap-2"><Phone size={14} /> {candidate.phone}</p>
                <p className="flex items-center gap-2"><GraduationCap size={14} /> {candidate.education}</p>
                <p className="flex items-center gap-2">
                  <Briefcase size={14} />
                  {candidate.experience_years != null ? `${candidate.experience_years} years experience` : "Experience not detected"}
                </p>
              </div>
              {candidate.resume_filename && (
                <p className="mt-3 truncate text-xs text-muted/70">Source file: {candidate.resume_filename}</p>
              )}
            </div>

            <div className="rounded-xl border border-border bg-white p-5">
              <h3 className="mb-2.5 font-display text-base font-semibold text-ink">Skills</h3>
              <div className="flex flex-wrap gap-1.5">
                {candidate.skills.length === 0 ? (
                  <p className="text-sm text-muted">Not detected</p>
                ) : (
                  candidate.skills.map((s) => {
                    const isMissing = candidate.score.missing_skills.includes(s);
                    const isMatched = candidate.score.matched_skills.includes(s);
                    return <SkillPill key={s} name={s} variant={isMatched ? "matched" : isMissing ? "missing" : "neutral"} />;
                  })
                )}
              </div>

              {candidate.score.missing_skills.length > 0 && (
                <>
                  <h4 className="mb-2 mt-4 text-xs font-medium uppercase tracking-wide text-muted">
                    Missing / unmatched skills
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {candidate.score.missing_skills.map((s) => (
                      <SkillPill key={s} name={s} variant="missing" />
                    ))}
                  </div>
                </>
              )}
            </div>

            <div className="rounded-xl border border-border bg-white p-5">
              <h3 className="mb-2 font-display text-base font-semibold text-ink">Certifications</h3>
              {candidate.certifications.length === 0 ? (
                <p className="text-sm text-muted">Not detected</p>
              ) : (
                <ul className="list-inside list-disc space-y-1 text-sm text-ink">
                  {candidate.certifications.map((c, i) => <li key={i}>{c}</li>)}
                </ul>
              )}
            </div>
          </div>

          {/* Right: score breakdown + explanation + projects/experience */}
          <div className="space-y-5 lg:col-span-2">
            <div className="rounded-xl border border-border bg-white p-5">
              <div className="mb-4 flex items-center justify-between">
                <h3 className="font-display text-base font-semibold text-ink">Job Match Analysis</h3>
                <div className="flex items-center gap-3">
                  <ScoreBadge label={scoreBand(candidate.score.overall_score)} />
                  <button
                    onClick={handleReanalyze}
                    disabled={reanalyzing}
                    className="flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-muted hover:bg-surface disabled:opacity-50"
                    title="Re-run scoring against the current job requirements"
                  >
                    <RefreshCcw size={13} className={reanalyzing ? "animate-spin" : ""} /> Re-analyze
                  </button>
                </div>
              </div>

              <div className="mb-5 flex items-end gap-4 rounded-lg bg-surface p-4">
                <span className="font-display text-4xl font-bold text-deepblue">{candidate.score.overall_score}%</span>
                <span className="pb-1 text-sm text-muted">Overall Job-Description Match Score</span>
              </div>

              <div className="space-y-3">
                <ScoreBar label="Skill Match" value={candidate.score.skill_score} color="var(--color-deepblue)" />
                <ScoreBar label="Experience Match" value={candidate.score.experience_score} color="var(--color-teal)" />
                <ScoreBar label="Education Match" value={candidate.score.education_score} color="var(--color-mint)" />
                <ScoreBar label="Project Relevance" value={candidate.score.project_score} color="#7fb3d5" />
                <ScoreBar label="Semantic Similarity" value={candidate.score.semantic_score} color="var(--color-navy)" />
              </div>

              <div className="mt-5 h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} stroke="var(--color-muted)" />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} stroke="var(--color-muted)" />
                    <Tooltip formatter={(v) => `${v}%`} />
                    <Bar dataKey="value" fill="var(--color-teal)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <p className="mt-2 text-xs text-muted">
                This is a job-description match score, not a measure of the candidate's overall quality or a hiring
                recommendation.
              </p>
            </div>

            <div className="rounded-xl border border-border bg-white p-5">
              <h3 className="mb-2.5 font-display text-base font-semibold text-ink">Why this score?</h3>
              <ExplanationList points={candidate.score.explanation} />
            </div>

            <div className="rounded-xl border border-border bg-white p-5">
              <h3 className="mb-2 font-display text-base font-semibold text-ink">Experience</h3>
              <p className="whitespace-pre-line text-sm text-ink">{candidate.experience_text}</p>
            </div>

            <div className="rounded-xl border border-border bg-white p-5">
              <h3 className="mb-2 font-display text-base font-semibold text-ink">Projects</h3>
              <p className="whitespace-pre-line text-sm text-ink">{candidate.projects_text}</p>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
