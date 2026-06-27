import os
import pandas as pd
import matplotlib.pyplot as plt

def generate_chart():
    summary_path = "/workspaces/NigeriaBAY/data/processed/nga_bay_lga_summary.csv"
    output_path = "/workspaces/NigeriaBAY/outputs/maps/top_lgas_chart.png"
    
    if not os.path.exists(summary_path):
        print(f"Error: summary dataset not found at {summary_path}")
        return
        
    df = pd.read_csv(summary_path)
    
    # Sort and select top 10
    top_10 = df.sort_values(by="risk_score", ascending=False).head(10)
    
    # Apply a modern clean dark/dim theme to the plot
    plt.style.use('dark_background')
    
    fig, ax = plt.subplots(figsize=(10, 6), facecolor="#0b0f19")
    ax.set_facecolor("#0f172a") # Lighter dark-blue card background
    
    # Create colors using a color map corresponding to the risk scores (Yellow -> Orange -> Red)
    # We scale the index to match the YlOrRd color range nicely
    colors = plt.cm.YlOrRd(top_10["risk_score"] * 0.75 + 0.25)
    
    # Generate the bar plot
    bars = ax.bar(
        top_10["LGA"], 
        top_10["risk_score"], 
        color=colors, 
        edgecolor=(1.0, 1.0, 1.0, 0.15), 
        width=0.55, 
        zorder=3
    )
    
    # Customize grid
    ax.grid(axis='y', linestyle='--', alpha=0.15, zorder=0)
    
    # Add title and labels
    ax.set_title("Top 10 High-Risk LGAs", fontsize=18, fontweight="bold", pad=20, color="#f3f4f6")
    ax.set_ylabel("Risk Score (0 - 1)", fontsize=12, labelpad=10, color="#9ca3af")
    ax.set_xlabel("Local Government Area (LGA)", fontsize=12, labelpad=10, color="#9ca3af")
    
    # Rotate X labels and set custom styles
    plt.xticks(rotation=45, ha='right', fontsize=11, color="#e5e7eb")
    plt.yticks(fontsize=10, color="#9ca3af")
    
    # Remove top and right borders (spines)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color((1.0, 1.0, 1.0, 0.1))
    ax.spines["bottom"].set_color((1.0, 1.0, 1.0, 0.1))
    
    # Add data values on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.3f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),  # 5 points vertical offset
            textcoords="offset points",
            ha='center', 
            va='bottom', 
            fontsize=10, 
            fontweight="bold", 
            color="#f3f4f6"
        )
                    
    # Save the figure
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"Chart generated and saved successfully to {output_path}")

if __name__ == "__main__":
    generate_chart()
