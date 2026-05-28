import numpy as np
import streamlit as st

from utils.calculations import bending_moment, sanitize_loads, shear_force
from utils.plotting import draw_beam_schematic, plot_sfd_bmd
from utils.report import append_progress_entry, calculate_grade_letter, generate_pdf_report, load_progress_for_student

st.set_page_config(page_title="Beam Analysis Tutor Pro", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
      .block-container {padding-top: 1rem; max-width: 1300px;}
      .hero {
        padding: 1rem 1.2rem; border-radius: 14px;
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc; margin-bottom: 0.9rem;
      }
      .soft-card {
        border: 1px solid rgba(148, 163, 184, 0.3);
        border-radius: 12px; padding: .8rem 1rem; background: #ffffff;
      }
      .muted {color: #475569; font-size: .93rem;}
      .stMetric {border: 1px solid rgba(148, 163, 184, 0.35); border-radius: 10px; padding: 0.45rem 0.6rem;}
      h2,h3 {letter-spacing: .2px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="hero"><h2 style="margin:0;">📐 Beam Analysis Tutor Pro</h2><div style="opacity:.9;">Elegant, classroom-ready beam analysis with benchmarking, grading, and PDF reporting.</div></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Student Profile")
    student_name = st.text_input("Name")
    roll_no = st.text_input("Roll No.")
    semester = st.text_input("Semester")
    branch = st.text_input("Branch")
    course_info = st.text_input("Course Info")

left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.subheader("1) Beam Model")
    r1, r2 = st.columns(2)
    length = r1.number_input("Beam length (m)", min_value=0.5, value=6.0, step=0.1)
    support = r2.selectbox("Support condition", ["simply_supported", "cantilever"])

    st.subheader("2) Load Definition")
    num_loads = int(st.number_input("Number of loads", min_value=1, max_value=8, value=2, step=1))
    raw_loads = []
    for i in range(num_loads):
        with st.container(border=True):
            st.markdown(f"**Load {i + 1}**")
            a, b = st.columns([0.42, 0.58])
            ltype = a.selectbox("Type", ["point", "udl"], key=f"type_{i}")
            if ltype == "point":
                P = b.number_input("Point load, P (kN)", min_value=0.0, value=10.0, key=f"P_{i}")
                x_pos = b.number_input("Location, x (m)", min_value=0.0, max_value=float(length), value=float(length / 2), key=f"a_{i}")
                raw_loads.append({"type": "point", "P": P, "a": x_pos})
            else:
                w = b.number_input("UDL intensity, w (kN/m)", min_value=0.0, value=5.0, key=f"w_{i}")
                s_col, e_col = b.columns(2)
                start = s_col.number_input("Start (m)", min_value=0.0, max_value=float(length), value=0.0, key=f"s_{i}")
                end = e_col.number_input("End (m)", min_value=0.0, max_value=float(length), value=float(length), key=f"e_{i}")
                raw_loads.append({"type": "udl", "w": w, "start": start, "end": end})

loads = sanitize_loads(length, raw_loads)
x = np.linspace(0, length, 500)
V_custom = np.array([shear_force(xi, length, loads, support) for xi in x])
M_custom = np.array([bending_moment(xi, length, loads, support) for xi in x])

with right:
    st.subheader("Live Summary")
    m1, m2 = st.columns(2)
    m1.metric("Peak |V|", f"{np.max(np.abs(V_custom)):.2f} kN")
    m2.metric("Peak |M|", f"{np.max(np.abs(M_custom)):.2f} kNm")
    m3, m4 = st.columns(2)
    m3.metric("Load entries", len(loads))
    m4.metric("Beam support", support.replace("_", " ").title())

    st.markdown('<div class="soft-card"><div class="muted">Schematic preview updates instantly as you edit loads and support type.</div></div>', unsafe_allow_html=True)
    st.pyplot(draw_beam_schematic(length, loads, support), use_container_width=True)

analysis_tab, benchmark_tab, grading_tab = st.tabs(["Analysis", "Benchmark", "Instructor Grading"])

with analysis_tab:
    st.subheader("Shear Force Diagram & Bending Moment Diagram")
    plot_sfd_bmd(x, V_custom, M_custom)

with benchmark_tab:
    st.subheader("Worked Example Comparison")
    example_choice = st.selectbox(
        "Reference case",
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

        plot_sfd_bmd(x, V_custom, M_custom, V_compare=V_example, M_compare=M_example)

        V_diff = V_custom - V_example
        M_diff = M_custom - M_example
        max_V_error = float(np.max(np.abs(V_diff)))
        rmse_V = float(np.sqrt(np.mean(V_diff**2)))
        max_M_error = float(np.max(np.abs(M_diff)))
        rmse_M = float(np.sqrt(np.mean(M_diff**2)))
    else:
        max_V_error = rmse_V = max_M_error = rmse_M = 0.0

    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Max Shear Error", f"{max_V_error:.3f} kN")
    e2.metric("RMSE Shear", f"{rmse_V:.3f} kN")
    e3.metric("Max Moment Error", f"{max_M_error:.3f} kNm")
    e4.metric("RMSE Moment", f"{rmse_M:.3f} kNm")

with grading_tab:
    st.subheader("Instructor Feedback")
    instructor_notes = st.text_area("Notes", placeholder="Add qualitative feedback and recommendations...")

    s1, s2, s3, s4 = st.columns(4)
    eq_score = s1.slider("Equations", 0, 10, 0)
    diag_score = s2.slider("Diagrams", 0, 10, 0)
    error_score = s3.slider("Error Analysis", 0, 10, 0)
    presentation_score = s4.slider("Presentation", 0, 10, 0)

    st.markdown("**Rubric weights (%)**")
    w1, w2, w3, w4 = st.columns(4)
    w_eq = w1.number_input("Equations", min_value=0, max_value=100, value=30)
    w_diag = w2.number_input("Diagrams", min_value=0, max_value=100, value=30)
    w_error = w3.number_input("Error", min_value=0, max_value=100, value=20)
    w_pres = w4.number_input("Presentation", min_value=0, max_value=100, value=20)

    if (w_eq + w_diag + w_error + w_pres) != 100:
        st.warning("Tip: Keep the total at 100% for standard normalization.")

    t1, t2, t3, t4 = st.columns(4)
    grade_A = t1.number_input("A ≥", min_value=0, max_value=40, value=36)
    grade_B = t2.number_input("B ≥", min_value=0, max_value=40, value=32)
    grade_C = t3.number_input("C ≥", min_value=0, max_value=40, value=24)
    grade_D = t4.number_input("D ≥", min_value=0, max_value=40, value=16)

    weighted_total = ((eq_score / 10) * w_eq + (diag_score / 10) * w_diag + (error_score / 10) * w_error + (presentation_score / 10) * w_pres) / 100 * 40
    letter_grade = calculate_grade_letter(weighted_total, grade_A, grade_B, grade_C, grade_D)
    st.success(f"Final score: {weighted_total:.2f}/40   |   Grade: {letter_grade}")

    if st.button("Save Progress & Generate PDF", type="primary", use_container_width=True):
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
            example_choice=example_choice if 'example_choice' in locals() else "None",
            V_example=V_example if 'V_example' in locals() else None,
            M_example=M_example if 'M_example' in locals() else None,
            max_V_error=max_V_error if 'max_V_error' in locals() else 0.0,
            rmse_V=rmse_V if 'rmse_V' in locals() else 0.0,
            max_M_error=max_M_error if 'max_M_error' in locals() else 0.0,
            rmse_M=rmse_M if 'rmse_M' in locals() else 0.0,
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

        st.download_button("Download Report", data=pdf_bytes, file_name="beam_analysis_report.pdf", mime="application/pdf", use_container_width=True)
        st.success("Saved successfully.")
