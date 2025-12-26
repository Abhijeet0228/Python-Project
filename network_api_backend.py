import pandas as pd
from flask import Flask, jsonify, request
import os

# --- Global DataFrame ---
# We load the data ONCE when the server starts.
df = None

def load_data():
    """Loads the main DataFrame from the CSV file."""
    global df
    filename = "mock_traffic.csv"
    if not os.path.exists(filename):
        print(f"Error: '{filename}' not found. Please run the original script once to generate it.")
        return False
        
    try:
        df = pd.read_csv(filename, parse_dates=["Timestamp"])
        print(f"Successfully loaded '{filename}' with {len(df):,} rows.")
        return True
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

# --- Helper Function for Filtering ---
def get_filtered_df(params):
    """
    Applies filters from the request arguments to the global DataFrame.
    """
    if df is None:
        return pd.DataFrame() # Return empty if data isn't loaded

    filtered_df = df.copy()

    # Protocol Filter
    selected_protocol = params.get('protocol')
    if selected_protocol and selected_protocol != "All":
        filtered_df = filtered_df[filtered_df['Protocol'] == selected_protocol]

    # Source IP Filter
    source_ip = params.get('source_ip')
    if source_ip:
        filtered_df = filtered_df[filtered_df['Source IP'].str.contains(source_ip, case=False, na=False)]

    # Destination IP Filter
    dest_ip = params.get('dest_ip')
    if dest_ip:
        filtered_df = filtered_df[filtered_df['Dest IP'].str.contains(dest_ip, case=False, na=False)]

    # Sorting
    sort_by = params.get('sort_by')
    if sort_by:
        ascending = params.get('ascending', 'True') == 'True'
        filtered_df.sort_values(by=sort_by, ascending=ascending, inplace=True)
        
    return filtered_df


# --- Flask App Initialization ---
app = Flask(__name__)

# --- API Endpoints ---

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Endpoint to get key metrics."""
    filtered_df = get_filtered_df(request.args)
    
    if filtered_df.empty:
        return jsonify({"error": "No data"}), 404

    total_packets = len(filtered_df)
    total_data_bytes = filtered_df['Length'].sum()
    total_data_mb = total_data_bytes / (1024 * 1024)
    avg_size = total_data_bytes / total_packets if total_packets > 0 else 0
    
    top_protocol = filtered_df['Protocol'].mode()[0] if not filtered_df['Protocol'].empty else "N/A"
    top_source_ip = filtered_df['Source IP'].mode()[0] if not filtered_df['Source IP'].empty else "N/A"
    top_dest_ip = filtered_df['Dest IP'].mode()[0] if not filtered_df['Dest IP'].empty else "N/A"
    unique_protocols = len(filtered_df['Protocol'].unique()) if not filtered_df['Protocol'].empty else 0

    time_range_str = "N/A"
    if not filtered_df['Timestamp'].empty:
        min_time = filtered_df['Timestamp'].min()
        max_time = filtered_df['Timestamp'].max()
        time_range_str = f"{min_time.strftime('%Y-%m-%d %H:%M')} to {max_time.strftime('%Y-%m-%d %H:%M')}"

    stats = {
        "total_packets": f"{total_packets:,}",
        "total_data_mb": f"{total_data_mb:.2f} MB ({total_data_bytes:,} bytes)",
        "avg_packet_size": f"{avg_size:.0f} bytes",
        "top_protocol": top_protocol,
        "top_source_ip": top_source_ip,
        "top_dest_ip": top_dest_ip,
        "unique_protocols": f"{unique_protocols}",
        "time_range": time_range_str
    }
    return jsonify(stats)

@app.route('/api/data', methods=['GET'])
def get_data():
    """Endpoint to get raw packet data for the table."""
    filtered_df = get_filtered_df(request.args)
    
    # Limit to 200 rows for performance
    filtered_df = filtered_df.head(200)
    
    # Format timestamp for JSON
    filtered_df['Timestamp'] = filtered_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Convert to JSON records
    data_json = filtered_df.to_dict('records')
    return jsonify(data_json)

@app.route('/api/plot/protocol', methods=['GET'])
def get_protocol_plot_data():
    """Endpoint for protocol distribution plot data."""
    filtered_df = get_filtered_df(request.args)
    if filtered_df.empty:
        return jsonify({})
        
    protocol_counts = filtered_df['Protocol'].value_counts()
    return jsonify(protocol_counts.to_dict())

@app.route('/api/plot/top_ips', methods=['GET'])
def get_top_ips_plot_data():
    """Endpoint for top destination IPs plot data."""
    filtered_df = get_filtered_df(request.args)
    if filtered_df.empty:
        return jsonify({})

    top_dest_ips = filtered_df['Dest IP'].value_counts().head(5)
    return jsonify(top_dest_ips.to_dict())

@app.route('/api/protocols', methods=['GET'])
def get_protocols():
    """Endpoint to get the list of unique protocols for the filter dropdown."""
    if df is None:
        return jsonify({"error": "Data not loaded"}), 500
    
    protocols = ["All"] + sorted(df['Protocol'].unique().tolist())
    return jsonify(protocols)

# --- Run the App ---
if __name__ == "__main__":
    if load_data():
        print("Backend server is starting...")
        # Note: 'debug=True' is great for development, but remove it for production.
        app.run(debug=True, port=5000)
    else:
        print("Failed to load data. Backend server is not running.")
