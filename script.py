import streamlit as st
import pandas as pd
import requests
from datetime import datetime

API_KEY = "iPUDaX0M0TySuAoLHWTm3O3K9KdYBwKY"
BASE_URL = "https://calendarific.com/api/v2/holidays"

st.set_page_config(page_title="🪔 Multifaith Festival Recommender", layout="wide")

STATE_FESTIVAL_MAP = {
    "Tamil Nadu": ["Pongal", "Thaipusam", "Karthigai Deepam", "Aadi Perukku", "Mahamaham"],
    "Kerala": ["Onam", "Vishu", "Thrissur Pooram", "Attukal Pongala", "Temple Festivals"],
    "Assam": ["Bihu", "Me-Dam-Me-Phi", "Baishagu", "Ambubachi Mela", "Rongali Bihu"],
    "Maharashtra": ["Ganesh Chaturthi", "Gudi Padwa", "Makar Sankranti", "Ellora Festival", "Nag Panchami"],
    "West Bengal": ["Durga Puja", "Kali Puja", "Poila Boishakh", "Rath Yatra", "Jagaddhatri Puja"],
    "Punjab": ["Lohri", "Baisakhi", "Hola Mohalla", "Maghi", "Guru Nanak Jayanti"],
    "Bihar": ["Chhath Puja", "Sama Chakeva", "Makar Sankranti", "Rajgir Mahotsav", "Pitrapaksha Mela"],
    "Karnataka": ["Ugadi", "Mysore Dasara", "Karaga Festival", "Makar Sankranti", "Kambala"],
    "Uttar Pradesh": ["Diwali", "Holi", "Kumbh Mela", "Ram Navami", "Janmashtami"],
    "Gujarat": ["Navratri", "Uttarayan", "Rath Yatra", "Janmashtami", "Diwali"],
    "Rajasthan": ["Gangaur", "Teej", "Mewar Festival", "Pushkar Fair", "Desert Festival"],
    "Odisha": ["Rath Yatra (Puri)", "Durga Puja", "Chhau Festival", "Puri Beach Festival", "Makar Mela"],
    "Delhi": ["Republic Day Parade", "Diwali", "Holi", "Janmashtami", "Independence Day"],
    "Madhya Pradesh": ["Khajuraho Dance Festival", "Diwali", "Holi", "Nag Panchami", "Tansen Music Festival"],
    "Telangana": ["Bonalu", "Bathukamma", "Ugadi", "Makar Sankranti", "Diwali"],
    "Andhra Pradesh": ["Ugadi", "Sankranti", "Rama Navami", "Vinayaka Chaturthi", "Diwali"],
    "Haryana": ["Holi", "Diwali", "Baisakhi", "Teej", "Lohri"],
    "Jharkhand": ["Sarhul", "Karma Festival", "Chhath Puja", "Tusu Festival", "Bandna"],
    "Chhattisgarh": ["Hareli", "Madai Festival", "Pola", "Diwali", "Chhath Puja"],
    "Goa": ["Carnival", "Shigmo", "Sao Joao", "Diwali", "Christmas"],
    "Meghalaya": ["Shad Suk Mynsiem", "Wangala", "Behdienkhlam", "Christmas", "Easter"],
    "Nagaland": ["Hornbill Festival", "Moatsu", "Sekrenyi", "Tuluni", "Christmas"],
    "Manipur": ["Yaoshang (Holi)", "Ningol Chakouba", "Cheiraoba", "Kang Festival", "Christmas"],
    "Mizoram": ["Chapchar Kut", "Mim Kut", "Pawl Kut", "Christmas", "Easter"],
    "Tripura": ["Kharchi Puja", "Ker Puja", "Diwali", "Durga Puja", "Christmas"],
    "Arunachal Pradesh": ["Losar", "Solung", "Nyokum", "Si-Donyi", "Dree Festival"],
    "Sikkim": ["Losar", "Saga Dawa", "Pang Lhabsol", "Dasain", "Tihar"],
    "Jammu and Kashmir": ["Eid", "Baisakhi", "Lohri", "Tulip Festival", "Navroz"],
}

FAITH_KEYWORDS = {
    "Hindu": [
        "diwali", "deepavali", "holi", "pongal", "ugadi", "gudi padwa", "navratri", "dussehra",
        "rath yatra", "makar sankranti", "ram navami", "janmashtami", "karwa chauth", "aadi perukku",
        "karthigai", "kali puja", "durga puja", "vishu", "ganesh", "vinayaka", "thai", "pongala",
        "mewar", "gangaur", "teej"
    ],
    "Islam": ["eid", "ramzan", "ramadan", "muharram", "bakrid", "eid-ul-fitr", "eid al-fitr", "eid-ul-adha"],
    "Christian": ["christmas", "easter", "good friday"],
    "Sikh": ["baisakhi", "guru nanak", "hola mohalla", "gurpurab"],
    "Buddhist": ["buddha purnima", "vesak", "losar", "saga dawa"],
    "Jain": ["mahavir", "paryushan", "paryushana"],
    "Zoroastrian": ["navroz", "nowruz", "navroze", "jamshedi navroz"],
    "Tribal / Indigenous": ["sarhul", "karma", "bandna", "tusu", "wangala", "behdienkhlam", "madai", "hornbill"]
}

def infer_state_from_name(festival_name: str) -> str:
    for state, fests in STATE_FESTIVAL_MAP.items():
        for f in fests:
            if f.lower() in festival_name.lower():
                return state
    return "All India"

def infer_faith_from_name(festival_name: str) -> str:
    name = festival_name.lower()
    for faith, kws in FAITH_KEYWORDS.items():
        for kw in kws:
            if kw in name:
                return faith
    return "Other"

@st.cache_data
def fetch_festivals(year=2024, country="IN") -> pd.DataFrame:
    url = f"{BASE_URL}?&api_key={API_KEY}&country={country}&year={year}"
    r = requests.get(url, timeout=20)
    data = r.json()
    holidays = data.get("response", {}).get("holidays", []) or []
    rows = []
    for h in holidays:
        name = h.get("name", "Unknown Festival")
        date_iso = h.get("date", {}).get("iso")
        desc = h.get("description", "") or "No description available"
        states_field = h.get("states")
        if isinstance(states_field, list):
            states_field = ", ".join(
                [s.get("name") for s in states_field if isinstance(s, dict) and s.get("name")]
            ) or "All India"
        elif not states_field or states_field == "All":
            states_field = infer_state_from_name(name)
        rows.append({
            "Festival": name,
            "Date": date_iso,
            "Description": desc,
            "States": states_field,
            "Faith": infer_faith_from_name(name)
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

def learn_more_link(name: str) -> str:
    return f"https://www.google.com/search?q={name.replace(' ', '+')}+festival+in+India"

def display_festivals(df: pd.DataFrame, title: str):
    st.markdown(f"### {title}")
    if df.empty:
        st.info("No festivals found.")
        return
    df = df.sort_values(by="Date", ascending=True)
    for _, row in df.iterrows():
        fname = row.get("Festival", "Festival")
        fdate = row["Date"].strftime("%d %B %Y") if pd.notnull(row.get("Date")) else "Not available"
        states = row.get("States", "All India")
        faith = row.get("Faith", "Other")
        url = learn_more_link(fname)
        st.markdown(
            f"""
            <div style="padding:15px; margin-bottom:10px; border-radius:10px;
                        box-shadow:0 2px 6px rgba(0,0,0,0.15); background:#f9f9f9;">
                <h4 style="margin:0; color:#e63946;">{fname}</h4>
                <p style="margin:0; color:#457b9d;"><b>Date:</b> {fdate}</p>
                <p style="margin:0; color:#2a9d8f;"><b>State(s):</b> {states}</p>
                <p style="margin:0; color:#7b2cbf;"><b>Faith:</b> {faith}</p>
                <p style="margin-top:8px; font-size:14px; color:#333;">{row.get('Description','')}</p>
                <a href="{url}" target="_blank" style="
                    display:inline-block; margin-top:8px; background:#2563eb; color:#fff;
                    padding:6px 12px; border-radius:6px; text-decoration:none; font-size:13px;">
                    🔎 Learn More
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

def create_fallback_row(festival: str, state: str) -> dict:
    return {
        "Festival": festival,
        "Date": pd.NaT,
        "Description": "Festival info not available via API",
        "States": state,
        "Faith": infer_faith_from_name(festival)
    }

def ensure_min_for_state(df_base: pd.DataFrame, state: str, faith: str = "All", min_n: int = 5) -> pd.DataFrame:
    df = df_base.copy()
    if state != "All India":
        df = df[df["States"].fillna("").str.contains(state, case=False, na=False)]
    if faith != "All":
        df = df[df["Faith"].fillna("").str.contains(faith, case=False, na=False)]
    if len(df) >= min_n or state == "All India":
        return df.drop_duplicates(subset=["Festival"]).sort_values("Date").head(min_n) if state != "All India" else df.drop_duplicates(subset=["Festival"]).sort_values("Date")
    existing = set(df["Festival"].str.lower().tolist())
    fallbacks = []
    for fest in STATE_FESTIVAL_MAP.get(state, []):
        fest_faith = infer_faith_from_name(fest)
        if (faith == "All" or fest_faith == faith) and fest.lower() not in existing:
            fallbacks.append(create_fallback_row(fest, state))
        if len(df) + len(fallbacks) >= min_n:
            break
    if fallbacks:
        df = pd.concat([df, pd.DataFrame(fallbacks)], ignore_index=True)
    return df.drop_duplicates(subset=["Festival"]).sort_values("Date").head(min_n)

def display_grouped_by_state(grouped: dict, title: str):
    st.markdown(f"### {title}")
    if not grouped:
        st.info("No festivals found.")
        return
    for state in sorted(grouped.keys()):
        sub = grouped[state]
        if sub.empty:
            continue
        st.markdown(f"#### {state}")
        display_festivals(sub, title="")  # will render cards without extra header

st.title("🪔 Multifaith Festival Recommender")

st.sidebar.header("⚙️ Options")
year = st.sidebar.number_input("Select Year", min_value=2000, max_value=2100, value=datetime.now().year)

festivals_df = fetch_festivals(year=year)
festivals_df["Date"] = pd.to_datetime(festivals_df["Date"], errors="coerce")

selected_date = st.sidebar.date_input("📆 Select a Date to View Festivals", value=datetime.now().date())
festivals_on_date = festivals_df[festivals_df["Date"].dt.date == selected_date]

st.sidebar.markdown("### 📅 Festivals on Selected Date:")
if festivals_on_date.empty:
    st.sidebar.info("No festivals found on this date.")
else:
    for _, row in festivals_on_date.iterrows():
        n = row["Festival"]
        url = learn_more_link(n)
        st.sidebar.markdown(
            f'<a href="{url}" target="_blank" style="text-decoration:none; color:#2563eb; font-weight:500;">🎉 {n} ({row["States"]})</a>',
            unsafe_allow_html=True
        )

st.subheader("🔍 Search Festivals")

col1, col2, col3 = st.columns(3)
with col1:
    q_name = st.text_input("Search by Festival Name")
with col2:
    all_states = ["All India"] + sorted(STATE_FESTIVAL_MAP.keys())
    q_state = st.selectbox("Search by State", all_states)
with col3:
    q_faith = st.selectbox("Search by Faith", ["All"] + list(FAITH_KEYWORDS.keys()))

if q_name:
    name_results = festivals_df[festivals_df["Festival"].str.contains(q_name, case=False, na=False)]
    display_festivals(name_results, f"Results for '{q_name}'")

if q_state == "All India" and q_faith == "All":
    display_festivals(festivals_df, "All Festivals")

elif q_state != "All India" and q_faith == "All":
    state_results = ensure_min_for_state(festivals_df, state=q_state, faith="All", min_n=5)
    display_festivals(state_results, f"Festivals in '{q_state}'")

elif q_state != "All India" and q_faith != "All":
    both_results = ensure_min_for_state(festivals_df, state=q_state, faith=q_faith, min_n=5)
    display_festivals(both_results, f"{q_faith} Festivals in '{q_state}'")

elif q_state == "All India" and q_faith != "All":
    api_faith = festivals_df[festivals_df["Faith"].fillna("").str.contains(q_faith, case=False, na=False)]
    grouped = {}
    for state, fest_list in STATE_FESTIVAL_MAP.items():
        df_state_api = api_faith[api_faith["States"].fillna("").str.contains(state, case=False, na=False)]
        fallback_rows = []
        existing = set(df_state_api["Festival"].str.lower().tolist())
        for f in fest_list:
            iff = infer_faith_from_name(f)
            if iff == q_faith and f.lower() not in existing:
                fallback_rows.append(create_fallback_row(f, state))
        df_state = df_state_api
        if fallback_rows:
            df_state = pd.concat([df_state_api, pd.DataFrame(fallback_rows)], ignore_index=True)
        df_state = df_state.drop_duplicates(subset=["Festival"]).sort_values("Date")
        if not df_state.empty:
            grouped[state] = df_state
    display_grouped_by_state(grouped, title=f"All-India view: {q_faith} Festivals (grouped by state)")

st.subheader("📅 Ongoing & Upcoming Festivals")

today = datetime.now().date()
this_month = today.month

ongoing = festivals_df[festivals_df["Date"].dt.date == today]
upcoming = festivals_df[(festivals_df["Date"].dt.month == this_month) & (festivals_df["Date"].dt.date > today)]

c1, c2 = st.columns(2)
with c1:
    if ongoing.empty:
        st.info("No ongoing festivals today.")
    else:
        display_festivals(ongoing, "🎉 Ongoing Festivals")
with c2:
    if upcoming.empty:
        st.info("No upcoming festivals this month.")
    else:
        display_festivals(upcoming, "⏳ Upcoming Festivals This Month")
