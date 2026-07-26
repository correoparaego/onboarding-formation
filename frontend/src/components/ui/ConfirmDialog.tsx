import Modal from "./Modal";
import Button from "./Button";

interface ConfirmDialogProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  danger?: boolean;
  "data-testid"?: string;
}

export default function ConfirmDialog({
  isOpen,
  onConfirm,
  onCancel,
  title,
  message,
  confirmLabel = "Confirmar",
  danger = false,
  "data-testid": testId,
}: ConfirmDialogProps) {
  return (
    <Modal
      data-testid={testId || "confirm-dialog"}
      isOpen={isOpen}
      onClose={onCancel}
      title={title}
      footer={
        <>
          <Button data-testid="cancel-btn" variant="secondary" onClick={onCancel}>
            Cancelar
          </Button>
          <Button data-testid="confirm-btn" variant={danger ? "danger" : "primary"} onClick={onConfirm}>
            {confirmLabel}
          </Button>
        </>
      }
    >
      <p style={{ color: "var(--color-text-secondary)" }}>{message}</p>
    </Modal>
  );
}
