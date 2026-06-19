"""Tkinter desktop interface for the Word accessibility fixer."""

from __future__ import annotations

from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .core import FixResult, audit_and_fix_docx


class AccessibilityFixerApp(tk.Tk):
    """Small Windows-friendly desktop app around ``audit_and_fix_docx``."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Word Accessibility Fixer")
        self.geometry("760x520")
        self.minsize(680, 460)

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.report_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Seleziona un documento .docx da correggere.")
        self._result_queue: queue.Queue[FixResult | Exception] = queue.Queue()

        self._build_ui()

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=18)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(5, weight=1)

        ttk.Label(root, text="Documento Word (.docx)").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(root, textvariable=self.input_var).grid(row=0, column=1, sticky="ew", padx=8, pady=(0, 8))
        ttk.Button(root, text="Sfoglia…", command=self._choose_input).grid(row=0, column=2, pady=(0, 8))

        ttk.Label(root, text="Nuovo documento corretto").grid(row=1, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(root, textvariable=self.output_var).grid(row=1, column=1, sticky="ew", padx=8, pady=(0, 8))
        ttk.Button(root, text="Salva come…", command=self._choose_output).grid(row=1, column=2, pady=(0, 8))

        ttk.Label(root, text="Report JSON (opzionale)").grid(row=2, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(root, textvariable=self.report_var).grid(row=2, column=1, sticky="ew", padx=8, pady=(0, 8))
        ttk.Button(root, text="Scegli…", command=self._choose_report).grid(row=2, column=2, pady=(0, 8))

        self.run_button = ttk.Button(root, text="Correggi accessibilità", command=self._start_fix)
        self.run_button.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(8, 12))

        ttk.Label(root, textvariable=self.status_var).grid(row=4, column=0, columnspan=3, sticky="w")

        self.output_text = tk.Text(root, wrap="word", height=14)
        self.output_text.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(12, 0))
        self.output_text.configure(state="disabled")

        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.output_text.yview)
        scrollbar.grid(row=5, column=3, sticky="ns", pady=(12, 0))
        self.output_text.configure(yscrollcommand=scrollbar.set)

    def _choose_input(self) -> None:
        selected = filedialog.askopenfilename(
            title="Scegli documento Word",
            filetypes=[("Documenti Word", "*.docx"), ("Tutti i file", "*.*")],
        )
        if not selected:
            return
        input_path = Path(selected)
        self.input_var.set(str(input_path))
        if not self.output_var.get():
            self.output_var.set(str(input_path.with_name(f"{input_path.stem}-accessibile.docx")))
        if not self.report_var.get():
            self.report_var.set(str(input_path.with_name(f"{input_path.stem}-accessibilita.json")))

    def _choose_output(self) -> None:
        selected = filedialog.asksaveasfilename(
            title="Salva documento corretto",
            defaultextension=".docx",
            filetypes=[("Documenti Word", "*.docx")],
        )
        if selected:
            self.output_var.set(selected)

    def _choose_report(self) -> None:
        selected = filedialog.asksaveasfilename(
            title="Salva report JSON",
            defaultextension=".json",
            filetypes=[("Report JSON", "*.json")],
        )
        if selected:
            self.report_var.set(selected)

    def _start_fix(self) -> None:
        input_path = Path(self.input_var.get().strip())
        output_path = Path(self.output_var.get().strip())
        report_text = self.report_var.get().strip()
        report_path = Path(report_text) if report_text else None

        if not input_path:
            messagebox.showwarning("Documento mancante", "Seleziona un file .docx da correggere.")
            return
        if not output_path:
            messagebox.showwarning("Output mancante", "Scegli dove salvare il nuovo documento corretto.")
            return

        self.run_button.configure(state="disabled")
        self.status_var.set("Correzione in corso…")
        self._write_output("Avvio analisi e correzione del documento.\n")
        thread = threading.Thread(target=self._run_fix, args=(input_path, output_path, report_path), daemon=True)
        thread.start()
        self.after(150, self._poll_result)

    def _run_fix(self, input_path: Path, output_path: Path, report_path: Path | None) -> None:
        try:
            self._result_queue.put(audit_and_fix_docx(input_path, output_path, report_path))
        except Exception as exc:  # noqa: BLE001 - surfaced to desktop user.
            self._result_queue.put(exc)

    def _poll_result(self) -> None:
        try:
            result = self._result_queue.get_nowait()
        except queue.Empty:
            self.after(150, self._poll_result)
            return

        self.run_button.configure(state="normal")
        if isinstance(result, Exception):
            self.status_var.set("Errore durante la correzione.")
            self._write_output(f"Errore: {result}\n")
            messagebox.showerror("Errore", str(result))
            return

        self.status_var.set("Documento corretto creato con successo.")
        self._write_output(f"Documento corretto: {result.output_path}\n")
        if result.report_path:
            self._write_output(f"Report JSON: {result.report_path}\n")
        self._write_output(f"Problemi rilevati: {len(result.issues)}\n")
        self._write_output(f"Correzioni applicate: {result.fixed_count}\n\n")
        for issue in result.issues:
            self._write_output(f"- [{issue.severity}] {issue.code}: {issue.message} ({issue.fix})\n")
        messagebox.showinfo("Completato", "Nuovo documento accessibile creato con successo.")

    def _write_output(self, text: str) -> None:
        self.output_text.configure(state="normal")
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.configure(state="disabled")


def main() -> int:
    app = AccessibilityFixerApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
