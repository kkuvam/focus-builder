def get_template_library():
    """Return a library of predefined templates for common productivity tools"""
    
    templates = {
        "Daily Habit Tracker": {
            "category": "tracker",
            "description": "Create a daily habit tracker with visual progress charts. I want to track multiple habits like exercise, reading, water intake, and meditation. Show my streaks, completion rates, and weekly/monthly progress with colorful charts.",
            "features": ["habit management", "daily check-offs", "progress visualization", "streak tracking", "statistics"]
        },
        
        "Project Task Dashboard": {
            "category": "dashboard",
            "description": "Build a project management dashboard to track tasks across different projects. Include task status (to-do, in-progress, completed), priority levels, due dates, and project progress visualization with Gantt-style timeline views.",
            "features": ["task management", "project organization", "status tracking", "timeline visualization", "priority management"]
        },
        
        "Weekly Meal Planner": {
            "category": "planner",
            "description": "Design a weekly meal planner that lets me plan breakfast, lunch, and dinner for each day. Include a shopping list generator, nutritional tracking, and the ability to save favorite meals for quick planning.",
            "features": ["meal scheduling", "shopping list", "nutrition tracking", "recipe storage", "weekly view"]
        },
        
        "Expense Budget Tracker": {
            "category": "tracker",
            "description": "Create a budget tracking tool that categorizes expenses, shows spending patterns with charts, alerts for budget limits, and provides monthly/yearly financial summaries with savings goals tracking.",
            "features": ["expense categorization", "budget limits", "spending analysis", "savings goals", "financial reports"]
        },
        
        "Study Schedule Planner": {
            "category": "planner",
            "description": "Build a study planner for students with subject scheduling, assignment tracking, exam preparation timeline, study session logging, and progress monitoring with performance analytics.",
            "features": ["subject management", "assignment tracking", "study sessions", "exam scheduling", "performance analytics"]
        },
        
        "Fitness Progress Dashboard": {
            "category": "dashboard",
            "description": "Design a fitness dashboard to track workouts, body measurements, weight progress, exercise routines, and display progress charts with goal achievements and workout statistics.",
            "features": ["workout logging", "body measurements", "progress charts", "goal tracking", "exercise library"]
        },
        
        "Reading List Manager": {
            "category": "tracker",
            "description": "Create a reading tracker that manages my book list, tracks reading progress, logs reading sessions, provides book ratings and reviews, and shows reading statistics with yearly goals.",
            "features": ["book management", "reading progress", "session logging", "ratings/reviews", "reading statistics"]
        },
        
        "Monthly Goal Planner": {
            "category": "planner",
            "description": "Build a goal-setting planner with monthly objectives, weekly milestones, daily action items, progress tracking, and motivational dashboards with achievement celebrations.",
            "features": ["goal setting", "milestone tracking", "daily actions", "progress monitoring", "achievement tracking"]
        }
    }
    
    return templates

def get_template_code(template_name):
    """Return sample code for a specific template (for reference only)"""
    
    template_codes = {
        "Daily Habit Tracker": '''
def execute_tool():
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    from datetime import datetime, date, timedelta
    
    st.subheader("📅 Daily Habit Tracker")
    
    # Initialize session state for habits
    if 'habits' not in st.session_state:
        st.session_state.habits = {}
    if 'habit_logs' not in st.session_state:
        st.session_state.habit_logs = []
    
    # Add new habit section
    with st.expander("➕ Add New Habit", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            new_habit_name = st.text_input("Habit Name")
            habit_target = st.number_input("Daily Target", min_value=1, value=1)
        with col2:
            habit_category = st.selectbox("Category", ["Health", "Productivity", "Learning", "Other"])
            habit_unit = st.text_input("Unit (e.g., glasses, minutes, pages)", value="times")
        
        if st.button("Add Habit") and new_habit_name:
            habit_id = len(st.session_state.habits)
            st.session_state.habits[habit_id] = {
                'name': new_habit_name,
                'target': habit_target,
                'category': habit_category,
                'unit': habit_unit,
                'created_date': datetime.now().date()
            }
            st.success(f"Added habit: {new_habit_name}")
            st.rerun()
    
    if not st.session_state.habits:
        st.info("🎯 Add your first habit to start tracking!")
        return
    
    # Today's habit tracking
    st.subheader("Today's Progress")
    today = date.today()
    
    for habit_id, habit in st.session_state.habits.items():
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{habit['name']}** ({habit['category']})")
        with col2:
            # Check today's completion
            today_log = next((log for log in st.session_state.habit_logs 
                            if log['habit_id'] == habit_id and log['date'] == today), None)
            current_value = today_log['value'] if today_log else 0
            
            new_value = st.number_input(
                f"Progress", 
                min_value=0, 
                value=current_value,
                key=f"habit_{habit_id}",
                help=f"Target: {habit['target']} {habit['unit']}"
            )
            
            # Update log
            if new_value != current_value:
                # Remove existing log for today
                st.session_state.habit_logs = [log for log in st.session_state.habit_logs 
                                             if not (log['habit_id'] == habit_id and log['date'] == today)]
                # Add new log
                if new_value > 0:
                    st.session_state.habit_logs.append({
                        'habit_id': habit_id,
                        'date': today,
                        'value': new_value,
                        'target': habit['target']
                    })
        
        with col3:
            progress_pct = min(100, (new_value / habit['target']) * 100)
            st.metric("Progress", f"{progress_pct:.0f}%")
    
    # Progress visualization
    if st.session_state.habit_logs:
        st.subheader("📊 Progress Overview")
        
        # Create DataFrame for visualization
        df_logs = pd.DataFrame(st.session_state.habit_logs)
        df_logs['habit_name'] = df_logs['habit_id'].map(lambda x: st.session_state.habits[x]['name'])
        df_logs['completion_rate'] = (df_logs['value'] / df_logs['target']) * 100
        
        # Weekly progress chart
        df_logs['date'] = pd.to_datetime(df_logs['date'])
        fig = px.line(df_logs, x='date', y='completion_rate', color='habit_name',
                     title="Habit Completion Rate Over Time",
                     labels={'completion_rate': 'Completion %', 'date': 'Date'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistics
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🏆 Current Streaks")
            for habit_id, habit in st.session_state.habits.items():
                habit_logs = [log for log in st.session_state.habit_logs if log['habit_id'] == habit_id]
                if habit_logs:
                    # Calculate streak (simplified)
                    recent_logs = sorted(habit_logs, key=lambda x: x['date'], reverse=True)
                    streak = 0
                    for log in recent_logs:
                        if log['completion_rate'] >= 100:
                            streak += 1
                        else:
                            break
                    st.metric(habit['name'], f"{streak} days")
        
        with col2:
            st.subheader("📈 This Week's Average")
            week_start = today - timedelta(days=today.weekday())
            week_logs = [log for log in st.session_state.habit_logs 
                        if log['date'] >= week_start]
            
            if week_logs:
                week_df = pd.DataFrame(week_logs)
                week_avg = week_df.groupby('habit_id')['completion_rate'].mean()
                for habit_id, avg_rate in week_avg.items():
                    habit_name = st.session_state.habits[habit_id]['name']
                    st.metric(habit_name, f"{avg_rate:.0f}%")
''',
        
        "Project Task Dashboard": '''
def execute_tool():
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    from datetime import datetime, date, timedelta
    
    st.subheader("📋 Project Task Dashboard")
    
    # Initialize session state
    if 'projects' not in st.session_state:
        st.session_state.projects = {}
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []
    
    # Project management
    with st.expander("🚀 Manage Projects", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            new_project_name = st.text_input("Project Name")
            project_description = st.text_area("Description")
        with col2:
            project_deadline = st.date_input("Deadline")
            project_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        
        if st.button("Add Project") and new_project_name:
            project_id = len(st.session_state.projects)
            st.session_state.projects[project_id] = {
                'name': new_project_name,
                'description': project_description,
                'deadline': project_deadline,
                'priority': project_priority,
                'created_date': datetime.now().date()
            }
            st.success(f"Added project: {new_project_name}")
            st.rerun()
    
    if not st.session_state.projects:
        st.info("🎯 Create your first project to start managing tasks!")
        return
    
    # Task management
    with st.expander("➕ Add New Task", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task Title")
            task_project = st.selectbox("Project", 
                                      [(pid, proj['name']) for pid, proj in st.session_state.projects.items()],
                                      format_func=lambda x: x[1])
        with col2:
            task_status = st.selectbox("Status", ["To Do", "In Progress", "Completed"])
            task_priority = st.selectbox("Task Priority", ["Low", "Medium", "High"])
        with col3:
            task_due_date = st.date_input("Due Date")
            task_estimate = st.number_input("Estimated Hours", min_value=0.5, value=1.0, step=0.5)
        
        task_description = st.text_area("Task Description")
        
        if st.button("Add Task") and task_title and task_project:
            st.session_state.tasks.append({
                'id': len(st.session_state.tasks),
                'title': task_title,
                'description': task_description,
                'project_id': task_project[0],
                'status': task_status,
                'priority': task_priority,
                'due_date': task_due_date,
                'estimate': task_estimate,
                'created_date': datetime.now().date()
            })
            st.success(f"Added task: {task_title}")
            st.rerun()
    
    # Dashboard overview
    if st.session_state.tasks:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tasks = len(st.session_state.tasks)
            st.metric("Total Tasks", total_tasks)
        
        with col2:
            completed_tasks = len([t for t in st.session_state.tasks if t['status'] == 'Completed'])
            st.metric("Completed", completed_tasks)
        
        with col3:
            in_progress = len([t for t in st.session_state.tasks if t['status'] == 'In Progress'])
            st.metric("In Progress", in_progress)
        
        with col4:
            overdue_tasks = len([t for t in st.session_state.tasks 
                               if t['due_date'] < date.today() and t['status'] != 'Completed'])
            st.metric("Overdue", overdue_tasks, delta_color="inverse")
        
        # Project progress visualization
        st.subheader("📊 Project Progress")
        
        df_tasks = pd.DataFrame(st.session_state.tasks)
        df_tasks['project_name'] = df_tasks['project_id'].map(lambda x: st.session_state.projects[x]['name'])
        
        # Status distribution by project
        status_counts = df_tasks.groupby(['project_name', 'status']).size().unstack(fill_value=0)
        fig = px.bar(status_counts, title="Task Status by Project")
        st.plotly_chart(fig, use_container_width=True)
        
        # Task list with filters
        st.subheader("📝 Task Management")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_project = st.selectbox("Filter by Project", 
                                        ["All"] + [proj['name'] for proj in st.session_state.projects.values()])
        with col2:
            filter_status = st.selectbox("Filter by Status", 
                                       ["All", "To Do", "In Progress", "Completed"])
        with col3:
            filter_priority = st.selectbox("Filter by Priority", 
                                         ["All", "Low", "Medium", "High"])
        
        # Apply filters
        filtered_tasks = st.session_state.tasks.copy()
        if filter_project != "All":
            filtered_tasks = [t for t in filtered_tasks 
                            if st.session_state.projects[t['project_id']]['name'] == filter_project]
        if filter_status != "All":
            filtered_tasks = [t for t in filtered_tasks if t['status'] == filter_status]
        if filter_priority != "All":
            filtered_tasks = [t for t in filtered_tasks if t['priority'] == filter_priority]
        
        # Display tasks
        for task in filtered_tasks:
            project_name = st.session_state.projects[task['project_id']]['name']
            
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"**{task['title']}** ({project_name})")
                    if task['description']:
                        st.caption(task['description'])
                
                with col2:
                    new_status = st.selectbox("Status", 
                                            ["To Do", "In Progress", "Completed"],
                                            index=["To Do", "In Progress", "Completed"].index(task['status']),
                                            key=f"status_{task['id']}")
                    if new_status != task['status']:
                        # Update task status
                        for t in st.session_state.tasks:
                            if t['id'] == task['id']:
                                t['status'] = new_status
                                break
                        st.rerun()
                
                with col3:
                    priority_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
                    st.write(f"{priority_color[task['priority']]} {task['priority']}")
                    st.caption(f"Due: {task['due_date']}")
                
                with col4:
                    if st.button("🗑️", key=f"delete_{task['id']}", help="Delete task"):
                        st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                        st.rerun()
                
                st.divider()
    else:
        st.info("📝 Add your first task to see the dashboard in action!")
'''
    }
    
    return template_codes.get(template_name, "# Template code not available")
