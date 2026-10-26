const STYLES = {
  Strong: "bg-good-bg text-good",
  Good: "bg-[#e6f0fb] text-deepblue",
  Fair: "bg-warn-bg text-warn",
  Weak: "bg-bad-bg text-bad",
};

export default function ScoreBadge({ label }) {
  const cls = STYLES[label] || STYLES.Weak;
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${cls}`}>
      {label}
    </span>
  );
}
