import numpy as np
import streamlit as st

from utils.calculations import bending_moment, sanitize_loads, shear_force
from utils.plotting import draw_beam_schematic, plot_sfd_bmd
from utils.report import (
    append_progress_entry,
    calculate_grade_letter,
    generate_pdf_report,
    load_progress_for_student,
)

st.set_page_config(page_title="Beam Analysis Tutor Pro", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.2rem;}
      .stMetric {border: 1px solid rgba(49, 51, 63, 0.2); border-radius: 12px; padding: 0.4rem 1rem;}
      h1, h2, h3 {letter-spacing: .2px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Beam Analysis Tutor Pro")
st.caption("Professional beam analysis workflow with error benchmarking, grading, and PDF reporting.")

with st.sidebar:
    st.header("Student Profile")
    student_name = st.text_input("Name")
    roll_no = st.text_input("Roll No.")
    semester = st.text_input("Semester")
    branch = st.text_input("Branch")
    course_info = st.text_input("Course Info")

left, right = st.columns([1.2, 1.0])

with left:
    st.subheader("Beam Definition")
    length = st.number_input("Beam length (m)", min_value=0.5, value=6.0, step=0.1)
    support = st.selectbox("Support condition", ["simply_supported", "cantilever"])

    st.subheader("Load Cases")
    num_loads = int(st.number_input("Number of loads", min_value=1, max_value=8, value=1, step=1))
    raw_loads = []
    for i in range(num_loads):
        with st.expander(f"Load {i+1}", expanded=(i == 0)):
            ltype = st.selectbox("Type", ["point", "udl"], key=f"type_{i}")
            if ltype == "point":
                P = st.number_input("Point load P (kN)", min_value=0.0, value=10.0, key=f"P_{i}")
                a = st.number_input("Position a (m from left)", min_value=0.0, max_value=float(length), value=float(length / 2), key=f"a_{i}")
                raw_loads.append({"type": "point", "P": P, "a": a})
            else:
                w = st.number_input("UDL intensity w (kN/m)", min_value=0.0, value=5.0, key=f"w_{i}")
                start = st.number_input("UDL start (m)", min_value=0.0, max_value=float(length), value=0.0, key=f"s_{i}")
                end = st.number_input("UDL end (m)", min_value=0.0, max_value=float(length), value=float(length), key=f"e_{i}")
                raw_loads.append({"type": "udl", "w": w, "start": start, "end": end})

loads = sanitize_loads(length, raw_loads)
x = np.linspace(0, length, 400)
V_custom = np.array([shear_force(xi, length, loads, support) for xi in x])
M_custom = np.array([bending_moment(xi, length, loads, support) for xi in x])

with right:
    st.subheader("Quick Results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Max |Shear| (kN)", f"{np.max(np.abs(V_custom)):.2f}")
    c2.metric("Max |Moment| (kNm)", f"{np.max(np.abs(M_custom)):.2f}")
    c3.metric("Loads", f"{len(loads)}")

    st.subheader("Beam Schematic")
    st.pyplot(draw_beam_schematic(length, loads, support), use_container_width=True)

st.subheader("SFD and BMD")
plot_sfd_bmd(x, V_custom, M_custom)

st.subheader("Worked Example Benchmark")
example_choice = st.selectbox(
    "Compare against",
    [
        "None",
        "Simply Supported Beam with Point Load at Midspan",
        "Simply Supported Beam with UDL across Full Span",
        "Cantilever Beam with Point Load at Free End",
        "Cantilever Beam with UDL across Full Span",
    ],
)

V_example, M_example = None, None
if example_choice != "None":
    L = length
    if example_choice == "Simply Supported Beam with Point Load at Midspan":
        P, a = 10.0, L / 2
        R1 = P * (L - a) / L
        V_example = np.array([R1 if xi < a else R1 - P for xi in x])
        M_example = np.array([R1 * xi if xi < a else R1 * xi - P * (xi - a) for xi in x])
    elif example_choice == "Simply Supported Beam with UDL across Full Span":
        w = 5.0
        R1 = w * L / 2
        V_example = np.array([R1 - w * xi for xi in x])
        M_example = np.array([R1 * xi - (w * xi**2) / 2 for xi in x])
    elif example_choice == "Cantilever Beam with Point Load at Free End":
        P = 12.0
        V_example = np.full_like(x, -P)
        M_example = np.array([-P * (L - xi) for xi in x])
    elif example_choice == "Cantilever Beam with UDL across Full Span":
        w = 6.0
        V_example = np.array([-w * (L - xi) for xi in x])
        M_example = np.array([-(w * (L - xi) ** 2) / 2 for xi in x])

    st.markdown("**Overlay: Custom (dashed) vs Example (solid)**")
    plot_sfd_bmd(x, V_custom, M_custom, V_compare=V_example, M_compare=M_example)

    V_diff = V_custom - V_example
    M_diff = M_custom - M_example
    max_V_error = float(np.max(np.abs(V_diff)))
    max_M_error = float(np.max(np.abs(M_diff)))
    rmse_V = float(np.sqrt(np.mean(V_diff**2)))
    rmse_M = float(np.sqrt(np.mean(M_diff**2)))
else:
    max_V_error = rmse_V = max_M_error = rmse_M = 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Max Shear Error", f"{max_V_error:.3f} kN")
m2.metric("RMSE Shear", f"{rmse_V:.3f} kN")
m3.metric("Max Moment Error", f"{max_M_error:.3f} kNm")
m4.metric("RMSE Moment", f"{rmse_M:.3f} kNm")

st.header("Instructor Feedback & Grading")
instructor_notes = st.text_area("Instructor notes")

c1, c2, c3, c4 = st.columns(4)
eq_score = c1.number_input("Equations", min_value=0, max_value=10, value=0)
diag_score = c2.number_input("Diagrams", min_value=0, max_value=10, value=0)
error_score = c3.number_input("Error Analysis", min_value=0, max_value=10, value=0)
presentation_score = c4.number_input("Presentation", min_value=0, max_value=10, value=0)

st.subheader("Rubric Weights & Grade Thresholds")
w1, w2, w3, w4 = st.columns(4)
w_eq = w1.number_input("Equations %", min_value=0, max_value=100, value=30)
w_diag = w2.number_input("Diagrams %", min_value=0, max_value=100, value=30)
w_error = w3.number_input("Error %", min_value=0, max_value=100, value=20)
w_pres = w4.number_input("Presentation %", min_value=0, max_value=100, value=20)

if (w_eq + w_diag + w_error + w_pres) != 100:
    st.warning("For consistent grading, set total weight to exactly 100%.")

g1, g2, g3, g4 = st.columns(4)
grade_A = g1.number_input("A threshold", min_value=0, max_value=40, value=36)
grade_B = g2.number_input("B threshold", min_value=0, max_value=40, value=32)
grade_C = g3.number_input("C threshold", min_value=0, max_value=40, value=24)
grade_D = g4.number_input("D threshold", min_value=0, max_value=40, value=16)

weighted_total = ((eq_score / 10) * w_eq + (diag_score / 10) * w_diag + (error_score / 10) * w_error + (presentation_score / 10) * w_pres) / 100 * 40
letter_grade = calculate_grade_letter(weighted_total, grade_A, grade_B, grade_C, grade_D)
st.success(f"Weighted Total: {weighted_total:.2f}/40  •  Grade: {letter_grade}")

if st.button("Save Progress & Generate PDF Report", type="primary"):
    append_progress_entry(student_name, roll_no, eq_score, diag_score, error_score, presentation_score, weighted_total, letter_grade)
    student_df = load_progress_for_student(roll_no)
    cumulative_avg = float(student_df["Total"].mean()) if not student_df.empty else weighted_total
    cumulative_grade = calculate_grade_letter(cumulative_avg, grade_A, grade_B, grade_C, grade_D)

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
        cumulative_grade=cumulative_grade,
    )

    st.download_button("Download PDF Report", data=pdf_bytes, file_name="beam_analysis_report.pdf", mime="application/pdf")
    st.success("Progress saved and report generated.")
