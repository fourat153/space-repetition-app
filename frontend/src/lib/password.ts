// Keep in sync with PASSWORD_RULES in app/schemas/auth.py.
export const PASSWORD_MIN_LENGTH = 8;
export const PASSWORD_MAX_LENGTH = 128;

// `hint` completes the sentence "Needs …".
export type PasswordRule = { hint: string; test: (value: string) => boolean };

export const passwordRules: PasswordRule[] = [
  {
    hint: `at least ${PASSWORD_MIN_LENGTH} characters`,
    test: (v) => v.length >= PASSWORD_MIN_LENGTH && v.length <= PASSWORD_MAX_LENGTH,
  },
  { hint: "a lowercase letter", test: (v) => /[a-z]/.test(v) },
  { hint: "an uppercase letter", test: (v) => /[A-Z]/.test(v) },
  { hint: "a number", test: (v) => /\d/.test(v) },
  { hint: "a symbol", test: (v) => /[^A-Za-z0-9\s]/.test(v) },
  { hint: "no spaces", test: (v) => v.length > 0 && /^\S+$/.test(v) },
];

export function isStrongPassword(value: string): boolean {
  return passwordRules.every((rule) => rule.test(value));
}

export type PasswordStrength = {
  /** 1 (weak) to 4 (meets every rule). */
  score: 1 | 2 | 3 | 4;
  label: string;
  missing: string[];
};

export function getPasswordStrength(value: string): PasswordStrength {
  const missing = passwordRules.filter((rule) => !rule.test(value)).map((rule) => rule.hint);
  const passed = passwordRules.length - missing.length;
  if (missing.length === 0) return { score: 4, label: "Strong", missing };
  if (passed >= 5) return { score: 3, label: "Almost there", missing };
  if (passed >= 3) return { score: 2, label: "Fair", missing };
  return { score: 1, label: "Weak", missing };
}

/** ["a", "b", "c"] -> "a, b and c" */
export function formatList(items: string[]): string {
  if (items.length <= 1) return items.join("");
  return `${items.slice(0, -1).join(", ")} and ${items[items.length - 1]}`;
}
