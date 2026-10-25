import json
import os
from datetime import datetime
from io import BytesIO

import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Multimodal Construction Intelligence Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1400px;}
.hero {padding: 1.4rem 1.6rem; border-radius: 18px; background: linear-gradient(120deg,#102a43,#176b87); color:white; margin-bottom:1rem;}
.hero h1 {color:white; margin:0 0 .35rem 0;}
.hero p {color:#e7f4f7; margin:0;}
.small-muted {color:#64748b;font-size:.9rem;}
div[data-testid="stMetric"] {border:1px solid rgba(128,128,128,.25);padding:12px;border-radius:12px;}
</style>
""", unsafe_allow_html=True)

# ---------- Gemini integration (optional) ----------
def get_api_key():
    try:
        return st.session_state.get("gemini_key", "").strip() or os.getenv("GEMINI_API_KEY", "").strip()
    except Exception:
        return os.getenv("GEMINI_API_KEY", "").strip()

def ask_gemini(prompt, image=None, system_instruction=None):
    """Return text from Gemini when configured; raise a readable exception otherwise."""
    key = get_api_key()
    if not key:
        raise RuntimeError("No Gemini API key configured. Use Demonstration Mode or add a key in the sidebar.")
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=key)
        contents = [prompt]
        if image is not None:
            img = image.convert("RGB")
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            contents.append(types.Part.from_bytes(data=buffer.getvalue(), mime_type="image/jpeg"))
        config = types.GenerateContentConfig(
            system_instruction=system_instruction or
            "You are an assistant for construction safety and planning. Be cautious, explain uncertainty, and return valid JSON when requested.",
            response_mime_type="application/json" if "JSON ONLY" in prompt else "text/plain",
            temperature=0.2,
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=config,
        )
        return response.text or ""
    except Exception as exc:
        raise RuntimeError(f"Gemini request failed: {exc}") from exc

def parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]
    return json.loads(text)

def demo_safety():
    return {
        "safety_score": 72,
        "overall_status": "Needs Improvement",
        "ppe_detection": {
            "helmet": "Not clearly verifiable from demo mode",
            "high_visibility_vest": "Not clearly verifiable from demo mode",
            "steel_toe_boots": "Not clearly verifiable from demo mode",
            "safety_harness": "Not clearly verifiable from demo mode"
        },
        "hazards": [
            {"hazard": "Unprotected edge / fall risk (example)", "severity": "High",
             "evidence": "Demonstration example only; no image analysis performed.",
             "corrective_remedy": "Install compliant guardrails or fall-arrest protection and restrict access until inspected."},
            {"hazard": "Housekeeping / trip risk (example)", "severity": "Medium",
             "evidence": "Demonstration example only; no image analysis performed.",
             "corrective_remedy": "Clear walkways, secure loose materials, and maintain designated access routes."}
        ],
        "limitations": "Demonstration data only. No image was analyzed by an AI model."
    }

def demo_crack():
    return {
        "defect_type": "Undetermined (demonstration mode)",
        "estimated_crack_width_mm": None,
        "severity": "Requires qualified inspection",
        "possible_root_causes": ["Cannot be determined without actual image analysis and site context"],
        "recommended_actions": [
            "Photograph the defect with a scale for width reference.",
            "Record whether the crack is growing, leaking, or associated with displacement.",
            "Have a qualified structural engineer inspect it before selecting a repair."
        ],
        "urgency": "Do not infer structural safety from this demo result.",
        "limitations": "Demonstration data only. No image was analyzed by an AI model."
    }

def show_json_download(data, filename):
    st.download_button(
        "⬇️ Download JSON report",
        data=json.dumps(data, indent=2, ensure_ascii=False),
        file_name=filename,
        mime="application/json",
        use_container_width=False,
    )

# ---------- Sidebar ----------
with st.sidebar:
    st.title("🏗️ Construction AI")
    st.caption("Skill Wallet Capstone · Project 1")
    st.subheader("AI configuration")
    entered_key = st.text_input(
        "Google Gemini API key",
        type="password",
        key="gemini_key",
        help="Optional. The key is used only for this app session. Do not share it or commit it to GitHub."
    )
    if entered_key:
        st.success("API key entered for this session.")
    else:
        st.info("Demonstration Mode is active until you add an API key.")
    st.markdown("---")
    st.subheader("Architecture overview")
    st.markdown("""
    - **UI:** Streamlit
    - **Vision & language:** Google Gemini (optional)
    - **Image processing:** Pillow
    - **Reports:** Downloadable JSON
    - **Storage:** No external database
    """)
    st.markdown("---")
    st.caption("AI outputs are decision support only. They are not a substitute for a site safety officer or licensed structural engineer.")

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <h1>Multimodal Construction Intelligence Platform</h1>
  <p>AI-assisted site safety, crack diagnostics, project estimation, and weather-aware construction guidance.</p>
</div>
""", unsafe_allow_html=True)

st.warning("Safety notice: AI may miss hazards or misclassify defects. Never use this tool alone to certify PPE compliance, structural integrity, or permission to continue work.")

tab1, tab2, tab3, tab4 = st.tabs([
    "🦺 Site Safety & PPE Audit",
    "🧱 Crack Diagnostics",
    "📐 Planning & Valuation",
    "🌦️ Site Assistant"
])

# ---------- Tab 1 ----------
with tab1:
    st.header("Site Safety & PPE Audit")
    st.write("Upload a construction-site photo to request a structured PPE and hazard review.")
    safety_file = st.file_uploader("Upload site photo (JPG / JPEG / PNG)", type=["jpg", "jpeg", "png"], key="safety_image")
    if safety_file:
        safety_img = Image.open(safety_file).convert("RGB")
        st.image(safety_img, caption="Uploaded site photo", use_container_width=True)
    analyze_safety = st.button("Analyze site safety", type="primary", key="analyze_safety")
    if analyze_safety:
        if not safety_file:
            st.error("Please upload a site photo first.")
        else:
            with st.spinner("Reviewing image..."):
                prompt = """Analyze this construction-site photo for visible PPE compliance and observable hazards.
Return JSON ONLY with this schema:
{
 "safety_score": integer 0-100,
 "overall_status": "Compliant"|"Needs Improvement"|"High Risk"|"Unable to Determine",
 "ppe_detection": {"helmet": string, "high_visibility_vest": string, "steel_toe_boots": string, "safety_harness": string},
 "hazards": [{"hazard": string, "severity": "Low"|"Medium"|"High"|"Critical", "evidence": string, "corrective_remedy": string}],
 "limitations": string
}
Use "not visible" when equipment cannot be verified. Do not infer hidden PPE. Describe only visible evidence. Reference OSHA and applicable Indian site rules cautiously; do not claim legal certification. JSON ONLY."""
                try:
                    result = parse_json(ask_gemini(prompt, safety_img))
                except Exception as exc:
                    st.warning(f"Live AI analysis unavailable: {exc}")
                    st.info("Showing clearly labelled demonstration data instead.")
                    result = demo_safety()
                st.session_state["last_safety"] = result
    if "last_safety" in st.session_state:
        data = st.session_state["last_safety"]
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Safety score", f"{data.get('safety_score', '—')}/100")
        with c2:
            st.metric("Overall status", str(data.get("overall_status", "—")))
        st.subheader("PPE checklist")
        ppe = data.get("ppe_detection", {})
        if isinstance(ppe, dict):
            for item, status in ppe.items():
                st.write(f"**{item.replace('_', ' ').title()}:** {status}")
        st.subheader("Identified hazards")
        hazards = data.get("hazards", [])
        if hazards:
            for i, hazard in enumerate(hazards, 1):
                with st.expander(f"{i}. {hazard.get('hazard','Hazard')} · {hazard.get('severity','Unknown')}"):
                    st.write("**Evidence:**", hazard.get("evidence", "Not provided"))
                    st.write("**Suggested corrective action:**", hazard.get("corrective_remedy", "Not provided"))
        else:
            st.info("No hazards were returned. This does not prove the site is safe.")
        if data.get("limitations"):
            st.caption(data["limitations"])
        show_json_download(data, "site_safety_report.json")

# ---------- Tab 2 ----------
with tab2:
    st.header("Crack Diagnostics & Structural Integrity")
    st.write("Use an image for preliminary visual triage. Width estimates from a photo are unreliable without a scale.")
    crack_file = st.file_uploader("Upload concrete / wall photo (JPG / JPEG / PNG)", type=["jpg", "jpeg", "png"], key="crack_image")
    if crack_file:
        crack_img = Image.open(crack_file).convert("RGB")
        st.image(crack_img, caption="Uploaded surface photo", use_container_width=True)
    crack_context = st.text_area("Optional context", placeholder="e.g., indoor wall, approximate building age, crack growing or stable, water leakage...", key="crack_context")
    analyze_crack = st.button("Assess visible crack", type="primary", key="analyze_crack")
    if analyze_crack:
        if not crack_file:
            st.error("Please upload a surface photo first.")
        else:
            with st.spinner("Assessing visible defect..."):
                prompt = f"""Review this concrete/wall image for visible defects. Context from user: {crack_context or 'Not provided'}.
Return JSON ONLY:
{{
 "defect_type": "Hairline"|"Settlement"|"Structural Shear"|"Thermal Expansion"|"Spalling"|"Other"|"Unable to Determine",
 "estimated_crack_width_mm": number or null,
 "severity": "Low"|"Medium"|"High"|"Requires qualified inspection",
 "possible_root_causes": [string],
 "recommended_actions": [string],
 "urgency": string,
 "limitations": string
}}
Do not make a definitive structural diagnosis from a photo. If there is no scale, set estimated width to null and explain why. Flag rapidly widening cracks, displacement, exposed/rebar corrosion, falling concrete, or sudden changes for prompt professional inspection. Do not claim the building is safe. JSON ONLY."""
                try:
                    result = parse_json(ask_gemini(prompt, crack_img))
                except Exception as exc:
                    st.warning(f"Live AI analysis unavailable: {exc}")
                    st.info("Showing clearly labelled demonstration data instead.")
                    result = demo_crack()
                st.session_state["last_crack"] = result
    if "last_crack" in st.session_state:
        data = st.session_state["last_crack"]
        st.metric("Preliminary defect category", data.get("defect_type", "Unknown"))
        st.write("**Estimated width (mm):**", data.get("estimated_crack_width_mm", "Not estimated"))
        st.write("**Severity:**", data.get("severity", "Not determined"))
        st.subheader("Possible causes")
        for cause in data.get("possible_root_causes", []):
            st.write(f"- {cause}")
        st.subheader("Suggested next steps")
        for action in data.get("recommended_actions", []):
            st.write(f"- {action}")
        st.warning(data.get("urgency", "Have concerning defects reviewed by a qualified engineer."))
        if data.get("limitations"):
            st.caption(data["limitations"])
        show_json_download(data, "crack_diagnostics_report.json")

# ---------- Tab 3 ----------
with tab3:
    st.header("Planning & Real Estate Valuation")
    st.write("Editable planning estimates for early-stage budgeting. Replace assumptions with local quotations and professional measurements.")
    c1, c2, c3 = st.columns(3)
    with c1:
        structure = st.selectbox("Structure type", ["Residential", "Commercial", "Industrial", "Institutional"])
        area = st.number_input("Built-up area (sq ft)", min_value=100, max_value=2_000_000, value=1500, step=100)
    with c2:
        city_tier = st.selectbox("Location tier", ["Tier 1", "Tier 2", "Tier 3"])
        completion = st.slider("Construction completion (%)", 0, 100, 25)
    with c3:
        cost_rate = st.number_input("Estimated construction rate (₹ / sq ft)", min_value=500, max_value=20000, value={"Tier 1": 2400, "Tier 2": 1900, "Tier 3": 1600}[city_tier], step=100)
        market_rate = st.number_input("Estimated market value (₹ / sq ft)", min_value=500, max_value=50000, value={"Tier 1": 5000, "Tier 2": 3500, "Tier 3": 2500}[city_tier], step=100)
    total_budget = area * cost_rate
    incurred = total_budget * completion / 100
    valuation = area * market_rate
    # Very rough thumb rules for early planning only; verify with engineer/quantity surveyor.
    cement_bags = area * 0.4
    steel_kg = area * 4.0
    st.markdown("### Estimate summary")
    m1, m2, m3 = st.columns(3)
    m1.metric("Estimated project budget", f"₹{total_budget:,.0f}", f"₹{total_budget/100000:.2f} lakh")
    m2.metric("Estimated cost incurred", f"₹{incurred:,.0f}", f"{completion}% complete")
    m3.metric("Indicative market valuation", f"₹{valuation:,.0f}", f"₹{valuation/100000:.2f} lakh")
    st.progress(completion / 100, text=f"Construction progress: {completion}%")
    st.markdown("### Indicative material quantities")
    m4, m5 = st.columns(2)
    m4.metric("Cement (rough thumb rule)", f"{cement_bags:,.0f} bags")
    m5.metric("Steel (rough thumb rule)", f"{steel_kg:,.0f} kg")
    st.caption("These material thumb rules are illustrative, not a bill of quantities. Actual quantities depend on design, structural system, specifications, wastage, soil and local rates.")
    estimate = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "structure_type": structure,
        "built_up_area_sqft": area,
        "location_tier": city_tier,
        "completion_percent": completion,
        "construction_rate_inr_per_sqft": cost_rate,
        "market_rate_inr_per_sqft": market_rate,
        "estimated_total_project_budget_inr": round(total_budget, 2),
        "estimated_cost_incurred_inr": round(incurred, 2),
        "estimated_market_valuation_inr": round(valuation, 2),
        "indicative_cement_bags": round(cement_bags),
        "indicative_steel_kg": round(steel_kg),
        "disclaimer": "Illustrative planning estimate only; validate with qualified professionals and current local rates."
    }
    show_json_download(estimate, "planning_valuation_report.json")

# ---------- Tab 4 ----------
with tab4:
    st.header("Daily Site Assistant & Weather-Aware Advisory")
    weather = st.selectbox("Current / expected weather", ["Normal", "High Wind", "Heavy Rain", "Extreme Heat"])
    advisory = {
        "Normal": [
            "Conduct the daily toolbox talk and confirm permits, PPE, access routes and emergency contacts.",
            "Inspect lifting gear, scaffolds, electrical tools and housekeeping before work starts.",
            "Follow the approved method statement and concrete curing plan."
        ],
        "High Wind": [
            "Pause crane, hoist, work-at-height and lifting activities whenever manufacturer limits or site rules require it.",
            "Secure loose materials, formwork, temporary fencing and elevated items.",
            "Reassess scaffolds and temporary structures before resuming work."
        ],
        "Heavy Rain": [
            "Assess flooding, slippery surfaces, excavation collapse risk and lightning exposure.",
            "Protect electrical equipment and isolate unsafe circuits; keep workers away from standing water around electrics.",
            "Review excavation support and access before allowing entry; protect fresh concrete according to the approved method."
        ],
        "Extreme Heat": [
            "Provide drinking water, shaded rest breaks and acclimatization; monitor workers for heat illness.",
            "Schedule strenuous tasks during cooler periods where practical.",
            "Follow the approved concrete placement and curing plan to reduce rapid moisture loss."
        ]
    }
    st.subheader(f"Advisory for: {weather}")
    for item in advisory[weather]:
        st.write(f"- {item}")
    st.caption("Advisories are general prompts, not a substitute for local weather alerts, site-specific risk assessments, or the competent person's stop-work decision.")
    st.markdown("---")
    st.subheader("Ask the construction assistant")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    user_question = st.chat_input("Ask about construction planning, site safety, materials, or work procedures...")
    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)
        answer = None
        try:
            answer = ask_gemini(
                f"Answer this construction site question: {user_question}\n"
                "Be practical and concise. State assumptions, avoid claiming to certify safety, and recommend a qualified engineer/site safety officer for high-risk decisions."
            )
        except Exception:
            answer = (
                "Demonstration-mode response: I can help you structure the question, but live AI answers require a Gemini API key. "
                "For immediate safety risks, stop the affected work and contact the site safety officer or qualified engineer. "
                "You asked: " + user_question
            )
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

st.markdown("---")
st.caption("Multimodal Construction Intelligence Platform · Skill Wallet Capstone Project 1 · Built with Streamlit")
