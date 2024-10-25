import tkinter as tk
from tkinter import messagebox
from fuzzy_logic import compute_need_for_action

def compute_action():
    try:
        # Get input values from GUI
        veg_cover_input = float(entry_veg_cover.get())
        build_density_input = float(entry_build_density.get())
        air_pollution_input = float(entry_air_pollution.get())
        population_density_input = float(entry_population_density.get())

        # Validate inputs
        if not (0 <= veg_cover_input <= 100):
            raise ValueError("Vegetation Cover must be between 0 and 100.")
        if not (0 <= build_density_input <= 100):
            raise ValueError("Building Density must be between 0 and 100.")
        if not (0 <= air_pollution_input <= 150):
            raise ValueError("Air Pollution must be between 0 and 150 µg/m³.")
        if not (0 <= population_density_input <= 20000):
            raise ValueError("Population Density must be between 0 and 20,000 people/km².")

        # Compute need for action
        na_score, na_level = compute_need_for_action(
            veg_cover_input, build_density_input, air_pollution_input, population_density_input
        )

        # Display results
        label_na_score.config(text=f"Need for Action Score: {na_score:.2f}")
        label_na_level.config(text=f"Need for Action Level: {na_level}")

        # Display recommendations
        if na_level == "High Need":
            recommendations = (
                "- Increase vegetation cover.\n"
                "- Implement green roofs and walls.\n"
                "- Use reflective surface materials.\n"
                "- Reduce emissions from traffic and industry."
            )
        elif na_level == "Moderate Need":
            recommendations = (
                "- Enhance existing green spaces.\n"
                "- Promote sustainable practices.\n"
                "- Monitor air quality."
            )
        else:
            recommendations = (
                "- Maintain current practices.\n"
                "- Engage the community in sustainability efforts."
            )
        text_recommendations.config(state=tk.NORMAL)
        text_recommendations.delete(1.0, tk.END)
        text_recommendations.insert(tk.END, recommendations)
        text_recommendations.config(state=tk.DISABLED)

    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create the GUI
root = tk.Tk()
root.title("Need for Green Infrastructure Action Assessment")

# Vegetation Cover (%)
label_veg_cover = tk.Label(root, text="Vegetation Cover (%)")
label_veg_cover.grid(row=0, column=0, padx=10, pady=5, sticky='e')
entry_veg_cover = tk.Entry(root)
entry_veg_cover.grid(row=0, column=1, padx=10, pady=5)

# Building Density (%)
label_build_density = tk.Label(root, text="Building Density (%)")
label_build_density.grid(row=1, column=0, padx=10, pady=5, sticky='e')
entry_build_density = tk.Entry(root)
entry_build_density.grid(row=1, column=1, padx=10, pady=5)

# Air Pollution (µg/m³)
label_air_pollution = tk.Label(root, text="Air Pollution (µg/m³)")
label_air_pollution.grid(row=2, column=0, padx=10, pady=5, sticky='e')
entry_air_pollution = tk.Entry(root)
entry_air_pollution.grid(row=2, column=1, padx=10, pady=5)

# Population Density (people/km²)
label_population_density = tk.Label(root, text="Population Density (people/km²)")
label_population_density.grid(row=3, column=0, padx=10, pady=5, sticky='e')
entry_population_density = tk.Entry(root)
entry_population_density.grid(row=3, column=1, padx=10, pady=5)

# Compute Button
button_compute = tk.Button(root, text="Compute", command=compute_action)
button_compute.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Display Results
label_na_score = tk.Label(root, text="Need for Action Score: ")
label_na_score.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

label_na_level = tk.Label(root, text="Need for Action Level: ")
label_na_level.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

# Recommendations
label_recommendations = tk.Label(root, text="Recommendations:")
label_recommendations.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

text_recommendations = tk.Text(root, width=50, height=5, state=tk.DISABLED)
text_recommendations.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

# Start the GUI main loop
root.mainloop()
