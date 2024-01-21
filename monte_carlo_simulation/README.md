# Monte Carlo Psychrotolerant Sporeformer Simulation v3.0

## Overview
Welcome to my Monte Carlo Psychrotolerant Sporeformer Simulation project. This script is a robust example of my capabilities in statistical modeling and simulation, applied in the context of dairy spoilage prediction. It demonstrates the application of Monte Carlo methods to estimate bacterial growth in milk, using various growth models.

## Key Features of the Script
- **Statistical Growth Models:** Implements Buchanan, Baranyi, and Gompertz models to simulate bacterial growth, showcasing my ability to apply complex statistical methods in practical scenarios.
- **Data Handling and Processing:** Involves importing, cleaning, and preparing data for analysis, reflecting my skills in managing and manipulating data sets.
- **Monte Carlo Simulation:** Utilizes Monte Carlo techniques to model variability in bacterial growth, demonstrating my proficiency in probabilistic modeling and simulation.
- **Data Visualization:** Generates bar charts to visualize the simulation results, highlighting my experience in data presentation and interpretation.

## Relevance to Data Science
While the script is specifically tailored to dairy spoilage modeling, the underlying principles and techniques are broadly applicable across various data science domains. Key skills demonstrated in this script include:
- **Complex Problem Solving:** Ability to conceptualize and implement solutions to complex, real-world problems using data-driven approaches.
- **Statistical Analysis and Modeling:** Proficiency in applying statistical models to interpret and predict data patterns.
- **Simulation Techniques:** Expertise in using simulation methods to estimate and forecast outcomes under uncertainty.
- **Data Visualization:** Skill in creating visual representations of data to convey findings effectively.

## Usage
The script is designed to be used in an R environment. Adjust `seed_value` for reproducibility, set file paths for data input, and run the script to perform the simulation and generate visualizations.

## About the Author
I am Mike Phillips, a data scientist with a passion for applying my statistical and programming skills to solve diverse and challenging problems. My background in computational biology and data analytics has provided me with a strong foundation in various data science methodologies, which I enjoy applying to new domains.

Including an outline of your code in the README is a great idea. It provides a clear roadmap of what the script does, making it easier for readers to understand its structure and functionality. Here's how you can incorporate the outline into the README:

## Code Outline

This code is a Monte Carlo simulation of spore growth in half-gallon samples of milk over a specified number of days, using various growth models (Buchanan, Baranyi, Gompertz) to calculate the log10N count based on growth parameters. Below is an outline of the key steps and functionalities in the script:

1. **Seed Setting for Reproducibility:**
   - Initializes the simulation with a fixed seed value using `set.seed()`, ensuring reproducibility of results.

2. **Growth Parameter Calculation Functions:**
   - `muAtNewTemp()`: Calculates the new growth rate (mu) at a given temperature.
   - `lagAtNewTemp()`: Computes the new lag phase duration at a new temperature. Both functions adjust parameters based on changes in temperature.

3. **Growth Model Definitions:**
   - `buchanan_log10N()`, `gompertz_log10N()`, `baranyi_log10N()`: Functions to compute the log10N (the log of the bacterial count on day N) count using respective growth models.

4. **Wrapper Function for Growth Models:**
   - `log10N_func()`: Calls the appropriate growth model function based on the chosen model name.

5. **Data Frame Initialization:**
   - Creates a data frame `data` to store daily counts, structured by simulation runs (`n_sim`), half-gallon lots (`n_halfgal`), and days (`n_day`).

6. **Import and Setup of Initial Data:**
   - Loads frequency data, growth parameters, and initial counts from input files. Sets up the initial conditions for the simulation.

7. **Monte Carlo Sampling:**
   - Samples the [Most Probable Number (MPN) distribution](https://www.sciencedirect.com/topics/agricultural-and-biological-sciences/most-probable-number-technique) and temperature data. Calculates initial MPN for each half-gallon and samples the rpoB allelic type (AT) for each half-gallon.

8. **Simulation Execution:**
   - Iterates over each row in the data frame, calculating the log10N count for each day using growth parameters corresponding to the AT and sampled temperature.

9. **Result Storage:**
   - Stores the calculated log10N count in the `count` column of the data frame, completing the simulation process.
