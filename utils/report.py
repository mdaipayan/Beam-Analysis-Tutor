import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from utils.plotting import draw_beam_schematic, plot_sfd_bmd

PROGRESS_FILE = "student_progress.csv"

def calculate_grade_letter(total_score, grade_A, grade_B, grade_C, grade_D):
    if total_score >= grade_A:
        return "A"
    elif total_score >= grade_B:
        return "B"
    elif total_score >= grade_C:
        return "C"
    elif total_score >= grade_D:
        return "D"
    else:
        return "F"

def append_progress_entry(name, roll_no, eq_score, diag_score, error_score, pres_score, total, grade):
    try:
        df = pd.read_csv(PROGRESS_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Name","RollNo","Date","Equations","Diagrams","Error","Presentation","Total","Grade"])
    entry = {
        "Name": name,
        "RollNo": roll_no,
        "Date": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "Equations": eq_score,
        "Diagrams": diag_score,
        "Error": error_score,
        "Presentation": pres_score,
        "Total": total,
        "Grade": grade
    }
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(PROGRESS_FILE, index=False)

def load_progress_for_student(roll_no):
    try:
        df = pd.read_csv(PROGRESS_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Name","RollNo","Date","Equations","Diagrams","Error","Presentation","Total","Grade"])
    if roll_no:
        return df[df["RollNo"] == roll_no].copy()
    return df

def generate_pdf_report(
    student_name, roll_no, semester, branch, course_info,
    support, length, loads, x, V_custom, M_custom,
    example_choice=None, V_example=None, M_example=None,
    max_V_error=0.0, rmse_V=0.0, max_M_error=0.0, rmse_M=0.0,
    eq_score=0, diag_score=0, error_score=0, presentation_score=0,
    w_eq=30, w_diag=30, w_error=20, w_pres=20,
    grade_A=36, grade_B=32, grade_C=24, grade_D=16,
    letter_grade="F", instructor_notes="",
    student_history=None, cumulative_avg=0.0, cumulative_grade="F"
):
    buf = io.BytesIO()
    with PdfPages(buf) as pdf:
        # Title page
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis("off")
        ax.text(0.5, 0.85, "Beam Analysis Report", fontsize=24, ha="center")
        ax.text(0.5, 0.78, f"Name: {student_name}", fontsize=12, ha="center")
        ax.text(0.5, 0.75, f"Roll No.: {roll_no}", fontsize=12, ha="center")
        ax.text(0.5, 0.72, f"Semester: {semester}", fontsize=12, ha="center")
        ax.text(0.5, 0.69, f"Branch: {branch}", fontsize=12, ha="center")
        ax.text(0.5, 0.66, f"Course Info: {course_info}", fontsize=12, ha="center")
        ax.text(0.5, 0.62, f"Support: {support}    Length: {length} m", fontsize=12, ha="center")
        pdf.savefig(fig)
        plt.close(fig)

        # Schematic page
        fig = draw_beam_schematic(length, loads, support)
        pdf.savefig(fig)
        plt.close(fig)

        # Equations / explanation page (simple auto text)
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis("off")
        ax.text(0.05, 0.95, "Step-by-Step Calculations", fontsize=16, va="top")
        lines = [
            "1. Identify support condition and loads.",
            "2. For simply supported beams, compute reactions using equilibrium:",
            "   Sum Fy = 0 and Sum M about a support = 0.",
            "3. Convert UDLs to equivalent point loads at centroids when needed.",
            "4. Construct piecewise shear force function by summing reactions and subtracting loads to the left of x.",
            "5. Construct bending moment by integrating shear or summing moments of loads to the left of x.",
            "",
            "Note: This report includes computed SFD and BMD plots and numerical error analysis if a worked example was selected."
        ]
        y = 0.9
        for ln in lines:
            ax.text(0.05, y, ln, fontsize=11, va="top")
            y -= 0.04
        pdf.savefig(fig)
        plt.close(fig)

        # Diagrams page
        fig = plt.figure(figsize=(8.5, 11))
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        ax1.plot(x, V_custom, linestyle="--", label="Custom (SFD)")
        if V_example is not None:
            ax1.plot(x, V_example, linestyle="-", label="Example (SFD)")
        ax1.axhline(0, color="black", linewidth=0.6)
        ax1.set_ylabel("Shear (kN)")
        ax1.grid(True)
        ax1.legend()

        ax2.plot(x, M_custom, linestyle="--", color="tab:red", label="Custom (BMD)")
        if M_example is not None:
            ax2.plot(x, M_example, linestyle="-", color="tab:orange", label="Example (BMD)")
        ax2.axhline(0, color="black", linewidth=0.6)
        ax2.set_ylabel("Moment (kNm)")
        ax2.set_xlabel("Position (m)")
        ax2.grid(True)
        ax2.legend()
        pdf.savefig(fig)
        plt.close(fig)

        # Error analysis page
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis("off")
        ax.text(0.05, 0.9, "Numerical Error Analysis", fontsize=16, va="top")
        ax.text(0.05, 0.82, f"Max Shear Error = {max_V_error:.3f} kN", fontsize=12)
        ax.text(0.05, 0.78, f"RMSE Shear = {rmse_V:.3f} kN", fontsize=12)
        ax.text(0.05, 0.74, f"Max Moment Error = {max_M_error:.3f} kNm", fontsize=12)
        ax.text(0.05, 0.70, f"RMSE Moment = {rmse_M:.3f} kNm", fontsize=12)
        pdf.savefig(fig)
        plt.close(fig)

        # Instructor notes page
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis("off")
        ax.text(0.5, 0.9, "Instructor Notes", fontsize=16, ha="center")
        if instructor_notes and instructor_notes.strip():
            y = 0.82
            for line in instructor_notes.split("\n"):
                ax.text(0.05, y, line, fontsize=11, va="top")
                y -= 0.04
        else:
            ax.text(0.5, 0.7, "No notes provided.", fontsize=12, ha="center")
        pdf.savefig(fig)
        plt.close(fig)

        # Grading rubric page
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis("off")
        ax.text(0.5, 0.92, "Grading Rubric", fontsize=16, ha="center")
        rubric_data = [
            ["Criteria", "Score (out of 10)", "Weight (%)"],
            ["Equations", f"{eq_score}/10", f"{w_eq}%"],
            ["Diagrams", f"{diag_score}/10", f"{w_diag}%"],
            ["Error Analysis", f"{error_score}/10", f"{w_error}%"],
            ["Presentation", f"{presentation_score}/10", f"{w_pres}%"],
            ["Weighted Total", f"{( (eq_score/10)*w_eq + (diag_score/10)*w_diag + (error_score/10)*w_error + (presentation_score/10)*w_pres )/100*40:.2f}/40", ""],
            ["Grade", letter_grade, ""],
            ["Thresholds", f"A≥{grade_A}, B≥{grade_B}, C≥{grade_C}, D≥{grade_D}", ""]
        ]
        table = ax.table(cellText=rubric_data, loc="center", cellLoc="center", colWidths=[0.45, 0.25, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2)
        pdf.savefig(fig)
        plt.close(fig)

        # Rubric contributions bar chart
        fig, ax = plt.subplots(figsize=(8.5, 6))
        categories = ["Equations", "Diagrams", "Error Analysis", "Presentation"]
        scores = np.array([eq_score, diag_score, error_score, presentation_score])
        weights = np.array([w_eq, w_diag, w_error, w_pres]) / 100.0
        contributions = (scores/10.0) * weights * 40.0
        bars = ax.bar(categories, contributions, color=["#4CAF50", "#2196F3", "#FFC107", "#E91E63"])
        ax.set_ylabel("Contribution to Total (out of 40)")
        ax.set_title("Rubric Contributions by Category")
        for i, v in enumerate(contributions):
            ax.text(i, v + 0.5, f"{v:.2f}", ha="center")
        pdf.savefig(fig)
        plt.close(fig)

        # Trendlines page (if history provided)
        if student_history is not None and not student_history.empty:
            df = student_history.sort_values("Date")
            fig, axs = plt.subplots(2, 2, figsize=(10, 8))
            cats = ["Equations", "Diagrams", "Error", "Presentation"]
            for i, cat in enumerate(cats):
                r, c = divmod(i, 2)
                axs[r, c].plot(df["Date"], df[cat], marker="o")
                axs[r, c].set_title(f"{cat} Progress")
                axs[r, c].set_ylim(0, 10)
                axs[r, c].tick_params(axis='x', rotation=45)
            fig.suptitle(f"Progress Trendlines for {student_name} ({roll_no})")
            pdf.savefig(fig)
            plt.close(fig)

            # Cumulative performance page
            fig, ax = plt.subplots(figsize=(8.5, 11))
            ax.axis("off")
            ax.text(0.5, 0.9, "Cumulative Performance Index", fontsize=16, ha="center")
            ax.text(0.5, 0.82, f"Average Weighted Score: {cumulative_avg:.2f}/40", fontsize=12, ha="center")
            ax.text(0.5, 0.78, f"Cumulative Grade: {cumulative_grade}", fontsize=12, ha="center")
            pdf.savefig(fig)
            plt.close(fig)

    buf.seek(0)
    return buf.getvalue()
