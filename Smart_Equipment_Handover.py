# region - Login credentials
# cd Desktop\CODING\PROJECTS\Python\Smart-Equipment-Handover
# streamlit run Smart_Equipment_Handover.py
# endregion

# region - Library Import
import streamlit as st
import pandas as pd
import os
import datetime as datetime
from datetime import date
from datetime import date, datetime
import plotly.express as px
from streamlit_option_menu import option_menu
from supabase import create_client, ClientOptions
from dotenv import load_dotenv
# endregion

# region - Supabase Initialization
st.set_page_config(page_title="EMERSON ERP", layout="wide")
load_dotenv()
@st.cache_resource
def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    # Increase timeout to 60 seconds for hotspot stability
    opts = ClientOptions(postgrest_client_timeout=60) 
    return create_client(url, key, options=opts)

supabase = get_supabase()
# endregion

# region - Supabase Database Integrity / Exrtra Functions
# @st.cache_resource
# def get_supabase_Client():
#     return create_client(url, key)

# supabase = get_supabase_Client()

# Maintenance Record
@st.cache_data(ttl=600)
def get_todos():
    response = supabase.table("maintenance_data").select("*").execute()
    return response.data
def add_todo():
    response = supabase.table("maintenance_data").insert(ticket_data).execute()
    return response

# Self-Inspection Record
@st.cache_data(ttl=600)
def self_inspection():
    response = supabase.table("self_inspection_data").select("*").execute()
    return response.data
def add_self_inspection(inspect):
    response = supabase.table("self_inspection_data").insert(new_data).execute()
    return response

# Customer Master Record
@st.cache_data(ttl=600)
def cus_master():
    response = supabase.table("customer_master").select("*").execute()
    return response.data
def add_cus_master(customer):
    response = supabase.table("customer_master").insert(customer_data).execute()
    return response

# Customer ID Unique code:-
def get_next_cus_code():
    try:
        response = supabase.rpc("generate_next_cus_code").execute()
        return response.data
    except Exception as e:
        return ("CUS-100")


# Item Master Record
@st.cache_data(ttl=600)
def item_master():
    response = supabase.table("item_master").select("*").execute()
    return response.data
def add_item_master(item):
    response = supabase.table("item_master").insert(item_data).execute()
    return response

# Item Unique Code:-
def generate_item_code(category, description):
    if not category or not description:
        return ""

    # 1. Category Mapping
    cat_map = {
        "Consumable": "CN",
        "Finish good": "FG",
        "Raw Material": "RM"
    }
    prefix_cat = cat_map.get(category, "XX")

    # 2. Extract Initials from Description
    # Example: "Industrial Grade Lubricant" -> "IGL"
    words = description.split()
    initials = "".join([word[0].upper() for word in words if word])
    
    # Base prefix for DB lookup
    search_prefix = f"{prefix_cat}-{initials}-"

    try:
        # 3. Get Sequence from Supabase
        response = supabase.rpc("get_next_item_sequence", {"p_prefix": search_prefix}).execute()
        sequence_num = response.data if response.data else 1
        
        # 4. Format final code (e.g., CN-IGL-01)
        return f"{search_prefix}{str(sequence_num).zfill(2)}"
    except Exception as e:
        st.error(f"Error generating code: {e}")
        return f"{search_prefix}01"

# BOM Master Record
@st.cache_data(ttl=600)
def bom_master():
    response = supabase.table("bom_master").select("*").execute()
    return response.data
def add_bom_master(item):
    response = supabase.table("bom_master").insert(parent_data).execute()
    return response

# Full BOM View Record
@st.cache_data(ttl=600)
def full_bom_view():
    response = supabase.table("full_bom_view").select("*").execute()
    return response.data

# BOM Unique Code:-
def get_next_bom_id():
    try:
        # Fixed typo from .excecute() to .execute()
        response = supabase.rpc("generate_next_bom_code").execute()
        return response.data
    except Exception as e:
        print(f"BOM ID Error: {e}") # This will show in your terminal/logs
        return "BO-AA-01"


# Sales Order Record
@st.cache_data(ttl=600)
def so_data():
    response = supabase.table("sales_order").select("*").execute()
    return response.data
def add_so_data(item):
    response = supabase.table("sales_order").insert(SO_data).execute()
    return response

# SO Unique code:-
def get_next_SO_code():
    response = supabase.table("sales_order").select("Sales_Order").order("Sales_Order", desc=True).limit(1).execute()
    if response.data:
        last_code = response.data[0]["Sales_Order"]
        parts = last_code.split('-')
        num = int(parts[2]) + 1
        return f"SO-AA-{num:03d}"
    return "SO-AA-001"

# Machine Master
@st.cache_data(ttl=600)
def machine_data():
    response = supabase.table("machine_master").select("*").execute()
    return response.data
def add_machine_data(item):
    response = supabase.table("machine_master").insert(mc_data).execute()
    return response

# Machine ID Unique code:-
def get_next_mc_code():
    try:
        response = supabase.rpc("generate_next_mc_code").execute()
        return response.data
    except Exception as e:
        return ("MAC-01")

# Process Master
@st.cache_data(ttl=600)
def process_data():
    response = supabase.table("process_master").select("*").execute()
    return response.data
def add_process_data(item):
    response = supabase.table("process_master").insert(item).execute()
    return response

# Process ID Unique code:-
def get_next_pr_code():
    try:
        # Call the SQL function we just created
        response = supabase.rpc("generate_next_pr_code").execute()
        return response.data
    except Exception as e:
        st.error(f"Error generating Process ID: {e}")
        return "PR-001" # Fallback

# Work Order Master
@st.cache_data(ttl=600)
def wo_data():
    response = supabase.table("work_order_master").select("*").execute() 
    return response.data
def add_wo_data(item):
    response = supabase.table("work_order_master").insert(item).execute()
    return response

def get_next_wo_code():
    try:
        # Call the SQL function we just created
        response = supabase.rpc("generate_next_wo_code").execute()
        return response.data
    except Exception as e:
        st.error(f"Error generating Process ID: {e}")
        return "PR-001" # Fallback
    
# Purchase Request Unique code:-
def get_next_pr_code_preview():
    # Fetch the latest code by sorting descending
    # We remove the length() function to avoid the APIError
    res = supabase.table("pr_master")\
          .select("purchase_code")\
          .order("purchase_code", desc=True)\
          .limit(1).execute()
    
    if not res.data:
        return "PR-AA-01"
    
    last_code = res.data[0]['purchase_code']
    
    # Use regex to find the number at the end
    import re
    match = re.search(r"(\d+)$", last_code)
    if match:
        num_str = match.group(1)
        prefix = last_code[:last_code.rfind(num_str)]
        next_num = int(num_str) + 1
        
        # Maintain the padding (e.g., 01, 02)
        return f"{prefix}{str(next_num).zfill(len(num_str))}"
    
    return "PR-AA-01"
#endregion

# region - Authentication Setup
if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.role is None:
    st.title("🛡️ EMERSON ERP Login")
    
    with st.form("login_form"):
        user_id = st.text_input("User ID (EMR1)")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", type="primary")

        if submit:
            try:
                # Query your registry table
                res = supabase.table("user_registry").select("*").match({"user_id": user_id, "user_password": password}).execute()
                
                if res.data:
                    st.session_state.role = res.data[0]["role"]
                    st.session_state.accessible_tabs = res.data[0]["accessible_tabs"]
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
            except Exception as e:
                st.error(f"Hotspot Timeout: {e}. Try again in a moment.")
else:
    # 4. DASHBOARD (Sequence: Home -> Access Control)
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"role": None}))
    
    icon_map = {
        "Home": "",
        "Master File": "", 
        "Production": "", 
        "Sales": "",               
        "Planning": "",        
        "Inventory": "",                
        "Procurement": "",              
        "S&H": "",                 
        "Dashboard": "",       
        "Access Control": ""
    }
    
    # Filter and Sort based on the map above
    user_tabs = st.session_state.get("accessible_tabs", ["Home"])
    available = [t for t in icon_map.keys() if t in user_tabs]
    
    selected = st.selectbox("Navigate", options=available, format_func=lambda x: f"{icon_map.get(x, "*")} {x}")
    st.write(f"Displaying {selected}")
    

# endregion        

# region - Self inspection report (Machine Configuration)
    st.sidebar.title(f"USER: {st.session_state.role.upper()}")

    machine_config = {
        "Molding Machine 1": [
            ("Top Heating Coil Temp", "top_heat"),
            ("Bottom Heating Coil Temp", "bot_heat"),
            ("Molding Die Clamping Pressure", "clamp_pres"),
            ("Wire Stripping Pressure Reading", "strip_pres")
        ],
        "Molding Machine 2": [
            ("Top Heating Coil Temp", "top_heat"),
            ("Bottom Heating Coil Temp", "bot_heat"),
            ("Molding Die Clamping Pressure", "clamp_pres"),
            ("Wire Stripping Pressure Reading", "strip_pres")
        ],
        "Hot Stamping M/C 1": [
            ("Top Heating Coil Temp", "top_heat"),
            ("Bottom Heating Coil Temp", "bot_heat"),
            ("Top Pnuematic Cylinder Pressure", "top_cylinder"),
            ("Bottom Pnuematic Cylinder Pressure", "bottom_cylinder"),
            ("LUX Index", "LUX")
        ],
        "Hot Stamping M/C 2": [
            ("Top Heating Coil Temp", "top_heat"),
            ("Bottom Heating Coil Temp", "bot_heat"),
            ("Top Pnuematic Cylinder Pressure", "top_cylinder"),
            ("Bottom Pnuematic Cylinder Pressure", "bottom_cylinder"),
            ("LUX Index", "LUX")
        ],
        "Terminal Clamping Machine": [
            ("Pneumatic Cylinder Pressure", "cylinder_pressure"),
            ("LUX Index", "LUX"),
        ],
        "Cliping Station 1": [
            ("Pneumatic Cylinder Pressure", "cylinder_pressure"),
            ("LUX Index", "LUX"),
        ],
        "Cliping Station 2": [
            ("Pneumatic Cylinder Pressure", "cylinder_pressure"),
            ("LUX Index", "LUX"),
        ],
        "Bar Code M/C": [
            ("Pneumatic Cylinder Pressure", "cylinder_pressure"),
            ("LUX Index", "LUX"),
        ]
    }
# endregion
    
# region - Master Files    
    if selected == "Home":
        pass

    elif selected == "Master File":
        with st.sidebar:
            menu = st.radio("Menu", ["Machine Master", "Process Master", "Work Order Master"])

# region - Master File >> Machine Master 
        
        if menu == "Machine Master":
            tab1, tab2, tab3 = st.tabs(["Add Machine", "Machine Database", "📝"])

            with tab1:
        
                default_specs = [
                    {"parameter": "Power", "Value": ""},
                    {"parameter": "Power", "Value": ""},
                    {"parameter": "Power", "Value": ""}
                ]

                mc_code = get_next_mc_code()

                if "editor_key" not in st.session_state:
                    st.session_state.editor_key = 0  # We use a number to make incrementing easy

                machine_id = st.text_input("Machine ID", value=mc_code, disabled=True, key="machine_id")
                machine_name = st.text_input("Machine Name", key="machine_name")
                category = st.selectbox("Category", ["CNC", "Milling", "Lathe", "Drilling", "Add New"], key="category")
                spec = st.data_editor(
                    default_specs,
                    num_rows = "dynamic",
                    column_config={
                        "parameter": st.column_config.TextColumn("Technical parameter"),
                        "Value": st.column_config.TextColumn("Specification Value")
                    }
                    )
                if st.button("Submit"):
                    if machine_id and machine_name:
                        mc_data = {
                            "Machine ID": machine_id,
                            "Machine Name": machine_name,
                            "Category": category,
                            "Specification": spec
                        }
                        
                        try:
                            add_machine_data(mc_data)
                            st.success(f"Machine, {machine_id}: {machine_name} is added in machine master")
                            st.rerun()
                        except Exception as e:
                            st.error(e)
                    else:
                        st.error("Please fill the form")
        
            with tab2:
                def format_specs(spec_list):
                    """Converts raw JSON spec list into a readable string."""
                    if not spec_list or not isinstance(spec_list, list):
                        return ""
                    # Join each parameter and value with a colon, then join rows with a newline
                    return "\n".join([f"{item.get('parameter', '')}: {item.get('Value', '')}" for item in spec_list])
                # Toolbar for Sync and Search
                db_col1, db_col2 = st.columns([1, 3])
                with db_col1:
                    if st.button("Sync Machines"):
                        st.cache_data.clear()
                        st.rerun()
                
                try:
                    # 1. Fetch data from Supabase machine_master table
                    # Using the function you already defined or direct call
                    machine_res = supabase.table("machine_master").select("*").execute()
                    machine_db_data = machine_res.data

                    if not machine_db_data:
                        st.info("The machine database is currently empty.")
                    else:
                        df_machine = pd.DataFrame(machine_db_data)

                        # 2. Define column order based on your database structure
                        column_order = ["Machine ID", "Machine Name", "Category", "Specification"]
                        
                        # Filter only columns that exist in the dataframe
                        df_machine = df_machine[[col for col in column_order if col in df_machine.columns]]

                        # 3. Search Filter Logic
                        with db_col2:
                            search_term = st.text_input("Search Machine Name or ID", placeholder="Search", key="machine_search")

                        if search_term:
                            # Filter by ID or Name
                            df_machine = df_machine[
                                df_machine['Machine Name'].str.contains(search_term, case=False, na=False) |
                                df_machine['Machine ID'].str.contains(search_term, case=False, na=False)
                            ]
                        
                        if 'Specification' in df_machine.columns:
                            df_machine['Technical Specs'] = df_machine['Specification'].apply(format_specs)

                        # 4. Display Dataframe with Specific Configuration
                        st.dataframe(
                            df_machine, 
                            use_container_width=True, 
                            hide_index=True,
                            column_config={
                                "Machine ID": st.column_config.TextColumn("Machine ID"),
                                "Machine Name": st.column_config.TextColumn("Machine Name"),
                                "Category": st.column_config.TextColumn("Category"),
                                "Specification": st.column_config.TextColumn("Specifications", help="Technical details")
                            },

                        column_order=("Machine ID", "Machine Name", "Category", "Technical Specs")

                        )
                        
                        # Quick Statistics
                        st.caption(f"Showing {len(df_machine)} registered machines")

                except Exception as e:
                    st.error(f"Error loading machine database: {e}")
            
            with tab3:
                try:
                    # 1. Fetch data from machine_master table
                    machines_res = supabase.table("machine_master").select("*").execute()
                    machines_data = machines_res.data

                    if not machines_data:
                        st.info("No machines found in the database.")
                    else:
                        # Create a map for the selectbox
                        machine_map = {f"{m['Machine ID']} - {m['Machine Name']}": m for m in machines_data}
                        selected_m_key = st.selectbox("Select Machine to Edit", options=list(machine_map.keys()), key="edit_mc_select")
                        curr_mc = machine_map[selected_m_key]

                        st.markdown("---")
                        ec1, ec2 = st.columns(2)
                        
                        with ec1:
                            # Primary key is disabled to prevent database errors
                            edit_id = st.text_input("Machine ID", value=curr_mc['Machine ID'], disabled=True)
                            edit_name = st.text_input("Machine Name", value=curr_mc['Machine Name'])
                        
                        with ec2:
                            # Pre-select the current category
                            categories = ["CNC", "Milling", "Lathe", "Drilling", "Add New"]
                            current_cat_index = categories.index(curr_mc['Category']) if curr_mc['Category'] in categories else 0
                            edit_cat = st.selectbox("Category", options=categories, index=current_cat_index)

                        st.write("### Edit Technical Specifications")
                        # Use data_editor to allow editing the JSON specification
                        edit_spec = st.data_editor(
                            curr_mc['Specification'], 
                            num_rows="dynamic",
                            key=f"edit_editor_{curr_mc['Machine ID']}", # Unique key for this machine
                            use_container_width=True
                        )

                        st.markdown("---")
                        eb_col1, eb_col2 = st.columns([1,1])

                        with eb_col1:
                            if st.button("UPDATE MACHINE", type="primary"):
                                updated_mc_payload = {
                                    "Machine Name": edit_name,
                                    "Category": edit_cat,
                                    "Specification": edit_spec # Updated JSON list
                                }
                                # Update Supabase using Machine ID as the filter
                                supabase.table("machine_master").update(updated_mc_payload).eq("Machine ID", curr_mc['Machine ID']).execute()
                                st.success(f"Machine '{edit_id}' updated successfully!")
                                st.rerun()

                        with eb_col2:
                            if st.button("DELETE MACHINE", type="secondary"):
                                # Delete from Supabase
                                supabase.table("machine_master").delete().eq("Machine ID", curr_mc['Machine ID']).execute()
                                st.warning(f"Machine '{edit_id}' has been removed.")
                                st.rerun()

                except Exception as e:
                    st.error(f"Error handling Machine Master: {e}")

# endregion

# region - Master File >> Process Master
    
        elif menu == "Process Master":

            # 1. Initialize Session State for the dynamic table
            if "process_editor_key" not in st.session_state:
                st.session_state.process_editor_key = 0

            # 2. Define Default Parameters (Standard set points)
            default_parameters = [
                {"Parameter": "Pressure", "Value": "", "Unit": "Bar"},
                {"Parameter": "Temperature", "Value": "", "Unit": "°C"},
                {"Parameter": "Speed", "Value": "", "Unit": "RPM"}
            ]

            if menu == "Process Master":
                tab1, tab2, tab3 = st.tabs(["Add Process", "Process Database", "📝"])

                with tab1:
                    st.subheader("Create New Process")
                
                    # Fetch the next Process ID (e.g., PR-001)
                    # Ensure you have a function 'get_next_pr_code' similar to 'get_next_mc_code'
                    pr_code = get_next_pr_code() 

                    # --- Layout for Basic Details ---
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        process_id = st.text_input("Process ID", value=pr_code, disabled=True)
                        process_name = st.text_input("Process Name", placeholder="e.g. Rough Turning", key="input_pr_name")
                        department = st.selectbox("Department", ["Production", "Quality", "Maintenance", "Assembly"], key="input_pr_dept")
                    
                    with col2:
                        # Link to Machine Categories from Machine Master
                        machine_cat = st.selectbox("Machine Category", ["CNC", "Milling", "Lathe", "Drilling", "Grinding"], key="input_pr_mc_cat")
                        cycle_time = st.number_input("Cycle Time (Minute)", min_value=0, help="Total time to complete one process per job", key="input_pr_cycle")
                    
                    process_desc = st.text_area("Process Description", placeholder="Describe the steps involved...", key="input_pr_desc")

                    # --- Layout for Parameters Table ---
                    st.subheader("Process Parameters")
                    st.caption("Define the standard operating conditions for this process.")
                    
                    param_table = st.data_editor(
                        default_parameters,
                        num_rows="dynamic",
                        key=f"pr_params_{st.session_state.process_editor_key}",
                        use_container_width=True,
                        column_config={
                            "Parameter": st.column_config.TextColumn("Standard Parameter"),
                            "Value": st.column_config.TextColumn("Actual Value"),
                            "Unit": st.column_config.TextColumn("Unit")
                            
                        }
                    )

                    # --- Submission Logic ---
                    if st.button("Submit Process", type="primary"):
                        if process_name and department and cycle_time and param_table:
                            process_payload = {
                                "Process ID": process_id,
                                "Process Name": process_name,
                                "Description": process_desc,
                                "Department": department,
                                "Machine Category": machine_cat,
                                "Cycle Time": cycle_time,
                                "Parameters": param_table  # Saves as JSON array
                            }
                            
                            try:
                                # Assuming your Supabase table is named 'process_master'
                                add_process_data(process_payload)
                                st.success(f"✅ Process {process_id}: {process_name} added successfully!")
                                                               
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Database Error: {e}")
                        else:
                            st.warning("⚠️ Please fill in the Process Name and Department.")
                with tab2:
                    # Toolbar for Sync and Search
                    db_col1, db_col2 = st.columns([1, 3])
                    with db_col1:
                        if st.button("Sync"):
                            st.cache_data.clear()
                            st.rerun()
                    
                    try:
                        # 1. Fetch data from Supabase 
                        pr_res = process_data()
                        pr_db_data = pr_res

                        if not pr_db_data:
                            st.info("The process database is currently empty.")
                        else:
                            df_pr = pd.DataFrame(pr_res)

                            # 2. Formatting Function for Parameters
                            def format_params(param_list):
                                if not param_list or not isinstance(param_list, list):
                                    return "No Parameters"
                                # Formats as: "Pressure: 10 Bar, Temperature: 50 °C"
                                return " | ".join([f"{p.get('Parameter')}: {p.get('Value')} {p.get('Unit')}" for p in param_list])

                            # Apply the formatting to a new display column
                            df_pr['Formatted Parameters'] = df_pr['Parameters'].apply(format_params)

                            # 3. Search Filter
                            with db_col2:
                                pr_search = st.text_input("Search", placeholder="Search by Name, ID, or Department...", key="pr_search_bar")

                            if pr_search:
                                df_pr = df_pr[
                                    df_pr['Process Name'].str.contains(pr_search, case=False, na=False) |
                                    df_pr['Process ID'].str.contains(pr_search, case=False, na=False) |
                                    df_pr['Department'].str.contains(pr_search, case=False, na=False)
                                ]

                            # 4. Display the Dataframe 
                            st.dataframe(
                                df_pr,
                                use_container_width=True,
                                hide_index=True,
                                column_order=("Process ID", "Process Name", "Department", "Machine Category", "Cycle Time", "Formatted Parameters"),
                                column_config={
                                    "Process ID": st.column_config.TextColumn("Process ID"),
                                    "Process Name": st.column_config.TextColumn("Process Name"),
                                    "Cycle Time": st.column_config.NumberColumn("Cycle (min)", format="%d min"),
                                    "Formatted Parameters": st.column_config.TextColumn("Standard Set Points", width="large")
                                }
                            )

                    except Exception as e:
                        st.error(f"Error loading process database: {e}")
                
                with tab3:
                    try:
                        # 1. Fetch current processes from Supabase
                        processes_res = supabase.table("process_master").select("*").execute() 
                        processes_data = processes_res.data

                        if not processes_data:
                            st.info("No processes found to edit.")
                        else:
                            # Create a searchable dropdown
                            process_map = {f"{p['Process ID']} - {p['Process Name']}": p for p in processes_data}
                            selected_pr_key = st.selectbox("Select Process to Edit/Delete", options=list(process_map.keys()), key="edit_pr_select")
                            curr_pr = process_map[selected_pr_key]

                            st.markdown("---")
                            
                            # 2. Form for Editing
                            ec1, ec2 = st.columns(2)
                            with ec1:
                                edit_pr_id = st.text_input("Process ID", value=curr_pr['Process ID'], disabled=True)
                                edit_pr_name = st.text_input("Process Name", value=curr_pr['Process Name'])
                                edit_dept = st.selectbox("Department", 
                                                        ["Production", "Quality", "Maintenance", "Assembly"],
                                                        index=["Production", "Quality", "Maintenance", "Assembly"].index(curr_pr['Department']) if curr_pr['Department'] in ["Production", "Quality", "Maintenance", "Assembly"] else 0)
                            
                            with ec2:
                                # Get current machine category index
                                mc_cats = ["CNC", "Milling", "Lathe", "Drilling", "Grinding"]
                                current_mc_idx = mc_cats.index(curr_pr['Machine Category']) if curr_pr['Machine Category'] in mc_cats else 0
                                edit_mc_cat = st.selectbox("Machine Category", options=mc_cats, index=current_mc_idx)
                                
                                edit_cycle = st.number_input("Cycle Time (Minute)", value=int(curr_pr['Cycle Time']), min_value=0)

                            edit_desc = st.text_area("Description", value=curr_pr['Description'])

                            st.subheader("Edit Parameters")
                            # Dynamic editor for JSON parameters
                            edit_params = st.data_editor(
                                curr_pr['Parameters'], 
                                num_rows="dynamic",
                                key=f"edit_pr_editor_{curr_pr['Process ID']}",
                                use_container_width=True
                            )

                            st.markdown("---")
                            # 3. Action Buttons
                            btn_col1, btn_col2 = st.columns([1, 1])

                            with btn_col1:
                                if st.button("UPDATE PROCESS", type="primary"):
                                    updated_payload = {
                                        "Process Name": edit_pr_name,
                                        "Description": edit_desc,
                                        "Department": edit_dept,
                                        "Machine Category": edit_mc_cat,
                                        "Cycle Time": edit_cycle,
                                        "Parameters": edit_params # Saves updated JSON list
                                    }
                                    supabase.table("process_master").update(updated_payload).eq("Process ID", curr_pr['Process ID']).execute()
                                    st.success(f"Process '{edit_pr_id}' updated successfully!")
                                    st.rerun()

                            with btn_col2:
                                # Add a simple double-check for deletion
                                if st.checkbox(f"Confirm to Delete {edit_pr_id}"):
                                    if st.button("DELETE PROCESS", type="secondary"):
                                        supabase.table("process_master").delete().eq("Process ID", curr_pr['Process ID']).execute()
                                        st.warning(f"Process '{edit_pr_id}' has been deleted.")
                                        st.rerun()

                    except Exception as e:
                        st.error(f"Error managing Process Master: {e}")

# endregion

# region - Master File >> Work Order Master
        elif menu == "Work Order Master": 

            tab1, tab2, tab3 = st.tabs(["Add WO", "WO Database", "📝"])

            with tab1:
                st.subheader("Create Work Order")
                
                # Auto-generate WO ID
                wo_id_code = get_next_wo_code()

                # --- Section 1: Basic Details ---
                col1, col2 = st.columns(2)
                with col1:
                    wo_id = st.text_input("Work Order ID", value=wo_id_code, disabled=True)
                    project_name = st.text_input("Work Order Name", placeholder="e.g. Engine Components")
                with col2:
                    wo_desc = st.text_area("WO Description", placeholder="General overview of this standard process...")

                # --- Section 2: Routing (From Process Master) ---
                st.subheader("Process Sequence")
                # Fetch processes for the dropdown
                process_data = supabase.table("process_master").select('"Process Name"', '"Cycle Time"').execute().data
                process_options = [p['Process Name'] for p in process_data]
                cycle_map = {p['Process Name']: p['Cycle Time'] for p in process_data}

                # Fetch Machines (Combined ID and Name)
                machine_res = supabase.table("machine_master").select('"Machine ID"', '"Machine Name"').execute()
                # Create a list like ["MAC-001 | 5-Axis CNC", "MAC-002 | Boring Mill", ...]
                machine_options = [f"{m['Machine ID']} | {m['Machine Name']}" for m in machine_res.data]

                routing_editor = st.data_editor(
                    [{"Step": 1, "Process": "", "Department": "Production", "Assigned Machine": "", "Notes": ""}],
                    num_rows="dynamic",
                    use_container_width=True,
                    key="wo_routing_editor",
                    column_config={
                        "Step": st.column_config.NumberColumn("Squence"),
                        "Process": st.column_config.SelectboxColumn("Process Name", options=process_options),
                        "Department": st.column_config.SelectboxColumn("Department", options=["Production", "Quality", "Maintenance", "Assembly"]),
                        "Assigned Machine": st.column_config.SelectboxColumn(
                            "Machine (ID | Name)", 
                            options=machine_options, 
                            width="large",
                            help="Select the specific machine for this operation"
                        ),
                        "Notes": st.column_config.TextColumn("Notes")
                    }
                )

                # Calculate Total Lead Time based on Cycle Times in Process Master
                total_seconds = sum([cycle_map.get(row['Process'], 0) for row in routing_editor if row['Process']])
                total_hrs = round(total_seconds/60, 2) if total_seconds > 0 else 0.0
                st.write(f"⏱️ **Standard Lead Time:** {total_hrs} Hours (Calculated from Process Master)")

                # --- Section 3: Specialized Notes ---
                st.write("---")
                n_col1, n_col2, n_col3 = st.columns(3)
                
                with n_col1:
                    st.caption("🔍 Quality Notes")
                    q_notes = st.data_editor([{"Note": ""}], num_rows="dynamic", key="q_notes", use_container_width=True)
                
                with n_col2:
                    st.caption("🛠️ Manufacturing Notes")
                    m_notes = st.data_editor([{"Note": ""}], num_rows="dynamic", key="m_notes", use_container_width=True)
                    
                with n_col3:
                    st.caption("📝 General Notes")
                    g_notes = st.data_editor([{"Note": ""}], num_rows="dynamic", key="g_notes", use_container_width=True)

                # --- Submission ---
                if st.button("Save WO Template", type="primary"):
                    payload = {
                        "WO ID": wo_id,
                        "Project": project_name,
                        "Description": wo_desc,
                        "Routing": routing_editor,
                        "Quality Notes": q_notes,
                        "Manufacturing Notes": m_notes,
                        "General Notes": g_notes,
                        "Total Lead Time Hrs": total_hrs
                    }
                    try:
                        add_wo_data(payload)
                        st.success(f"Standard WO {wo_id} saved!")
                        st.rerun()
                    except Exception as e:
                        st.error(e)

            
            with tab2:

                # Function to convert JSON notes into clean readable text
                def format_notes_vertically(notes_list):
                    if not notes_list or not isinstance(notes_list, list):
                        return "No notes added."
                    
                    # Extract the text and filter out empty entries
                    clean_items = [item['Note'] for item in notes_list if item.get('Note') and item['Note'].strip() != ""]
                    
                    if not clean_items:
                        return "No notes added."
                    
                    # Join with double newline for true vertical spacing in Markdown
                    return "\n\n".join([f"• {text}" for text in clean_items])
                
                # 1. Fetch all WO Templates
                try:
                    if st.button("Sync"):
                            st.cache_data.clear()
                            st.rerun()

                    wo_res = supabase.table("work_order_master").select("*").execute()
                    if not wo_res.data:
                        st.info("No Standard Work Orders found.")
                    else:
                        df_wo = pd.DataFrame(wo_res.data)

                        # --- SECTION 1: DETAILED PREVIEW (Now at the top) ---
                        st.subheader("🔍 Work Order Preview")
                        selected_wo_id = st.selectbox("Select WO to view details", options=df_wo["WO ID"].tolist())
                        
                        if selected_wo_id:
                            wo_detail = next(item for item in wo_res.data if item["WO ID"] == selected_wo_id)
                            
                            # Header Info
                            p_col1, p_col2 = st.columns(2)
                            p_col1.metric("Project", wo_detail["Project"])
                            p_col2.metric("Est. Duration", f"{wo_detail['Total Lead Time Hrs']} Hrs")
                            
                            # Display Routing
                            st.write("**Operation Sequence:**")
                            st.table(wo_detail["Routing"])
                            
                            # Display Notes in 3 columns
                            n1, n2, n3 = st.columns(3)
                            with n1:
                                st.markdown("🔍 **Quality Notes**")
                                with st.container(border=True):
                                    formatted_q = format_notes_vertically(wo_detail.get("Quality Notes"))
                                    st.markdown(formatted_q)

                            with n2:
                                st.markdown("🛠️ **Manufacturing Notes**")
                                with st.container(border=True):
                                    formatted_m = format_notes_vertically(wo_detail.get("Manufacturing Notes"))
                                    st.markdown(formatted_m)
                                    
                            with n3:
                                st.markdown("📝 **General Notes**")
                                with st.container(border=True):
                                    formatted_g = format_notes_vertically(wo_detail.get("General Notes"))
                                    st.markdown(formatted_g)

                        st.write("---")

                        # --- SECTION 2: SUMMARY TABLE (Now at the bottom) ---
                        st.subheader("📋 All Registered Templates")
                        st.dataframe(
                            df_wo[["WO ID", "Project", "Description", "Total Lead Time Hrs"]],
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Total Lead Time Hrs": st.column_config.NumberColumn("Lead Time", format="%.2f Hrs")
                            }
                        )

                except Exception as e:
                    st.error(f"Error loading repository: {e}")
                    
            with tab3:
                st.subheader("🛠️ Edit / Delete Standard WO")
                
                if not wo_res.data:
                    st.info("No templates available to edit.")
                else:
                    # Selection
                    edit_target = st.selectbox("Select Template to Modify", options=df_wo["WO ID"].tolist(), key="edit_wo_select")
                    edit_data = next(item for item in wo_res.data if item["WO ID"] == edit_target)

                    # Edit Fields
                    e_col1, e_col2 = st.columns(2)
                    with e_col1:
                        u_project = st.text_input("Project Name", value=edit_data["Project"])
                    with e_col2:
                        u_desc = st.text_area("Description", value=edit_data["Description"])

                    # Edit Routing
                    st.write("### Edit Routing")
                    u_routing = st.data_editor(edit_data["Routing"], num_rows="dynamic", key=f"u_route_{edit_target}", use_container_width=True)

                    # Edit Notes
                    en1, en2, en3 = st.columns(3)
                    with en1:
                        st.caption("Quality Notes")
                        u_q = st.data_editor(edit_data["Quality Notes"], num_rows="dynamic", key=f"u_q_{edit_target}")
                    with en2:
                        st.caption("Manufacturing Notes")
                        u_m = st.data_editor(edit_data["Manufacturing Notes"], num_rows="dynamic", key=f"u_m_{edit_target}")
                    with en3:
                        st.caption("General Notes")
                        u_g = st.data_editor(edit_data["General Notes"], num_rows="dynamic", key=f"u_g_{edit_target}")

                    # Action Buttons
                    st.write("---")
                    btn_u, btn_d = st.columns([1, 4])
                    
                    with btn_u:
                        if st.button("Update Template", type="primary"):
                            # Recalculate lead time
                            u_seconds = sum([cycle_map.get(r['Process'], 0) for r in u_routing if r.get('Process')])
                            u_hrs = round(u_seconds/3600, 2)
                            
                            u_payload = {
                                "Project": u_project,
                                "Description": u_desc,
                                "Routing": u_routing,
                                "Quality Notes": u_q,
                                "Manufacturing Notes": u_m,
                                "General Notes": u_g,
                                "Total Lead Time Hrs": u_hrs
                            }
                            supabase.table("work_order_master").update(u_payload).eq("WO ID", edit_target).execute()
                            st.success(f"WO {edit_target} updated!")
                            st.rerun()
                    
                    with btn_d:
                        if st.checkbox(f"Confirm Delete {edit_target}"):
                            if st.button("Confirm Permanent Delete"):
                                supabase.table("work_order_master").delete().eq("WO ID", edit_target).execute()
                                st.warning(f"Template {edit_target} removed.")
                                st.rerun()

# endregion

# endregion
 
# region - Self Inspection report page
    # PAGE 1 - New Inspection
    elif selected == "Production":

        with st.sidebar:
            menu = st.radio("Menu", ["Machine Inspection Report", "Breakdown Ticket"])

        if menu == "Machine Inspection Report":
            st.subheader("📋 Machine Self Inspection Report")
            st.write("Note: Machine self inspection report should be filled by the operator before staring the shift. All the information should be filled after verifing readings physically")

            col1, col2 = st.columns(2)

            with col1:
                operator = st.text_input("Operator Name")
                shift = st.selectbox("Shift", ["1st Shift", "2nd Shift", "3rd Shift"])

            with col2:
                machine = st.selectbox("Machine ID", list(machine_config.keys()))
                date = st.date_input("Select a date", datetime.date.today())
            

            st.divider()

            st.subheader(f"{machine} Parameter")

            params = machine_config.get(machine, [])

            input_values = []
            machine_value = {}

            for i, (label, suffix) in enumerate (params):
                val = st.number_input(label, key=f"{machine}_{suffix}", value=0, min_value = 0)
                input_values.append(val)
                machine_value[label] = val

            kk = "N/A"

            if "Molding" in machine:
                kk = st.radio("Molding Die Visual Inspection", ["OK", "NOT-OK"], horizontal=True)

            sub_button = st.button("Submit Report", disabled = is_operator)

            if sub_button:
                    if all(v > 0 for v in input_values) and operator:
                        st.success("Report subitted")
                    else:
                        st.error("Please fill all values")

                
            if sub_button:
                clean_date = date.isoformat()
                new_data = {
                    "operator": operator,
                    "shift": shift,
                    "machine_id": machine,
                    "date": date.isoformat(),
                    "top_heating_coil_temp": machine_value.get("Top Heating Coil Temp"),
                    "bottom_heating_coil_temp": machine_value.get("Bottom Heating Coil Temp"),
                    "molding_die_clamping_pressure": machine_value.get("Molding Die Clamping Pressure"),
                    "wire_stripping_pressure": machine_value.get("Wire Stripping Pressure Reading"),
                    "top_pneumatic_cylinder_pressure": machine_value.get("Top Pnuematic Cylinder Pressure"),
                    "bottom_pneumatic_cylinder_pressure": machine_value.get("Bottom Pnuematic Cylinder Pressure"),
                    "lux_index": machine_value.get("LUX Index"),
                    "pneumatic_cylinder_pressure": machine_value.get("Pneumatic Cylinder Pressure"),
                    "molding_dei_visual_inspection": kk
                }

                try:
                    add_self_inspection(new_data)
                except Exception as e:
                    st.error(f"Error {e}")
# endregion

# region - Machine Breakdown report page
        elif menu == "Breakdown Ticket":
            st.header("Equipment Breakdown Ticket")
            st.write("Please fill below mentioned details to raise the ticket")
            col1, col2 = st.columns(2)

            with col1:
                dept_name = st.selectbox("Department Name", ["WSS", "ABS", "Machine Shop1", "Machine Shop2", "Inward 1", "Inward 2", "Packaging"])
                supervisor_name = st.text_input("Supervisor Name")
                operator_name = st.text_input("Operator Name")
                date1 = st.date_input("Select a date", datetime.date.today())
            
            with col2:
                shift1 = st.selectbox("Shift", ["1st Shift", "2nd Shift", "3rd Shift"])
                machine1 = st.selectbox("Machine ID", list(machine_config.keys()))
                time1 = st.text_input("Time", value=datetime.datetime.now().strftime("%H:%M"), disabled=True)
            
            des = st.text_input("Breakdown Description")   

            EBT = st.button("Submit") 

            if EBT:
                if supervisor_name and operator_name and des:
                    pass
                else:
                    st.error("Please fill the form")

            if EBT:
                if supervisor_name and operator_name and des:
                    clean_date1 = date1.isoformat()
                    ticket_data = {
                        "dept_name": dept_name,    
                        "supervisor": supervisor_name,
                        "date": date1.isoformat(), # Fixed the date error here
                        "shift": shift1,
                        "machine_id": machine1,    
                        "time": time1,
                        "description": des, # Ensure this column was added to the table
                        "operator": operator_name
                    }
                    st.success("Form Submitted")

                    try:
                        add_todo(ticket_data)
                    except Exception as e:
                        st.error(f"Error {e}")     
# endregion 

#region - Sales page (Customer Database)
    elif selected == "Sales":
        with st.sidebar:
            menu = st.radio("Menu", ["Customer Database", "Sales Order", "Work Order", "Product Mapping", "Sales Invoice", "Sales Return"])

        if menu == "Customer Database":
            st.subheader("Customer Database")

            tab1, tab2, tab3 = st.tabs(["Add Customer", "Customer DataBase", "📝"])
            next_cus_code = get_next_cus_code()

            with tab2:
                if st.button("Sync"):
                    st.cache_data.clear()
                    st.rerun()
                cus_s_data = cus_master()
                df = pd.DataFrame(cus_s_data)

                try:
                    st.dataframe(df)
                except:
                    st.error("Not data present")

            with tab1:
                with st.form("customer_form", clear_on_submit=True):
                    col1, col2 = st.columns(2)

                    with col1:
                        customer_id = st.text_input("Customer ID", value=next_cus_code, disabled=True)
                        customer_Name = st.text_input("Customer Name", key="customer_Name")
                        customer_number = st.text_input("Customer Number", max_chars = 10, key="customer_number")
                        cus_sector = st.selectbox("Sector", ["Automobile", "Defense", "Medical", "other"], key="cus_sector")

                    with col2:
                        cus_email = st.text_input("Email", key="cus_email")
                        cus_address = st.text_input("Address", key="cus_address")
                        cus_city = st.text_input("City", key="cus_city")
                        cus_gstno = st.text_input("GST No.", key="cus_gstno")
                    
                    submitted = st.form_submit_button("Submit")
                
                #cus_list = ()
                if submitted:
                    if all([ customer_Name, customer_number, cus_email, cus_address, cus_sector, cus_gstno, cus_city]):
                        customer_data = {
                            "customer_id": customer_id,
                            "Customer_Name": customer_Name,
                            "customer_number": customer_number,
                            "cus_sector": cus_sector,
                            "cus_email": cus_email,
                            "cus_address": cus_address,
                            "cus_city": cus_city,
                            "cus_gstno": cus_gstno
                        }
                        
                        try:
                            add_cus_master(customer_data)
                            st.success("Customer Added Successfully")
                            
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.error("Please fill the form")
                    st.rerun()
                        
            
            with tab3:
                st.write("Manage Existing Customer")

                select_cus = st.selectbox("Select Customer", df['Customer_Name'].unique())

                current_data = df[df['Customer_Name'] == select_cus].iloc[0]

                col1, col2 = st.columns(2)
                with col1:
                    cus_new_name = st.text_input("Customer Name", value = current_data['Customer_Name'])
                    cus_new_number = st.text_input("Customer ID", value = str(current_data['customer_id']), max_chars=10, disabled=True)
                    cus_new_gstno = st.text_input("GST No.", value=current_data['cus_gstno'])

                
                with col2:
                    cus_new_email = st.text_input("Customer Email", value=current_data['cus_email'])
                    cus_new_address = st.text_input("Address", value=current_data['cus_address'])
                    cus_new_city = st.text_input("City", value=current_data['cus_city'])
                
                edit_col, delete_col = st.columns([1,1])

                with edit_col:
                   if st.button("Update Customer"):
                         try:
                            # 1. This dictionary must be indented inside the try block
                            updated_info = {
                                "Customer_Name": cus_new_name,
                                "customer_number": cus_new_number,
                                "cus_email": cus_new_email,
                                "cus_address": cus_new_address,
                                "cus_city": cus_new_city,
                                "cus_gstno": cus_new_gstno
                            }
                            
                            # 2. This line MUST align perfectly with 'updated_info' above
                            response = supabase.table("customer_master").update(updated_info).eq("customer_id", current_data['customer_id']).execute()
                            
                            # 3. These must also align
                            st.success(f"Record for {cus_new_name} updated successfully")
                            # st.cache_data.clear() 
                            # st.rerun()
                            
                         except Exception as e:
                            st.error(f"Update fail: {e}")
                with delete_col:
                    if st.button("Delete Customer"):
                        try:
                            supabase.table("customer_master").delete().eq("customer_id", current_data['customer_id']).execute()
                            st.warning(f"Customer {cus_new_name} deleted")
                            # st.cache_data.clear()
                            # st.rerun()
                        except Exception as e:
                            st.error(f"Delete fail: {e}")
# endregion

# region - sales page (Sales Order)

        if menu == "Sales Order":
            st.subheader("Sales Order")

            tab1, tab2, tab3 = st.tabs(["New Order", "Order Database", "Order Tracking"])

# region - sales Order >> New Order
            with tab1:
                # Always generate fresh code (no session caching)
                current_so_code = get_next_SO_code()
                if not current_so_code:
                    st.stop()  # Stop if no code

                if "so_items_list" not in st.session_state:
                    st.session_state.so_items_list = []

                # Customer prep
                customer_master = cus_master()
                customer_names = [c["Customer_Name"] for c in customer_master]

                # Work Order perp
                wo_master = wo_data()
                wo_id = [c["WO ID"] for c in wo_master]

                col1, col2 = st.columns(2)

                with col1:
                    current_so_code = get_next_SO_code()
                    sales_order = st.text_input("Sales Order Number", value=current_so_code or "SO-AA-001", disabled=True)
                    booking_date = st.date_input("Booking Date", date.today())
                    cus_name = st.selectbox("Customer Name", options=customer_names)
                    sec_detail = next((item for item in customer_master if item["Customer_Name"] == cus_name), {})
                    customer_sector = st.text_input("Customer Sector", value=sec_detail.get("cus_sector", ""), disabled=True)
                    order_type = st.selectbox("Order Type", ["Project", "Schedule", "NPD", "HOLD"])

                with col2:
                    po_rec_date = st.date_input("PO Receive Date", date.today())
                    po_date = st.date_input("PO Date", date.today())
                    po_number = st.text_input("PO Number")
                    delivery_date = st.date_input("Delivery Date", date.today())
                    upload_file = st.file_uploader("Upload Document", type=["pdf", "docx", "png"])

                st.markdown("---")

                # Item popup
                @st.dialog("Add New Sales Item")
                def add_new_item_popup():
                    master_data = item_master()
                    finish_goods = [i for i in master_data if i.get("Category") == "Finish good"]
                    item_des_list = [i["Description"] for i in finish_goods]
                    selected_desc = st.selectbox("Select Item Description", options=item_des_list)
                    item_details = next((i for i in finish_goods if i["Description"] == selected_desc), {})
                    i_code = st.text_input("Item Code", value=item_details.get("Item_Code", ""), disabled=True)
                    work_order = st.selectbox("Work Order No.", options=wo_id,)
                    qty = st.number_input("Quantity", min_value=1.0)
                    rate = st.number_input("Rate", min_value=0.0)
                    if st.button("Add to List", type="primary"):
                        st.session_state.so_items_list.append({
                            "Item_Code": i_code, "Description": selected_desc, "WO": work_order,
                            "Qty": qty, "Rate": rate, "Total": qty * rate
                        })
                        st.rerun()

                if st.button("➕ Add Item"):
                    add_new_item_popup()

                if st.session_state.so_items_list:
                    df = pd.DataFrame(st.session_state.so_items_list)
                    st.table(df)
                    if st.button("🗑️ Clear All Items", type="secondary"):
                        st.session_state.so_items_list = []
                        st.rerun()
                else:
                    st.info("No items added yet.")

                st.markdown("---")

                if st.button("🚀 Submit Sales Order", type="primary", use_container_width=True):
                    if not po_number:
                        st.error("Please provide a Work Order Number.")
                    elif not st.session_state.so_items_list:
                        st.error("Add items first!")
                    else:
                        try:
                            # Parent insert (NO Document_URL)
                            SO_data = {
                                "Sales_Order": sales_order,
                                "Booking_Date": booking_date.isoformat(),
                                "Customer_ID": cus_name,
                                "Sector": customer_sector,
                                "Order_Type": order_type,
                                "PO_Recive_Date": po_rec_date.isoformat(),
                                "PO_Number": po_number or None,
                                "PO_Date": po_date.isoformat(),
                                "Delivery_Date": delivery_date.isoformat()
                            }
                            supabase.table("sales_order").insert(SO_data).execute()

                            # Child items
                            items_to_insert = []
                            for row in st.session_state.so_items_list:
                                items_to_insert.append({
                                    "SO_Number": sales_order,
                                    "Item_Code": row["Item_Code"],
                                    "Description": row["Description"],
                                    "Work Order": row["WO"] or None,
                                    "Qty": int(row["Qty"]),  # ← FIX: Convert to integer
                                    "Rate": float(row["Rate"])
                                })
                                supabase.table("sales_order_items").insert(items_to_insert).execute()

                            st.success(f"Saved Order {sales_order}!")
                            st.session_state.so_items_list = []
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                                
                
# endregion
# region - sales Order >> Order Database
            with tab2:
                def get_all_orders():
                    return supabase.table("sales_order").select("*").execute().data
                
                def delete_order(order_id):
                    try:
                        # 1. Delete child items first to avoid foreign key errors
                        supabase.table("sales_order_items").delete().eq("SO_Number", order_id).execute()
                        # 2. Delete the main order header
                        supabase.table("sales_order").delete().eq("Sales_Order", order_id).execute()
                        st.success(f"Order {order_id} deleted successfully!")
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Failed to delete order: {e}")

                @st.dialog("Edit Sales Order")
                def edit_order_dialog(order_data):
                    st.subheader(f"📝 Edit Order: {order_data['Sales_Order']}")
                    
                    # 1. Fetch Master Data for Selectboxes
                    customer_master = cus_master()
                    customer_names = [c["Customer_Name"] for c in customer_master]
                    
                    wo_master = wo_data()
                    wo_ids = [c["WO ID"] for c in wo_master]

                    # 2. Form Layout
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Customer Selection
                        current_cus = order_data.get("Customer_ID", "")
                        try:
                            cus_index = customer_names.index(current_cus)
                        except ValueError:
                            cus_index = 0
                            
                        new_cus_name = st.selectbox("Customer Name", options=customer_names, index=cus_index, key="new_cus_name")
                        
                        # Booking Date parsing
                        b_date = pd.to_datetime(order_data.get("Booking_Date")).date()
                        new_booking_date = st.date_input("Booking Date", value=b_date)
                        
                        # Order Type
                        o_types = ["Project", "Schedule", "NPD", "HOLD"]
                        try:
                            type_index = o_types.index(order_data.get("Order_Type", "Project"))
                        except ValueError:
                            type_index = 0
                        new_order_type = st.selectbox("Order Type", options=o_types, index=type_index, key="new_order_type")
                        
                        new_po_number = st.text_input("PO Number", value=order_data.get("PO_Number", ""))

                    with col2:
                        # Dates
                        pr_date = pd.to_datetime(order_data.get("PO_Recive_Date")).date()
                        new_po_rec_date = st.date_input("PO Receive Date", value=pr_date)
                        
                        p_date = pd.to_datetime(order_data.get("PO_Date")).date()
                        new_po_date = st.date_input("PO Date", value=p_date)
                        
                        d_date = pd.to_datetime(order_data.get("Delivery_Date")).date()
                        new_delivery_date = st.date_input("Delivery Date", value=d_date)
                        
                        # Sector (Auto-fetched based on selection)
                        sec_detail = next((item for item in customer_master if item["Customer_Name"] == new_cus_name), {})
                        new_sector = st.text_input("Customer Sector", value=sec_detail.get("cus_sector", ""), disabled=True, key="new_sector")

                    st.divider()
                    
                    # 3. Save Logic
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Save Changes", type="primary", use_container_width=True):
                            updated_payload = {
                                "Customer_ID": new_cus_name,
                                "Booking_Date": new_booking_date.isoformat(),
                                "Order_Type": new_order_type,
                                "PO_Number": new_po_number,
                                "PO_Recive_Date": new_po_rec_date.isoformat(),
                                "PO_Date": new_po_date.isoformat(),
                                "Delivery_Date": new_delivery_date.isoformat(),
                                "Sector": new_sector
                            }
                            
                            try:
                                supabase.table("sales_order").update(updated_payload).eq("Sales_Order", order_data['Sales_Order']).execute()
                                st.success("Sales Order Header Updated!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Update failed: {e}")
                                
                    with c2:
                        if st.button("Cancel", use_container_width=True):
                            st.rerun()
                
                # --- SEARCH SECTION START ---
                search_query = st.text_input("Search Bar", placeholder="🔍 Search by Sales Order or Customer Name")
                
                orders = get_all_orders()

                if search_query:
                    # Filters the list if the query matches either Sales_Order or Customer_Name (case-insensitive)
                    orders = [
                        o for o in orders 
                        if search_query.lower() in str(o.get("Sales_Order", "")).lower() 
                        or search_query.lower() in str(o.get("Customer_ID", "")).lower()
                    ]
                # --- SEARCH SECTION END ---

                if not orders:
                    st.info("No matching orders found.")
                else:
                    for order in orders:
                        # Using Customer_Name in the label for better clarity
                        with st.expander(f"📦 Order: {order['Sales_Order']} | 👤 {order.get('Customer_ID', 'N/A')}"):
                            col1, col2 = st.columns([3,1])

                            with col1:
                                st.write(f"**Booking Date:** {order['Booking_Date']}")
                                st.write(f"**Delivery Date:** {order['Delivery_Date']}")
                                col_list = ["SO_Number", "item_label", "Item_Code", "Description", "Qty", "Rate", '"Work Order"']
                                items = supabase.table("sales_order_items").select(",".join(col_list)).eq("SO_Number", order["Sales_Order"]).execute().data
                                if items:
                                    st.dataframe(items, use_container_width=True, hide_index=True)

                            with col2:
                                st.info("Actions")
                                if st.button("✏️ Edit Order", key=f"edit_{order['Sales_Order']}"):
                                    edit_order_dialog(order)
                                if st.button("🗑️ Delete Order", key=f"del_{order['Sales_Order']}", type="primary"):
                                    delete_order(order['Sales_Order'])


# endregion

# endregion

# region - Procurement
    elif selected == "Procurement":
        st.subheader("Procurement")

        with st.sidebar:
            # Note: Fixed the radio syntax to pass the list directly
            menu = st.radio("Menu", ["Vendor Details", "Purchase Request", "RFX Management", "Purchase Order", "GRN", "Inward QTY", "Purchase Return"])

# region - Procurement (Vendor Details)
        if menu == "Vendor Details": 
            tab1, tab2, tab3 = st.tabs(["Create Vendor", "Vendor Database", "Edit / Remove Vendor"])

            # --- TAB 1: CREATE VENDOR ---
            with tab1:
                with st.form("vendor_create_form", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        v_code = st.text_input("Vendor Code")
                        v_name = st.text_input("Vendor Name")
                        v_address = st.text_input("Address")
                        v_state = st.text_input("State")

                    with col2:
                        v_mobile = st.text_input("Mobile", max_chars = 10, key="v_mobile")
                        v_email = st.text_input("Email ID")
                        v_gst = st.text_input("GST Number")

                    if st.form_submit_button("Save Vendor"):
                        if v_code and v_name:  # Basic validation
                            vendor_data = {
                                "Vendor_Code": v_code,
                                "Vendor_Name": v_name,
                                "Address": v_address,
                                "State": v_state,
                                "Mobile": v_mobile,
                                "Email_ID": v_email,
                                "GST_Number": v_gst,
                                "Status": "False"
                            }
                            try:
                                supabase.table("vendor_master").insert(vendor_data).execute()
                                st.success(f"Vendor '{v_name}' created successfully!")
                            except Exception as e:
                                st.error(f"Error saving to database: {e}")
                        else:
                            st.warning("Please fill in at least the Vendor Code and Name.")

            with tab2:

                # Toolbar for Sync and Search
                db_col1, db_col2 = st.columns([1, 3])

                with db_col1:
                    if st.button("Sync"):
                        st.cache_data.clear()
                        st.rerun()
                
                try:
                    # Fetch data from Supabase
                    vendor_res = supabase.table("vendor_master").select("*").execute()
                    vendor_db_data = vendor_res.data

                    if not vendor_db_data:
                        st.info("The vendor database is currently empty.")
                    else:
                        df_vendor = pd.DataFrame(vendor_db_data)

                        if 'Status' in df_vendor.columns:
                            df_vendor['Status'] = df_vendor['Status'].map({True: 'APPROVE', False: 'NOT-APPROVE'})

                        # Optional: Reorder columns for better readability
                        column_order = [
                            "Vendor_Code", "Vendor_Name", "Mobile", 
                            "Email_ID", "GST_Number", "State", "Address", "Status"
                        ]
                        # Filter only columns that exist in the dataframe
                        df_vendor = df_vendor[[col for col in column_order if col in df_vendor.columns]]

                        # Search Filter
                        with db_col2:
                            search_term = st.text_input("Search Vendor Name or Code", placeholder="Search")

                        if search_term:
                            df_vendor = df_vendor[
                                df_vendor['Vendor_Name'].str.contains(search_term, case=False, na=False) |
                                df_vendor['Vendor_Code'].str.contains(search_term, case=False, na=False)
                            ]

                        # Display Dataframe
                        st.dataframe(
                            df_vendor, 
                            use_container_width=True, 
                            hide_index=True,
                            column_config={
                                "Vendor_Code": st.column_config.TextColumn("Code"),
                                "Vendor_Name": st.column_config.TextColumn("Vendor Name"),
                                "Email_ID": st.column_config.TextColumn("Email"),
                                "GST_Number": st.column_config.TextColumn("GSTIN"),
                                "Status": st.column_config.TextColumn("Status")
                            }
                        )
                        
                        # Quick Statistics
                        st.caption(f"Showing {len(df_vendor)} vendors")

                except Exception as e:
                    st.error(f"Error loading database: {e}")

            # --- TAB 3: EDIT / REMOVE VENDOR ---
            with tab3:
                
                try:
                    vendors_res = supabase.table("vendor_master").select("*").execute()
                    vendors_data = vendors_res.data

                    if not vendors_data:
                        st.info("No vendors found.")
                    else:
                        vendor_map = {v['Vendor_Name']: v for v in vendors_data}
                        selected_v_name = st.selectbox("Vendor Code", options=list(vendor_map.keys()), key="edit_vendor_select")
                        curr = vendor_map[selected_v_name]

                        st.markdown("---")
                        ec1, ec2 = st.columns(2)
                        
                        with ec1:
                            new_v_code = st.text_input("Vendor Code", value=curr['Vendor_Code'], disabled=True)
                            new_v_name = st.text_input("Vendor Name", value=curr['Vendor_Name'])
                            new_v_address = st.text_input("Address", value=curr['Address'])
                            
                        with ec2:
                            new_v_email = st.text_input("Email ID", value=curr['Email_ID'])
                            new_v_gst = st.text_input("GST Number", value=curr['GST_Number'])
                            
                            # --- NEW APPROVAL SYSTEM ---
                            # Map Boolean to String for the UI
                            current_status_str = "Approve" if curr.get('Status') is True else "Not Approve"
                            approval_choice = st.selectbox(
                                "Vendor Approval Status", 
                                options=["Not Approve", "Approve"], 
                                index=0 if current_status_str == "Not Approve" else 1,
                                help="Setting to Approve allows this vendor to be used in Purchase Orders."
                            )
                            # Convert back to Boolean for Supabase
                            new_status_bool = True if approval_choice == "Approve" else False

                        st.markdown("---")
                        eb_col1, eb_col2, = st.columns([1,1])

                        with eb_col1:
                            if st.button("UPDATE", type="primary"):
                                updated_payload = {
                                    "Vendor_Name": new_v_name,
                                    "Address": new_v_address,
                                    "Email_ID": new_v_email,
                                    "GST_Number": new_v_gst,
                                    "Status": new_status_bool  # Saving the boolean value
                                }
                                supabase.table("vendor_master").update(updated_payload).eq("Vendor_Code", curr['Vendor_Code']).execute() 
                                st.success(f"Vendor '{new_v_name}' updated successfully!")
                                st.rerun()

                        with eb_col2:
                            if st.button("DELETE", type="secondary"):
                                supabase.table("vendor_master").delete().eq("Vendor_Code", curr['Vendor_Code']).execute()
                                st.warning("Vendor deleted.")
                                st.rerun()

                except Exception as e:
                    st.error(f"Error: {e}")
    # endregion

 # region - Procurement (Purchase Request)

        elif menu == "Purchase Request":

            tab1, tab2, tab3, tab4 = st.tabs(["Create PR", "Auto PR", "PR Edit", "PR Database"])

            # --- TAB 1: CREATE PR ---
            with tab1:
                # 1. Initialize Session State for the item list
                if 'pr_items_list' not in st.session_state:
                    st.session_state.pr_items_list = []

                st.subheader("📦 Create New Purchase Request")

                # Header Section (pr_master)
                col1, col2 = st.columns(2)
                with col1:
                    # Note: You can use your 'get_next_pr_id()' logic here for Purchase_Code
                    predicted_code = get_next_pr_code_preview()
                    p_code = st.text_input("PURCHASE CODE (PR Number)", value=predicted_code, disabled=True)
                    p_des = st.text_input("PURCHASE DESCRIPTION")
                    
                with col2:
                    p_date = st.date_input("PR Date", date.today())
                    r_date = st.date_input("REQUIRED DATE", date.today())

                # 2. Dialog for adding items
                @st.dialog("Add Item to PR")
                def add_item_to_pr():
                    # Fetch data from your existing item_master function
                    master_data = item_master() 
                    item_list = [row['Description'] for row in master_data if row.get("Category") != "Finish good"]

                    selected_desc = st.selectbox("SELECT ITEM", options=item_list)
                    
                    # Auto-fetch details based on selection
                    details = next((i for i in master_data if i["Description"] == selected_desc), {})
                    
                    i_code = st.text_input("ITEM CODE", value=details.get("Item_Code", ""), disabled=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        p_unit = st.text_input("PRIMARY UNIT", value=details.get("Primary_Unit", ""), disabled=True)
                    with c2:
                        a_unit = st.text_input("ALTERNATE UNIT", value=details.get("Alternative_Unit", ""), disabled=True)

                    qty = st.number_input("QUANTITY", min_value=10, step=1)
                    price = st.text_input("LATEST PRICE", value=details.get("Latest_Purchase_Price", "0"), disabled=True)
                    
                    if st.button("Add to Request List"):
                        if p_code and i_code:
                            # Store in session state using SQL-ready keys
                            new_row = {
                                "pr_code": p_code, # Links to Purchase_Code in master
                                "item_code": i_code,
                                "item_description": selected_desc,
                                "primary_unit": p_unit,
                                "alternate_unit": a_unit,
                                "quantity": qty,
                                "latest_purchase_price": float(price) if price else 0
                            }
                            st.session_state.pr_items_list.append(new_row)
                            st.rerun()
                        else:
                            st.error("Please ensure PR Code and Item are valid.")

                # 3. Items Table Management
                st.markdown("---")
                btn_col1, btn_col2 = st.columns([1, 5])
                with btn_col1:
                    if st.button("➕ Add Item"):
                        add_item_to_pr()
                with btn_col2:
                    if st.button("🗑️ Clear List"):
                        st.session_state.pr_items_list = []
                        st.rerun()

                # Display items added so far
                if st.session_state.pr_items_list:
                    st.table(st.session_state.pr_items_list)
                else:
                    st.info("No items added to this PR yet.")

                # 4. Final Save to Supabase
                if st.button("🚀 Submit Purchase Request", type="primary"):
                    if not p_code:
                        st.error("Purchase Code is required!")
                    elif not st.session_state.pr_items_list:
                        st.error("At least one item must be added.")
                    else:
                        try:
                            # A. Insert into pr_master
                            master_payload = {
                                "purchase_code": p_code,
                                "purchase_description": p_des,
                                "pr_date": str(p_date),      # Convert date object to string "YYYY-MM-DD"
                                "required_date": str(r_date),
                                "status": "Not-Approve",
                                "auto_generated": False
                            }
                            supabase.table("pr_master").insert(master_payload).execute()

                            # B. Insert into pr_item_details
                            # The session state already has the correct keys and the PR_Code link
                            supabase.table("pr_item_details").insert(st.session_state.pr_items_list).execute()

                            st.success(f"PR {p_code} saved successfully!")
                            st.session_state.pr_items_list = [] # Reset list
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to save PR: {e}")
            

            with tab2:
                st.write("### ⚠️ Low Stock Alerts")
                st.caption("Items below Min_Qty in Item Master appear here automatically.")

                # 1. Fetch Item Master for stock levels
                items_master = supabase.table("item_master").select("*").execute()

                # 2. FETCH CURRENT ACTIVE PR ITEMS (This makes the button reappear if deleted)
                # We check the details table to see what is already "requested"
                active_prs_query = supabase.table("pr_item_details").select("item_code").execute()
                # Create a set of codes for fast lookup
                active_pr_items = {row['item_code'] for row in active_prs_query.data} if active_prs_query.data else set()

                # 3. Filter items needing restock
                to_restock = [
                    i for i in items_master.data 
                    if (i.get('Stock_Qty') or 0) < (i.get('Min_Qty') or 0) 
                    and i.get('Category') != "Finish good"
                ]

                if to_restock:
                    for item in to_restock:
                        i_code = item['Item_Code']
                        min_q = item.get('Min_Qty') or 0 
                        stock_q = item.get('Stock_Qty') or 0
                        shortfall = min_q - stock_q
                        
                        with st.container(border=True):
                            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                            c1.write(f"**{item['Description']}** ({i_code})")
                            c2.write(f"Stock: {stock_q}")
                            c3.write(f"Min: {min_q}")
                            
                            # --- DYNAMIC BUTTON LOGIC ---
                            if i_code in active_pr_items:
                                # If it exists in pr_item_details, show the note
                                c4.info("✅ PR Created")
                            else:
                                # If it was deleted or doesn't exist, show the button
                                if c4.button("Create PR", key=f"auto_gen_{i_code}"):
                                    try:
                                        # Step A: Insert into Master (Trigger handles purchase_code & pr_date)
                                        master_resp = supabase.table("pr_master").insert({
                                            "purchase_description": f"Auto-Restock: {item['Description']}",
                                            "required_date": str(date.today()),
                                            "status": "Not-Approve",
                                            "auto_generated": True
                                        }).execute()

                                        new_pr_id = master_resp.data[0]['purchase_code']

                                        # Step B: Insert into Details
                                        supabase.table("pr_item_details").insert({
                                            "pr_code": new_pr_id,
                                            "item_code": i_code,
                                            "item_description": item['Description'],
                                            "quantity": shortfall,
                                            "latest_purchase_price": item.get('Latest_Purchase_Price', 0)
                                        }).execute()
                                        
                                        st.success(f"PR {new_pr_id} Generated!")
                                        st.rerun() # Refresh to update active_pr_items list
                                        
                                    except Exception as e:
                                        st.error(f"Error: {e}")
                else:
                    st.success("✅ All items are above minimum stock levels.")

            # --- TAB 2: PR EDIT ---
            with tab3:
                st.subheader("⚙️ PR Command Center")

                # 1. Setup Vendor Data (Fetch from your vendor_master table)
                v_query = supabase.table("vendor_master").select("Vendor_Name, Vendor_Code").execute()
                v_data = v_query.data if v_query.data else []
                
                # Create helper dictionary and list for dropdown
                vendor_map = {v['Vendor_Name']: v['Vendor_Code'] for v in v_query.data}
                vendor_options = list(vendor_map.keys())

                # 2. Fetch PRs
                search_q = st.text_input("🔍 Find PR (Code/Description)", key="edit_search_v2")
                
                if search_q:
                    pr_query = supabase.table("pr_master").select("*")\
                        .or_(f"purchase_code.ilike.%{search_q}%,purchase_description.ilike.%{search_q}%")\
                        .order("created_at", desc=True).execute()
                else:
                    pr_query = supabase.table("pr_master").select("*")\
                        .order("created_at", desc=True).limit(20).execute()

                if pr_query.data:
                    for pr in pr_query.data:
                        p_id = pr['purchase_code']
                        
                        with st.expander(f"📦 PR: {p_id} | Status: {pr['status']}"):
                            # --- HEADER SECTION ---
                            h_col1, h_col2, h_col3 = st.columns(3)
                            new_desc = h_col1.text_input("Description", value=pr['purchase_description'], key=f"h_desc_{p_id}")
                            
                            # Handling PR Date (added)
                            pr_date_val = datetime.strptime(pr['pr_date'], '%Y-%m-%d') if pr.get('pr_date') else datetime.now()
                            new_pr_date = h_col2.date_input("PR Date", value=pr_date_val, key=f"h_pr_date_{p_id}")
                            
                            status_list = ["Not-Approve", "Approve", "Hold", "Reject"]
                            curr_idx = status_list.index(pr['status']) if pr['status'] in status_list else 0
                            new_status = h_col3.selectbox("Status", status_list, index=curr_idx, key=f"h_stat_{p_id}")

                            # --- ITEM SECTION (Edit Qty & Vendor) ---
                            items_fetch = supabase.table("pr_item_details").select("*").eq("pr_code", p_id).execute()
                            
                            if items_fetch.data:
                                df_items = pd.DataFrame(items_fetch.data)
                                
                                st.info("💡 You can edit Qty/Vendor or select a row and press Delete on your keyboard to remove an item.")
                                
                                edited_df = st.data_editor(
                                    df_items,
                                    column_config={
                                        "item_code": st.column_config.TextColumn("Item Code", disabled=True),
                                        "item_description": st.column_config.TextColumn("Description", disabled=True),
                                        "quantity": st.column_config.NumberColumn("Qty", min_value=1, required=True),
                                        "vendor_name": st.column_config.SelectboxColumn("Vendor Name", options=vendor_options, required=False),
                                        "vendor_code": st.column_config.TextColumn("Vendor Code", disabled=True), # Keep this disabled to prevent manual entry
                                        "latest_purchase_price": st.column_config.NumberColumn("Price", disabled=True)
                                    },
                                    disabled=["id", "pr_code", "item_code", "item_description", "latest_purchase_price", "vendor_code"],
                                    hide_index=True,
                                    num_rows="dynamic", # Enables the ability to remove items
                                    key=f"item_editor_{p_id}",
                                    use_container_width=True
                                )

                            st.write("---")
                            
                            # --- SAVE LOGIC ---
                            btn_save, btn_del_check = st.columns([1, 2])
                            
                            if btn_save.button("💾 Update PR", key=f"btn_save_{p_id}", type="primary"):
                                # 1. Update Master
                                supabase.table("pr_master").update({
                                    "purchase_description": new_desc,
                                    "status": new_status,
                                    "pr_date": str(new_pr_date)
                                }).eq("purchase_code", p_id).execute()
                                
                                # 2. Handle Item Deletions 
                                # Compare original IDs with current editor IDs to find removed items
                                original_ids = set(df_items['id'].tolist())
                                current_ids = set(edited_df['id'].dropna().tolist())
                                deleted_ids = original_ids - current_ids
                                
                                if deleted_ids:
                                    supabase.table("pr_item_details").delete().in_("id", list(deleted_ids)).execute()

                                # 3. Update Remaining Items
                                for _, row in edited_df.iterrows():
                                    # Autofill Vendor Code from name
                                    v_code = vendor_map.get(row['vendor_name'], "")
                                    
                                    supabase.table("pr_item_details").update({
                                        "quantity": row['quantity'],
                                        "vendor_name": row['vendor_name'],
                                        "vendor_code": v_code # Auto-filling based on selection
                                    }).eq("id", row['id']).execute()
                                
                                st.success("Changes Synchronized!")
                                st.rerun()

                            with btn_del_check:
                                if st.checkbox("Enable Full PR Delete", key=f"full_del_chk_{p_id}"):
                                    if st.button(f"🗑️ Delete PR {p_id}", key=f"full_del_btn_{p_id}"):
                                        supabase.table("pr_master").delete().eq("purchase_code", p_id).execute()
                                        st.rerun()
                

            # --- TAB 3: PR DATABASE ---
            with tab4:
                st.subheader("📊 Purchase Request History")

                # 1. Search Interface
                search_col1, search_col2 = st.columns([3, 1])
                with search_col1:
                    db_search = st.text_input("🔍 Search Database (PR Code, Description, or Status)", key="db_history_search")
                with search_col2:
                    st.write(" ") # Alignment padding
                    st.write(" ")
                    refresh_db = st.button("🔄 Refresh Data")

                # 2. Query Logic
                try:
                    if db_search:
                        # Search across all records if user provides a query
                        db_query = supabase.table("pr_master")\
                            .select("*")\
                            .or_(f"purchase_code.ilike.%{db_search}%,purchase_description.ilike.%{db_search}%,status.ilike.%{db_search}%")\
                            .order("created_at", desc=True)\
                            .execute()
                    else:
                        # Default: Show only the 30 most recent records
                        db_query = supabase.table("pr_master")\
                            .select("*")\
                            .limit(30)\
                            .order("created_at", desc=True)\
                            .execute()

                    # 3. Display the Data
                    if db_query.data:
                        # Convert to DataFrame for a clean, searchable table UI
                        import pandas as pd
                        df = pd.DataFrame(db_query.data)
                        
                        # Clean up the column names for display
                        df_display = df.rename(columns={
                            "purchase_code": "PR Code",
                            "purchase_description": "Description",
                            "pr_date": "Date",
                            "required_date": "Required Date",
                            "status": "Status",
                            "auto_generated": "Auto-Gen",
                            "created_at": "Timestamp"
                        })

                        # Reordering columns to put PR Code and Status first
                        cols = ["PR Code", "Description", "Status", "Date", "Required Date", "Auto-Gen"]
                        st.dataframe(df_display[cols], use_container_width=True, hide_index=True)
                        
                        st.caption(f"Showing {len(db_query.data)} records. Search to find older entries.")
                    else:
                        st.info("No Purchase Requests found in the database.")

                except Exception as e:
                    st.error(f"Error fetching database history: {e}")
# endregion
        
# region - Procurement (RFX Management)
        elif menu == "RFX Management":
            
            tab1, tab11, tab2, tab3 = st.tabs(["RFQ", "RFQ Database", "Compare Quotation", "Quotation"])

            with tab1:
                st.header("🏢 RFI Master Review")
                
                # 1. Fetch live vendor list for the dropdown
                vendor_query = supabase.table("vendor_master").select("Vendor_Name, Mobile, Email_ID").execute()
                vendor_options = [v['Vendor_Name'] for v in vendor_query.data] if vendor_query.data else []
                vendor_dict = {v['Vendor_Name']: v for v in vendor_query.data} if vendor_query.data else {}

                # 2. Fetch pending requests
                rfi_query = supabase.table("rfi_master").select("*").eq("status", "Pending").execute()

                if rfi_query.data:
                    for rfi in rfi_query.data:
                        with st.expander(f"🔍 Review: {rfi['rfi_code']} - {rfi['rfi_item_name']}"):
                            
                            # --- SECTION 1: PROPERLY FORMATTED REQUEST DETAILS ---
                            st.write("#### 📋 Request Details")
                            # Using columns for a cleaner "line-wise" look
                            rd1, rd2, rd3 = st.columns(3)
                            rd1.markdown(f"**Item Name:**\n{rfi['rfi_item_name']}")
                            rd1.markdown(f"**Item Code:**\n`{rfi['rfi_item_code']}`")
                            
                            rd2.markdown(f"**Required Qty:**\n{rfi['rfi_qty']}")
                            rd2.markdown(f"**Required Date:**\n{rfi['rfi_date']}")
                            
                            rd3.markdown(f"**Frequency:**\n{rfi.get('rfi_freq', 1)} / year")
                            rd3.markdown(f"**Status:**\n🟡 {rfi['status']}")

                            st.markdown("**Detailed Description:**")
                            st.info(rfi['rfi_item_des'] if rfi['rfi_item_des'] else "No technical description provided.")
                            
                            if rfi.get('rfi_comment'):
                                st.markdown("**Staff Comments:**")
                                st.caption(rfi['rfi_comment'])

                            st.divider()

                            # --- SECTION 2: VENDOR LIVE PREVIEW ---
                            st.write("#### ✍️ Purchase Team Enrichment")
                            
                            # Multiselect for vendors (Placed outside form if you want instant detail preview)
                            v_list = st.multiselect(
                                f"Select Vendors for {rfi['rfi_code']}", 
                                options=vendor_options,
                                key=f"v_select_{rfi['rfi_code']}"
                            )

                            # Auto-show vendor details if selected
                            if v_list:
                                with st.container(border=True):
                                    st.caption("👥 Selected Vendor Contacts:")
                                    for v_name in v_list:
                                        v_info = vendor_dict.get(v_name, {})
                                        st.write(f"• **{v_name}** | Contact: {v_info.get('Mobile', 'N/A')} | Email: {v_info.get('Email_ID', 'N/A')}")

                            # --- SECTION 3: ENRICHMENT FORM ---
                            with st.form(key=f"rfi_enrich_{rfi['rfi_code']}"):
                                col1, col2 = st.columns(2)
                                t_cond = col1.selectbox("Payment Terms", ["Net 30", "Advance", "COD", "LC 90 Days"])
                                p_notes = col2.text_area("Procurement Notes", placeholder="Internal instructions...")

                                # Actions
                                b1, b2, _ = st.columns([1, 1, 2])
                                
                                if b1.form_submit_button("✅ Submit RFQ", type="primary"):
                                    if not v_list:
                                        st.error("Please select at least one vendor before submitting.")
                                    else:
                                        supabase.table("rfi_master").update({
                                            "assigned_vendors": v_list,
                                            "terms_conditions": t_cond,
                                            "procurement_notes": p_notes,
                                            "status": "Submitted"
                                        }).eq("rfi_code", rfi['rfi_code']).execute()
                                        st.success(f"RFI {rfi['rfi_code']} sent to {len(v_list)} vendors!")
                                        st.rerun()

                                if b2.form_submit_button("🗑️ Delete"):
                                    supabase.table("rfi_master").delete().eq("rfi_code", rfi['rfi_code']).execute()
                                    st.warning("Request deleted.")
                                    st.rerun()
                else:
                    st.info("No pending RFI requests found.")
            
            with tab11: 
                st.title("📂 RFI Master Database")
                st.caption("Central repository for all Request for Information records.")

                # 1. Fetch data
                rfi_db_query = supabase.table("rfi_master").select("*").order("created_at", desc=True).execute()
                
                if rfi_db_query.data:
                    df = pd.DataFrame(rfi_db_query.data)

                    # --- SECTION 1: INDIVIDUAL RFI INSPECTOR ---
                    st.subheader("🔍 Individual RFI Inspector")
                    # Create a selection list for individual lookup
                    rfi_list = df['rfi_code'].tolist()
                    selected_rfi_code = st.selectbox("Select RFI Code to view full details", ["-- Select --"] + rfi_list)

                    if selected_rfi_code != "-- Select --":
                        # Filter the single row
                        rfi_details = df[df['rfi_code'] == selected_rfi_code].iloc[0]
                        
                        with st.container(border=True):
                            c1, c2, c3 = st.columns(3)
                            c1.metric("Status", rfi_details['status'])
                            c2.metric("Quantity", f"{rfi_details['rfi_qty']}")
                            c3.metric("Required Date", str(rfi_details['rfi_date']))
                            
                            det1, det2 = st.columns(2)
                            with det1:
                                st.write("**📦 Item Details**")
                                st.write(f"**Name:** {rfi_details['rfi_item_name']}")
                                st.write(f"**Code:** `{rfi_details['rfi_item_code']}`")
                                st.write(f"**Description:** {rfi_details['rfi_item_des']}")
                            
                            with det2:
                                st.write("**🤝 Procurement Info**")
                                st.write(f"**Assigned Vendors:** {', '.join(rfi_details['assigned_vendors']) if rfi_details['assigned_vendors'] else 'None'}")
                                st.write(f"**Terms:** {rfi_details['terms_conditions']}")
                                st.write(f"**Procurement Notes:** {rfi_details['procurement_notes']}")
                            
                            st.write("**💬 Staff Comment:**")
                            st.info(rfi_details['rfi_comment'] if rfi_details['rfi_comment'] else "No comments.")

                    st.divider()

                    # --- SECTION 2: SEARCH & TABLE VIEW ---
                    st.subheader("📊 Database Table View")
                    search_col1, search_col2 = st.columns([2, 1])
                    search_query = search_col1.text_input("Search by Item Name or RFI Code", placeholder="Type here...")
                    status_filter = search_col2.multiselect("Filter Status", options=df['status'].unique(), default=df['status'].unique())

                    # Apply Filters
                    filtered_df = df[df['status'].isin(status_filter)]
                    if search_query:
                        # Note: Ensure these column names match your SQL exactly (Item_Name vs rfi_item_name)
                        filtered_df = filtered_df[
                            filtered_df['rfi_item_name'].str.contains(search_query, case=False, na=False) |
                            filtered_df['rfi_code'].str.contains(search_query, case=False, na=False)
                        ]

                    # Formatting Vendors for table display
                    display_df = filtered_df.copy()
                    display_df['assigned_vendors'] = display_df['assigned_vendors'].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)

                    # Column renaming for UI
                    ui_df = display_df[['rfi_code', 'status', 'rfi_item_name', 'rfi_qty', 'rfi_date', 'assigned_vendors']]
                    ui_df.columns = ['ID', 'Status', 'Item Description', 'Qty', 'Target Date', 'Vendors']

                    # Display the Table
                    st.dataframe(ui_df, use_container_width=True, hide_index=True)

                    # Download Option
                    csv = filtered_df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download CSV", data=csv, file_name=f"RFI_Log_{date.today()}.csv", mime='text/csv')

                else:
                    st.info("The RFI database is currently empty.")

# endregion

# endregion

# region - Inventory Page

# region Inventory >> ITEM
    elif selected == "Inventory":
            with st.sidebar:
                menu = st.radio("Menu", ["ITEM", "BOM"])
                

            if menu == "ITEM":
                st.subheader("Item Database")

                col0, col1, col2, col3, col4 = st.tabs(["RFI", "Add Item", "Create Item", "Item Database", "Edit & Remove Item"])

                with col0:
                    st.subheader("Request for Item")
                    with st.form("vendor_create_form", clear_on_submit=True):
                        cel1, cel2 = st.columns(2)
                        with cel1:
                            # RFI Code left blank to let SQL Trigger handle it for integrity
                            rfi_item_code = st.text_input("Item Code", placeholder="e.g., RFI-001")
                            rfi_item_name = st.text_input("Item Name")
                            rfi_item_des = st.text_area("Item Description", help="Technical specs")
                        with cel2:
                            rfi_qty = st.number_input("Required QTY", value=5.0, step=1.0, min_value=1.0)
                            rfi_freq = st.number_input("Frequency of Order (per year)", value=1.0, step=1.0, min_value=1.0)
                            rfi_date = st.date_input("Item Required Date", date.today())
                            rfi_comment = st.text_area("Comment", placeholder="Why is this needed?")

                        if st.form_submit_button("Submit Request"):
                            if not rfi_item_code or not rfi_item_name:
                                # st.error("Item Code and Name are required.")
                                pass
                            else:
                                try:
                                    data = {
                                        "rfi_item_code": rfi_item_code,
                                        "rfi_item_name": rfi_item_name,
                                        "rfi_item_des": rfi_item_des,
                                        "rfi_qty": rfi_qty,
                                        "rfi_freq": rfi_freq,
                                        "rfi_date": str(rfi_date),
                                        "rfi_comment": rfi_comment
                                    }
                                    supabase.table("rfi_master").insert(data).execute()
                                    st.success("Request sent to Purchase Team!")
                                except Exception as e:
                                    st.error(f"Integrity Error: {e}")
                    
                

                with col1:
                    st.subheader("Add Stock to Existing Item")

                    if st.button("Sync", key="add_item_sync_button"):
                        st.cache_data.clear()
                        st.rerun()

                    # Fetch latest data
                    item_i_data = item_master()
                    df_items = pd.DataFrame(item_i_data)

                    if not df_items.empty:
                        # Unique list for dropdown
                        item_desc_list = df_items['Description'].unique().tolist()
                        selected_desc = st.selectbox("Select Item Description", options=item_desc_list, key="stock_update_desc_selector")
                        
                        # Filter current record
                        item_record = df_items[df_items['Description'] == selected_desc].iloc[0]
                        
                        c1, c2 = st.columns(2)
                        
                        with c1:
                            # We add suffix '_stock' to keys to prevent DuplicateWidgetID errors
                            st.text_input("Item Code", value=item_record['Item_Code'], disabled=True, key="item_code_stock")
                            st.text_input("Primary Unit", value=item_record['Primary_Unit'], disabled=True, key="pri_unit_stock")
                            st.text_input("Alternate Unit", value=item_record['Alternative_Unit'], disabled=True, key="alt_unit_stock")

                        with c2:
                            # 5. Add QTY (New Number Input)
                            add_qty = st.number_input("Add QTY", min_value=0.0, step=1.0, key="add_qty_input")
                            
                            # 6. Purchase Price (Editable)
                            # Fetching current Latest_Purchase_Price to show as default
                            current_lp = float(item_record.get('Latest_Purchase_Price', 0))
                            purchase_price = st.number_input("Purchase Price", value=current_lp, step=1.0, key="purchase_price_input")
                            
                            # 7. Current Cost/unit = Purchase Price / Add QTY
                            if add_qty > 0:
                                calculated_cost = purchase_price / add_qty
                            else:
                                calculated_cost = 0.0
                                
                            st.info(f"Calculated Cost/Unit: {calculated_cost:.2f}")

                        if st.button("Submit Stock Update", type="primary", key="btn_stock_update"):
                            try:
                                # 8. Append Quantity Logic
                                # Get existing qty (Handling potential None values)
                                existing_qty = float(item_record.get('Stock_Qty', 0)) if item_record.get('Stock_Qty') else 0.0
                                new_total_qty = existing_qty + float(add_qty)

                                # Preparing update dictionary
                                update_vals = {
                                    "Latest_Purchase_Price": float(purchase_price), # Replaces old price
                                    "Current_Cost": calculated_cost,         # Calculated from current batch
                                    "Stock_Qty": float(new_total_qty)             # Appends/Adds to old qty
                                }
                                
                                # Execute Update
                                supabase.table("item_master").update(update_vals).eq("Item_Code", item_record['Item_Code']).execute()
                                
                                st.success(f"Stock for {selected_desc} updated! New Total Qty: {new_total_qty}")
                                st.cache_data.clear()
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Failed to update stock: {e}")
                    else:
                        st.warning("No items found. Please create an item first.")


                with col2:
                    with st.container(border=True):
                        st.subheader("Create Item")
                        cel1, cel2 = st.columns(2)


                        with cel1:
                            category = st.selectbox("Category", ["Finish good", "Raw Material", "Consumable"], key="categaory")
                            description = st.text_input("Description")
                            generated_code = generate_item_code(category, description)
                            itemcode = st.text_input("Item Code", value=generated_code, disabled = True)
                            #type = st.radio("Type", ["Boughout", "Inhouse", "Both"], horizontal=True)
                            p_unit = st.selectbox("Primary Unit", ["BAG", "BOX", "BUNDLE", "CAN", "DRUM", "MT", "KG", "LTR", "MTR", "PAIR", "PCS", "PKT", "ROLL", "SQM", "Nos"], key="p_unit")
                            

                        with cel2:
                            # con_factor = st.number_input("Conversion Factor", step=1)
                            L_p_p = st.number_input("Latest Purchase Price", step=1)
                            # s_c = st.number_input("Stock Cost", step=1)
                            c_s = st.number_input("Current Cost", step=1)
                            min_qty = st.number_input("Minimum Inventory QTY", value=10, step=1)
                            a_unit = st.selectbox("Alternate Unit", ["BAG", "BOX", "BUNDLE", "CAN", "DRUM", "MT", "KG", "LTR", "MTR", "PAIR", "PCS", "PKT", "ROLL", "SQM", "Nos"], key="a_unit")
                            #img = st.file_uploader("Image", type=["jpg", "png"])


                        if st.button("Submit Item", type="primary"):
                            if all([category, itemcode, description, p_unit, a_unit, L_p_p, c_s]):
                                item_data = {
                                    "Item_Code": itemcode,
                                    "Category": category,
                                    "Description": description,
                                    "Primary_Unit": p_unit,
                                    "Alternative_Unit": a_unit,
                                    "Latest_Purchase_Price": L_p_p,
                                    "Current_Cost": c_s,
                                    "Min_Qty": min_qty
                                }
                                st.success("Customer Added Successfully")
                                try:
                                    add_item_master(item_data)
                                except Exception as e:
                                    st.error(f"Error: {e}")
                            else:
                                st.error("Please fill the form")
                
                with col3:
                    if st.button("Sync"):
                        st.cache_data.clear()
                        st.rerun()
                    item_i_data = item_master()
                    df = pd.DataFrame(item_i_data)

                    try:
                        st.dataframe(df)
                    except:
                        st.error("Not data present")
                
                with col4:
                    st.write("Manage Existing Item")

                    select_cus = st.selectbox("Select Item", df['Item_Code'].unique())

                    current_data = df[df['Item_Code'] == select_cus].iloc[0]

                    col1, col2 = st.columns(2)
                    with col1:
                        # cus_new_name = st.text_input("Customer Name", value = current_data['Customer_Name'])
                        # cus_new_number = st.text_input("Customer Name", value = str(current_data['customer_number']), max_chars=10)
                        # cus_new_gstno = st.text_input("GST No.", value=current_data['cus_gstno'])
                        cat_options = ["Finish good", "Raw Material", "Consumable", "Raw material"]
                        n_category = st.selectbox("Category", cat_options, index=cat_options.index(current_data['Category']),key="edit_category")
                        n_itemcode = st.text_input("Item Code", value = current_data['Item_Code'])
                        n_description = st.text_input("Description", value = current_data['Description'])
                        #type = st.radio("Type", ["Boughout", "Inhouse", "Both"], horizontal=True)
                        unit_options = ["BAG", "BOX", "BUNDLE", "CAN", "DRUM", "MT", "KG", "LTR", "MTR", "PAIR", "PCS", "PKT", "ROLL", "SQM", "Nos"]
                        n_p_unit = st.selectbox("Primary Unit", unit_options, index=unit_options.index(current_data['Primary_Unit']), key="edit_p_unit")

                    
                    with col2:
                        n_L_p_p = st.number_input("Latest Purchase Price", step=1.00, value = float(current_data['Latest_Purchase_Price']))
                        # s_c = st.number_input("Stock Cost", step=1)
                        n_c_s = st.number_input("Current Cost", step=1.00, value = float(current_data['Current_Cost']))
                        n_m_q = st.number_input("Minimum Inventory QTY", step=1.00, value=float(current_data["Min_Qty"]))
                        n_a_unit = st.selectbox("Alternate Unit", unit_options, index=unit_options.index(current_data['Alternative_Unit']), key="edit_a_unit")
                    
                    edit_col, delete_col = st.columns([1,1])

                    with edit_col:
                        if st.button("Update Item"):
                                try:
                                    # 1. This dictionary must be indented inside the try block
                                    updated_info = {
                                        "Category": n_category,
                                        "Item_Code": n_itemcode,
                                        "Description": n_description,
                                        "Primary_Unit": n_p_unit,
                                        "Latest_Purchase_Price": n_L_p_p,
                                        "Current_Cost": n_c_s,
                                        "Alternative_Unit": n_a_unit,
                                        "Min_Qty": n_m_q
                                    }
                                    
                                    # 2. This line MUST align perfectly with 'updated_info' above
                                    response = supabase.table("item_master").update(updated_info).eq("Item_Code", current_data['Item_Code']).execute()
                                    
                                    # 3. These must also align
                                    st.success(f"Record for {n_itemcode} updated successfully")
                                    st.cache_data.clear() 
                                    st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"Update fail: {e}")
                        with delete_col:
                            if st.button("Delete Customer"):
                                try:
                                    supabase.table("item_master").delete().eq("Item_Code", current_data['Item_Code']).execute()
                                    st.warning(f"Customer {n_itemcode} deleted")
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Delete fail: {e}")
# endregion

# region Inventory page >> BOM

# region Inventory page >> BOM >> ADD BOM
            elif menu == "BOM":
                st.subheader("BOM")

                cell1, cell2, cell3 = st.tabs(["ADD BOM", "BOM DATABASE", "EDIT / REMOVE BOM"])

                

                with cell1:
                    if 'temp_items' not in st.session_state:
                        st.session_state['temp_items'] = []
                
                    master_data = item_master()
                    b_item_descriptions = [row['Description'] for row in master_data if row.get("Category") == "Finish good"]
                    item_descriptions = [row['Description'] for row in master_data if row.get("Category") != "Finish good"]

                    so_data = supabase.table("sales_order_items").select("SO_Number").execute()
                    so_options = [""] + sorted({row['SO_Number'] for row in so_data.data})

                    st.subheader("ADD BOM Details")
                    next_code = get_next_bom_id()
                    col1, col2 = st.columns(2)
                    with col1:
                        bom_code = st.text_input("BOM CODE", value=next_code, disabled = True)
                        bom_des = st.text_input("BOM DESCRIPTION")
                        selected_so = st.selectbox("SELECT SALES ORDER", options=so_options, index=None, key="parent_so_select")
                        label_query = supabase.table("sales_order_items") \
                            .select("item_label") \
                            .eq("SO_Number", selected_so) \
                            .execute()
                        
                        label_options = [row['item_label'] for row in label_query.data]
                        selected_label = st.selectbox("SELECT ITEM LABEL", options=label_options)
                        item_details_query = supabase.table("sales_order_items") \
                            .select("Item_Code, Description", "Qty") \
                            .eq("SO_Number", selected_so) \
                            .eq("item_label", selected_label) \
                            .maybe_single() \
                            .execute()

                        # Extract info for display
                        if item_details_query:
                            current_item_code = item_details_query.data.get("Item_Code", "")
                            current_item_des = item_details_query.data.get("Description", "")
                            current_item_qty = str(item_details_query.data.get("Qty", "0"))
                        else:
                            current_item_code = ""
                            current_item_des = ""
                            current_item_qty = "0"
                        product_des = st.text_input("PRODUCT DESCRIPTION", value=current_item_des)
                        so_item = st.text_input("ITEM CODE", value=current_item_code)
                        
                    with col2:
                        bom_qty = st.text_input("BOM Qty", value=current_item_qty)
                        created_date = st.date_input("Booking Date", date.today())
                        cost = st.number_input("COST", format="%.2f")
                        bom_ver = st.number_input("VERSION", min_value=1)
                        

                    @st.dialog("Add Item to BOM")
                    def add_item_dialog():
                        selected_des = st.selectbox("SELECT ITEM DESCRIPTION", options=item_descriptions, key="selected_des")
                        item_details = next((item for item in master_data if item["Description"] == selected_des), None)
                        
                        item_code = st.text_input("ITEM CODE", value=item_details.get("Item_Code", ""), disabled=True)
                        #item_des = st.selectbox("SELECT ITEM DESCRIPTION", options=item_descriptions)
                        item_qty = st.number_input("REQUIRED QTY Per Unit", min_value=1)
                        calc_value = float(item_qty) * float(bom_qty) if item_qty and bom_qty else 0.0
                        actual_qty = st.number_input("Actual Qty", value=float(calc_value), disabled=True)
                        col1, col2 = st.columns(2)
                        with col1:
                            pr_unit = st.text_input("PRIMARY UNIT", value=item_details.get("Primary_Unit", ""), disabled=True)
                        with col2:
                            al_unit = st.text_input("ALTERNATE UNIT", value=item_details.get("Alternative_Unit", ""), disabled=True)
                        #item_inhand = st.number_input("ITEM IN-HAND", value=0.0)
                        #item_onorder = st.number_input("ITEM ON-ORDER", value=0.0)
                        i_cost = st.number_input("COST", value=0.0, format="%.2f")
                        
                        if st.button("Add to List"):
                            if item_code and item_qty:
                                # Create the item dictionary
                                new_item = {
                                    "Item_Code": item_details.get("Item_Code"),
                                    "Description": selected_des,
                                    # "Primary_Unit": pr_unit,
                                    # "Alternative_Unit": al_unit,
                                    "Qty": item_qty,
                                    "Cost": i_cost,
                                    "Actual_Qty": calc_value
                                    
                                }
                                # APPEND to session state instead of Database
                                st.session_state['temp_items'].append(new_item)
                                st.success(f"Added {item_code} to temporary list!")
                                st.rerun()
                            else:
                                st.error("Item Code and Qty are required")
                    st.write("---")
                    st.subheader("Items in this BOM")

                    col_a, col_b = st.columns([1,7]) # Adjust width ratio as needed

                    with col_a:
                        if st.button("Add New Item"):
                            add_item_dialog()

                    with col_b:
                        # Adding the Clear button here
                        if st.button("Clear Item List", type="secondary"):
                            st.session_state['temp_items'] = []
                            st.rerun()

                    if st.session_state['temp_items']:
                        st.table(st.session_state['temp_items'])
                    else:
                        st.info("No items added yet.")

                    # --- FINAL SUBMIT (Saves to Supabase) ---
                    if st.button("Submit Full BOM", type="primary"):
                        if not bom_code or not st.session_state['temp_items']:
                            st.error("Please provide a BOM Code and add at least one item.")
                        else:
                            try:
                                formatted_date = created_date.isoformat()
                                # 1. Save Parent to 'bom_master'
                                parent_data = {
                                    "Bom_Code": bom_code,
                                    "Bom_Description": bom_des,
                                    "Sales_order": selected_so,
                                    "so_item": selected_label,
                                    "Created_Date": formatted_date,
                                    "Product_Des": product_des,
                                    "Cost": cost,
                                    "Version": bom_ver,
                                    "Bom_QTY": bom_qty,
                                    "Item_ID": so_item
                                    
                                }
                                add_bom_master(parent_data)

                                # 2. Save the items to your SECOND table
                                for item in st.session_state['temp_items']:
                                    item_data = {
                                        "parent_bom_code": bom_code,
                                        **item 
                                    }
                                    # MAKE SURE THIS NAME MATCHES YOUR NEW TABLE
                                    supabase.table("bom_item_details").insert(item_data).execute()
                                
                                st.success("Full BOM and all items saved to Database!")
                                
                                # 3. Clear the temporary list for the next entry
                                st.session_state['temp_items'] = []
                                st.cache_data.clear()
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Database Error: {e}")
# endregion

# region Inventory page >> BOM >> BOM DATABASE
                with cell2:
                    
                    # 1. Sync and Clear Cache
                    if st.button("Sync"):
                        st.cache_data.clear()
                        st.rerun()

                    try:
                        def duplicate_bom(original_bom_id, parent_info, items_df):
                            try:
                                # 1. Get a fresh auto-incremented code for the new BOM
                                new_bom_code = get_next_bom_id() 
                                
                                # 2. Prepare Parent Data (Copying from original)
                                new_parent_payload = {
                                    "Bom_Code": new_bom_code,
                                    "Bom_Description": f"Copy of {parent_info.get('Bom_Description', '')}",
                                    "Product_Des": parent_info.get('Product_Description'),
                                    "Item_ID": parent_info.get('Product_Code'),
                                    "Bom_QTY": parent_info.get('BOM_QTY', 1),
                                    "Sales_order": parent_info.get('Sales_Order'),
                                    "so_item": parent_info.get('SO_Item'),
                                    "Version": 1, # Reset version for the new duplicate
                                    "Cost": parent_info.get('Total_Production_Cost', 0),
                                    "Created_Date": date.today().isoformat() #
                                }
                                
                                # Insert new parent
                                supabase.table("bom_master").insert(new_parent_payload).execute()
                                
                                # 3. Prepare Child Items (Copying from items_df)
                                new_items = []
                                for _, row in items_df.iterrows():
                                    new_items.append({
                                        "parent_bom_code": new_bom_code,
                                        "Item_Code": row["Item_Code"],
                                        "Description": row["Item_Description"],
                                        "Actual_Qty": item["Actual_Qty"],
                                        "Qty": row["Required_Quantity"],
                                        "Cost": row["Unit_Cost"]
                                    })
                                    
                                if new_items:
                                    supabase.table("bom_item_details").insert(new_items).execute()
                                    
                                st.success(f"Successfully duplicated {original_bom_id} to {new_bom_code}!")
                                st.cache_data.clear()
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Duplication failed: {e}")

                        # Fetch data from your view
                        data = full_bom_view() # Ensure this returns a list of dicts
                        
                        if not data:
                            st.info("No records present.")
                        else:
                            df = pd.DataFrame(data)

                            # 2. Search Bar Logic (Searching by Parent Item Code or Description)
                            search_query = st.text_input("🔍 Search BOM by Item Code or Description", placeholder="Type to filter...")
                            
                            if search_query:
                                mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
                                df = df[mask]

                            # 3. Grouping Logic
                            # Assuming your view has 'Parent_Item_Code' or 'Bom_Code' to identify the main assembly
                            # Adjust 'Bom_Code' to match your actual column name
                            unique_boms = df["BOM_ID"].unique()

                            for bom_id in unique_boms:
                                # Filter rows for this specific BOM
                                bom_details = df[df["BOM_ID"] == bom_id]
                                parent_info = bom_details.iloc[0] # Get header info from first row

                                with st.expander(f"BOM ID: {bom_id} | {parent_info.get('Bom_Description', 'Main Assembly')}"):
                                    col1, col2 = st.columns([4, 1])

                                    with col1:
                                        cel1, cel2 = st.columns([2,3])
                                        with cel1:
                                            st.write(f"**Product Code:** {parent_info.get('Product_Code', 'N/A')}")
                                            st.write(f"**Product Description:** {parent_info.get('Product_Description', 'N/A')}")
                                            st.write(f"**Cost:** {parent_info.get('Total_Production_Cost', 'N/A')}")
                                        with cel2:
                                            st.write(f"**Sales Order:** {parent_info.get('Sales_Order', 'N/A')}")
                                            st.write(f"**SO Item:** {parent_info.get('SO_Item', 'N/A')}")
                                            st.write(f"**Created Date:** {parent_info.get('Created_Date', 'N/A')}")
                                            st.write(f"**Version:** {parent_info.get('BOM_Version', 'N/A')}")
                                            

                                        st.write("**Material Requirements:**")
                                        
                                        # Display child items in a clean table
                                        # Selecting only relevant columns for the child items list
                                        child_cols = ["Item_Code", "Item_Description", "Required_Quantity", "Actual_qty", "Unit_Cost"]
                                        # Ensure these columns exist in your view
                                        display_df = bom_details[[c for c in child_cols if c in bom_details.columns]]
                                        st.table(display_df)

                                    with col2:
                                        st.info("Actions")
                                         # New Duplicate Button
                                        if st.button("Duplicate", key=f"dup_{bom_id}", use_container_width=True):
                                            duplicate_bom(bom_id, parent_info, bom_details)
                    except Exception as e:
                        st.error(f"Error loading BOM Database: {e}")
# endregion

# region Inventory page >> BOM >> Edit / Remove BOM
                        
                with cell3:
                    
                    try:
                    
                        # 1. Fetch all existing BOMs for selection
                        all_boms_res = supabase.table("bom_master").select("Bom_Code, Bom_Description").execute()
                        bom_list = all_boms_res.data
                        
                        if not bom_list:
                            st.info("No records available to edit.")
                        else:
                            # Create selection map
                            bom_options = {f"{row['Bom_Code']} - {row['Bom_Description']}": row['Bom_Code'] for row in bom_list}
                            selected_bom_label = st.selectbox("Select BOM to Edit/Remove", options=list(bom_options.keys()))
                            selected_bom_id = bom_options[selected_bom_label]

                            # 2. Fetch current Parent Data
                            current_bom = supabase.table("bom_master").select("*").eq("Bom_Code", selected_bom_id).single().execute().data

                            if current_bom:
                                # --- PARENT EDIT INPUTS (Buttons moved to bottom) ---
                                st.markdown("### BOM Details")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.text_input("BOM CODE", value=current_bom.get("Bom_Code"), disabled=True, key="parent_code_display")
                                    new_des = st.text_input("BOM DESCRIPTION", value=current_bom.get("Bom_Description"), key="parent_desc_input")
                                    
                                    m_data = item_master()
                                    finish_goods = [r['Description'] for r in m_data if r.get("Category") == "Finish good"]
                                    try:
                                        default_idx = finish_goods.index(current_bom.get("Product_Des"))
                                    except ValueError:
                                        default_idx = 0
                                    
                                    new_prod_des = st.selectbox("PRODUCT DESCRIPTION", options=finish_goods, index=default_idx, key="parent_prod_select")
                                    new_qty = st.number_input("BOM QTY", min_value=0, value=int(current_bom.get("Bom_QTY", 0)), key="parent_qty_input")

                                with col2:
                                    new_cost = st.number_input("COST", format="%.2f", value=float(current_bom.get("Cost", 0.0)), key="parent_cost_input")
                                    new_ver = st.number_input("VERSION", min_value=1, value=int(current_bom.get("Version", 1)), key="parent_ver_input")
                                    item_info = next((i for i in m_data if i["Description"] == new_prod_des), None)
                                    new_item_id = st.text_input("ITEM ID", value=item_info.get("Item_Code", "") if item_info else "", disabled=True, key="parent_itemid_display")

                                st.markdown("---")
                                
                                # --- CHILD ITEM EDIT SECTION ---
                                st.markdown("### Edit BOM Items")
                                child_res = supabase.table("bom_item_details").select("*").eq("parent_bom_code", str(selected_bom_id)).execute()
                                child_items = child_res.data

                                if child_items:
                                    item_options = {f"{item['Item_Code']} - {item['Description']}": item['id'] for item in child_items}
                                    selected_item_label = st.selectbox("Select Component to Modify", options=list(item_options.keys()), key="child_select_mod")
                                    selected_item_id = item_options[selected_item_label]
                                    curr_item = next(item for item in child_items if item['id'] == selected_item_id)

                                    c1, c2 = st.columns(2)
                                    with c1:
                                        st.text_input("Component Code", value=curr_item.get("Item_Code"), disabled=True, key="comp_code_view")
                                        edit_qty = st.number_input("Update Qty", value=float(curr_item.get("Qty", 1.0)), key="comp_qty_edit")
                                    with c2:
                                        st.text_input("Description", value=curr_item.get("Description"), disabled=True, key="comp_desc_view")
                                        edit_cost = st.number_input("Update Unit Cost", value=float(curr_item.get("Cost", 0.0)), key="comp_cost_edit")

                                    cb1, cb2, _ = st.columns([1, 1, 2])
                                    with cb1:
                                        if st.button("EDIT ITEM", use_container_width=True, key="btn_update_child"):
                                            supabase.table("bom_item_details").update({"Qty": edit_qty, "Cost": edit_cost}).eq("id", selected_item_id).execute()
                                            st.success("Component updated!")
                                            st.rerun()
                                    with cb2:
                                        if st.button("REMOVE ITEM", use_container_width=True, key="btn_remove_child"):
                                            supabase.table("bom_item_details").delete().eq("id", selected_item_id).execute()
                                            st.warning("Component removed.")
                                            st.rerun()
                                else:
                                    st.info("No child items found for this BOM.")

                                # --- ADD NEW MATERIAL SECTION ---
                                with st.expander("➕ Add New Material to this BOM"):
                                    raw_materials = [r for r in m_data if r.get("Category") != "Finish good"]
                                    rm_descriptions = [r['Description'] for r in raw_materials]

                                    if rm_descriptions:
                                        nm_col1, nm_col2 = st.columns(2)
                                        with nm_col1:
                                            sel_rm_desc = st.selectbox("Select New Material", options=rm_descriptions, key="new_mat_select")
                                            mat_info = next((i for i in raw_materials if i["Description"] == sel_rm_desc), None)
                                            nm_code = st.text_input("Mat. Code", value=mat_info.get("Item_Code", "") if mat_info else "", disabled=True, key="new_mat_code")
                                            nm_qty = st.number_input("Qty Required", min_value=0.1, value=1.0, key="new_mat_qty")
                                        
                                        with nm_col2:
                                            st.text_input("Unit", value=mat_info.get("Primary_Unit", "") if mat_info else "", disabled=True, key="new_mat_unit")
                                            nm_cost = st.number_input("Unit Cost", value=float(mat_info.get("Current_Cost", 0.0)) if mat_info else 0.0, key="new_mat_cost")

                                        if st.button("Add to BOM", type="primary", key="btn_add_new_mat"):
                                            new_row = {
                                                "parent_bom_code": str(selected_bom_id),
                                                "Item_Code": nm_code,
                                                "Description": sel_rm_desc,
                                                "Qty": nm_qty,
                                                "Cost": nm_cost
                                            }
                                            supabase.table("bom_item_details").insert(new_row).execute()
                                            st.success("Material Added!")
                                            st.rerun()

                                # --- FINAL ACTION BUTTONS (Moved to the end) ---
                                st.markdown("---")
                                st.markdown("### Finalize BOM Changes")
                                final_col1, final_col2, _ = st.columns([1, 1, 2])
                                
                                with final_col1:
                                    if st.button("UPDATE", type="primary", use_container_width=True, key="final_parent_update"):
                                        supabase.table("bom_master").update({
                                            "Bom_Description": new_des, 
                                            "Product_Des": new_prod_des,
                                            "Bom_QTY": new_qty, 
                                            "Cost": new_cost, 
                                            "Version": new_ver, 
                                            "Item_ID": new_item_id
                                        }).eq("Bom_Code", selected_bom_id).execute()
                                        st.success("Parent BOM updated successfully!")
                                        st.rerun()

                                with final_col2:
                                    if st.button("DELETE", type="secondary", use_container_width=True, key="final_parent_delete"):
                                        # Delete children first (referential integrity), then parent
                                        supabase.table("bom_item_details").delete().eq("parent_bom_code", str(selected_bom_id)).execute()
                                        supabase.table("bom_master").delete().eq("Bom_Code", selected_bom_id).execute()
                                        st.warning("Full BOM and all components deleted.")
                                        st.rerun()

                    except Exception as e:
                        st.error(f"Error: {e}")
                
# endregion

# endregion
# endregion

# region - Dashboard
    elif selected == "Dashboard":
        st.header("Dashboard")
        if st.button("Sync"):
            st.cache_data.clear()
            st.rerun()

        raw_data = self_inspection()

        if raw_data:
            df = pd.DataFrame(raw_data)

            total_checks = len(df)

            fail_rate = len(df[df['molding_dei_visual_inspection'] == 'NOT-OK'])

            m1, m2 = st.columns(2)
            m1.metric("Total Inspection", total_checks)
            m2.metric("Failures Detected", fail_rate, delta_color="inverse")

            st.subheader("Inspection Result by Machine")
            fig = px.histogram(df, x="machine_id", color="molding_dei_visual_inspection", barmode="group")
            st.plotly_chart(fig, use_container_width = True) 

            st.subheader("Recent Logs")
            st.dataframe(df.tail(1))
        else:
            st.info("No data available yet.")

    elif selected == "Access Control":
        st.title("👤 User Access Management")
        
        tab_add, tab_manage = st.tabs(["➕ Add New User", "⚙️ Manage Existing"])
        
        with tab_add:
            # Fetch current count to suggest the next EMR ID
            user_count_query = supabase.table("user_registry").select("count", count="exact").execute()
            mgr_d = supabase.table("user_registry").select().execute()
            mgr = [c["user_name"] for c in mgr_d.data]
            mgr_u = ["NULL"] + mgr
            next_id_num = (user_count_query.count if user_count_query.count else 0) + 1
            suggested_id = f"EMR{next_id_num}"

            with st.form("new_user_form", clear_on_submit=True):
                st.info(f"🆔 **Next Available User ID:** {suggested_id}")
                
                # Row 1: Credentials
                c1, c2, c3 = st.columns(3)
                u_id = c1.text_input("User ID", value=suggested_id, disabled=True)
                u_pass = c2.text_input("User Password", type="password")
                u_role = c3.selectbox("System Role", ["Staff", "Manager", "Admin"])

                # Row 2: Personal Details (The missing fields)
                c4, c5, c6 = st.columns(3)
                u_name = c4.text_input("Full Name")
                u_email = c5.text_input("User Email")
                u_mob = c6.text_input("Mobile No.")

                # Row 3: Organizational Details
                c7, c8, c9 = st.columns(3)
                u_dept = c7.selectbox("Department", ["Production", "Procurement", "Inventory", "Planning", "IT", "HR"])
                u_doj = c8.date_input("Date of Joining")
                u_mgr = c9.selectbox("Reporting Manager", index=0, options=mgr_u)
                
                st.divider()
                st.subheader("🛠️ Module-Specific Permissions")
                
                modules = ["Vendor", "Inventory", "RFX Management", "Production", "BOM"]
                module_perms = {}

                for module in modules:
                    st.write(f"**{module} Module**")
                    p1, p2, p3, p4, p5, _ = st.columns([1, 1, 1, 1, 1, 1])
                    module_perms[module] = {
                        "view": p1.checkbox("View", key=f"v_{module}"),
                        "create": p2.checkbox("Create", key=f"c_{module}"),
                        "edit": p3.checkbox("Edit", key=f"e_{module}"),
                        "delete": p4.checkbox("Delete", key=f"d_{module}"),
                        "approve": p5.checkbox("Approve", key=f"a_{module}")
                    }
                
                st.divider()
                available_tabs = ["Home", "Production", "Planning", "Master File", "Inventory", "Procurement", "Dashboard", "Access Control"]
                selected_tabs = st.multiselect("Grant Tab Access", options=available_tabs)

                if st.form_submit_button("Register User", type="primary"):
                    if not u_id or not u_pass or not u_email or not u_name:
                        st.error("User ID, Password, Name, and Email are all mandatory.")
                    else:
                        new_user_data = {
                            "user_id": u_id,
                            "user_password": u_pass,
                            "user_name": u_name, 
                            "user_email": u_email, 
                            "user_mobile": u_mob,
                            "department": u_dept,
                            "role": u_role,
                            "date_of_joining": str(u_doj),
                            "user_manager": u_mgr,
                            "module_permissions": module_perms,
                            "accessible_tabs": selected_tabs
                        }
                        try:
                            supabase.table("user_registry").insert(new_user_data).execute()
                            st.success(f"User {u_id} ({u_name}) registered successfully!")
                            st.balloons()
                        except Exception as e:
                            st.error(f"Error: {e}")
# endregion
        