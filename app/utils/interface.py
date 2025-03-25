import customtkinter as ctk
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from typing import Dict, List, Callable, Any
import datetime
import logging
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox

# Get logger
logger = logging.getLogger(__name__)

# Define a modern color palette
COLORS = {
    'primary': "#2CC985",       # Main green
    'primary_dark': "#0CAB6B",  # Darker green for hover
    'secondary': "#5D87FF",     # Blue accent
    'light_bg': "#F8F9FA",      # Light background
    'dark_text': "#212529",     # Dark text
    'light_text': "#F8F9FA",    # Light text
    'neutral': "#DEE2E6",       # Neutral gray
    'warning': "#FFC107",       # Warning color
    'danger': "#DC3545",        # Error color
    'success': "#29CC97",       # Success color
}

class ModernFrame(ctk.CTkFrame):
    """A modern frame with consistent styling."""
    def __init__(self, master, **kwargs):
        kwargs.setdefault("corner_radius", 10)
        kwargs.setdefault("border_width", 0)
        kwargs.setdefault("fg_color", COLORS['light_bg'])
        super().__init__(master, **kwargs)
        
class ModernButton(ctk.CTkButton):
    """A modern button with hover effects."""
    def __init__(self, master, **kwargs):
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("border_width", 0)
        kwargs.setdefault("fg_color", COLORS['primary'])
        kwargs.setdefault("hover_color", COLORS['primary_dark'])
        kwargs.setdefault("text_color", COLORS['light_text'])
        kwargs.setdefault("font", ("Helvetica", 12, "bold"))
        super().__init__(master, **kwargs)

class ModernLabel(ctk.CTkLabel):
    """A modern label with consistent styling."""
    def __init__(self, master, **kwargs):
        # Set default values
        kwargs.setdefault("font", ("Helvetica", 12))
        kwargs.setdefault("text_color", COLORS['dark_text'])
        kwargs.setdefault("anchor", "w")
        super().__init__(master, **kwargs)

class ModernSlider(ModernFrame):
    """A modern slider with value display."""
    def __init__(self, master, label: str, from_: float, to: float, **kwargs):
        super().__init__(master, **kwargs)
        
        # Initialize attributes to prevent AttributeError
        self.label = None
        self.value_label = None
        self.slider = None
        self.original_command = None
        
        # Save the original command if provided and remove from kwargs
        self.original_command = kwargs.pop("command", None)
        
        # Initialize grid layout
        self.grid_columnconfigure(1, weight=1)
        
        # Create labels
        self.label = ModernLabel(self, text=label, font=("Helvetica", 12, "bold"))
        self.label.grid(row=0, column=0, sticky="w")
        
        self.value_label = ModernLabel(self, text="0.0", width=40, anchor="e", font=("Helvetica", 12))
        self.value_label.grid(row=0, column=2, sticky="e")
        
        # Create the CTk slider
        self.slider = ctk.CTkSlider(
            self,
            from_=from_,
            to=to,
            fg_color=COLORS['neutral'],
            button_color=COLORS['primary'],
            button_hover_color=COLORS['primary_dark'],
            progress_color=COLORS['primary'],
            command=self._handle_slider_change
        )
        self.slider.grid(row=0, column=1, padx=(10, 10), sticky="ew")
        
        # Set transparent background for the frame
        super().configure(fg_color="transparent")
    
    def get(self) -> float:
        """Get the current slider value."""
        if self.slider is None:
            return 0.0
        return self.slider.get()
    
    def set(self, value: float):
        """Set the slider value."""
        if self.slider is None:
            return
        self.slider.set(value)
        self.update_value_label(value)
    
    def update_value_label(self, value):
        """Update the value label."""
        if self.value_label is None:
            return
        self.value_label.configure(text=f"{value:.1f}")
    
    def _handle_slider_change(self, value):
        """Handle slider value change event."""
        self.update_value_label(value)
        if self.original_command:
            self.original_command(value)
    
    def configure(self, **kwargs):
        """Configure the slider."""
        if self.slider is None:
            # If configure is called before slider is initialized, save for later
            return super().configure(**kwargs)
            
        if "command" in kwargs:
            self.original_command = kwargs.pop("command")
            
        # Configure the slider if it exists
        if kwargs and self.slider:
            try:
                self.slider.configure(**kwargs)
            except Exception as e:
                logger.error(f"Error configuring slider: {str(e)}")
        
        # Pass remaining kwargs to parent
        return super().configure(**kwargs)

class ChatMessage:
    def __init__(self, text: str, is_user: bool, timestamp: datetime.datetime = None):
        self.text = text
        self.is_user = is_user
        self.timestamp = timestamp or datetime.datetime.now()

class ModernChatFrame(ModernFrame):
    """A modern chat interface frame with clean styling."""
    def __init__(self, master, on_send, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create chat display container
        chat_container = ModernFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color="#E0E0E0"
        )
        chat_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        chat_container.grid_columnconfigure(0, weight=1)
        chat_container.grid_rowconfigure(0, weight=1)
        
        # Create chat display area using standard tkinter Text
        self.chat_display = tk.Text(
            chat_container,
            font=("Helvetica", 12),
            wrap="word",
            bg="#FFFFFF",
            fg="#333333",
            relief="flat",
            padx=15,
            pady=15,
            cursor="arrow"
        )
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Add scrollbar with custom style
        scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=self.chat_display.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=2)
        self.chat_display.configure(yscrollcommand=scrollbar.set)
        
        # Create input area frame
        input_frame = ModernFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color="#E0E0E0"
        )
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Create input field
        self.input_field = ctk.CTkTextbox(
            input_frame,
            height=60,
            font=("Helvetica", 12),
            wrap="word",
            fg_color="#FFFFFF",
            text_color="#333333",
            border_width=0,
            corner_radius=10
        )
        self.input_field.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Create send button
        self.send_button = ModernButton(
            input_frame,
            text="Send Message",
            width=120,
            height=35,
            font=("Helvetica", 12, "bold"),
            corner_radius=10,
            fg_color="#2CC985",
            hover_color="#0CAB6B",
            command=self._on_send
        )
        self.send_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Bind enter key to send
        self.input_field.bind("<Return>", lambda e: self._on_send() if not e.state & 1 else None)
        self.input_field.bind("<Shift-Return>", lambda e: self.input_field.insert("end", "\n"))
        
        # Store callback
        self.on_send = on_send
        
        # Initialize message styles
        self.user_message_style = {
            "text_color": "#000000",
            "prefix": "You",
            "prefix_color": "#2CC985",
            "align": "right"
        }
        
        self.bot_message_style = {
            "text_color": "#000000",
            "prefix": "🌱 Assistant",
            "prefix_color": "#2CC985",
            "align": "left"
        }
        
        # Configure text tags
        self.chat_display.tag_configure(
            "user_text",
            foreground=self.user_message_style["text_color"],
            font=("Helvetica", 12),
            spacing1=5,
            spacing3=10,
            rmargin=50,
            lmargin1=50,
            lmargin2=50
        )
        self.chat_display.tag_configure(
            "bot_text",
            foreground=self.bot_message_style["text_color"],
            font=("Helvetica", 12),
            spacing1=5,
            spacing3=10,
            rmargin=50,
            lmargin1=50,
            lmargin2=50
        )
        self.chat_display.tag_configure(
            "user_prefix",
            foreground=self.user_message_style["prefix_color"],
            font=("Helvetica", 12, "bold"),
            justify="left",
            spacing1=10
        )
        self.chat_display.tag_configure(
            "bot_prefix",
            foreground=self.bot_message_style["prefix_color"],
            font=("Helvetica", 12, "bold"),
            justify="left",
            spacing1=10
        )
        self.chat_display.tag_configure(
            "time",
            foreground="#757575",
            font=("Helvetica", 9),
            spacing1=5
        )
        
        # Make text widget read-only
        self.chat_display.configure(state="disabled")
    
    def _on_send(self):
        """Handle send button click."""
        message = self.input_field.get("1.0", "end-1c").strip()
        if message:
            self.add_user_message(message)
            self.input_field.delete("1.0", "end")
            if self.on_send:
                self.on_send(message)
    
    def _format_message(self, message, style, is_user=False):
        """Format a message with the given style."""
        self.chat_display.insert("end", "\n")  # Add spacing
        
        # Get current time
        current_time = datetime.datetime.now().strftime("%H:%M")
        
        # Determine tags
        text_tag = "user_text" if is_user else "bot_text"
        prefix_tag = "user_prefix" if is_user else "bot_prefix"
        
        # Insert prefix and time
        self.chat_display.insert("end", f"{style['prefix']} • {current_time}\n", prefix_tag)
        
        # Insert message
        lines = message.split('\n')
        for i, line in enumerate(lines):
            if i > 0:
                self.chat_display.insert("end", "\n")
            self.chat_display.insert("end", line, text_tag)
        
        # Add extra spacing
        self.chat_display.insert("end", "\n")
        
        # Scroll to bottom
        self.chat_display.see("end")
    
    def add_user_message(self, message):
        """Add a user message to the chat."""
        self.chat_display.configure(state="normal")
        self._format_message(message, self.user_message_style, is_user=True)
        self.chat_display.configure(state="disabled")
    
    def add_bot_message(self, message):
        """Add a bot message to the chat."""
        self.chat_display.configure(state="normal")
        self._format_message(message, self.bot_message_style, is_user=False)
        self.chat_display.configure(state="disabled")

class VisualizationFrame(ModernFrame):
    """Frame for displaying visualizations."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create a title label
        self.title_label = ModernLabel(
            self, 
            text="Parameter Visualization",
            font=("Helvetica", 14, "bold")
        )
        self.title_label.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        
        # Create figure and canvas
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        
        # Style the plots
        self.fig.patch.set_facecolor("#FFFFFF")
        self.ax1.set_facecolor("#FFFFFF")
        self.ax2.set_facecolor("#FFFFFF")
        
        # Add description label
        self.description = ModernLabel(
            self,
            text="Adjust the sliders to see how different parameters affect crop recommendations.",
            font=("Helvetica", 10),
            text_color="#757575"
        )
        self.description.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 15))
        
    def update_visualization(self, soil_params: Dict[str, float], climate_params: Dict[str, float]):
        """Update the visualization with new data."""
        try:
            # Clear previous plots
            self.ax1.clear()
            self.ax2.clear()
            
            # Plot soil parameters with green colors
            soil_values = list(soil_params.values())
            soil_keys = list(soil_params.keys())
            bars1 = self.ax1.bar(soil_keys, soil_values, color="#2CC985")
            self.ax1.set_title('Soil Parameters', fontweight='bold')
            self.ax1.set_ylabel('Value')
            
            # Add value labels
            for bar in bars1:
                height = bar.get_height()
                self.ax1.text(
                    bar.get_x() + bar.get_width()/2.,
                    height,
                    f'{height:.1f}',
                    ha='center', 
                    va='bottom'
                )
            
            # Plot climate parameters with green colors
            climate_values = list(climate_params.values())
            climate_keys = list(climate_params.keys())
            bars2 = self.ax2.bar(climate_keys, climate_values, color="#2CC985")
            self.ax2.set_title('Climate Parameters', fontweight='bold')
            self.ax2.set_ylabel('Value')
            
            # Add value labels
            for bar in bars2:
                height = bar.get_height()
                self.ax2.text(
                    bar.get_x() + bar.get_width()/2.,
                    height,
                    f'{height:.1f}',
                    ha='center', 
                    va='bottom'
                )
            
            # Adjust layout and update canvas
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating visualization: {str(e)}")

class CropAdvisorFrame(ModernFrame):
    """The main frame for the Crop Advisor feature."""
    def __init__(self, master, on_predict: Callable[[Dict[str, float]], Any], **kwargs):
        super().__init__(master, **kwargs)
        
        # Create main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        # Create left panel for inputs
        self.input_frame = ModernFrame(self)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        # Create soil parameters section
        soil_label = ModernLabel(
            self.input_frame,
            text="Soil Parameters",
            font=("Helvetica", 14, "bold")
        )
        soil_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Create soil parameter sliders
        self.sliders = {}
        
        # Nitrogen slider
        row = 1
        self.sliders["Nitrogen"] = ModernSlider(
            self.input_frame, 
            "Nitrogen (N)", 
            0, 
            140
        )
        self.sliders["Nitrogen"].grid(row=row, column=0, pady=5, sticky="ew")
        row += 1
        
        # Phosphorus slider
        self.sliders["Phosphorus"] = ModernSlider(
            self.input_frame, 
            "Phosphorus (P)", 
            0, 
            145
        )
        self.sliders["Phosphorus"].grid(row=row, column=0, pady=5, sticky="ew")
        row += 1
        
        # Potassium slider
        self.sliders["Potassium"] = ModernSlider(
            self.input_frame, 
            "Potassium (K)", 
            0, 
            205
        )
        self.sliders["Potassium"].grid(row=row, column=0, pady=5, sticky="ew")
        row += 1
        
        # pH slider
        self.sliders["pH_Value"] = ModernSlider(
            self.input_frame, 
            "pH", 
            0, 
            14
        )
        self.sliders["pH_Value"].grid(row=row, column=0, pady=5, sticky="ew")
        row += 1
        
        # Create climate parameters section
        climate_label = ModernLabel(
            self.input_frame,
            text="Climate Parameters",
            font=("Helvetica", 14, "bold")
        )
        climate_label.grid(row=row, column=0, sticky="w", pady=(20, 10))
        row += 1
        
        # Temperature slider
        self.sliders["Temperature"] = ModernSlider(
            self.input_frame, 
            "Temperature (°C)", 
            0, 
            50
        )
        self.sliders["Temperature"].grid(row=row, column=0, pady=5, sticky="ew")
        row += 1
        
        # Humidity slider
        self.sliders["Humidity"] = ModernSlider(
            self.input_frame, 
            "Humidity (%)", 
            0, 
            100
        )
        self.sliders["Humidity"].grid(row=row, column=0, pady=5, sticky="ew")
        row += 1
        
        # Rainfall slider
        self.sliders["Rainfall"] = ModernSlider(
            self.input_frame, 
            "Rainfall (mm)", 
            0, 
            300
        )
        self.sliders["Rainfall"].grid(row=row, column=0, pady=5, sticky="ew")
        row += 1
        
        # Add predict button
        self.predict_button = ModernButton(
            self.input_frame,
            text="Get Crop Recommendation",
            command=self._on_predict
        )
        self.predict_button.grid(row=row, column=0, pady=(20, 10))
        
        # Right panel for visualization
        self.viz_frame = VisualizationFrame(self)
        self.viz_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Store callback
        self.on_predict = on_predict
        
        # Set initial slider values
        for slider in self.sliders.values():
            slider.set(slider.slider.cget("from_") + (slider.slider.cget("to") - slider.slider.cget("from_")) / 2)
        
        # Update visualization initially
        self._update_visualization()
        
        # Add slider change callbacks
        for name, slider in self.sliders.items():
            slider.original_command = lambda val, n=name: self._on_slider_change(n, val)
    
    def _on_slider_change(self, name, value):
        """Handle slider value change."""
        self._update_visualization()
    
    def _update_visualization(self):
        """Update the visualization with current slider values."""
        try:
            # Group soil parameters
            soil_params = {
                "Nitrogen": self.sliders["Nitrogen"].get(),
                "Phosphorus": self.sliders["Phosphorus"].get(),
                "Potassium": self.sliders["Potassium"].get(),
                "pH": self.sliders["pH_Value"].get()
            }
            
            # Group climate parameters
            climate_params = {
                "Temperature": self.sliders["Temperature"].get(),
                "Humidity": self.sliders["Humidity"].get(),
                "Rainfall": self.sliders["Rainfall"].get()
            }
            
            # Update visualization
            self.viz_frame.update_visualization(soil_params, climate_params)
            
        except Exception as e:
            logger.error(f"Error updating visualization: {str(e)}")
    
    def _on_predict(self):
        """Handle predict button click."""
        try:
            # Collect parameter values
            params = {
                "Nitrogen": self.sliders["Nitrogen"].get(),
                "Phosphorus": self.sliders["Phosphorus"].get(),
                "Potassium": self.sliders["Potassium"].get(),
                "Temperature": self.sliders["Temperature"].get(),
                "Humidity": self.sliders["Humidity"].get(),
                "pH_Value": self.sliders["pH_Value"].get(),
                "Rainfall": self.sliders["Rainfall"].get()
            }
            
            # Call prediction callback
            if self.on_predict:
                self.on_predict(params)
                
        except Exception as e:
            logger.error(f"Error in predict button handler: {str(e)}")
    
    def set_initial_values(self):
        """Set initial values for all sliders."""
        try:
            # Set default values that are good for most crops
            default_values = {
                "Nitrogen": 70,     # Mid-range nitrogen
                "Phosphorus": 70,   # Mid-range phosphorus
                "Potassium": 100,   # Mid-range potassium
                "Temperature": 25,   # Room temperature
                "Humidity": 60,     # Moderate humidity
                "pH_Value": 6.5,    # Slightly acidic (good for most plants)
                "Rainfall": 150     # Moderate rainfall
            }
            
            # Set values for each slider
            for name, value in default_values.items():
                if name in self.sliders:
                    self.sliders[name].set(value)
                    
            # Update visualization with initial values
            self._update_visualization()
            
        except Exception as e:
            logger.error(f"Error setting initial values: {str(e)}")

# Add the SustainabilityTipsFrame class
class SustainabilityTipsFrame(ModernFrame):
    """Frame for sustainability tips and chat interface."""
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create welcome section
        self._create_welcome_section()
        
        # Create chat interface
        self.chat_frame = ModernChatFrame(
            self,
            on_send=app._handle_chat_message
        )
        self.chat_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Add initial bot message
        self.chat_frame.add_bot_message(
            "Welcome to the Sustainability Assistant! 🌱\n\n"
            "I'm here to help you with:\n"
            "• Urban farming techniques and best practices\n"
            "• Sustainable gardening methods\n"
            "• Water conservation tips\n"
            "• Soil health management\n"
            "• Eco-friendly pest control\n"
            "• Tool recommendations\n\n"
            "Feel free to ask any questions about sustainable farming!"
        )
    
    def _create_welcome_section(self):
        """Create the welcome section at the top."""
        welcome_frame = ModernFrame(self)
        welcome_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        welcome_frame.grid_columnconfigure(1, weight=1)
        
        # Add icon
        icon_label = ModernLabel(
            welcome_frame,
            text="🌿",
            font=("Segoe UI Emoji", 32)
        )
        icon_label.grid(row=0, column=0, padx=(0, 15))
        
        # Add title and subtitle
        text_frame = ModernFrame(welcome_frame)
        text_frame.grid(row=0, column=1, sticky="ew")
        
        title = ModernLabel(
            text_frame,
            text="Sustainability Assistant",
            font=("Helvetica", 18, "bold"),
            text_color="#2CC985"
        )
        title.grid(row=0, column=0, sticky="w")
        
        subtitle = ModernLabel(
            text_frame,
            text="Get expert advice on sustainable urban farming practices",
            font=("Helvetica", 12),
            text_color="#666666"
        )
        subtitle.grid(row=1, column=0, sticky="w") 