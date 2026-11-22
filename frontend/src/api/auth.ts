import { api } from "./client";

export type User = {
  id: string;
  email: string;
  created_at: string;
};

type Token = {
  access_token: string;
  token_type: string;
};

export const authApi = {
  register: (email: string, password: string) =>
    api<User>("/auth/register", { method: "POST", json: { email, password } }),

  login: (email: string, password: string) =>
    api<Token>("/auth/login", { method: "POST", form: { username: email, password } }),

  me: () => api<User>("/auth/me"),
};
