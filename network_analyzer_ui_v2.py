import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import os
import time

# --- 1. Mock Data Generation 
def create_mock_data(filename="mock_traffic.csv"):
    """
    Creates a mock network traffic CSV file if one doesn't already exist.
    """
    if os.path.exists(filename):
        print(f"'{filename}' already exists. Skipping creation.")
        return

    print(f"Creating mock data file: '{filename}'...")
    data = []
    protocols = ["TCP", "UDP", "ICMP", "HTTP", "DNS", "FTP", "SSH", "HTTPS"]
    # More varied IPs
    internal_ips = [f"192.168.1.{random.randint(2, 254)}" for _ in range(30)]
    internal_ips.extend([f"10.0.0.{random.randint(2, 254)}" for _ in range(15)])
    internal_ips.extend([f"172.16.{random.randint(1, 31)}.{random.randint(2, 254)}" for _ in range(15)])
    
    external_ips = [f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}" for _ in range(70)]
    all_ips = internal_ips + external_ips

    start_time = int(time.time())

    for i in range(5000): # Generate more mock packets for richer data
        timestamp = start_time - random.randint(0, 3600 * 24 * 7) # Traffic from the last 7 days
        protocol = random.choice(protocols)
        
        port = None
        if protocol == "HTTP": port = 80
        elif protocol == "HTTPS": port = 443
        elif protocol == "SSH": port = 22
        elif protocol == "DNS": port = 53
        elif protocol == "FTP": port = 21
        elif protocol == "TCP" or protocol == "UDP": port = random.choice([80, 443, 21, 22, 23, 53, 110, 143, 3389, random.randint(1024, 65535)])
        else: port = random.randint(1, 65535)

        data.append({
            "Timestamp": pd.to_datetime(timestamp, unit='s'),
            "Source IP": random.choice(all_ips),
            "Dest IP": random.choice(all_ips),
            "Protocol": protocol,
            "Length": random.randint(64, 1500), # Packet length in bytes
            "Port": port
        })
    
    df = pd.DataFrame(data)
    df.sort_values("Timestamp", inplace=True)
    df.to_csv(filename, index=False)
    print(f"Successfully created '{filename}'.")

# --- 2. Main Application Class ---
class NetTrafficAnalyzer(tk.Tk):
    """
    The main application class for the Network Traffic Analyzer GUI.
    """
    def __init__(self):
        super().__init__()
        self.title("Advanced Network Traffic Analyzer")
        self.geometry("1400x900") # Slightly larger window
        self.min_width = 1200
        self.min_height = 700
        self.minsize(self.min_width, self.min_height)
        
        self.df = None # To hold the *original* loaded DataFrame
        self.current_df = None # To hold the *filtered and sorted* DataFrame
        self.sort_state = {} # Dictionary to track column sort direction
        
        self._setup_styles()
        self._create_widgets()
        self.update_status("Application ready. Load data to begin.")

    def _setup_styles(self):
        """Configures the ttk styles for a more colorful and modern look."""        
        self.style = ttk.Style(self)
        
        try:
            self.tk.call('source', 'azure.tcl') 
            self.style.theme_use('azure') 
            print("Successfully loaded 'azure' theme.")
        except tk.TclError:
            print("'azure' theme not available or 'azure.tcl' file not found, falling back to 'clam'.")
            self.style.theme_use('clam')
       

        # Define a color palette
        self.colors = {
            'bg_primary': '#e0f2f7',    # Light blue background
            'bg_secondary': '#ffffff',  # White for frames
            'accent_blue': '#2196f3',   # Material Blue 500
            'accent_green': '#4caf50',  # Material Green 500
            'text_dark': '#333333',
            'text_light': '#f0f0f0',
            'header_bg': '#007bff',     # Darker blue for header
            'button_hover': '#0056b3',
            'border_light': '#cccccc'
        }

        # Global background
        self.configure(bg=self.colors['bg_primary']) 
        self.style.configure('.', font=('Segoe UI', 10), background=self.colors['bg_primary'], foreground=self.colors['text_dark'])

        # Header and Buttons
        self.style.configure('Header.TLabel', font=('Segoe UI', 20, 'bold'), foreground=self.colors['text_light'], background=self.colors['header_bg'])
        self.style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=8, background=self.colors['accent_blue'], foreground=self.colors['text_light'], relief="flat")
        self.style.map('TButton', background=[('active', self.colors['button_hover'])])
        self.style.configure('Accent.TButton', background=self.colors['accent_green'])
        self.style.map('Accent.TButton', background=[('active', '#388e3c')]) # Darker green on hover

        # Frames and Labels
        self.style.configure('TFrame', background=self.colors['bg_primary'])
        
        # --- FIX: Define a new style for the header frame ---
        self.style.configure('Header.TFrame', background=self.colors['header_bg'])
        
        self.style.configure('Card.TFrame', background=self.colors['bg_secondary'], relief="flat", borderwidth=1, bordercolor=self.colors['border_light'])
        self.style.configure('TLabelframe', background=self.colors['bg_secondary'], foreground=self.colors['accent_blue'], font=('Segoe UI', 12, 'bold'), borderwidth=1, relief="solid", bordercolor=self.colors['border_light'])
        self.style.configure('TLabelframe.Label', background=self.colors['bg_secondary'], foreground=self.colors['accent_blue'], font=('Segoe UI', 12, 'bold'))
        self.style.configure('Status.TLabel', foreground='blue', font=('Segoe UI', 9, 'italic'), background=self.colors['bg_primary'])
        self.style.configure('Stat.TLabel', font=('Segoe UI', 11, 'bold'), foreground=self.colors['text_dark'], background=self.colors['bg_secondary'])
        self.style.configure('StatValue.TLabel', font=('Segoe UI', 11), foreground=self.colors['accent_blue'], background=self.colors['bg_secondary'])


        # Treeview (Table)
        self.style.configure('Treeview', 
                             rowheight=28, 
                             font=('Segoe UI', 9), 
                             background=self.colors['bg_secondary'], 
                             foreground=self.colors['text_dark'], 
                             fieldbackground=self.colors['bg_secondary'],
                             borderwidth=0,
                             relief="flat"
                            )
        self.style.configure('Treeview.Heading', 
                             font=('Segoe UI', 10, 'bold'), 
                             background=self.colors['accent_blue'], 
                             foreground=self.colors['text_light'], 
                             relief="flat",
                             padding=(5,5,5,5) # Add padding to headings
                            )
        self.style.map('Treeview.Heading', 
                       background=[('active', self.colors['button_hover'])]
                      )
        self.style.map('Treeview', 
                       background=[('selected', self.colors['accent_blue'])],
                       foreground=[('selected', self.colors['text_light'])]
                      )
        
        # Matplotlib Figure styling to match Tkinter theme
        plt.rcParams.update({
            'figure.facecolor': self.colors['bg_secondary'],
            'axes.facecolor': self.colors['bg_secondary'],
            'axes.edgecolor': self.colors['border_light'],
            'text.color': self.colors['text_dark'],
            'axes.labelcolor': self.colors['text_dark'],
            'xtick.color': self.colors['text_dark'],
            'ytick.color': self.colors['text_dark'],
            'grid.color': self.colors['border_light'],
            'font.family': 'Segoe UI',
            'font.size': 9
        })


    def _create_widgets(self):
        """
        Creates and lays out all the widgets in the main window with improved organization.
        """
        # --- Header Frame ---
        # --- FIX: Apply the new 'Header.TFrame' style ---
        header_frame = ttk.Frame(self, style='Header.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        # --- FIX: Removed the error-causing .configure line ---
        
        title_label = ttk.Label(header_frame, text="Network Traffic Analyzer Dashboard", style='Header.TLabel')
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.load_button = ttk.Button(header_frame, text="Load Traffic Data (.csv)", command=self.load_data, style='Accent.TButton')
        self.load_button.pack(side=tk.RIGHT, padx=20, pady=10)

        # --- Main Content Area (Paned Window for Resizing) ---
        main_content_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_content_paned.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # --- Left Pane: Statistics and Controls ---
        left_pane = ttk.Frame(main_content_paned, style='TFrame', width=350)
        main_content_paned.add(left_pane, weight=1) # Give less weight to stats/controls

        # Summary Statistics Frame
        stats_frame_container = ttk.LabelFrame(left_pane, text="Key Metrics")
        stats_frame_container.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_frame = ttk.Frame(stats_frame_container, style='Card.TFrame', padding=15)
        self.stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Use a grid for stats for better alignment
        stats_data = [
            ("Total Packets:", "total_packets"),
            ("Total Data Transferred:", "total_data_mb"),
            ("Avg. Packet Size:", "avg_packet_size"),
            ("Top Protocol:", "top_protocol"),
            ("Top Source IP:", "top_source_ip"),
            ("Top Dest. IP:", "top_dest_ip"),
            ("Unique Protocols:", "unique_protocols"),
            ("Time Range:", "time_range")
        ]
        self.stats_labels = {}
        for i, (label_text, key) in enumerate(stats_data):
            ttk.Label(self.stats_frame, text=label_text, style='Stat.TLabel').grid(row=i, column=0, sticky='w', padx=5, pady=3)
            self.stats_labels[key] = ttk.Label(self.stats_frame, text="N/A", style='StatValue.TLabel', wraplength=200)
            self.stats_labels[key].grid(row=i, column=1, sticky='w', padx=5, pady=3)

        # Filter and Search Frame (New)
        filter_frame = ttk.LabelFrame(left_pane, text="Filter & Search")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        filter_inner_frame = ttk.Frame(filter_frame, style='Card.TFrame', padding=10)
        filter_inner_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_inner_frame, text="Protocol:").grid(row=0, column=0, sticky='w', padx=5, pady=3)
        self.protocol_filter_var = tk.StringVar(self)
        self.protocol_filter_combobox = ttk.Combobox(filter_inner_frame, textvariable=self.protocol_filter_var, state='readonly', width=15)
        self.protocol_filter_combobox.grid(row=0, column=1, sticky='ew', padx=5, pady=3)
        self.protocol_filter_combobox.bind("<<ComboboxSelected>>", self.apply_filter)

        ttk.Label(filter_inner_frame, text="Source IP:").grid(row=1, column=0, sticky='w', padx=5, pady=3)
        self.source_ip_filter_var = tk.StringVar(self)
        self.source_ip_entry = ttk.Entry(filter_inner_frame, textvariable=self.source_ip_filter_var, width=15)
        self.source_ip_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=3)

        ttk.Label(filter_inner_frame, text="Dest. IP:").grid(row=2, column=0, sticky='w', padx=5, pady=3)
        self.dest_ip_filter_var = tk.StringVar(self)
        self.dest_ip_entry = ttk.Entry(filter_inner_frame, textvariable=self.dest_ip_filter_var, width=15)
        self.dest_ip_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=3)
        
        filter_inner_frame.grid_columnconfigure(1, weight=1) # Make entry widgets expand

        filter_buttons_frame = ttk.Frame(filter_inner_frame, style='TFrame')
        filter_buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(filter_buttons_frame, text="Apply Filters", command=self.apply_filter).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_buttons_frame, text="Clear Filters", command=self.clear_filters).pack(side=tk.LEFT, padx=5)

        # Status Bar (at the bottom of the left pane)
        self.status_label = ttk.Label(left_pane, text="Ready.", style='Status.TLabel', anchor='w')
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)


        # --- Right Pane: Data Table and Visualizations ---
        right_pane = ttk.Frame(main_content_paned, style='TFrame')
        main_content_paned.add(right_pane, weight=3) # Give more weight to data and plots

        # Packet Data Table
        table_frame = ttk.LabelFrame(right_pane, text="Raw Packet Data (Limited to 200 Rows)")
        # --- UI CORRECTION: Set expand=True to fill vertical space ---
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10)) 
        
        self.tree = ttk.Treeview(table_frame, show='headings')
        # Scrollbars for Treeview
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(expand=True, fill=tk.BOTH)

        # Visualizations Frame
        viz_frame = ttk.LabelFrame(right_pane, text="Traffic Visualizations")
        viz_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Use a PanedWindow for plots to allow resizing them too
        viz_paned_window = ttk.PanedWindow(viz_frame, orient=tk.VERTICAL)
        viz_paned_window.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Plot 1: Protocol Distribution
        plot1_frame = ttk.Frame(viz_paned_window, style='Card.TFrame')
        viz_paned_window.add(plot1_frame, weight=1)
        self.fig1, self.ax1 = plt.subplots(figsize=(6, 4))
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=plot1_frame)
        self.canvas_widget1 = self.canvas1.get_tk_widget()
        self.canvas_widget1.pack(expand=True, fill=tk.BOTH)
        self.ax1.set_title("Load data to see Protocol Distribution")
        self.fig1.tight_layout()
        self.canvas1.draw()

        # Plot 2: Top 5 Destination IPs
        plot2_frame = ttk.Frame(viz_paned_window, style='Card.TFrame')
        viz_paned_window.add(plot2_frame, weight=1)
        self.fig2, self.ax2 = plt.subplots(figsize=(6, 4))
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=plot2_frame)
        self.canvas_widget2 = self.canvas2.get_tk_widget()
        self.canvas_widget2.pack(expand=True, fill=tk.BOTH)
        self.ax2.set_title("Load data to see Top Destination IPs")
        self.fig2.tight_layout()
        self.canvas2.draw()

    def update_status(self, message):
        """Updates the status bar with the given message."""
        self.status_label.config(text=message)
        self.update_idletasks() # Ensure it updates immediately

    def load_data(self):
        """
        Opens a file dialog to load a CSV file and triggers dashboard update.
        """
        filepath = filedialog.askopenfilename(
            title="Select Traffic CSV File",
            filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")),
            initialdir=os.getcwd()
        )
        if not filepath:
            self.update_status("Data loading cancelled.")
            return
        
        self.update_status(f"Loading data from '{os.path.basename(filepath)}'...")
        try:
            self.df = pd.read_csv(filepath, parse_dates=["Timestamp"])
            self.current_df = self.df.copy() # Set current_df to the full, newly loaded data
            self._populate_filter_options()
            self.update_dashboard()
            self.update_status(f"Successfully loaded {len(self.df):,} packets.")
        except Exception as e:
            messagebox.showerror("Error Loading Data", f"Failed to load data: {e}")
            self.update_status(f"Error loading data: {e}")
            self.df = None
            self.current_df = None
            self._clear_dashboard() # Clear UI on load failure

    def _populate_filter_options(self):
        """Populates the combobox with unique protocols."""
        try:
            if self.df is not None:
                protocols = ["All"] + sorted(self.df['Protocol'].unique().tolist())
                self.protocol_filter_combobox['values'] = protocols
                self.protocol_filter_var.set("All") # Default selection
            else:
                self.protocol_filter_combobox['values'] = ["All"]
                self.protocol_filter_var.set("All")
        except Exception as e:
            self.update_status(f"Error populating filters: {e}")


    def apply_filter(self, event=None):
        """Applies filters based on user input and updates the dashboard."""
        if self.df is None:
            self.update_status("No data loaded to filter.")
            return

        try:
            filtered_df = self.df.copy()
            applied_filters = []

            # Protocol Filter
            selected_protocol = self.protocol_filter_var.get()
            if selected_protocol and selected_protocol != "All":
                filtered_df = filtered_df[filtered_df['Protocol'] == selected_protocol]
                applied_filters.append(f"Protocol: {selected_protocol}")

            # Source IP Filter
            source_ip = self.source_ip_filter_var.get().strip()
            if source_ip:
                # Add na=False to handle potential NaN values gracefully
                filtered_df = filtered_df[filtered_df['Source IP'].str.contains(source_ip, case=False, na=False)]
                applied_filters.append(f"Source IP: {source_ip}")

            # Destination IP Filter
            dest_ip = self.dest_ip_filter_var.get().strip()
            if dest_ip:
                filtered_df = filtered_df[filtered_df['Dest IP'].str.contains(dest_ip, case=False, na=False)]
                applied_filters.append(f"Destination IP: {dest_ip}")

            self.current_df = filtered_df
            self.update_dashboard()
            
            if applied_filters:
                self.update_status(f"Filters applied. Displaying {len(self.current_df):,} packets.")
            else:
                self.update_status(f"All filters cleared. Displaying {len(self.current_df):,} packets.")
        except Exception as e:
            self.update_status(f"Error applying filter: {e}")
            print(f"Filter Error: {e}")

    def clear_filters(self):
        """Clears all filter inputs and resets to the original DataFrame."""
        self.protocol_filter_var.set("All")
        self.source_ip_filter_var.set("")
        self.dest_ip_filter_var.set("")
        self.sort_state = {} # Reset sort state
        self.apply_filter() # Re-apply (which now resets to original df)

    # --- REFACTORED AND SIMPLIFIED METHODS ---

    def update_dashboard(self):
        """
        Updates all UI elements (stats, table, plots) using the current DataFrame.
        This is now a simple "manager" function.
        """
        if self.current_df is None or self.current_df.empty:
            self._clear_dashboard()
            return
        
        # We have data, so update all sections.
        # Wrap each update in a try-except for maximum robustness.
        try:
            self._update_stats(self.current_df)
        except Exception as e:
            self.update_status(f"Error updating stats: {e}")
            print(f"Stats Error: {e}")

        try:
            self._update_table(self.current_df)
        except Exception as e:
            self.update_status(f"Error updating table: {e}")
            print(f"Table Error: {e}")
            
        try:
            self._update_plots(self.current_df)
        except Exception as e:
            self.update_status(f"Error updating plots: {e}")
            print(f"Plots Error: {e}")

    def _clear_dashboard(self):
        """Clears all data-driven UI elements."""
        # Clear stats
        for key in self.stats_labels:
            self.stats_labels[key].config(text="N/A")
        
        # Clear table
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Clear plots
        self.ax1.clear()
        self.ax1.set_title("No Data to Display")
        self.ax1.set_xticks([])
        self.ax1.set_yticks([])
        self.canvas1.draw()
        
        self.ax2.clear()
        self.ax2.set_title("No Data to Display")
        self.ax2.set_xticks([])
        self.ax2.set_yticks([])
        self.canvas2.draw()

    def _update_stats(self, df):
        """Updates only the 'Key Metrics' section."""
        total_packets = len(df)
        total_data_bytes = df['Length'].sum()
        total_data_mb = total_data_bytes / (1024 * 1024)
        avg_size = np.mean(df['Length']) if total_packets > 0 else 0
        
        top_protocol = df['Protocol'].mode()[0] if not df['Protocol'].empty else "N/A"
        top_source_ip = df['Source IP'].mode()[0] if not df['Source IP'].empty else "N/A"
        top_dest_ip = df['Dest IP'].mode()[0] if not df['Dest IP'].empty else "N/A"
        unique_protocols = len(df['Protocol'].unique()) if not df['Protocol'].empty else 0

        time_range_str = "N/A"
        if not df['Timestamp'].empty:
            min_time = df['Timestamp'].min()
            max_time = df['Timestamp'].max()
            time_range_str = f"{min_time.strftime('%Y-%m-%d %H:%M')} to {max_time.strftime('%Y-%m-%d %H:%M')}"

        self.stats_labels["total_packets"].config(text=f"{total_packets:,}")
        self.stats_labels["total_data_mb"].config(text=f"{total_data_mb:.2f} MB ({total_data_bytes:,} bytes)")
        self.stats_labels["avg_packet_size"].config(text=f"{avg_size:.0f} bytes")
        self.stats_labels["top_protocol"].config(text=f"{top_protocol}")
        self.stats_labels["top_source_ip"].config(text=f"{top_source_ip}")
        self.stats_labels["top_dest_ip"].config(text=f"{top_dest_ip}")
        self.stats_labels["unique_protocols"].config(text=f"{unique_protocols}")
        self.stats_labels["time_range"].config(text=time_range_str)

    def _update_table(self, df):
        """Updates only the Treeview table."""
        # Clear old data
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # (Re)set columns and headings
        cols = list(df.columns)
        self.tree["columns"] = cols
        for col in cols:
            # Set heading text and command
            # The command lambda now tracks the *next* sort direction
            current_reverse = self.sort_state.get(col, False)
            self.tree.heading(col, text=col, command=lambda _col=col, _rev=current_reverse: self._sort_treeview(_col, not _rev))
            self.tree.column(col, width=120, anchor='w', minwidth=60)
        
        # Insert new data (limit to first 200 rows for performance)
        for index, row in df.head(200).iterrows():
            row_values = list(row)
            row_values[0] = row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            self.tree.insert("", "end", values=row_values)

    def _update_plots(self, df):
        """Updates all plots."""
        self._update_protocol_distribution_plot(df)
        self._update_top_dest_ips_plot(df)

    def _sort_treeview(self, col, reverse):
        """
        SIMPLIFIED: Sorts the *current_df* using pandas and refreshes the table.
        """
        if self.current_df is None or self.current_df.empty:
            return

        try:
            # Store the sort state
            self.sort_state = {col: reverse} # Only track last sort
            
            # Sort the DataFrame
            ascending = not reverse
            self.current_df.sort_values(by=col, ascending=ascending, inplace=True)
            
            # Refresh the table with the sorted data
            self._update_table(self.current_df)
            self.update_status(f"Sorted by {col} {'descending' if reverse else 'ascending'}.")
        except Exception as e:
            self.update_status(f"Error sorting by {col}: {e}")
            print(f"Sort Error: {e}")

    def _update_protocol_distribution_plot(self, df):
        """Updates the Protocol Distribution bar chart."""
        self.ax1.clear()
        if not df.empty:
            protocol_counts = df['Protocol'].value_counts()
            colors = plt.cm.Dark2.colors 
            protocol_counts.plot(
                kind='bar', 
                ax=self.ax1, 
                color=colors, 
                edgecolor='black',
                alpha=0.8
            )
            self.ax1.set_title("Protocol Frequency", fontsize=12, color=self.colors['text_dark'])
            self.ax1.set_ylabel("Packet Count", fontsize=10, color=self.colors['text_dark'])
            self.ax1.set_xlabel("Protocol", fontsize=10, color=self.colors['text_dark'])
            self.ax1.tick_params(axis='x', rotation=45, labelsize=8)
            self.ax1.tick_params(axis='y', labelsize=8)
            self.ax1.grid(axis='y', linestyle='--', alpha=0.7)
        else:
            self.ax1.set_title("No Protocol Data")
            self.ax1.set_xticks([])
            self.ax1.set_yticks([])

        self.fig1.tight_layout(pad=2.0)
        self.canvas1.draw()

    def _update_top_dest_ips_plot(self, df):
        """Updates the Top 5 Destination IPs bar chart."""
        self.ax2.clear()
        if not df.empty:
            top_dest_ips = df['Dest IP'].value_counts().head(5)
            colors = plt.cm.Paired.colors 
            top_dest_ips.plot(
                kind='bar', 
                ax=self.ax2, 
                color=colors, 
                edgecolor='black',
                alpha=0.8
            )
            self.ax2.set_title("Top 5 Destination IPs", fontsize=12, color=self.colors['text_dark'])
            self.ax2.set_ylabel("Packet Count", fontsize=10, color=self.colors['text_dark'])
            self.ax2.set_xlabel("Destination IP", fontsize=10, color=self.colors['text_dark'])
            self.ax2.tick_params(axis='x', rotation=45, labelsize=8)
            self.ax2.tick_params(axis='y', labelsize=8)
            self.ax2.grid(axis='y', linestyle='--', alpha=0.7)
        else:
            self.ax2.set_title("No Destination IP Data")
            self.ax2.set_xticks([])
            self.ax2.set_yticks([])

        self.fig2.tight_layout(pad=2.0)
        self.canvas2.draw()
            
if __name__ == "__main__":

    
    # First, create the mock data file if it doesn't exist
    create_mock_data()
    
    # Now, run the tkinter app
    app = NetTrafficAnalyzer()
    app.mainloop()

