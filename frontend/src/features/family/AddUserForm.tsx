import { useState } from "react";
import { useCreateUser } from "./useCreateUser";
import { Button } from "../../components/ui/Button";
import { Plus } from "lucide-react";

const EMOJI_OPTIONS = ["😊", "😎", "🤩", "🥳", "😋", "🧒", "👦", "👧", "👨", "👩"];

export function AddUserForm({ onSuccess }: { onSuccess?: () => void }) {
  const [isOpen, setIsOpen] = useState(false);
  const [name, setName] = useState("");
  const [emoji, setEmoji] = useState(EMOJI_OPTIONS[0]);
  const { mutate, isPending } = useCreateUser();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    mutate(
      { name, emoji },
      {
        onSuccess: () => {
          setName("");
          setIsOpen(false);
          onSuccess?.();
        },
      },
    );
  }

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="flex h-14 w-14 items-center justify-center rounded-full border-2 border-dashed border-gray-300 text-gray-400 transition-colors hover:border-primary hover:text-primary"
        aria-label="Add family member"
      >
        <Plus size={24} />
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-xs space-y-3 rounded-xl bg-gray-50 p-4">
      <input
        type="text"
        required
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Name"
        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary focus:outline-none"
        autoFocus
      />
      <div className="flex flex-wrap gap-1.5">
        {EMOJI_OPTIONS.map((e) => (
          <button
            key={e}
            type="button"
            onClick={() => setEmoji(e)}
            className={`h-9 w-9 rounded-lg text-lg ${emoji === e ? "bg-primary/10 ring-2 ring-primary" : "bg-white hover:bg-gray-100"}`}
          >
            {e}
          </button>
        ))}
      </div>
      <div className="flex gap-2">
        <Button type="submit" size="sm" disabled={isPending}>
          Add
        </Button>
        <Button type="button" variant="ghost" size="sm" onClick={() => setIsOpen(false)}>
          Cancel
        </Button>
      </div>
    </form>
  );
}
