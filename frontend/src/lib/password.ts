// Keep in sync with PASSWORD_RULES in app/schemas/auth.py.
export const PASSWORD_MIN_LENGTH = 8;
export const PASSWORD_MAX_LENGTH = 128;

export type PasswordRule = { label: string; test: (value: string) => boolean };

export const passwordRules: PasswordRule[] = [
  {
    label: `${PASSWORD_MIN_LENGTH}–${PASSWORD_MAX_LENGTH} characters`,
    test: (v) => v.length >= PASSWORD_MIN_LENGTH && v.length <= PASSWORD_MAX_LENGTH,
  },
  { label: "A lowercase letter", test: (v) => /[a-z]/.test(v) },
  { label: "An uppercase letter", test: (v) => /[A-Z]/.test(v) },
  { label: "A digit", test: (v) => /\d/.test(v) },
  { label: "A special character", test: (v) => /[^A-Za-z0-9\s]/.test(v) },
  { label: "No spaces", test: (v) => v.length > 0 && /^\S+$/.test(v) },
];

export function isStrongPassword(value: string): boolean {
  return passwordRules.every((rule) => rule.test(value));
}
