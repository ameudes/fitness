#Library
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import streamlit.components.v1 as components
import json
import base64
import random
import numpy as np

# Data analysis
# Data analysis Part 1 (Welcome Page)
    ## Dataset Loading
fitness = pd.read_excel("Fitness.xlsx") 
    ## Participants list
participant=list(fitness['Nom'])
    ## Days
days = [col for col in fitness.columns if col.startswith("Jour")]

    ## Number of exercise days for men
fitness_men = fitness[fitness['Homme'] == 1]
fitness_men['Days'] = fitness_men[days].notna().sum(axis=1)
fitness_men=fitness_men[['Nom', 'Days']].sort_values(by='Days', ascending=False)
ranked_men = list(zip(fitness_men['Nom'], fitness_men['Days']))

    ## Number of exercise dfays for women
fitness_women = fitness[fitness['Homme'] == 0]
fitness_women['Days'] = fitness_women[days].notna().sum(axis=1)
fitness_women=fitness_women[['Nom', 'Days']].sort_values(by='Days', ascending=False)
ranked_women = list(zip(fitness_women['Nom'], fitness_women['Days']))


# Data analysis Part 2 (Individual Performance)
df = pd.read_excel("Fitness.xlsx") 
    ## Initial transformation Transform days in rows
df_long = df.melt(id_vars=["Nom", "Homme", "Programme"], value_vars=days,
                  var_name="Jour", value_name="Heure")
    ##  Identify valid days of working out
df_long["Valid"] = df_long["Heure"].notna()
    ## Compute number of valid workout days 
effectif_par_nom = df_long.groupby("Nom")["Valid"].sum().reset_index(name="valid")  
    ##  Program per participant
programme_par_nom = df[["Nom", "Programme"]]
    ## Merging to compute programm completion metric
metric_program_df = pd.merge(effectif_par_nom, programme_par_nom, on="Nom")
metric_program_df["metric_program"] = (metric_program_df["valid"] / (metric_program_df["Programme"] * 10)) * 100
    ## Add a delta to the metric
metric_program_df["metric_program_delta"] = (metric_program_df["valid"] - metric_program_df["valid"].mean()) / (metric_program_df["Programme"] * 10)*100
    ## Track the maximum number of consecutive working out days
df_long_sorted = df_long.sort_values(by=["Nom", "Jour"])
df_long_sorted["Valid_Int"] = df_long_sorted["Valid"].astype(int) # Create a helper column: 1 if valid, 0 if not
        ### Group by participant and compute max consecutive valid days
def max_consecutive_days(series):
    arr = series.values
    max_streak = 0
    current_streak = 0
    for v in arr:
        if v == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    return max_streak
consec_days = df_long_sorted.groupby("Nom")["Valid_Int"].apply(max_consecutive_days).reset_index(name="max_consec_days")
    ### Merge this new metric into the main metric_program_df
metric_program_df = pd.merge(metric_program_df, consec_days, on="Nom", how="left")
    ## Extract day number from "Jour" column and compute the week number
df_long_sorted["Jour_Num"] = df_long_sorted["Jour"].str.extract("(\d+)").astype(int)
df_long_sorted["Week"] = ((df_long_sorted["Jour_Num"] - 1) // 7) + 1
    ## Filter only valid workout days
df_valid = df_long_sorted[df_long_sorted["Valid"]]
    ## Count unique weeks per participant with at least one valid workout
weeks_active = df_valid.groupby("Nom")["Week"].nunique().reset_index(name="active_weeks")
        ### Merge into metric_program_df
metric_program_df = pd.merge(metric_program_df, weeks_active, on="Nom", how="left")
    ## Map an animal to each participant
beast_map = {
             "Eudes":"🐯 Tiger",
             "Bordas":"🦁 Lion",
             "Justine":"🐂 Taurus",
             "Arnec":"🦍 Gorilla",
             "Carel":"🦈 Shark",
             "Eloise":"🐎 Horse",
             "Pona":"🐬 Dolphin",
             "Rachid":"🐘 Elephant",
             "Toussaint":"🐻 Bear",
             "Mafouz":"🐃 Buffalo"}
metric_program_df["beast"] = metric_program_df["Nom"].map(beast_map)
    ## Add participant activity list
def presence_list(row):
    return [1 if pd.notna(row[day]) else 0 for day in days]
activity_series = df.set_index("Nom").apply(presence_list, axis=1)
metric_program_df = metric_program_df.set_index("Nom")
metric_program_df["activity"] = activity_series
metric_program_df = metric_program_df.reset_index()
    ## Add day frequency
days_columns = [f"Jour {i}" for i in range(1, 71)]
def count_weekly_sessions(row):
    counts = [0]*7  # index 0 = lundi, ..., 6 = dimanche
    for i, day in enumerate(days_columns):
        if pd.notna(row[day]):
            # i commence à 0 donc Jour 1 => i=0 donc %7 = 0 => lundi
            weekday = i % 7
            counts[weekday] += 1
    return counts
weekly_series = df.set_index("Nom").apply(count_weekly_sessions, axis=1)
metric_program_df = metric_program_df.set_index("Nom")
metric_program_df["weekly"] = weekly_series
metric_program_df = metric_program_df.reset_index()
    ## Add hour frequency
def extract_hour(h):
    if pd.isna(h):
        return np.nan
    try:
        return int(str(h).lower().split('h')[0])
    except:
        return np.nan

df_long['Hour_int'] = df_long['Heure'].apply(extract_hour)
df_valid_hours = df_long[df_long['Valid'] == True]

def count_hourly_sessions(group):
    counts = [0]*24
    hours = group['Hour_int'].dropna().astype(int)
    for h in hours:
        if 0 <= h <= 23:
            counts[h] += 1
    return counts
hourly_freq_series = df_valid_hours.groupby('Nom').apply(count_hourly_sessions)
metric_program_df = metric_program_df.set_index('Nom')
metric_program_df['hourly'] = hourly_freq_series
metric_program_df = metric_program_df.reset_index()









#Function to display our metric (container 1) depending on the delta

def metric (label, value, delta):
    return (
        f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-content">
                <div class="metric-value">{value}</div>
                <div class="metric-delta">+{delta}% <span style="color: green;">&#x25B2;</span></div>
            </div>
        </div>
        """
    ) if delta >=0 else (
        
        
        f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-content">
                <div class="metric-value">{value}</div>
                <div class="metric-delta">{delta}% <span style="color: red;">&#x25BC;</span></div>
            </div>
        </div>
        """
    )
        
#Function to display metric (container 2) depending on the delta        
def metric2 (label, value, delta):
    return (
        f"""
        <div class="metric-container2">
            <div class="metric-label">{label}</div>
            <div class="metric-content">
                <div class="metric-value2">{value}</div>
                <div class="metric-delta">+{delta}% <span style="color: green;">&#x25B2;</span></div>
            </div>
        </div>
        """
    ) if delta >=0 else (
        
        
        f"""
        <div class="metric-container2">
            <div class="metric-label">{label}</div>
            <div class="metric-content">
                <div class="metric-value2">{value}</div>
                <div class="metric-delta">{delta}% <span style="color: red;">&#x25BC;</span></div>
            </div>
        </div>
        """
    )
    
    
#Function to display metric (container 2) depending on the delta        
def metric_beast (label, value):
    return (
        f"""
        <div class="metric-container2">
            <div class="metric-label">{label}</div>
            <div class="metric-content">
                <div class="metric-value2">{value}</div>
            </div>
        </div>
        """
    )    
    







#############################

#Start building
st.set_page_config(layout="wide")

# Style Config
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

with open("style2.css") as f:
    css_styles = f"<style>{f.read()}</style>"

# Side bar

## Icone
image = Image.open("icone.png")


## Title and Image
st.sidebar.header("Fitness Goal Tracking")
st.sidebar.image(image, width=70)
st.sidebar.markdown("""---""")

## Menu
menu = st.sidebar.selectbox('MENU', ('General Overview', 'Individual level')) 

## Author
st.sidebar.markdown("""
<hr style="margin-top: 3rem; margin-bottom: 1rem;">
<div style='font-size: 0.85rem; color: grey;'>

<br>Created by **Eudes ADIBA**<br>

🔗 [LinkedIn](https://www.linkedin.com/in/eudes-adiba/) 📧 [Mail](mailto:eudes1adiba11@gmail.com)  
🐙 [Github](https://github.com/ameudes) 🧑‍🔬 [Research](https://orcid.org/0009-0000-6316-9100)

</div>
""", unsafe_allow_html=True)


# Navigation Menu 
## PAGE "GENERAL OVERVIEW"
if menu == 'General Overview':
    ### HEADER
    #st.header("GENERAL OVERVIEW OF ALL PARTICIPANTS")
    
    column1, column2 = st.columns(2)
    
    with column1 :
        
        st.markdown("### Men Ranking 🏋️‍♂️")
         


        # Generate HTML for each person
        rank_html = ""
        for i, (name, day) in enumerate(ranked_men, 1):
            trophy = ""
            if i == 1:
                trophy = "🥇"
            elif i == 2:
                trophy = "🥈"
            elif i == 3:
                trophy = "🥉"
            elif i == 4:
                trophy = "🔥"
            elif i == 5:
                trophy = "🔥"

            rank_html += f"""
            <div class="rank-item">
                <div class="rank-badge">{i}</div>
                <div class="rank-text">
                    <div class="name">{trophy} {name}</div>
                    <div class="days">{day} days</div>
                </div>
            </div>
            """

        rank= f"""
        <head>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap" rel="stylesheet">
        <style>
            .rank-list {{
                width: 100%;
                max-width: 340px;
                margin: auto;
                font-family: 'Montserrat', sans-serif;
            }}
            .rank-item {{
                display: flex;
                align-items: center;
                background: #fff;
                border: 1px solid #eee;
                border-left: 5px solid rgb(250, 111, 86);
                padding: 10px 14px;
                margin-bottom: 10px;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            }}
            .rank-badge {{
                width: 30px;
                height: 30px;
                background-color: rgb(250, 111, 86);
                color: white;
                font-weight: bold;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 12px;
                font-size: 14px;
            }}
            .rank-text .name {{
                font-size: 14px;
                font-weight: 600;
                color: #333;
            }}
            .rank-text .days {{
                font-size: 12px;
                color: #777;
            }}
        </style>
        </head>
        <body>
            <div class="rank-list">
                {rank_html}
            </div>
        </body>
        """

        components.html(rank, height=450)

    with column2:
        
        st.markdown("### Women Ranking 🏋️‍♀️")
         


        # Generate HTML for each person
        rank_html2 = ""
        for i, (name, day) in enumerate(ranked_women, 1):
            trophy = ""
            if i == 1:
                trophy = "🥇"
            elif i == 2:
                trophy = "🥈"
            elif i == 3:
                trophy = "🥉"

            rank_html2 += f"""
            <div class="rank-item">
                <div class="rank-badge">{i}</div>
                <div class="rank-text">
                    <div class="name">{trophy} {name}</div>
                    <div class="days">{day} days</div>
                </div>
            </div>
            """

        rank2= f"""
        <head>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap" rel="stylesheet">
        <style>
            .rank-list {{
                width: 100%;
                max-width: 340px;
                margin: auto;
                font-family: 'Montserrat', sans-serif;
            }}
            .rank-item {{
                display: flex;
                align-items: center;
                background: #fff;
                border: 1px solid #eee;
                border-left: 5px solid rgb(250, 111, 86);
                padding: 10px 14px;
                margin-bottom: 10px;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            }}
            .rank-badge {{
                width: 30px;
                height: 30px;
                background-color: rgb(250, 111, 86);
                color: white;
                font-weight: bold;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 12px;
                font-size: 14px;
            }}
            .rank-text .name {{
                font-size: 14px;
                font-weight: 600;
                color: #333;
            }}
            .rank-text .days {{
                font-size: 12px;
                color: #777;
            }}
        </style>
        </head>
        <body>
            <div class="rank-list">
                {rank_html2}
            </div>
        </body>
        """

        components.html(rank2, height=360)


## PAGE "INDIVIDUAL LEVEL"
elif menu == 'Individual level':
    #st.markdown("### Your dashboard")
    st.title("Your dashboard 📊")

    h1, h2= st.columns([2,1])
    with h1:
        st.markdown("<div style='height: 0px;'></div>", unsafe_allow_html=True)
        # Selection of a person
        selected_name = st.selectbox("", participant)
    #with h2:  
        #st.markdown("<div style='height: 1px;'></div>", unsafe_allow_html=True)
        #Download button    
        #components.html("""
        #    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
        #    <div style="margin-top: 20px;">
        #        <button onclick="capturePage()" style="padding: 10px 16px; background-color: #4CAF50; color: white; 
        #                border: none; border-radius: 4px; font-weight: bold; cursor: pointer;">
        #            📸 Download as PNG
        #        </button>
        #    </div>
        #    <script>
        #        function capturePage() {
        #            html2canvas(document.body).then(function(canvas) {
        #                var link = document.createElement('a');
        #                link.download = 'streamlit_page.png';
        #                link.href = canvas.toDataURL('image/png');
        #                link.click();
        #            });
        #        }
        #    </script>
        #""", height=70)

    
    #index = names.index(selected_name)
    #selected_days = days[index]
       
    ### Firt division in 2 columns
    c1, c2 = st.columns([1,3])
    
    ### SECOND column elements
    with c2:
        st.markdown("<div style='height: 23px;'></div>", unsafe_allow_html=True)
        #st.markdown("")
        #### First row of metrics
        col1, col2, col3 = st.columns(3, gap="medium")
        with col1: 
            st.markdown("")
            st.markdown(metric("#DAYS", round(list(metric_program_df[metric_program_df['Nom']==selected_name]['valid'])[0]),round(list(metric_program_df[metric_program_df['Nom']==selected_name]['valid'])[0]-metric_program_df["valid"].mean())),
            unsafe_allow_html=True)
        
        with col2: 
            st.markdown("")
            st.markdown(metric2("Plan (#days)",round(list(metric_program_df[metric_program_df['Nom']==selected_name]['Programme'])[0])*10,round(list(metric_program_df[metric_program_df['Nom']==selected_name]['valid'])[0]-metric_program_df["valid"].mean())),
            unsafe_allow_html=True)
            
        with col3: 
            st.markdown("")
            st.markdown(metric("% Program",round(list(metric_program_df[metric_program_df['Nom']==selected_name]['metric_program'])[0]),round(list(metric_program_df[metric_program_df['Nom']==selected_name]['metric_program_delta'])[0])),
            unsafe_allow_html=True)


        st.markdown("")
        
        #### Second row of metrics
        colu1, colu2, colu3= st.columns(3, gap="medium")
        with colu1: 
            st.markdown(metric2("Active Weeks",round(list(metric_program_df[metric_program_df['Nom']==selected_name]['active_weeks'])[0]),round(list(metric_program_df[metric_program_df['Nom']==selected_name]['active_weeks'])[0]-metric_program_df["active_weeks"].mean())),
            unsafe_allow_html=True)            
        with colu2: 
            st.markdown(metric("Max Streak", round(list(metric_program_df[metric_program_df['Nom']==selected_name]['max_consec_days'])[0]),round(list(metric_program_df[metric_program_df['Nom']==selected_name]['max_consec_days'])[0]-metric_program_df["max_consec_days"].mean())),
            unsafe_allow_html=True)
        with colu3: 
            st.markdown(metric_beast("Beast mode",list(metric_program_df[metric_program_df['Nom']==selected_name]['beast'])[0]),
            unsafe_allow_html=True)
            
        #### Third row : Activity map
        activity_data = list(metric_program_df[metric_program_df['Nom']==selected_name]['activity'])[0]
        activity_json = json.dumps(activity_data)
        st.markdown("")
        st.markdown("##### Activity (70 days)")     
        heatmap_html = f"""
        {css_styles}
        <div class="heatmap" id="heatmap"></div>

        <script>
        const activity = {activity_json};
        const weeks = 10;
        const daysPerWeek = 7;
        const heatmap = document.getElementById("heatmap");

        let index = 0;
        for (let w = 0; w < weeks; w++) {{
            const weekColumn = document.createElement("div");
            weekColumn.classList.add("week");

            for (let d = 0; d < daysPerWeek; d++) {{
            const daySquare = document.createElement("div");
            daySquare.classList.add("day");

            if (activity[index] === 1) {{
                daySquare.classList.add("active");
            }}

            weekColumn.appendChild(daySquare);
            index++;
            }}

            heatmap.appendChild(weekColumn);
        }}
        </script>
        """
        components.html(heatmap_html, height=100, scrolling=False)            
            
    ### FIRST COLUMN ELEMENTS        
    with c1:
        st.markdown("<div style='height: 0px;'></div>", unsafe_allow_html=True)
        image_path = "image/gym.jpg" 
        image_best=f"image/{selected_name}.jpg"
        name=selected_name
        with open(image_path, "rb") as img_file:
            base64_img = base64.b64encode(img_file.read()).decode()
            image_html = f"""
            <head>
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap" rel="stylesheet">
            </head>
            <div style="display: flex; justify-content: center; align-items: center;">
            <div style="position: relative; width: 200px; height: 200px; font-family: 'Montserrat', sans-serif;">
                <img src="data:image/jpeg;base64,{base64_img}" alt="Image"
                    style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;">
                
                <div style="position: absolute; top: 0; left: 0;
                            width: 100%; height: 100%;
                            background-color: rgba(0, 0, 0, 0.4); 
                            border-radius: 8px;
                            display: flex; justify-content: center; align-items: center;">
                            
                <p style="color: white; font-size: 16px; font-weight: 600; text-align: center; margin: 0;">
                    🔥 {name} you did {list(metric_program_df[metric_program_df['Nom']==selected_name]['max_consec_days'])[0]} days without interruption 💪 
                </p>
                
                </div>
            </div>
            </div>
            """
        with open(image_best, "rb") as best_file:
            best_img = base64.b64encode(best_file.read()).decode()    
            best = f"""
            <head>
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap" rel="stylesheet">
            </head>
            <div style="display: flex; justify-content: center; align-items: center;">
            <div style="position: relative; width: 200px; height: 150px; font-family: 'Montserrat', sans-serif;">
                <img src="data:image/jpeg;base64,{best_img}" alt="Image"
                    style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;">
                
                <div style="position: absolute; top: 0; left: 0;
                            width: 100%; height: 100%;
                            background-color: rgba(0, 0, 0, 0.4); 
                            border-radius: 8px;
                            display: flex; justify-content: center; align-items: center;">
                            
                <div style="position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%);
                color: white; font-size: 16px; font-weight: 600; font-family: 'Montserrat', sans-serif;
                text-align: center;">
                    Best pic 🏋️‍♂️
                </div>
                
                </div>
            </div>
            </div>
            """
        st.markdown("<div style='height: 0px;'></div>", unsafe_allow_html=True)
        components.html(image_html, height=200)
        #st.markdown(        """
        #<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap" rel="stylesheet">
        #<div style='text-align: center; font-family: "Montserrat", sans-serif; 
        #            font-size: 18px; color: #000000;'>
        #    Truly amazing!
        #</div>
        #""",unsafe_allow_html=True)
        components.html(best, height=200)
    
    ### Another element after the first division in two columns
    colum1, colum2= st.columns(2)
    
    with colum2 : 
        st.markdown('##### Weekly consistency')
        #### Weekly distribution Monday to Friday
        values = list(metric_program_df[metric_program_df['Nom']==selected_name]['weekly'])[0]  # Values for Mon–Sun
        labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        #### Chart size
        svg_width = 450
        svg_height = 150
        bar_width = 20
        bar_spacing = 0
        margin_top = 30
        margin_bottom = 20

        max_val = max(values)

        #### Normalize values to bar heights
        normalized_heights = [(v / max_val) * (svg_height - margin_top - margin_bottom) for v in values]
        x_positions = np.linspace(30, svg_width - 30 - bar_width, len(values))
        
        #### Create bars and labels
        svg_bars = ""
        svg_labels = ""
        for i, (x, h) in enumerate(zip(x_positions, normalized_heights)):
            y = svg_height - margin_bottom - h
            svg_bars += f'<rect x="{x}" y="{y}" width="{bar_width}" height="{h}" fill="rgb(250, 111, 86)" rx="4" />'
            svg_labels += f'<text x="{x + bar_width / 2}" y="{svg_height - 5}" text-anchor="middle" font-size="14" fill="#333">{labels[i]}</text>'

        #### Combine HTML + SVG
        svg_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap" rel="stylesheet">
        <style>
            .chart-container {{
                width: 100%;
                max-width: 800px;
                margin: auto;
                font-family: 'Montserrat', sans-serif;
            }}
        </style>
        </head>
        <body>
        <div class="chart-container">
            <svg viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">
                {svg_bars}
                {svg_labels}
            </svg>
        </div>
        </body>
        </html>
        """

        #### Display weekly frequency in Streamlit
        st.components.v1.html(svg_html, height=400)

    with colum1: 
        st.markdown('##### Workout hours')
        #### Weekly distribution Monday to Friday
        activity_by_hour = list(metric_program_df[metric_program_df['Nom']==selected_name]['hourly'])[0]

        html_segments = ""
        for i in range(24):
            # 
            angle = (i - 6) * 15
            color = "rgb(250, 111, 86)" if activity_by_hour[i]==max(activity_by_hour) else "#e0e0e0"
            html_segments += f'''
                <div class="hour" style="transform: rotate({angle}deg) translate(100px) rotate(-{angle}deg); background-color: {color};">
                    {i}
                </div>
            '''

        html_code = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500&display=swap" rel="stylesheet">
            <style>
                .clock {{
                    position: relative;
                    width: 300px;
                    height: 300px;
                    border-radius: 50%;
                    margin: auto;
                    background: #fff;
                    box-shadow: inset 0 0 10px #ccc;
                    overflow: visible;
                }}
                .hour {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    width: 30px;
                    height: 30px;
                    margin: -15px;
                    border-radius: 50%;
                    font-family: 'Montserrat', sans-serif;
                    font-size: 10px;
                    font-weight: 500;
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .center-icon {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="clock">
                {html_segments}
                <div class="center-icon">🕒</div>
            </div>
        </body>
        </html>
        """

        components.html(html_code, height=380)


