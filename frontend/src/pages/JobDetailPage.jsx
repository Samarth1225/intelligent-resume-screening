import { useEffect, useMemo, useState, useCallback } from "react";
import { useParams, useNavigate, Navigate } from "react-router-dom";
import { Search, SlidersHorizontal, UploadCloud, ChevronDown, Trash2 } from "lucide-react";
import Layout from "../components/Layout";
import StatCard from "../components/StatCard";
import ScoreBadge from "../components/ScoreBadge";
import EmptyState from "../components/EmptyState";
import LoadingSpinner from "../components/LoadingSpinner";
import UploadDropzone from "../components/UploadDropzone";
import DeleteJobModal from "../components/DeleteJobModal";
import { jobsApi, apiErrorMessage } from "../api/client";

const SORT_OPTIONS = [
  { value: "score_desc", label: "Score: High to low" },
  { value: "score_asc", label: "Score: Low to high" },
  { value: "name_asc", label: "Name: A to Z" },
  { value: "name_desc", label: "Name: Z to A" },
];

export default function JobDetailPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();

  const [job, setJob] = useState(null);
  const [candidates, setCandidates] = useState(null);
  const [error, setError] = useState("");
  const [showUpload, setShowUpload] = useState(false);
  const [showDelete, setShowDelete] = useState(false);

  const [search, setSearch] = useState("");
  const [minScore, setMinScore] = useState(0);
  const [sortBy, setSortBy] = useState("score_desc");
  const [skillFilter, setSkillFilter] = useState([]);
  const [showSkillMenu, setShowSkillMenu] = useState(false);

  const loadJob = useCallback(async () => {
    try {
      const data = await jobsApi.get(jobId);
      setJob(data);
    } catch (err) {
      setError(apiErrorMessage(err, "Could not load this job."));
    }
  }, [jobId]);

  const loadCandidates = useCallback(async () => {
    try {
      const params = { sort_by: sortBy };
      if (search.trim()) params.search = search.trim();
      if (minScore > 0) params.min_score = minScore;
      if (skillFilter.length) params.skills = skillFilter.join(",");
      const data = await jobsApi.candidates(jobId, params);
      setCandidates(data);
    } catch (err) {
      setError(apiErrorMessage(err, "Could not load candidates."));
    }
  }, [jobId, search, minScore, sortBy, skillFilter]);

  useEffect(() => {
    loadJob();
  }, [loadJob]);

  useEffect(() => {
    const t = setTimeout(loadCandidates, 200); // light debounce for search typing
    return () => clearTimeout(t);
  }, [loadCandidates]);

  const allSkillOptions = useMemo(() => {
    if (!job) return [];
    return [...new Set([...job.required_skills, ...job.preferred_skills])];
  }, [job]);

  if (!jobId || Number.isNaN(Number(jobId))) return <Navigate to="/jobs" replace />;

  function toggleSkillFilter(skill) {
    setSkillFilter((prev) => (prev.includes(skill) ? prev.filter((s) => s !== skill) : [...prev, skill]));
  }

  async function handleUploaded() {
    await Promise.all([loadJob(), loadCandidates()]);
  }

  return (
    <Layout
      title={job ? job.title : "Job"}
      actions={
        job && (
          <>
            <button
              onClick={() => setShowDelete(true)}
              className="flex items-center gap-1.5 rounded-lg border border-bad/40 px-4 py-2.5 text-sm font-semibold text-bad hover:bg-bad-bg"
            >
              <Trash2 size={16} /> Delete
            </button>
            <button
              onClick={() => setShowUpload((v) => !v)}
              className="flex items-center gap-1.5 rounded-lg bg-deepblue px-4 py-2.5 text-sm font-semibold text-white hover:bg-navy"
            >
              <UploadCloud size={16} /> Upload Resumes
            </button>
          </>
        )
      }
    >
      {error && <p className="mb-4 text-sm text-bad">{error}</p>}

      {!job ? (
        <LoadingSpinner label="Loading job…" />
      ) : (
        <>
          <div className="rounded-xl border border-border bg-white p-5">
            <p className="text-sm leading-relaxed text-muted">{job.description}</p>
            <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm">
              <Meta label="Min. experience" value={`${job.min_experience} yrs`} />
              <Meta label="Education" value={job.education_requirement} />
            </div>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <SkillGroup label="Required skills" skills={job.required_skills} tone="required" />
              <SkillGroup label="Preferred skills" skills={job.preferred_skills} tone="preferred" />
            </div>
          </div>

          {showUpload && (
            <div className="mt-4 rounded-xl border border-border bg-white p-5">
              <h3 className="mb-3 font-display text-base font-semibold text-ink">Upload resumes</h3>
              <UploadDropzone jobId={job.id} onUploaded={handleUploaded} />
            </div>
          )}

          <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard label="Total Candidates" value={job.stats.total_candidates} />
            <StatCard label="Resumes Processed" value={job.stats.resumes_processed} />
            <StatCard label="Average Match Score" value={`${job.stats.average_match_score}%`} />
            <StatCard label="Candidates Above 80%" value={job.stats.candidates_above_80} />
          </div>

          <div className="mt-8">
            <div className="mb-3 flex flex-wrap items-center gap-3">
              <div className="relative min-w-[200px] max-w-sm flex-1">
                <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search by name or email…"
                  className="w-full rounded-lg border border-border bg-white py-2.5 pl-9 pr-3 text-sm outline-none focus:border-teal"
                />
              </div>

              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="rounded-lg border border-border bg-white px-3 py-2.5 text-sm outline-none focus:border-teal"
              >
                {SORT_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>

              <div className="flex items-center gap-2 rounded-lg border border-border bg-white px-3 py-2.5 text-sm">
                <SlidersHorizontal size={14} className="text-muted" />
                <span className="text-muted">Min score</span>
                <input
                  type="range"
                  min={0}
                  max={100}
                  step={5}
                  value={minScore}
                  onChange={(e) => setMinScore(Number(e.target.value))}
                  className="w-28 accent-teal"
                />
                <span className="w-9 text-right font-medium text-ink">{minScore}%</span>
              </div>

              {allSkillOptions.length > 0 && (
                <div className="relative">
                  <button
                    onClick={() => setShowSkillMenu((v) => !v)}
                    className="flex items-center gap-1.5 rounded-lg border border-border bg-white px-3 py-2.5 text-sm text-ink"
                  >
                    Skills {skillFilter.length > 0 && `(${skillFilter.length})`}
                    <ChevronDown size={14} className="text-muted" />
                  </button>
                  {showSkillMenu && (
                    <div className="absolute right-0 z-10 mt-1 w-56 rounded-lg border border-border bg-white p-2 shadow-lg">
                      {allSkillOptions.map((skill) => (
                        <label key={skill} className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-surface">
                          <input
                            type="checkbox"
                            checked={skillFilter.includes(skill)}
                            onChange={() => toggleSkillFilter(skill)}
                            className="accent-teal"
                          />
                          <span className="capitalize">{skill}</span>
                        </label>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {candidates === null ? (
              <LoadingSpinner label="Loading candidates…" />
            ) : candidates.length === 0 ? (
              <EmptyState
                title={job.stats.total_candidates === 0 ? "No candidates yet" : "No candidates match these filters"}
                description={
                  job.stats.total_candidates === 0
                    ? "Upload resumes to start scoring and ranking candidates for this role."
                    : "Try widening your search, score range, or skill filters."
                }
                action={
                  job.stats.total_candidates === 0 && (
                    <button
                      onClick={() => setShowUpload(true)}
                      className="rounded-lg bg-deepblue px-4 py-2.5 text-sm font-semibold text-white hover:bg-navy"
                    >
                      Upload resumes
                    </button>
                  )
                }
              />
            ) : (
              <div className="overflow-x-auto rounded-xl border border-border bg-white">
                <table className="w-full min-w-[820px] text-left text-sm">
                  <thead>
                    <tr className="border-b border-border bg-surface text-xs uppercase tracking-wide text-muted">
                      <th className="px-4 py-3 font-medium">Rank</th>
                      <th className="px-4 py-3 font-medium">Candidate</th>
                      <th className="px-4 py-3 font-medium">Email</th>
                      <th className="px-4 py-3 font-medium">Skills Matched</th>
                      <th className="px-4 py-3 font-medium">Experience</th>
                      <th className="px-4 py-3 font-medium">Match Score</th>
                      <th className="px-4 py-3 font-medium">Status</th>
                      <th className="px-4 py-3 font-medium"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {candidates.map((c) => (
                      <tr key={c.id} className="border-b border-border last:border-0 hover:bg-surface/60">
                        <td className="px-4 py-3 font-semibold text-ink">{c.rank}</td>
                        <td className="px-4 py-3 font-medium text-ink">{c.name}</td>
                        <td className="px-4 py-3 text-muted">{c.email}</td>
                        <td className="px-4 py-3 text-muted">{c.skills_matched_label}</td>
                        <td className="px-4 py-3 text-muted">
                          {c.experience_years != null ? `${c.experience_years} yrs` : "Not detected"}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="h-2 w-16 rounded-full bg-border">
                              <div
                                className="h-2 rounded-full bg-teal"
                                style={{ width: `${Math.min(100, c.overall_score)}%` }}
                              />
                            </div>
                            <span className="font-semibold text-ink">{c.overall_score}%</span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <ScoreBadge label={c.status_label} />
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button
                            onClick={() => navigate(`/candidates/${c.id}`)}
                            className="text-sm font-medium text-deepblue hover:underline"
                          >
                            View Details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}

      {showDelete && job && (
        <DeleteJobModal
          job={job}
          onClose={() => setShowDelete(false)}
          onDeleted={() => navigate("/jobs")}
        />
      )}
    </Layout>
  );
}

function Meta({ label, value }) {
  return (
    <div>
      <span className="text-muted">{label}: </span>
      <span className="font-medium text-ink">{value}</span>
    </div>
  );
}

function SkillGroup({ label, skills, tone }) {
  return (
    <div>
      <p className="mb-1.5 text-xs font-medium text-muted">{label}</p>
      {skills.length === 0 ? (
        <p className="text-xs text-muted/70">None specified</p>
      ) : (
        <div className="flex flex-wrap gap-1.5">
          {skills.map((s) => (
            <span
              key={s}
              className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${
                tone === "required" ? "bg-[#e6f0fb] text-deepblue" : "bg-[#eef3f7] text-ink"
              }`}
            >
              {s}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
