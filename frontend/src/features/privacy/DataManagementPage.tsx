import { useState } from "react";
import { useNavigate } from "react-router";
import { Button } from "../../components/ui/Button";
import { Modal } from "../../components/ui/Modal";
import { Spinner } from "../../components/ui/Spinner";
import { useCurrentFamily } from "../../hooks/useCurrentFamily";
import { useAppStore } from "../../store/appStore";
import { exportFamilyData, deleteFamily } from "../../api/families";
import { Download, Trash2 } from "lucide-react";

export default function DataManagementPage() {
  const navigate = useNavigate();
  const { currentFamilyId } = useCurrentFamily();
  const clearTokens = useAppStore((s) => s.clearTokens);
  const [isExporting, setIsExporting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [password, setPassword] = useState("");
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  async function handleExport() {
    if (!currentFamilyId) return;
    setIsExporting(true);
    try {
      const data = await exportFamilyData(currentFamilyId);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "weather-kitchen-data.json";
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert("Failed to export data. Please try again.");
    } finally {
      setIsExporting(false);
    }
  }

  async function handleDelete() {
    if (!currentFamilyId) return;
    setDeleteError(null);
    setIsDeleting(true);
    try {
      await deleteFamily(currentFamilyId, password);
      clearTokens();
      navigate("/");
    } catch {
      setDeleteError("Failed to delete. Check your password and try again.");
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="mb-6 text-2xl font-bold text-text">Data Management</h1>

      <div className="space-y-6">
        <div className="rounded-xl bg-surface p-6 shadow-sm">
          <div className="flex items-start gap-3">
            <Download size={24} className="mt-0.5 text-secondary" />
            <div className="flex-1">
              <h2 className="text-lg font-semibold text-text">Export My Data</h2>
              <p className="mt-1 text-sm text-text-muted">
                Download all your family data as a JSON file. This includes your family info, users,
                ingredients, and favorites.
              </p>
              <Button
                variant="secondary"
                size="sm"
                className="mt-3"
                onClick={handleExport}
                disabled={isExporting}
              >
                {isExporting ? <Spinner size="sm" /> : "Download Data"}
              </Button>
            </div>
          </div>
        </div>

        <div className="rounded-xl border-2 border-danger/20 bg-surface p-6 shadow-sm">
          <div className="flex items-start gap-3">
            <Trash2 size={24} className="mt-0.5 text-danger" />
            <div className="flex-1">
              <h2 className="text-lg font-semibold text-text">Delete My Data</h2>
              <p className="mt-1 text-sm text-text-muted">
                Permanently delete all your family data. This action cannot be undone. Your data
                will be completely removed after 30 days.
              </p>
              <Button
                variant="danger"
                size="sm"
                className="mt-3"
                onClick={() => setShowDeleteModal(true)}
              >
                Delete All Data
              </Button>
            </div>
          </div>
        </div>
      </div>

      <Modal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setPassword("");
          setDeleteError(null);
        }}
        title="Confirm Data Deletion"
      >
        <p className="mb-4 text-sm text-text-muted">
          Enter your password to confirm. All data will be permanently deleted.
        </p>
        {deleteError && (
          <div className="mb-3 rounded-lg bg-danger/10 p-3 text-sm text-danger">{deleteError}</div>
        )}
        <input
          type="password"
          placeholder="Enter password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mb-4 w-full rounded-lg border border-gray-300 px-3 py-2.5 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
          autoFocus
        />
        <div className="flex gap-2">
          <Button
            variant="danger"
            className="flex-1"
            onClick={handleDelete}
            disabled={password.length < 8 || isDeleting}
          >
            {isDeleting ? <Spinner size="sm" /> : "Delete Everything"}
          </Button>
          <Button variant="ghost" className="flex-1" onClick={() => setShowDeleteModal(false)}>
            Cancel
          </Button>
        </div>
      </Modal>
    </div>
  );
}
