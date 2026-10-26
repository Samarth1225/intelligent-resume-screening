export default function ScoreBar({ label, value, color = "var(--color-teal)" }) {
  const pct = Math.max(0, Math.min(100, value ?? 0));
  return (
    <div className="flex items-center gap-3">
      <span className="w-40 shrink-0 text-sm text-muted">{label}</span>
      <div className="h-2.5 flex-1 rounded-full bg-border">
        <div
          className="h-2.5 rounded-full transition-[width] duration-500"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      <span className="w-12 shrink-0 text-right text-sm font-semibold text-ink">{Math.round(pct)}%</span>
    </div>
  );
}
