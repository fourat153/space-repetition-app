import { api } from "./client";

export type Deck = {
  id: string;
  name: string;
  description: string | null;
  card_count: number;
  created_at: string;
  updated_at: string;
};

export type DeckInput = {
  name: string;
  description?: string | null;
};

export const decksApi = {
  list: () => api<Deck[]>("/decks"),
  get: (id: string) => api<Deck>(`/decks/${id}`),
  create: (data: DeckInput) => api<Deck>("/decks", { method: "POST", json: data }),
  update: (id: string, data: Partial<DeckInput>) =>
    api<Deck>(`/decks/${id}`, { method: "PATCH", json: data }),
  remove: (id: string) =>
    api<{ id: string; deleted_cards: number }>(`/decks/${id}`, { method: "DELETE" }),
};
