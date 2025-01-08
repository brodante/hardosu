import os
import time
import random
import pyautogui
import keyboard
import pygetwindow as gw  # Import pygetwindow
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

# A function to simulate perfect timing with slight human-like randomness
def simulate_perfect_timing(beatmap_timing):
    """
    Simulate human-like perfect timing behavior for osu!
    Presses the correct key at perfect timing with slight variations.
    """
    for timing in beatmap_timing:
        # Calculate the time until the note should be hit
        time_to_wait = timing['time'] - time.time()  # Timing difference
        if time_to_wait > 0:
            time.sleep(time_to_wait)
        
        # Introduce slight randomness in when the key is pressed
        # Random variation between -50ms and +50ms
        random_delay = random.uniform(-0.05, 0.05)
        time.sleep(random_delay)
        
        # Simulate keypress (e.g., 'z' for perfect timing)
        pyautogui.press('z')
        print(f"Pressed 'z' for timing: {timing['time']} with delay: {random_delay}")

# A function to simulate imperfect timing with human-like variation
def simulate_imperfect_timing(beatmap_timing):
    """
    Simulate human-like imperfect timing behavior for osu!
    Introduces some error, so it's not always perfect 300 timing.
    """
    for timing in beatmap_timing:
        # Calculate the time until the note should be hit
        time_to_wait = timing['time'] - time.time()  # Timing difference
        if time_to_wait > 0:
            time.sleep(time_to_wait)
        
        # Introduce a human-like error
        error = random.uniform(-0.2, 0.2)  # Error in timing, more variation
        time.sleep(error)
        
        # Simulate keypress (e.g., 'z' for imperfect timing)
        pyautogui.press('z')
        print(f"Pressed 'z' for timing: {timing['time']} with error: {error}")


# Function to get osu! directory from the file
def get_osu_directory():
    osu_directory_path = "config/osu_directory.txt"
    if os.path.exists(osu_directory_path):
        with open(osu_directory_path, 'r') as file:
            return file.read().strip()
    else:
        print("osu! directory not found in osu_directory.txt!")
        return None

# Function to parse beatmaps and group by map name with respective difficulties
def get_beatmaps(osu_songs_directory):
    beatmaps = {}
    for root, dirs, files in os.walk(osu_songs_directory):
        for file in files:
            if file.endswith(".osu"):
                # Extract the map name and difficulty from the file path
                parts = root.split(os.path.sep)
                map_name = parts[-1]  # Example: Thaehan - Insert Coin
                difficulty = file.split("[")[1].split("]")[0]  # Example: Hard

                # Group the beatmaps by map name
                if map_name not in beatmaps:
                    beatmaps[map_name] = []
                beatmaps[map_name].append(difficulty)
    return beatmaps

# Function to display a menu for selecting difficulty
def choose_difficulty(difficulties):
    print("\nChoose a difficulty:")
    for idx, difficulty in enumerate(difficulties, 1):
        print(f"{idx}. {difficulty}")
    
    try:
        selection = int(input("\nEnter the number corresponding to your choice: "))
        if 1 <= selection <= len(difficulties):
            return difficulties[selection - 1]
        else:
            print("Invalid selection.")
            return None
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None

# Function to select the mode (perfect or imperfect)
def choose_mode():
    print("\nSelect mode:")
    print("1. Perfect Timing (z)")
    print("2. Imperfect Timing (x)")

    # Wait for z or x keypress to start the mode
    while True:
        if keyboard.is_pressed('z'):
            current_time = time.time()
            print(f"Pressed 'z' at {current_time:.2f} seconds - Starting perfect timing mode...")
            return "perfect"
        elif keyboard.is_pressed('x'):
            current_time = time.time()
            print(f"Pressed 'x' at {current_time:.2f} seconds - Starting imperfect timing mode...")
            return "imperfect"
        time.sleep(0.1)  # Check for the key press repeatedly

def get_beatmap_timing(map_name, difficulty, osu_file_path):
    osu_directory = get_osu_directory()
    if osu_directory:
        osu_songs_directory = os.path.join(osu_directory, 'Songs', map_name, difficulty)
        
        # Ensure the file exists
        if os.path.exists(osu_file_path):
            with open(osu_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            # Find the [HitObjects] section
            hit_objects_start = False
            beatmap_timing = []

            for line in lines:
                if line.strip() == "[HitObjects]":
                    hit_objects_start = True
                    continue
                
                if hit_objects_start:
                    # Process lines in the [HitObjects] section
                    parts = line.strip().split(',')
                    if len(parts) >= 5:
                        time_ms = int(parts[2])  # Time in milliseconds
                        note_type = "circle"  # Default to circle, could extend for sliders, etc.

                        if int(parts[3]) == 1:
                            note_type = "slider"
                        elif int(parts[3]) == 2:
                            note_type = "spinner"
                        
                        # Convert milliseconds to seconds
                        beatmap_timing.append({
                            'time': time_ms / 1000.0,
                            'note_type': note_type
                        })
            
            return beatmap_timing
        else:
            print(f"Could not find beatmap file at: {osu_file_path}")
            return []
    else:
        print("osu! directory not found!")
        return []

# Function to open the beatmap folder and scan for difficulty
def open_beatmap_folder_and_scan_for_difficulty(osu_songs_directory, selected_map_name, difficulty):
    # Construct the folder path for the selected map
    map_folder_path = os.path.join(osu_songs_directory, selected_map_name)
    
    # Open the folder in the file explorer
    if os.path.exists(map_folder_path):
        print(f"Opening folder: {map_folder_path}")
        os.startfile(map_folder_path)  # This will open the folder in file explorer
        
        # Scan for the correct .osu file that matches the difficulty
        for file in os.listdir(map_folder_path):
            if file.endswith(".osu") and difficulty in file:
                print(f"Found .osu file for {difficulty}: {file}")
                osu_file_path = os.path.join(map_folder_path, file)  # Full file path including the map name and difficulty
                return osu_file_path
        print(f"Could not find .osu file for difficulty: {difficulty}")
        return None
    else:
        print(f"Map folder not found: {map_folder_path}")
        return None


# Function to check if osu! window is active
def is_osu_window_active():
    try:
        active_window = gw.getActiveWindow()
        if active_window and "osu!" in active_window.title.lower():
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking window: {e}")
        return False


# Function to log all key presses
def log_key_presses():
    print("Press any key to log the press with a timestamp. Press 'esc' to stop.")
    
    while True:
        event = keyboard.read_event()  # Wait for any key event
        
        if event.event_type == keyboard.KEY_DOWN:  # When a key is pressed down
            key = event.name
            current_time = time.time()
            print(f"Key '{key}' pressed at {current_time:.2f} seconds.")
        
        # Stop logging when 'esc' is pressed
        if keyboard.is_pressed('esc'):
            print("Exiting key logging...")
            break


# Main function to initialize
def main():
    osu_directory = get_osu_directory()
    if osu_directory:
        print(f"Using saved osu! directory: {osu_directory}")
        osu_songs_directory = os.path.join(osu_directory, 'Songs')
        print(f"Using osu! Songs directory: {osu_songs_directory}")

        # Get list of beatmaps
        beatmaps = get_beatmaps(osu_songs_directory)
        print(f"Found {len(beatmaps)} beatmaps.")
        
        # Display beatmaps for selection
        print("\nAvailable Beatmaps:")
        for idx, map_name in enumerate(beatmaps.keys(), 1):
            print(f"{idx}. {map_name}")

        try:
            map_selection = int(input("\nEnter the number corresponding to your map choice: "))
            if 1 <= map_selection <= len(beatmaps):
                selected_map_name = list(beatmaps.keys())[map_selection - 1]
                difficulties = beatmaps[selected_map_name]

                # Display and choose difficulty
                difficulty = choose_difficulty(difficulties)
                if difficulty:
                    print(f"You selected: {selected_map_name} - {difficulty}")
                    # Open the map folder and scan for the selected difficulty
                    osu_file_path = open_beatmap_folder_and_scan_for_difficulty(osu_songs_directory, selected_map_name, difficulty)
                    if osu_file_path:
                        print("\nGo in the game window and tap the first beat with 'z' for perfect mode or 'x' for imperfect mode to start.")
                        
                        # Wait for Z or X key press to start
                        mode = choose_mode()  # This will wait for keypress and start mode

                        # Fetch beatmap timing data
                        beatmap_timing = get_beatmap_timing(selected_map_name, difficulty, osu_file_path)

                        # Run the appropriate function based on mode
                        if mode == "perfect":
                            simulate_perfect_timing(beatmap_timing)
                        elif mode == "imperfect":
                            simulate_imperfect_timing(beatmap_timing)
                    else:
                        print("Failed to find the beatmap file. Exiting...")
                        return
                else:
                    print("Invalid difficulty selection.")
            else:
                print("Invalid map selection.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        
        # Optionally start logging keys in the background
        log_key_presses()

    else:
        print("Failed to load osu! directory. Please ensure osu_directory.txt is present.")


if __name__ == "__main__":
    main()
