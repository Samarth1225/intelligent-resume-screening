const BANDS = [
  { threshold: 80, label: "Strong" },
  { threshold: 65, label: "Good" },
  { threshold: 50, label: "Fair" },
  { threshold: 0, label: "Weak" },
];

export function scoreBand(score) {
  for (const b of BANDS) {
    if (score >= b.threshold) return b.label;
  }
  return "Weak";
}
