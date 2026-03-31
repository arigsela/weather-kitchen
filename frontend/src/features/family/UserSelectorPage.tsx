import { useNavigate } from "react-router";
import { useUsers } from "./useUsers";
import { UserAvatar } from "./UserAvatar";
import { AddUserForm } from "./AddUserForm";
import { Spinner } from "../../components/ui/Spinner";
import { useCurrentUser } from "../../hooks/useCurrentUser";

export default function UserSelectorPage() {
  const navigate = useNavigate();
  const { data: users, isLoading } = useUsers();
  const { currentUserId, setCurrentUser } = useCurrentUser();

  function handleSelect(userId: string) {
    setCurrentUser(userId);
    navigate("/");
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-lg text-center">
      <h1 className="mb-2 text-2xl font-bold text-text">Who's cooking today?</h1>
      <p className="mb-8 text-text-muted">Pick a chef to get started</p>

      <div className="flex flex-wrap items-start justify-center gap-6">
        {users?.map((user) => (
          <UserAvatar
            key={user.id}
            emoji={user.emoji}
            name={user.name}
            size="lg"
            isActive={user.id === currentUserId}
            onClick={() => handleSelect(user.id)}
          />
        ))}
        <AddUserForm />
      </div>
    </div>
  );
}
