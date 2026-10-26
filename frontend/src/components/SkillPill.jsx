export default function SkillPill({ name, variant = "neutral" }) {
  const styles = {
    matched: "bg-good-bg text-good border-good/30",
    missing: "bg-bad-bg text-bad border-bad/30",
    neutral: "bg-[#eef3f7] text-ink border-border",
  };
  return (
    <span className={`inline-block rounded-full border px-3 py-1 text-xs font-medium capitalize ${styles[variant]}`}>
      {name}
    </span>
  );
}
