import pandas as pd
import plotly.express as px
import streamlit as st


def generate_all_charts(df: pd.DataFrame, theme: str = "plotly"):
    """Auto-generate the most useful charts for the given dataframe."""
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    categorical_cols = df.select_dtypes(include='object').columns.tolist()

    if not numeric_cols and not categorical_cols:
        st.warning("No plottable columns found in this dataset.")
        return

    # Row 1: Histogram + Bar Chart
    col1, col2 = st.columns(2)

    with col1:
        if numeric_cols:
            selected_num = st.selectbox(
                "📊 Histogram column", numeric_cols, key="hist_col"
            )
            fig = px.histogram(
                df, x=selected_num,
                title=f"Distribution of {selected_num}",
                template=theme,
                color_discrete_sequence=["#667eea"]
            )
            fig.update_layout(margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if categorical_cols and numeric_cols:
            cat_col = st.selectbox(
                "📈 Category column", categorical_cols, key="bar_cat"
            )
            num_col = st.selectbox(
                "📈 Value column", numeric_cols, key="bar_num"
            )
            top_n = df.groupby(cat_col)[num_col].sum().nlargest(10).reset_index()
            fig = px.bar(
                top_n, x=cat_col, y=num_col,
                title=f"Top 10: {num_col} by {cat_col}",
                template=theme,
                color=num_col,
                color_continuous_scale="Viridis"
            )
            fig.update_layout(margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
        elif len(numeric_cols) >= 1:
            selected_col = st.selectbox(
                "📈 Box plot column", numeric_cols, key="box_col"
            )
            fig = px.box(
                df, y=selected_col,
                title=f"Box Plot: {selected_col}",
                template=theme
            )
            st.plotly_chart(fig, use_container_width=True)

    # Row 2: Scatter + Correlation Heatmap
    if len(numeric_cols) >= 2:
        col3, col4 = st.columns(2)

        with col3:
            x_col = st.selectbox("🔵 X axis", numeric_cols, key="scatter_x")
            y_col = st.selectbox(
                "🔴 Y axis", numeric_cols,
                index=min(1, len(numeric_cols) - 1), key="scatter_y"
            )
            color_col = categorical_cols[0] if categorical_cols else None
            fig = px.scatter(
                df, x=x_col, y=y_col,
                color=color_col,
                title=f"Scatter: {x_col} vs {y_col}",
                template=theme,
                opacity=0.7
            )
            fig.update_layout(margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

        with col4:
            corr = df[numeric_cols].corr().round(2)
            fig = px.imshow(
                corr,
                title="Correlation Heatmap",
                template=theme,
                color_continuous_scale="RdBu",
                text_auto=True,
                aspect="auto"
            )
            fig.update_layout(margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

    # Row 3: Pie Chart + Missing Values
    col5, col6 = st.columns(2)

    with col5:
        if categorical_cols:
            pie_col = st.selectbox(
                "🥧 Pie chart column", categorical_cols, key="pie_col"
            )
            pie_data = df[pie_col].value_counts().head(8)
            fig = px.pie(
                values=pie_data.values,
                names=pie_data.index,
                title=f"Distribution: {pie_col}",
                template=theme
            )
            fig.update_layout(margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

    with col6:
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if not missing.empty:
            fig = px.bar(
                x=missing.index,
                y=missing.values,
                title="Missing Values per Column",
                labels={"x": "Column", "y": "Missing Count"},
                template=theme,
                color=missing.values,
                color_continuous_scale="Reds"
            )
            fig.update_layout(margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No missing values found in this dataset!")

    # Trend Line
    if numeric_cols:
        st.markdown("#### 📉 Trend View")
        trend_col = st.selectbox(
            "Select column for trend", numeric_cols, key="trend_col"
        )
        fig = px.line(
            df.reset_index(), y=trend_col,
            title=f"Trend: {trend_col}",
            template=theme,
            color_discrete_sequence=["#764ba2"]
        )
        fig.update_layout(margin=dict(t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)