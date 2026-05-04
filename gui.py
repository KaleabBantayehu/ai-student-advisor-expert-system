import re
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

from src.inference_engine import InferenceEngine


class StudentAdvisorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("AI Student Academic Advisor")
        root.resizable(True, True)
        root.geometry("850x750")  # Set initial size

        self.style = ttk.Style(root)
        self.style.theme_use("clam")
        
        # Configure bold font for section titles
        self.style.configure("Bold.TLabelframe.Label", font=("TkDefaultFont", 10, "bold"))
        
        # Configure larger font for result labels
        self.style.configure("Result.TLabel", font=("TkDefaultFont", 9))
        self.style.configure("Header.TLabel", font=("TkDefaultFont", 9, "bold"))

        # Configure grid weights for proper expansion
        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)

        self._build_input_frame()
        self._build_button_frame()
        self._build_output_frame()

    def _build_input_frame(self) -> None:
        input_frame = ttk.LabelFrame(self.root, text="Student Inputs", style="Bold.TLabelframe")
        input_frame.grid(row=0, column=0, padx=20, pady=(20, 12), sticky="ew")

        self.gpa_var = tk.StringVar()
        self.attendance_var = tk.StringVar()
        self.study_hours_var = tk.StringVar()
        self.assignment_completed_var = tk.BooleanVar(value=True)

        labels = ["GPA", "Attendance (%)", "Study Hours", "Assignments Complete"]
        fields = [self.gpa_var, self.attendance_var, self.study_hours_var]

        for index, label_text in enumerate(labels[:3]):
            label = ttk.Label(input_frame, text=label_text + ":", style="Header.TLabel")
            label.grid(row=index, column=0, padx=(16, 8), pady=8, sticky="e")

            entry = ttk.Entry(input_frame, textvariable=fields[index], width=28)
            entry.grid(row=index, column=1, padx=(0, 16), pady=8, sticky="w")

        assignment_check = ttk.Checkbutton(
            input_frame,
            text="Yes",
            variable=self.assignment_completed_var,
            onvalue=True,
            offvalue=False
        )
        assignment_label = ttk.Label(input_frame, text=labels[3] + ":", style="Header.TLabel")
        assignment_label.grid(row=3, column=0, padx=(16, 8), pady=8, sticky="e")
        assignment_check.grid(row=3, column=1, padx=(0, 16), pady=8, sticky="w")

    def _build_button_frame(self) -> None:
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="ew")

        evaluate_button = ttk.Button(button_frame, text="Evaluate Student", command=self.evaluate_student)
        evaluate_button.grid(row=0, column=0, pady=4, sticky="ew")

    def _build_output_frame(self) -> None:
        output_frame = ttk.LabelFrame(self.root, text="Evaluation Results", style="Bold.TLabelframe")
        output_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        output_frame.columnconfigure(1, weight=1)
        output_frame.rowconfigure(4, weight=1)

        self.final_status_var = tk.StringVar(value="No evaluation yet.")
        self.risk_level_var = tk.StringVar(value="No evaluation yet.")

        # Final Status - single line label
        status_label = ttk.Label(output_frame, text="Final Status:", style="Header.TLabel")
        status_label.grid(row=0, column=0, padx=(16, 8), pady=(16, 8), sticky="ne")
        status_value = ttk.Label(output_frame, textvariable=self.final_status_var, wraplength=550, justify="left", style="Result.TLabel")
        status_value.grid(row=0, column=1, padx=(0, 16), pady=(16, 8), sticky="ew")

        # Risk Level - single line label
        risk_label = ttk.Label(output_frame, text="Risk Level:", style="Header.TLabel")
        risk_label.grid(row=1, column=0, padx=(16, 8), pady=8, sticky="ne")
        risk_value = ttk.Label(output_frame, textvariable=self.risk_level_var, wraplength=550, justify="left", style="Result.TLabel")
        risk_value.grid(row=1, column=1, padx=(0, 16), pady=8, sticky="ew")

        # Severity Context - multi-line text widget
        severity_label = ttk.Label(output_frame, text="Severity Context:", style="Header.TLabel")
        severity_label.grid(row=2, column=0, padx=(16, 8), pady=8, sticky="ne")
        self.severity_text = tk.Text(output_frame, height=4, wrap="word", borderwidth=1, relief="solid", state="disabled", font=("TkDefaultFont", 9))
        self.severity_text.grid(row=2, column=1, padx=(0, 16), pady=8, sticky="ew")

        # Advice - multi-line text widget
        advice_label = ttk.Label(output_frame, text="Advice:", style="Header.TLabel")
        advice_label.grid(row=3, column=0, padx=(16, 8), pady=8, sticky="ne")
        self.advice_text = tk.Text(output_frame, height=4, wrap="word", borderwidth=1, relief="solid", state="disabled", font=("TkDefaultFont", 9))
        self.advice_text.grid(row=3, column=1, padx=(0, 16), pady=8, sticky="ew")

        # Explanation - scrollable text widget
        explanation_label = ttk.Label(output_frame, text="Explanation:", style="Header.TLabel")
        explanation_label.grid(row=4, column=0, padx=(16, 8), pady=8, sticky="ne")
        self.explanation_text = ScrolledText(
            output_frame,
            height=10,
            wrap="word",
            borderwidth=1,
            relief="solid",
            state="disabled",
            font=("TkDefaultFont", 9),
            padx=8,
            pady=8
        )
        self.explanation_text.grid(row=4, column=1, padx=(0, 16), pady=8, sticky="nsew")

    def evaluate_student(self) -> None:
        try:
            inputs = self._validate_inputs()
        except ValueError as err:
            messagebox.showerror("Validation Error", str(err))
            return

        try:
            engine = InferenceEngine()
            result = engine.evaluate(inputs)
        except Exception as err:
            messagebox.showerror("Evaluation Error", f"Unable to evaluate the student:\n{err}")
            return

        self._display_results(result, inputs)

    def _validate_inputs(self) -> dict:
        try:
            gpa = float(self.gpa_var.get().strip())
        except ValueError:
            raise ValueError("GPA must be a number between 0 and 4.")

        try:
            attendance = float(self.attendance_var.get().strip())
        except ValueError:
            raise ValueError("Attendance must be a number between 0 and 100.")

        try:
            study_hours = float(self.study_hours_var.get().strip())
        except ValueError:
            raise ValueError("Study Hours must be a non-negative number.")

        if not (0.0 <= gpa <= 4.0):
            raise ValueError("GPA must be between 0 and 4.")

        if not (0.0 <= attendance <= 100.0):
            raise ValueError("Attendance must be between 0 and 100.")

        if study_hours < 0:
            raise ValueError("Study Hours cannot be negative.")

        return {
            "gpa": gpa,
            "attendance": attendance,
            "study_hours": study_hours,
            "assignment_completion": bool(self.assignment_completed_var.get())
        }

    def _compute_risk_level(self, result, inputs: dict) -> str:
        if inputs["gpa"] < 2.0 or len(result.severity_context) > 1:
            return "High"
        if inputs["gpa"] < 3.0 or len(result.severity_context) == 1:
            return "Moderate"
        return "Low"

    @staticmethod
    def _format_section(entries: list[dict], default: str) -> str:
        if not entries:
            return default

        formatted_lines = []
        for entry in entries:
            message = entry.get("message", "").strip()
            if message:
                formatted_lines.append(f"• {message}")

        return "\n".join(formatted_lines) if formatted_lines else default

    def _display_results(self, result, inputs: dict) -> None:
        self.final_status_var.set(result.final_status.get("message", "Unknown"))
        self.risk_level_var.set(self._compute_risk_level(result, inputs))

        # Update severity context text widget
        severity_content = self._format_section(result.severity_context, "No critical issues detected.")
        self.severity_text.configure(state="normal")
        self.severity_text.delete("1.0", tk.END)
        self.severity_text.insert(tk.END, severity_content)
        self.severity_text.configure(state="disabled")

        # Update advice text widget
        advice_content = self._format_section(result.advice_list, "No recommendations at this time.")
        self.advice_text.configure(state="normal")
        self.advice_text.delete("1.0", tk.END)
        self.advice_text.insert(tk.END, advice_content)
        self.advice_text.configure(state="disabled")

        explanation = result.reasoning_narrative or "No explanation provided."
        formatted_explanation = self._format_explanation_text(explanation)
        self.explanation_text.configure(state="normal")
        self.explanation_text.delete("1.0", tk.END)
        self.explanation_text.insert(tk.END, formatted_explanation)
        self.explanation_text.configure(state="disabled")

    @staticmethod
    def _format_explanation_text(text: str) -> str:
        if not text:
            return ""

        # Clean up extra whitespace
        clean_text = re.sub(r"\s+", " ", text).strip()

        # Remove any double periods that might exist
        clean_text = re.sub(r"\.\s*\.", ".", clean_text)

        # Ensure single space after periods
        clean_text = re.sub(r"\.\s+", ". ", clean_text)

        # Clean up any trailing punctuation issues
        clean_text = clean_text.rstrip(".")

        return clean_text


def main() -> None:
    root = tk.Tk()
    StudentAdvisorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
