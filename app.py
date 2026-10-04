
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EduPro Learner Analytics", page_icon="🎓", layout="wide")

st.title("🎓 Learner Demographics and Course Enrollment Behavior Analysis on EduPro")
st.caption("Descriptive learner intelligence dashboard for understanding who learners are and how they engage with courses.")

@st.cache_data
def load_data():
    users = pd.read_csv("data/users.csv")
    courses = pd.read_csv("data/courses.csv")
    teachers = pd.read_csv("data/teachers.csv")
    tx = pd.read_csv("data/transactions.csv", parse_dates=["TransactionDate"])
    return users, courses, teachers, tx

users, courses, teachers, tx = load_data()

# Join transaction behavior to learner and course attributes.
df = tx.merge(users, on="UserID", how="left").merge(courses, on="CourseID", how="left")

st.sidebar.header("Filters")
age_min, age_max = int(users["Age"].min()), int(users["Age"].max())
age_range = st.sidebar.slider("Age range", age_min, age_max, (age_min, age_max))
gender_options = sorted(users["Gender"].dropna().unique().tolist())
gender = st.sidebar.multiselect("Gender", gender_options, default=gender_options)
category_options = sorted(courses["CourseCategory"].dropna().unique().tolist())
category = st.sidebar.multiselect("Course category", category_options, default=category_options)
level_options = ["Beginner", "Intermediate", "Advanced"]
level = st.sidebar.multiselect("Course level", level_options, default=level_options)

f_users = users[users["Age"].between(*age_range) & users["Gender"].isin(gender)]
f_df = df[
    df["UserID"].isin(f_users["UserID"])
    & df["CourseCategory"].isin(category)
    & df["CourseLevel"].isin(level)
]

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Learners", f_users["UserID"].nunique())
c2.metric("Enrollments", f_df["TransactionID"].nunique())
c3.metric("Course Categories", f_df["CourseCategory"].nunique())
c4.metric("Avg. Course Rating", f"{f_df['CourseRating'].mean():.2f}" if len(f_df) else "0.00")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "👥 Demographics", "📚 Enrollment Analysis", "🔎 Preference Analysis", "📈 Behavioral Insights"
])

with tab1:
    st.subheader("Learner Demographic Overview")
    a, b = st.columns(2)
    with a:
        age_bins = [0, 17, 25, 35, 45, 100]
        age_labels = ["≤17", "18–25", "26–35", "36–45", "45+"]
        tmp = f_users.copy()
        tmp["Age Group"] = pd.cut(tmp["Age"], bins=age_bins, labels=age_labels, include_lowest=True)
        age_counts = tmp["Age Group"].value_counts().reindex(age_labels, fill_value=0).reset_index()
        age_counts.columns = ["Age Group", "Learners"]
        st.plotly_chart(px.bar(age_counts, x="Age Group", y="Learners", title="Learners by Age Group"), use_container_width=True)
    with b:
        g = f_users["Gender"].value_counts().reset_index()
        g.columns = ["Gender", "Learners"]
        st.plotly_chart(px.pie(g, names="Gender", values="Learners", title="Gender Distribution"), use_container_width=True)

    st.subheader("Learner Sample")
    st.dataframe(f_users[["UserID","UserName","Age","Gender"]].head(20), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Course Enrollment Distribution")
    a, b = st.columns(2)
    with a:
        cat_counts = f_df["CourseCategory"].value_counts().reset_index()
        cat_counts.columns = ["CourseCategory", "Enrollments"]
        st.plotly_chart(px.bar(cat_counts, x="CourseCategory", y="Enrollments", title="Enrollments by Course Category"), use_container_width=True)
    with b:
        type_counts = f_df["CourseType"].value_counts().reset_index()
        type_counts.columns = ["CourseType", "Enrollments"]
        st.plotly_chart(px.pie(type_counts, names="CourseType", values="Enrollments", title="Free vs Paid Enrollment"), use_container_width=True)

    level_counts = f_df["CourseLevel"].value_counts().reindex(level_options, fill_value=0).reset_index()
    level_counts.columns = ["CourseLevel", "Enrollments"]
    st.plotly_chart(px.bar(level_counts, x="CourseLevel", y="Enrollments", title="Enrollment by Course Level"), use_container_width=True)

with tab3:
    st.subheader("Demographics × Course Preference")
    a, b = st.columns(2)
    with a:
        age_bins = [0, 17, 25, 35, 45, 100]
        age_labels = ["≤17", "18–25", "26–35", "36–45", "45+"]
        tmp = f_df.copy()
        tmp["Age Group"] = pd.cut(tmp["Age"], bins=age_bins, labels=age_labels, include_lowest=True)
        heat = pd.crosstab(tmp["Age Group"], tmp["CourseCategory"]).reindex(age_labels, fill_value=0)
        st.plotly_chart(px.imshow(heat, text_auto=True, aspect="auto", title="Age Group vs Course Category"), use_container_width=True)
    with b:
        gender_cat = pd.crosstab(f_df["Gender"], f_df["CourseCategory"])
        st.plotly_chart(px.imshow(gender_cat, text_auto=True, aspect="auto", title="Gender vs Course Category"), use_container_width=True)

    pref = f_df.groupby("CourseCategory").agg(
        Enrollments=("TransactionID","count"),
        AvgRating=("CourseRating","mean"),
        AvgDuration=("CourseDuration","mean")
    ).sort_values("Enrollments", ascending=False).reset_index()
    st.dataframe(pref.round(2), use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Behavioral Insights")
    per_user = f_df.groupby("UserID").agg(
        Enrollments=("TransactionID","count"),
        AvgCourseRating=("CourseRating","mean"),
        AvgDuration=("CourseDuration","mean"),
        TotalSpend=("Amount","sum")
    ).reset_index()

    a, b, c = st.columns(3)
    a.metric("Avg. enrollments / learner", f"{per_user['Enrollments'].mean():.2f}" if len(per_user) else "0.00")
    b.metric("Avg. course duration", f"{f_df['CourseDuration'].mean():.2f}" if len(f_df) else "0.00")
    c.metric("Total transaction value", f"${f_df['Amount'].sum():,.2f}" if len(f_df) else "$0.00")

    st.plotly_chart(
        px.histogram(per_user, x="Enrollments", nbins=15, title="Enrollment Count per Active Learner"),
        use_container_width=True
    )

st.divider()
st.caption("Project scope: descriptive learner intelligence, course enrollment behavior, demographic analysis, and course preference exploration.")
