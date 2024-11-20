import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re 

def parse_input(input_data):
    # Handle input that's already a list of lines
    if isinstance(input_data, list):
        lines = input_data
    # If it's a string, split into lines
    elif isinstance(input_data, str):
        lines = input_data.strip().split('\n')
    else:
        raise ValueError("Input must be a string or list of lines")
    
    rows, cols = 8, 12  # Define grid dimensions
    grid = np.full((rows, cols), np.nan, dtype=object)

    # Regular expression to match the expected format
    line_regex = re.compile(r'\[(\d+),(\d+)\]\s*,\s*\{\d+\}\s*,\s*(\w+)')

    for line_number, line in enumerate(lines, 1):
        try:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Use regex to extract the parts from each line
            match = line_regex.match(line)
            if not match:
                print(f"Skipping improperly formatted line {line_number}: {line}")
                continue

            # Extract position and container from the regex match
            row_str, col_str, container = match.groups()
            
            # Debugging output for row and column strings
            print(f"Debug: row_str: '{row_str}', col_str: '{col_str}' at line {line_number}")

            # Convert to zero-based indices
            row = rows - int(row_str)
            col = int(col_str) - 1

            # Validate row and column
            if 0 <= row < rows and 0 <= col < cols:
                # Debugging output for container value
                print(f"Debug: Container at line {line_number}: '{container}'")

                # Fill grid cell based on container type
                if container == 'NAN':
                    grid[row, col] = np.nan
                elif container == 'UNUSED':
                    grid[row, col] = "UNUSED"  # Set unused cells as a distinct string
                else:
                    grid[row, col] = container
            else:
                print(f"Invalid position at line {line_number}: {line} (row: {row}, col: {col})")
        
        except Exception as e:
            print(f"Error processing line {line_number}: {line}")
            print(f"Error details: {e}")
    
    return grid

def display_grid(grid, title="Grid Layout"):
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_title(title, fontsize=16)

    # Loop through the grid and display cells
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            value = grid[i, j]

            # Determine color and text based on cell value
            if pd.isna(value):  # NAN cells
                color = "lightgray"
                text = "NAN"
            elif value == "UNUSED":  # UNUSED cells
                color = "white"
                text = "UNUSED"
            else:  # Valid container values
                color = "lightblue"
                text = str(value)

            # Add colored rectangle
            ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=color, edgecolor='black', linewidth=1))

            # Add text to cell
            if text:  # Only add text if it's not empty
                ax.text(j + 0.5, i + 0.5, text, color='black',
                        ha='center', va='center', fontsize=10)

    # Set grid properties
    ax.set_xlim(0, grid.shape[1])
    ax.set_ylim(0, grid.shape[0])
    ax.set_xticks(np.arange(grid.shape[1]) + 0.5)
    ax.set_yticks(np.arange(grid.shape[0]) + 0.5)
    ax.set_xticklabels(range(1, grid.shape[1] + 1))
    ax.set_yticklabels(range(1, grid.shape[0] + 1))
    ax.grid(True, color='black', linestyle='-', linewidth=0.5)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

