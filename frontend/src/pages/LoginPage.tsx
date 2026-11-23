import { useState, type FormEvent } from "react";
import { Navigate } from "react-router-dom";
import { AlertCircle, Check, Layers, Loader2, X } from "lucide-react";

import { useAuth } from "@/auth/AuthContext";
import { isStrongPassword, passwordRules } from "@/lib/password";
import { cn } from "@/lib/utils";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function LoginPage() {
  const { user, login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const isLogin = mode === "login";
  const passwordsMismatch = confirmPassword.length > 0 && confirmPassword !== password;

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    if (!isLogin) {
      if (!isStrongPassword(password)) {
        setError("Password doesn't meet all the requirements below.");
        return;
      }
      if (password !== confirmPassword) {
        setError("Passwords do not match.");
        return;
      }
    }
    setSubmitting(true);
    try {
      if (isLogin) await login(email, password);
      else await register(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-4">
      <div className="flex items-center gap-2 text-2xl font-bold">
        <Layers className="text-primary size-7" />
        Chall
      </div>

      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle className="text-xl">{isLogin ? "Welcome back" : "Create an account"}</CardTitle>
          <CardDescription>
            {isLogin ? "Log in to continue reviewing your cards." : "Start building your decks."}
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleSubmit}>
          <CardContent className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder={isLogin ? "Your password" : "Choose a strong password"}
                autoComplete={isLogin ? "current-password" : "new-password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={isLogin ? undefined : 8}
                maxLength={isLogin ? undefined : 128}
                aria-describedby={isLogin ? undefined : "password-rules"}
                required
              />
              {!isLogin && (
                <ul id="password-rules" className="grid gap-1 text-xs" aria-live="polite">
                  {passwordRules.map((rule) => {
                    const ok = rule.test(password);
                    return (
                      <li
                        key={rule.label}
                        className={cn(
                          "flex items-center gap-1.5",
                          ok ? "text-emerald-600 dark:text-emerald-400" : "text-muted-foreground",
                        )}
                      >
                        {ok ? <Check className="size-3.5" /> : <X className="size-3.5" />}
                        {rule.label}
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
            {!isLogin && (
              <div className="grid gap-2">
                <Label htmlFor="confirm-password">Confirm password</Label>
                <Input
                  id="confirm-password"
                  type="password"
                  placeholder="Repeat your password"
                  autoComplete="new-password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  aria-invalid={passwordsMismatch}
                  aria-describedby={passwordsMismatch ? "confirm-password-error" : undefined}
                  required
                />
                {passwordsMismatch && (
                  <p id="confirm-password-error" className="text-destructive text-xs">
                    Passwords do not match.
                  </p>
                )}
              </div>
            )}

            {error && (
              <Alert variant="destructive">
                <AlertCircle />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </CardContent>

          <CardFooter className="mt-6 flex-col gap-2">
            <Button type="submit" className="w-full" disabled={submitting}>
              {submitting && <Loader2 className="animate-spin" />}
              {isLogin ? "Log in" : "Sign up"}
            </Button>
            <Button
              type="button"
              variant="link"
              onClick={() => {
                setMode(isLogin ? "register" : "login");
                setError(null);
                setConfirmPassword("");
              }}
            >
              {isLogin ? "No account? Sign up" : "Have an account? Log in"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </main>
  );
}
