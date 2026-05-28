import streamlit as st
import numpy as np
import pandas as pd
from utils.calculations import shear_force, bending_moment
from utils.plotting import plot_sfd_bmd, draw_beam_schematic
from utils.report import generate_pdf_report, append_progress_entry, load_progress_for_student, calculate_grade_letter

st.set_page_config(layout="wide", page_title="Beam Analysis Tutor")

st.title("📊 Beam Analysis Tutor")

# Sidebar: Student Info
st.sidebar.header("Student Information")
student_name = st.sidebar.text_input("Name", value="")
roll_no = st.sidebar.text_input("Roll No.", value="")
semester = st.sidebar.text_input("Semester", value="")
branch = st.sidebar.text_input("Branch", value="")
course_info = st.sidebar.text_input("Course Info", value="")

# Beam Setup
st.header("Beam Setup")
length = st.number_input("Beam length (m)", min_value=0.5, value=6.0, step=0.1)
support = st.selectbox("Support condition", ["simply_supported", "cantilever"])

# Loads input
st.subheader("Loads")
num_loads = st.number_input("Number of loads", min_value=1, max_value=6, value=1, step=1)
loads = []
for i in range(int(num_loads)):
    st.markdown(f"**Load {i+1}**")
    ltype = st.selectbox(f"Type {i+1}", ["point", "udl"], key=f"type_{i}")
    if ltype == "point":
        P = st.number_input(f"Point load {i+1} (kN)", value=10.0, key=f"P_{i}")
        a = st.number_input(f"Position {i+1} (m from left)", min_value=0.0, max_value=length, value=length/2, key=f"a_{i}")
        loads.append({"type": "point", "P": float(P), "a": float(a)})
    else:
        w = st.number_input(f"UDL intensity {i+1} (kN/m)", value=5.0, key=f"w_{i}")
        start = st.number_input(f"UDL start {i+1} (m)", min_value=0.0, max_value=length, value=0.0, key=f"s_{i}")
        end = st.number_input(f"UDL end {i+1} (m)", min_value=0.0, max_value=length, value=length, key=f"e_{i}")
        loads.append({"type": "udl", "w": float(w), "start": float(start), "end": float(end)})

# Compute SFD/BMD
x = np.linspace(0, length, 400)
V_custom = np.array([shear_force(xi, length, loads, support) for xi in x])
M_custom = np.array([bending_moment(xi, length, loads, support) for xi in x])

# Plot diagrams
st.subheader("Diagrams")
plot_sfd_bmd(x, V_custom, M_custom)

# Comparison with worked example
st.subheader("Compare with Worked Example")
example_choice = st.selectbox("Worked Example", [
    "None",
    "Simply Supported Beam with Point Load at Midspan",
    "Simply Supported Beam with UDL across Full Span",
    "Cantilever Beam with Point Load at Free End",
    "Cantilever Beam with UDL across Full Span"
])

V_example = None
M_example = None
if example_choice != "None":
    L = length
    if example_choice == "Simply Supported Beam with Point Load at Midspan":
        P = 10.0
        a = L/2
        R1 = P * (L - a) / L
        V_example = np.array([R1 if xi < a else R1 - P for xi in x])
        M_example = np.array([R1*xi if xi < a else R1*xi - P*(xi-a) for xi in x])
    elif example_choice == "Simply Supported Beam with UDL across Full Span":
        w = 5.0
        R1 = R2 = w*L/2
        V_example = np.array([R1 - w*xi for xi in x])
        M_example = np.array([R1*xi - (w*xi**2)/2 for xi in x])
    elif example_choice == "Cantilever Beam with Point Load at Free End":
        P = 12.0
        V_example = np.array([-P for _ in x])
        M_example = np.array([P*(L - xi) for xi in x])
    elif example_choice == "Cantilever Beam with UDL across Full Span":
        w = 6.0
        V_example = np.array([-w*xi for xi in x])
        M_example = np.array([-(w*xi**2)/2 for xi in x])

    # Overlay plot
    st.markdown("**Overlay: Custom (dashed) vs Example (solid)**")
    plot_sfd_bmd(x, V_custom, M_custom, V_compare=V_example, M_compare=M_example)

    # Error analysis
    V_diff = V_custom - V_example
    M_diff = M_custom - M_example
    max_V_error = float(np.max(np.abs(V_diff)))
    max_M_error = float(np.max(np.abs(M_diff)))
    rmse_V = float(np.sqrt(np.mean(V_diff**2)))
    rmse_M = float(np.sqrt(np.mean(M_diff**2)))

    st.subheader("Numerical Error Analysis")
    st.markdown(f"- **Max Shear Error:** {max_V_error:.3f} kN")
    st.markdown(f"- **RMSE Shear:** {rmse_V:.3f} kN")
    st.markdown(f"- **Max Moment Error:** {max_M_error:.3f} kNm")
    st.markdown(f"- **RMSE Moment:** {rmse_M:.3f} kNm")
else:
    max_V_error = rmse_V = max_M_error = rmse_M = 0.0

# Schematic
st.subheader("Beam Schematic")
fig_schem = draw_beam_schematic(length, loads, support)
st.pyplot(fig_schem)

# Instructor notes and grading
st.header("Instructor Feedback & Grading")
instructor_notes = st.text_area("Instructor Notes (feedback)")

eq_score = st.number_input("Equations (0-10)", min_value=0, max_value=10, value=0)
diag_score = st.number_input("Diagrams (0-10)", min_value=0, max_value=10, value=0)
error_score = st.number_input("Error Analysis (0-10)", min_value=0, max_value=10, value=0)
presentation_score = st.number_input("Presentation (0-10)", min_value=0, max_value=10, value=0)

# Weights and thresholds
st.subheader("Weighted Rubric & Grade Thresholds")
w_eq = st.number_input("Weight Equations (%)", min_value=0, max_value=100, value=30)
w_diag = st.number_input("Weight Diagrams (%)", min_value=0, max_value=100, value=30)
w_error = st.number_input("Weight Error Analysis (%)", min_value=0, max_value=100, value=20)
w_pres = st.number_input("Weight Presentation (%)", min_value=0, max_value=100, value=20)

grade_A = st.number_input("Minimum score for A (out of 40)", min_value=0, max_value=40, value=36)
grade_B = st.number_input("Minimum score for B (out of 40)", min_value=0, max_value=40, value=32)
grade_C = st.number_input("Minimum score for C (out of 40)", min_value=0, max_value=40, value=24)
grade_D = st.number_input("Minimum score for D (out of 40)", min_value=0, max_value=40, value=16)

# Weighted total calculation
weights_sum = w_eq + w_diag + w_error + w_pres
if weights_sum == 0:
    st.warning("Total weight is 0. Please set weights so they sum to > 0.")
    weights_sum = 1

weighted_total = (
    (eq_score/10)*w_eq +
    (diag_score/10)*w_diag +
    (error_score/10)*w_error +
    (presentation_score/10)*w_pres
) / 100 * 40

letter_grade = calculate_grade_letter(weighted_total, grade_A, grade_B, grade_C, grade_D)

st.markdown(f"**Weighted Total:** {weighted_total:.2f} / 40")
st.markdown(f"**Assigned Grade:** {letter_grade}")

# Progress tracking and trendlines
if st.button("Save Progress & Generate PDF Report"):
    # Append progress
    append_progress_entry(
        student_name, roll_no, eq_score, diag_score, error_score, presentation_score,
        weighted_total, letter_grade
    )

    # Load student history for trendlines and cumulative
    student_df = load_progress_for_student(roll_no)
    cumulative_avg = float(student_df["Total"].mean()) if not student_df.empty else weighted_total
    cumulative_grade = calculate_grade_letter(cumulative_avg, grade_A, grade_B, grade_C, grade_D)

    # Generate PDF
    pdf_bytes = generate_pdf_report(
        student_name=student_name,
        roll_no=roll_no,
        semester=semester,
        branch=branch,
        course_info=course_info,
        support=support,
        length=length,
        loads=loads,
        x=x,
        V_custom=V_custom,
        M_custom=M_custom,
        example_choice=example_choice,
        V_example=V_example,
        M_example=M_example,
        max_V_error=max_V_error,
        rmse_V=rmse_V,
        max_M_error=max_M_error,
        rmse_M=rmse_M,
        eq_score=eq_score,
        diag_score=diag_score,
        error_score=error_score,
        presentation_score=presentation_score,
        w_eq=w_eq,
        w_diag=w_diag,
        w_error=w_error,
        w_pres=w_pres,
        grade_A=grade_A,
        grade_B=grade_B,
        grade_C=grade_C,
        grade_D=grade_D,
        letter_grade=letter_grade,
        instructor_notes=instructor_notes,
        student_history=student_df,
        cumulative_avg=cumulative_avg,
        cumulative_grade=cumulative_grade
    )

    st.success("Report generated and progress saved.")
    st.download_button("Download PDF Report", data=pdf_bytes, file_name="beam_analysis_report.pdf", mime="application/pdf")
