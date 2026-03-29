"""
F1 Telemetry Analysis - Helper Functions
Reusable utilities for F1 data analysis
"""

import fastf1
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib import cm

def load_session_cached(year, gp, session_type, cache_dir='../data_cache'):
    """
    Load F1 session with caching enabled
    
    Parameters:
    -----------
    year : int
        Season year
    gp : str
        Grand Prix name
    session_type : str
        'R', 'Q', 'FP1', 'FP2', 'FP3', 'S'
    cache_dir : str
        Cache directory path
    
    Returns:
    --------
    session : fastf1.Session
        Loaded session object
    """
    fastf1.Cache.enable_cache(cache_dir)
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    return session


def clean_lap_data(laps, max_time=200):
    """
    Clean lap data by removing outliers and converting times
    
    Parameters:
    -----------
    laps : pd.DataFrame
        Laps dataframe from FastF1
    max_time : float
        Maximum valid lap time in seconds
    
    Returns:
    --------
    clean_laps : pd.DataFrame
        Cleaned dataframe with time in seconds
    """
    clean_laps = laps.copy()
    
    # Convert timedelta to seconds
    clean_laps['LapTime_sec'] = clean_laps['LapTime'].dt.total_seconds()
    clean_laps['Sector1Time_sec'] = clean_laps['Sector1Time'].dt.total_seconds()
    clean_laps['Sector2Time_sec'] = clean_laps['Sector2Time'].dt.total_seconds()
    clean_laps['Sector3Time_sec'] = clean_laps['Sector3Time'].dt.total_seconds()
    
    # Remove outliers (pit laps, safety car, etc.)
    clean_laps = clean_laps[
        (clean_laps['LapTime_sec'] > 0) & 
        (clean_laps['LapTime_sec'] < max_time)
    ]
    
    return clean_laps


def get_driver_color(driver_code):
    """
    Get team color for a driver
    
    Parameters:
    -----------
    driver_code : str
        Three-letter driver code (e.g., 'VER', 'HAM')
    
    Returns:
    --------
    color : str
        Hex color code
    """
    driver_colors = {
        'VER': '#0600EF',  # Red Bull
        'PER': '#0600EF',
        'HAM': '#00D2BE',  # Mercedes
        'RUS': '#00D2BE',
        'LEC': '#DC0000',  # Ferrari
        'SAI': '#DC0000',
        'NOR': '#FF8700',  # McLaren
        'PIA': '#FF8700',
        'ALO': '#006F62',  # Aston Martin
        'STR': '#006F62',
        'OCO': '#0090FF',  # Alpine
        'GAS': '#0090FF',
        'BOT': '#900000',  # Alfa Romeo
        'ZHO': '#900000',
        'MAG': '#FFFFFF',  # Haas
        'HUL': '#FFFFFF',
        'TSU': '#2B4562',  # AlphaTauri
        'RIC': '#2B4562',
        'ALB': '#005AFF',  # Williams
        'SAR': '#005AFF',
    }
    
    return driver_colors.get(driver_code, '#808080')


def plot_speed_comparison(driver_laps_list, driver_codes, title="Speed Comparison"):
    """
    Plot speed comparison for multiple drivers
    
    Parameters:
    -----------
    driver_laps_list : list
        List of fastest lap objects for each driver
    driver_codes : list
        List of driver codes
    title : str
        Plot title
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
    ax : matplotlib.axes.Axes
    """
    fig, ax = plt.subplots(figsize=(16, 7))
    
    for lap, driver in zip(driver_laps_list, driver_codes):
        tel = lap.get_telemetry().add_distance()
        color = get_driver_color(driver)
        
        ax.plot(tel['Distance'], tel['Speed'], 
                label=driver, color=color, linewidth=2.5)
        ax.fill_between(tel['Distance'], 0, tel['Speed'], 
                        alpha=0.1, color=color)
    
    ax.set_xlabel('Distance (m)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Speed (km/h)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig, ax


def plot_gear_map(lap, driver_code):
    """
    Create a colored track map showing gear usage
    
    Parameters:
    -----------
    lap : fastf1.Lap
        Lap object
    driver_code : str
        Driver code
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
    ax : matplotlib.axes.Axes
    """
    tel = lap.get_telemetry()
    
    x = tel['X']
    y = tel['Y']
    color = tel['nGear']
    
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    cmap = cm.get_cmap('viridis')
    lc = LineCollection(segments, cmap=cmap, norm=plt.Normalize(1, 8), 
                       linewidth=4, alpha=0.8)
    lc.set_array(color)
    
    ax.add_collection(lc)
    ax.axis('equal')
    ax.tick_params(labelleft=False, labelbottom=False, 
                  left=False, bottom=False)
    
    cbar = plt.colorbar(lc, ax=ax, label='Gear', ticks=range(1, 9))
    cbar.ax.set_yticklabels(['1', '2', '3', '4', '5', '6', '7', '8'])
    
    ax.set_title(f'{driver_code} - Gear Usage Map', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig, ax


def calculate_stint_stats(laps):
    """
    Calculate statistics for each stint
    
    Parameters:
    -----------
    laps : pd.DataFrame
        Laps dataframe
    
    Returns:
    --------
    stint_stats : pd.DataFrame
        Statistics per stint
    """
    laps_clean = clean_lap_data(laps)
    
    stint_stats = laps_clean.groupby('Stint').agg({
        'LapNumber': ['min', 'max', 'count'],
        'LapTime_sec': ['mean', 'min', 'std'],
        'Compound': 'first',
        'TyreLife': 'max'
    }).reset_index()
    
    stint_stats.columns = [
        'Stint', 'Start_Lap', 'End_Lap', 'Num_Laps',
        'Avg_Time', 'Fastest_Time', 'Std_Dev', 'Compound', 'Tyre_Life'
    ]
    
    return stint_stats


def detect_overtakes(session, driver1, driver2):
    """
    Detect potential overtakes between two drivers
    
    Parameters:
    -----------
    session : fastf1.Session
        Session object
    driver1 : str
        First driver code
    driver2 : str
        Second driver code
    
    Returns:
    --------
    overtakes : list
        List of lap numbers where position changes occurred
    """
    laps1 = session.laps.pick_driver(driver1)[['LapNumber', 'Position']]
    laps2 = session.laps.pick_driver(driver2)[['LapNumber', 'Position']]
    
    merged = pd.merge(laps1, laps2, on='LapNumber', suffixes=('_1', '_2'))
    
    overtakes = []
    for i in range(len(merged) - 1):
        curr_pos1 = merged.iloc[i]['Position_1']
        curr_pos2 = merged.iloc[i]['Position_2']
        next_pos1 = merged.iloc[i + 1]['Position_1']
        next_pos2 = merged.iloc[i + 1]['Position_2']
        
        # Check if positions swapped
        if curr_pos1 > curr_pos2 and next_pos1 < next_pos2:
            overtakes.append({
                'lap': merged.iloc[i + 1]['LapNumber'],
                'overtaker': driver1,
                'overtaken': driver2
            })
        elif curr_pos1 < curr_pos2 and next_pos1 > next_pos2:
            overtakes.append({
                'lap': merged.iloc[i + 1]['LapNumber'],
                'overtaker': driver2,
                'overtaken': driver1
            })
    
    return overtakes


def calculate_pace_delta(laps1, laps2):
    """
    Calculate average pace delta between two drivers
    
    Parameters:
    -----------
    laps1 : pd.DataFrame
        Laps for driver 1
    laps2 : pd.DataFrame
        Laps for driver 2
    
    Returns:
    --------
    delta : float
        Average time difference in seconds
    """
    laps1_clean = clean_lap_data(laps1)
    laps2_clean = clean_lap_data(laps2)
    
    avg1 = laps1_clean['LapTime_sec'].mean()
    avg2 = laps2_clean['LapTime_sec'].mean()
    
    return avg1 - avg2


def get_tyre_degradation(laps, compound=None):
    """
    Calculate tyre degradation rate
    
    Parameters:
    -----------
    laps : pd.DataFrame
        Laps dataframe
    compound : str, optional
        Filter by specific compound
    
    Returns:
    --------
    degradation : pd.DataFrame
        Degradation data with lap time vs tyre age
    """
    laps_clean = clean_lap_data(laps)
    
    if compound:
        laps_clean = laps_clean[laps_clean['Compound'] == compound]
    
    # Group by tyre age
    degradation = laps_clean.groupby('TyreLife').agg({
        'LapTime_sec': ['mean', 'std', 'count']
    }).reset_index()
    
    degradation.columns = ['TyreLife', 'Avg_LapTime', 'Std_LapTime', 'Count']
    
    return degradation


def format_laptime(seconds):
    """
    Format lap time from seconds to MM:SS.mmm
    
    Parameters:
    -----------
    seconds : float
        Lap time in seconds
    
    Returns:
    --------
    formatted : str
        Formatted time string
    """
    if pd.isna(seconds):
        return "N/A"
    
    minutes = int(seconds // 60)
    secs = seconds % 60
    
    return f"{minutes}:{secs:06.3f}"


def get_session_summary(session):
    """
    Generate a summary of the session
    
    Parameters:
    -----------
    session : fastf1.Session
        Session object
    
    Returns:
    --------
    summary : dict
        Dictionary with session statistics
    """
    laps = session.laps
    laps_clean = clean_lap_data(laps)
    
    summary = {
        'event_name': session.event['EventName'],
        'event_date': session.event['EventDate'],
        'location': session.event['Location'],
        'session_type': session.name,
        'total_laps': len(laps),
        'total_drivers': laps['Driver'].nunique(),
        'fastest_lap': laps_clean['LapTime_sec'].min(),
        'fastest_driver': laps_clean.loc[laps_clean['LapTime_sec'].idxmin(), 'Driver'],
        'compounds_used': laps['Compound'].unique().tolist()
    }
    
    return summary


# Example usage in notebooks:
"""
from utils.f1_helper import *

# Load session
session = load_session_cached(2021, 'Abu Dhabi', 'R')

# Get clean data
laps = clean_lap_data(session.laps)

# Compare drivers
ver_laps = session.laps.pick_driver('VER')
ham_laps = session.laps.pick_driver('HAM')

ver_fastest = ver_laps.pick_fastest()
ham_fastest = ham_laps.pick_fastest()

fig, ax = plot_speed_comparison([ver_fastest, ham_fastest], ['VER', 'HAM'])
plt.show()

# Get session summary
summary = get_session_summary(session)
print(summary)
"""