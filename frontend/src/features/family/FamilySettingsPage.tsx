import { useState } from "react";
import { useFamily } from "./useFamily";
import { useUsers } from "./useUsers";
import { UserAvatar } from "./UserAvatar";
import { Button } from "../../components/ui/Button";
import { Spinner } from "../../components/ui/Spinner";
import { useAppStore } from "../../store/appStore";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateFamily } from "../../api/families";

export default function FamilySettingsPage() {
  const { data: family, isLoading: familyLoading } = useFamily();
  const { data: users } = useUsers();
  const queryClient = useQueryClient();
  const currentFamilyId = useAppStore((s) => s.currentFamilyId);
  const logout = useAppStore((s) => s.clearTokens);

  const [name, setName] = useState("");
  const [familySize, setFamilySize] = useState(4);
  const [initialized, setInitialized] = useState(false);

  if (family && !initialized) {
    setName(family.name);
    setFamilySize(family.family_size);
    setInitialized(true);
  }

  const updateMutation = useMutation({
    mutationFn: () => updateFamily(currentFamilyId!, { name, family_size: familySize }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["family"] });
    },
  });

  if (familyLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="mb-6 text-2xl font-bold text-text">Family Settings</h1>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          updateMutation.mutate();
        }}
        className="space-y-4 rounded-xl bg-surface p-6 shadow-sm"
      >
        <div>
          <label htmlFor="name" className="mb-1 block text-sm font-medium text-text">
            Family Name
          </label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2.5 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
          />
        </div>

        <div>
          <label htmlFor="size" className="mb-1 block text-sm font-medium text-text">
            Family Size: {familySize}
          </label>
          <input
            id="size"
            type="range"
            min={1}
            max={20}
            value={familySize}
            onChange={(e) => setFamilySize(Number(e.target.value))}
            className="w-full accent-primary"
          />
        </div>

        <Button type="submit" className="w-full" disabled={updateMutation.isPending}>
          {updateMutation.isPending ? "Saving..." : "Save Changes"}
        </Button>
      </form>

      {users && users.length > 0 && (
        <div className="mt-8">
          <h2 className="mb-4 text-lg font-semibold text-text">Family Members</h2>
          <div className="flex flex-wrap gap-4">
            {users.map((user) => (
              <UserAvatar key={user.id} emoji={user.emoji} name={user.name} />
            ))}
          </div>
        </div>
      )}

      <div className="mt-8 border-t border-gray-200 pt-6">
        <Button variant="danger" onClick={logout} className="w-full">
          Sign Out
        </Button>
      </div>
    </div>
  );
}
