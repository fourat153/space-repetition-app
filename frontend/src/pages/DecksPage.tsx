import { useEffect, useState, type FormEvent } from "react";
import { Layers, LogOut, Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { decksApi, type Deck } from "@/api/decks";
import { useAuth } from "@/auth/AuthContext";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardAction, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";

const errorMessage = (err: unknown, fallback: string) => (err instanceof Error ? err.message : fallback);
const byName = (a: Deck, b: Deck) => a.name.localeCompare(b.name);
const plural = (n: number) => (n === 1 ? "1 card" : `${n} cards`);

export function DecksPage() {
  const { user, logout } = useAuth();
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(true);
  const [newName, setNewName] = useState("");
  const [renaming, setRenaming] = useState<Deck | null>(null);
  const [deleting, setDeleting] = useState<Deck | null>(null);

  useEffect(() => {
    decksApi
      .list()
      .then(setDecks)
      .catch((err) => toast.error(errorMessage(err, "Could not load decks")))
      .finally(() => setLoading(false));
  }, []);

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    const name = newName.trim();
    if (!name) return;
    try {
      const deck = await decksApi.create({ name });
      setDecks((current) => [...current, deck].sort(byName));
      setNewName("");
      toast.success(`Deck "${deck.name}" created`);
    } catch (err) {
      toast.error(errorMessage(err, "Could not create deck"));
    }
  }

  async function handleRename(deck: Deck, name: string) {
    try {
      const updated = await decksApi.update(deck.id, { name });
      setDecks((current) => current.map((d) => (d.id === deck.id ? updated : d)).sort(byName));
      setRenaming(null);
      toast.success("Deck renamed");
    } catch (err) {
      toast.error(errorMessage(err, "Could not rename deck"));
    }
  }

  async function handleDelete(deck: Deck) {
    try {
      const { deleted_cards } = await decksApi.remove(deck.id);
      setDecks((current) => current.filter((d) => d.id !== deck.id));
      toast.success(`"${deck.name}" deleted with ${plural(deleted_cards)}`);
    } catch (err) {
      toast.error(errorMessage(err, "Could not delete deck"));
    } finally {
      setDeleting(null);
    }
  }

  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-6 p-4 sm:p-6">
      <header className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Layers className="text-primary size-6" />
          <h1 className="text-2xl font-bold">My decks</h1>
        </div>
        <div className="flex items-center gap-1">
          <span className="text-muted-foreground hidden text-sm sm:inline">{user?.email}</span>
          <Button variant="ghost" size="icon" onClick={logout} aria-label="Log out">
            <LogOut />
          </Button>
        </div>
      </header>

      <form onSubmit={handleCreate} className="flex gap-2">
        <Input
          placeholder="New deck name, e.g. Spanish verbs"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          maxLength={100}
        />
        <Button type="submit" disabled={!newName.trim()}>
          <Plus />
          Add
        </Button>
      </form>

      {loading ? (
        <div className="grid gap-3">
          {[0, 1, 2].map((i) => (
            <Skeleton key={i} className="h-[88px] rounded-xl" />
          ))}
        </div>
      ) : decks.length === 0 ? (
        <div className="text-muted-foreground flex flex-col items-center gap-2 rounded-xl border border-dashed py-12 text-center">
          <Layers className="size-8" />
          <p className="font-medium">No decks yet</p>
          <p className="text-sm">Create your first deck above.</p>
        </div>
      ) : (
        <ul className="grid gap-3">
          {decks.map((deck) => (
            <li key={deck.id}>
              <Card className="gap-0">
                <CardHeader>
                  <CardTitle className="text-base">{deck.name}</CardTitle>
                  <CardDescription>
                    <Badge variant="secondary">{plural(deck.card_count)}</Badge>
                  </CardDescription>
                  <CardAction className="flex gap-1">
                    <Button variant="ghost" size="icon" onClick={() => setRenaming(deck)} aria-label="Rename">
                      <Pencil />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-destructive hover:text-destructive"
                      onClick={() => setDeleting(deck)}
                      aria-label="Delete"
                    >
                      <Trash2 />
                    </Button>
                  </CardAction>
                </CardHeader>
              </Card>
            </li>
          ))}
        </ul>
      )}

      <RenameDeckDialog deck={renaming} onClose={() => setRenaming(null)} onSave={handleRename} />

      <AlertDialog open={deleting !== null} onOpenChange={(open) => !open && setDeleting(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete "{deleting?.name}"?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete the deck and its {plural(deleting?.card_count ?? 0)}. This can't be
              undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive hover:bg-destructive/90 text-white"
              onClick={() => deleting && handleDelete(deleting)}
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </main>
  );
}

type RenameDeckDialogProps = {
  deck: Deck | null;
  onClose: () => void;
  onSave: (deck: Deck, name: string) => Promise<void>;
};

function RenameDeckDialog({ deck, onClose, onSave }: RenameDeckDialogProps) {
  const [name, setName] = useState("");

  useEffect(() => {
    if (deck) setName(deck.name);
  }, [deck]);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = name.trim();
    if (!deck || !trimmed || trimmed === deck.name) return onClose();
    onSave(deck, trimmed);
  }

  return (
    <Dialog open={deck !== null} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <form onSubmit={handleSubmit} className="grid gap-4">
          <DialogHeader>
            <DialogTitle>Rename deck</DialogTitle>
            <DialogDescription>Give "{deck?.name}" a new name.</DialogDescription>
          </DialogHeader>
          <Input value={name} onChange={(e) => setName(e.target.value)} maxLength={100} autoFocus />
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">Save</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
