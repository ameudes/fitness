# Fitness

A personal dashboard project analyzing fitness data and visualizing metrics. You can access the dashboard here  : https://fitnessgoal.streamlit.app/ 

## Overview 
<img width="1877" height="775" alt="Screenshot 2025-10-13 173824" src="https://github.com/user-attachments/assets/2cd0f900-1e0f-4994-ac0e-2a79e45aa7ae" />
<img width="1721" height="781" alt="Screenshot 2025-10-13 173919" src="https://github.com/user-attachments/assets/2432aa6b-9b26-4bd3-91a5-46cba4dcd2c9" />
<img width="1845" height="605" alt="Screenshot 2025-10-13 173939" src="https://github.com/user-attachments/assets/f8933a7f-414a-4465-a287-091c5b40ef02" />


## Repo Contents

| Item | Description |
|---|---|
| `v1.py` | Main Python script for the dashboard |
| `data analysis.ipynb` | Jupyter Notebook containing exploratory data analysis |
| `Fitness.xlsx` | Raw fitness data (Excel format) |
| `image/icone.png` | Icon or asset used in reports or website |
| `style.css`, `style2.css` | Styling sheets for HTML reports or dashboards |
| `requirements.txt` | Python dependencies |
| `LICENSE` | MIT license file |

## Getting Started

### Prerequisites

- Python 3.x  
- Required Python libraries (see `requirements.txt`)  
- (Optionally) Jupyter notebook environment

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/ameudes/fitness.git
   cd fitness
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Open the notebook:
   ```bash
   jupyter notebook "data analysis.ipynb"
   ```

### Usage

- Run `v1.py` to execute data processing or analysis workflows.  
- Use the notebook `data analysis.ipynb` for exploratory analysis:
  - Load the `Fitness.xlsx` data  
  - Visualize trends, correlations, or performance patterns  
  - Apply transformations or generate charts  
- CSS files are used when exporting HTML reports or building a small front-end to display analysis results.

## Project Goals & Future Work

- Expand analysis to include more fitness metrics (e.g., heart rate, sleep, calories)  
- Build an interactive dashboard using Dash, Streamlit, or Flask  
- Automate data ingestion from fitness trackers or APIs  
- Improve visualizations and reports with interactivity and design consistency  
- Write tests and modularize code for reusability

## Contributing

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/my-feature`)  
3. Commit your changes (`git commit -m "Add feature"`)  
4. Push to your branch (`git push origin feature/my-feature`)  
5. Submit a pull request

Please ensure your code is clean, documented, and any new dependencies are added to `requirements.txt`.

## License

This project is licensed under the **MIT License** 

