#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
from io import StringIO
from datetime import datetime, timedelta

st.set_page_config(page_title="CSV Pivot Table Viewer", layout="wide")

st.title("CSV Pivot Table Viewer")

# File upload section
st.subheader("Upload CSV File")

col1, col2 = st.columns([3, 1])
with col1:
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
with col2:
    use_sample = st.checkbox("Use sample data instead", value=True)

df = None
if use_sample:
    # Sample data path
    sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data.csv")
    if os.path.exists(sample_path):
        df = pd.read_csv(sample_path)
        # Try to convert date columns
        for col in df.columns:
            if 'date' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass
        st.success(f"Loaded sample data with {len(df)} rows and {len(df.columns)} columns.")
    else:
        st.error("Sample data file not found. Please upload a CSV file.")
elif uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        # Try to convert date columns
        for col in df.columns:
            if 'date' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass
        st.success(f"Loaded CSV file with {len(df)} rows and {len(df.columns)} columns.")
    except Exception as e:
        st.error(f"Failed to load CSV file: {str(e)}")

if df is not None:
    # Data Preview in an expandable section
    with st.expander("Data Preview", expanded=True):
        st.dataframe(df.head(20), use_container_width=True)

    # Define column types for filtering
    column_types = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            column_types[col] = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            column_types[col] = "datetime"
        else:
            column_types[col] = "categorical"
    
    # Main layout with columns
    main_left, main_right = st.columns([1, 3])
    
    # Left column for configuration and filtering
    with main_left:
        st.subheader("Pivot Table Configuration")
        
        # Start with an unfiltered dataframe
        filtered_df = df.copy()
        total_rows = len(df)
        filtered_rows = len(filtered_df)
        
        # Get column names
        columns = df.columns.tolist()
        
        # Filter for numeric columns for values
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Default selections
        default_row = columns[0] if columns else None
        default_col = columns[1] if len(columns) > 1 else None
        
        # Row selection with inline filter
        st.write("**Row Field**")
        row_field = st.selectbox("Select row field:", columns, index=columns.index(default_row) if default_row else 0, key="row_field")
        
        # Add filter for row field
        if st.checkbox(f"Filter {row_field} values", key="filter_row"):
            if column_types[row_field] == "numeric":
                # For numeric columns, use range sliders
                min_val = float(df[row_field].min())
                max_val = float(df[row_field].max())
                
                filter_range = st.slider(
                    f"Range for {row_field}:", 
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val),
                    step=(max_val - min_val) / 100,
                    key="row_filter_range"
                )
                
                # Apply filter
                filtered_df = filtered_df[(filtered_df[row_field] >= filter_range[0]) & 
                                       (filtered_df[row_field] <= filter_range[1])]
                
            elif column_types[row_field] == "categorical":
                # For categorical columns, use multiselect
                unique_values = sorted(df[row_field].unique())
                selected_values = st.multiselect(
                    f"Values for {row_field}:",
                    unique_values,
                    default=unique_values,
                    key="row_filter_values"
                )
                
                # Apply filter
                if selected_values:
                    filtered_df = filtered_df[filtered_df[row_field].isin(selected_values)]
            
            elif column_types[row_field] == "datetime":
                # For datetime columns with timeline chart
                min_date = df[row_field].min().date()
                max_date = df[row_field].max().date()
                
                # Create a histogram to show data distribution over time
                date_counts = df[row_field].dt.date.value_counts().sort_index()
                date_df = pd.DataFrame({
                    'date': date_counts.index,
                    'count': date_counts.values
                })
                
                # Display the timeline chart
                st.write("Data distribution over time:")
                fig = px.bar(date_df, x='date', y='count', 
                            title=f"Timeline for {row_field}",
                            labels={'date': 'Date', 'count': 'Count'},
                            height=200)
                fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig, use_container_width=True)
                
                # Add date range selector
                date_range = st.date_input(
                    f"Select date range for {row_field}:",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key="row_filter_dates"
                )
                
                if len(date_range) == 2:
                    st.caption(f"Selected range: {date_range[0]} to {date_range[1]}")
                    filtered_df = filtered_df[
                        (filtered_df[row_field].dt.date >= date_range[0]) & 
                        (filtered_df[row_field].dt.date <= date_range[1])
                    ]
        
        # Column selection with inline filter
        st.write("**Column Field (optional)**")
        col_field = st.selectbox("Select column field:", ["None"] + columns, 
                               index=columns.index(default_col) + 1 if default_col else 0, key="col_field")
        col_field = None if col_field == "None" else col_field
        
        # Add filter for column field if a column is selected
        if col_field and st.checkbox(f"Filter {col_field} values", key="filter_col"):
            if column_types[col_field] == "numeric":
                min_val = float(df[col_field].min())
                max_val = float(df[col_field].max())
                
                filter_range = st.slider(
                    f"Range for {col_field}:", 
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val),
                    step=(max_val - min_val) / 100,
                    key="col_filter_range"
                )
                
                filtered_df = filtered_df[(filtered_df[col_field] >= filter_range[0]) & 
                                       (filtered_df[col_field] <= filter_range[1])]
                
            elif column_types[col_field] == "categorical":
                unique_values = sorted(df[col_field].unique())
                selected_values = st.multiselect(
                    f"Values for {col_field}:",
                    unique_values,
                    default=unique_values,
                    key="col_filter_values"
                )
                
                if selected_values:
                    filtered_df = filtered_df[filtered_df[col_field].isin(selected_values)]
            
            elif column_types[col_field] == "datetime":
                min_date = df[col_field].min().date()
                max_date = df[col_field].max().date()
                
                # Create a histogram to show data distribution over time
                date_counts = df[col_field].dt.date.value_counts().sort_index()
                date_df = pd.DataFrame({
                    'date': date_counts.index,
                    'count': date_counts.values
                })
                
                # Display the timeline chart
                st.write("Data distribution over time:")
                fig = px.bar(date_df, x='date', y='count', 
                            title=f"Timeline for {col_field}",
                            labels={'date': 'Date', 'count': 'Count'},
                            height=200)
                fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig, use_container_width=True)
                
                # Add date range selector
                date_range = st.date_input(
                    f"Select date range for {col_field}:",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key="col_filter_dates"
                )
                
                if len(date_range) == 2:
                    st.caption(f"Selected range: {date_range[0]} to {date_range[1]}")
                    filtered_df = filtered_df[
                        (filtered_df[col_field].dt.date >= date_range[0]) & 
                        (filtered_df[col_field].dt.date <= date_range[1])
                    ]
        
        # ENHANCEMENT: Multiple value fields with inline filters
        st.write("**Value Fields**")
        if numeric_columns:
            value_fields = st.multiselect(
                "Select value fields:",
                numeric_columns,
                default=[numeric_columns[0]] if numeric_columns else [],
                key="value_fields"
            )
        else:
            value_fields = st.multiselect(
                "Select value fields:",
                columns,
                default=[columns[0]] if columns else [],
                key="value_fields_alt"
            )
        
        # Add filters for value fields
        for val_field in value_fields:
            if st.checkbox(f"Filter {val_field} values", key=f"filter_{val_field}"):
                if column_types[val_field] == "numeric":
                    min_val = float(df[val_field].min())
                    max_val = float(df[val_field].max())
                    
                    filter_range = st.slider(
                        f"Range for {val_field}:", 
                        min_value=min_val,
                        max_value=max_val,
                        value=(min_val, max_val),
                        step=(max_val - min_val) / 100,
                        key=f"{val_field}_filter_range"
                    )
                    
                    filtered_df = filtered_df[(filtered_df[val_field] >= filter_range[0]) & 
                                          (filtered_df[val_field] <= filter_range[1])]
        
        # Additional filters section
        with st.expander("Additional Filters", expanded=False):
            st.write("Apply filters to other columns:")
            
            # Get remaining columns that aren't already being filtered
            used_columns = [row_field]
            if col_field:
                used_columns.append(col_field)
            used_columns.extend(value_fields)
            
            remaining_columns = [col for col in columns if col not in used_columns]
            
            # Add filters for remaining columns
            for col in remaining_columns:
                if st.checkbox(f"Filter {col}", key=f"extra_filter_{col}"):
                    if column_types[col] == "numeric":
                        min_val = float(df[col].min())
                        max_val = float(df[col].max())
                        
                        filter_range = st.slider(
                            f"Range for {col}:", 
                            min_value=min_val,
                            max_value=max_val,
                            value=(min_val, max_val),
                            step=(max_val - min_val) / 100,
                            key=f"extra_{col}_range"
                        )
                        
                        filtered_df = filtered_df[(filtered_df[col] >= filter_range[0]) & 
                                              (filtered_df[col] <= filter_range[1])]
                        
                    elif column_types[col] == "categorical":
                        unique_values = sorted(df[col].unique())
                        selected_values = st.multiselect(
                            f"Values for {col}:",
                            unique_values,
                            default=unique_values,
                            key=f"extra_{col}_values"
                        )
                        
                        if selected_values:
                            filtered_df = filtered_df[filtered_df[col].isin(selected_values)]
                    
                    elif column_types[col] == "datetime":
                        try:
                            min_date = df[col].min().date()
                            max_date = df[col].max().date()
                            
                            # Create a histogram to show data distribution over time
                            date_counts = df[col].dt.date.value_counts().sort_index()
                            date_df = pd.DataFrame({
                                'date': date_counts.index,
                                'count': date_counts.values
                            })
                            
                            # Display the timeline chart
                            st.write("Data distribution over time:")
                            fig = px.bar(date_df, x='date', y='count', 
                                        title=f"Timeline for {col}",
                                        labels={'date': 'Date', 'count': 'Count'},
                                        height=200)
                            fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Add date range selector
                            date_range = st.date_input(
                                f"Select date range for {col}:",
                                value=(min_date, max_date),
                                min_value=min_date,
                                max_value=max_date,
                                key=f"extra_{col}_dates"
                            )
                            
                            if len(date_range) == 2:
                                st.caption(f"Selected range: {date_range[0]} to {date_range[1]}")
                                filtered_df = filtered_df[
                                    (filtered_df[col].dt.date >= date_range[0]) & 
                                    (filtered_df[col].dt.date <= date_range[1])
                                ]
                        except:
                            st.warning(f"Could not convert {col} to datetime.")
                            unique_values = sorted(df[col].unique())
                            selected_values = st.multiselect(
                                f"Values for {col}:",
                                unique_values,
                                default=unique_values,
                                key=f"extra_{col}_text"
                            )
                            
                            if selected_values:
                                filtered_df = filtered_df[filtered_df[col].isin(selected_values)]
        
        # Aggregation method
        st.write("**Aggregation Method**")
        agg_method = st.selectbox("Select aggregation method:", 
                                ["sum", "mean", "count", "min", "max"], key="agg_method")
        
        # Display filter status
        filtered_rows = len(filtered_df)
        if filtered_rows < total_rows:
            st.info(f"Filtered data: {filtered_rows} of {total_rows} rows ({filtered_rows/total_rows:.1%})")
            
        # Add a small refresh button for manual refresh
        manual_refresh = st.button("Refresh View", key="refresh_view", help="Manually refresh the pivot table")
        
    # Right side for results
    with main_right:
        # Auto-generate pivot table whenever fields are selected
        try:
            if not value_fields:
                st.subheader("Filtered Data Preview")
                st.dataframe(filtered_df.head(20), use_container_width=True)
                st.info("Please select at least one value field to create a pivot table.")
            else:
                st.subheader("Pivot Table Result")
                st.caption("Automatically updates as you select fields and filters")
                
                # Create a dictionary of aggregation methods for each value field
                agg_dict = {field: agg_method for field in value_fields}
                
                if col_field:
                    # Create pivot table with multiple value fields
                    pivot_result = pd.pivot_table(
                        filtered_df, 
                        values=value_fields, 
                        index=row_field, 
                        columns=col_field, 
                        aggfunc=agg_method,
                        fill_value=0
                    )
                    
                    # Format the pivot table for display
                    if len(value_fields) > 1 and isinstance(pivot_result.columns, pd.MultiIndex):
                        # For multiple value fields, flatten the column names
                        pivot_result.columns = [f"{val}_{col}" if col_field else val 
                                            for val, col in pivot_result.columns]
                    
                    # Display the pivot table
                    st.dataframe(pivot_result, use_container_width=True)
                    
                    # Show row count
                    st.caption(f"Showing {len(pivot_result)} rows × {len(pivot_result.columns)} columns")
                else:
                    # If no column field is selected, just group by row field
                    pivot_result = filtered_df.groupby(row_field)[value_fields].agg(agg_method).reset_index()
                    # Display the grouped data
                    st.dataframe(pivot_result, use_container_width=True)
                    
                    # Show row count
                    st.caption(f"Showing {len(pivot_result)} rows × {len(pivot_result.columns)} columns")
                
                # Export option
                if isinstance(pivot_result, pd.DataFrame) and not pivot_result.empty:
                    csv = pivot_result.reset_index().to_csv(index=False)
                    st.download_button(
                        label="Download Pivot Table as CSV",
                        data=csv,
                        file_name='pivot_table.csv',
                        mime='text/csv',
                    )
                    
                # Show filtered data preview in an expander
                with st.expander("View Filtered Data", expanded=False):
                    st.dataframe(filtered_df.head(20), use_container_width=True)
                    st.caption(f"Showing first 20 of {len(filtered_df)} filtered rows")
        except Exception as e:
            st.error(f"Failed to create pivot table: {str(e)}")
            # Show the filtered data on error
            st.subheader("Filtered Data Preview")
            st.dataframe(filtered_df.head(20), use_container_width=True)
else:
    st.info("Please upload a CSV file or use the sample data to get started.")