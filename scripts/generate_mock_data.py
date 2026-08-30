import pandas as pd
import numpy as np
import os

def generate_mock_data(output_dir):
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # 1. Countries and Regions
    countries = [
        "USA", "China", "Germany", "Japan", "South Korea",
        "Taiwan", "Netherlands", "Singapore", "Malaysia", "Vietnam",
        "India", "Mexico", "Canada", "UK", "France"
    ]
    regions = {
        "USA": "North America", "Canada": "North America", "Mexico": "North America",
        "China": "Asia", "Japan": "Asia", "South Korea": "Asia", "Taiwan": "Asia", 
        "Singapore": "Asia", "Malaysia": "Asia", "Vietnam": "Asia", "India": "Asia",
        "Germany": "Europe", "Netherlands": "Europe", "UK": "Europe", "France": "Europe"
    }
    
    # 2. Product Categories in Semiconductors
    products = [
        "Logic ICs", "Memory ICs", "Analog ICs", 
        "Microprocessors", "Optoelectronics", "Sensors"
    ]
    
    # Generate random trade flows for 5 years (2019 - 2023)
    years = [2019, 2020, 2021, 2022, 2023]
    
    data = []
    
    for year in years:
        for _ in range(500): # 500 random transactions per year
            reporter = np.random.choice(countries)
            partner = np.random.choice(countries)
            while reporter == partner:
                partner = np.random.choice(countries)
                
            flow_type = np.random.choice(["Import", "Export"])
            product = np.random.choice(products)
            
            # Base value with some randomness
            base_val = np.random.lognormal(mean=10, sigma=2)
            
            # Add some country specific weights to simulate concentration
            if partner in ["Taiwan", "South Korea"] and product == "Memory ICs":
                base_val *= 3.0
            if partner == "China" and flow_type == "Import":
                base_val *= 2.5
            if partner == "USA" and product == "Microprocessors":
                base_val *= 2.0
                
            # Tariff rate (0 to 15%)
            tariff = round(np.random.uniform(0, 0.15), 3)
            if reporter == "USA" and partner == "China":
                tariff = round(np.random.uniform(0.10, 0.25), 3)
                
            # Disruption risk score (1 to 10)
            risk = np.random.randint(1, 11)
            
            data.append({
                "Year": year,
                "Reporter_Country": reporter,
                "Reporter_Region": regions[reporter],
                "Partner_Country": partner,
                "Partner_Region": regions[partner],
                "Flow_Type": flow_type,
                "Product_Category": product,
                "Trade_Value_USD": round(base_val, 2),
                "Tariff_Rate": tariff,
                "Disruption_Risk_Score": risk
            })
            
    df = pd.DataFrame(data)
    
    # Save to CSV
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "semiconductor_trade_flows.csv")
    df.to_csv(file_path, index=False)
    print(f"Mock dataset generated successfully at {file_path}!")

if __name__ == "__main__":
    generate_mock_data("data/raw")
