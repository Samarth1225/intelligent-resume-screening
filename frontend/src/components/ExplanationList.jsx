export default function ExplanationList({ points }) {
  if (!points || points.length === 0) {
    return <p className="text-sm text-muted">No explanation available for this candidate yet.</p>;
  }
  return (
    <ul className="space-y-2.5">
      {points.map((p, i) => (
        <li key={i} className="flex items-start gap-3 text-sm">
          <span
            className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white ${
              p.type === "+" ? "bg-good" : "bg-bad"
            }`}
            aria-hidden="true"
          >
            {p.type === "+" ? "+" : "\u2212"}
          </span>
          <span className="text-ink">{p.text}</span>
        </li>
      ))}
    </ul>
  );
}
