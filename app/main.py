import os
import sys
import logging
import customtkinter as ctk
from utils.interface import ModernFrame, ModernButton, ModernLabel, CropAdvisorFrame, ModernChatFrame, SustainabilityTipsFrame
from utils.data_processor import DataProcessor
from utils.sustainability_bot import SustainabilityBot
import tkinter as tk
from tkinter import messagebox

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class UrbanFarmAI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("UrbanFarm AI")
        self.geometry("1200x800")
        
        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        
        # Initialize components
        self.data_processor = DataProcessor()
        self.sustainability_bot = SustainabilityBot()
        
        # Create main container
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create header
        self._create_header()
        
        # Create main content area
        self._create_main_content()
        
        # Initialize model
        self._initialize_model()
    
    def _create_header(self):
        """Create the application header."""
        header = ModernFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        # Add title
        title = ModernLabel(
            header,
            text="UrbanFarm AI",
            font=("Helvetica", 24, "bold")
        )
        title.grid(row=0, column=0, padx=20, pady=20)
    
    def _create_main_content(self):
        """Create the main content area."""
        # Create tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        # Add tabs
        self.tab_advisor = self.tabview.add("Crop Advisor")
        self.tab_tips = self.tabview.add("Sustainability Tips")
        
        # Create Crop Advisor tab
        self._create_crop_advisor_tab()
        
        # Create Sustainability Tips tab
        self._create_sustainability_tab()
    
    def _create_crop_advisor_tab(self):
        """Create the Crop Advisor tab content."""
        tab = self.tab_advisor
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Create Crop Advisor frame
        self.crop_advisor = CropAdvisorFrame(
            tab,
            on_predict=self._handle_crop_prediction
        )
        self.crop_advisor.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    def _create_sustainability_tab(self):
        """Create the Sustainability Tips tab content."""
        tab = self.tab_tips
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Create Sustainability Tips frame
        self.sustainability_tips = SustainabilityTipsFrame(
            tab,
            app=self
        )
        self.sustainability_tips.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    def _initialize_model(self):
        """Initialize the crop recommendation model."""
        try:
            if not self.data_processor.load_model():
                logger.warning("Failed to load model. Training new model...")
                if not self.data_processor.train_model():
                    logger.error("Failed to train model")
                    self._show_error_dialog(
                        "Model Error",
                        "Failed to initialize the crop recommendation model."
                    )
                else:
                    logger.info("Successfully trained new model")
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}")
            self._show_error_dialog(
                "Initialization Error",
                "An error occurred while initializing the application."
            )
    
    def _handle_crop_prediction(self, params):
        """Handle crop prediction request."""
        try:
            # Convert parameter names to match model expectations
            model_params = {
                'n': params['Nitrogen'],
                'p': params['Phosphorus'],
                'k': params['Potassium'],
                'temperature': params['Temperature'],
                'humidity': params['Humidity'],
                'ph': params['pH_Value'],
                'rainfall': params['Rainfall']
            }
            
            # Make prediction
            result = self.data_processor.predict(model_params)
            
            if result is None:
                raise ValueError("Failed to get prediction result")
            
            # Format prediction message
            message = self._format_prediction_message(result)
            
            # Show prediction dialog
            self._show_prediction_dialog(message)
            
        except Exception as e:
            logger.error(f"Error handling prediction: {str(e)}")
            self._show_error_dialog(
                "Prediction Error",
                "An error occurred while making the prediction."
            )
    
    def _format_prediction_message(self, result):
        """Format the prediction result message."""
        try:
            # Get the top prediction and confidence
            prediction = result['prediction']
            confidence = result['confidence']
            top_3 = result['top_3']
            
            # Format message with emojis and better formatting
            message = "🌟 Best Recommendation 🌟\n"
            message += "═══════════════════════\n"
            message += f"🌱 {prediction}\n"
            message += f"📊 Confidence: {confidence:.1%}\n\n"
            
            message += "📋 Other Suitable Crops\n"
            message += "═══════════════════════\n"
            for crop, prob in top_3[1:]:
                message += f"🌿 {crop:<15} {prob:.1%}\n"
            
            # Add a note at the bottom
            message += "\n💡 Note: Confidence scores indicate how well\n"
            message += "    the conditions match each crop's requirements."
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting prediction message: {str(e)}")
            return "Error formatting prediction result"
    
    def _show_prediction_dialog(self, message):
        """Show the prediction result in a dialog."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Crop Recommendation")
        dialog.geometry("500x400")
        
        # Make dialog modal
        dialog.transient(self)
        dialog.grab_set()
        
        # Create main container
        container = ModernFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add header
        header = ModernFrame(container)
        header.pack(fill="x", pady=(0, 20))
        
        title = ModernLabel(
            header,
            text="Crop Recommendation Results",
            font=("Helvetica", 18, "bold"),
            text_color="#2CC985"  # Green color for title
        )
        title.pack(side="left")
        
        # Add content in a frame with border
        content_frame = ModernFrame(container)
        content_frame.pack(fill="both", expand=True)
        
        # Add scrollable text area with custom font and colors
        content = ctk.CTkTextbox(
            content_frame,
            width=460,
            height=280,
            font=("Consolas", 12),  # Monospace font for better alignment
            text_color="#333333",  # Dark gray for better readability
            fg_color="#FFFFFF",    # White background
            border_width=1,
            border_color="#E0E0E0" # Light gray border
        )
        content.pack(padx=10, pady=10)
        content.insert("1.0", message)
        content.configure(state="disabled")
        
        # Add close button with custom styling
        button_frame = ModernFrame(container)
        button_frame.pack(fill="x", pady=(20, 0))
        
        close_btn = ModernButton(
            button_frame,
            text="Close",
            command=dialog.destroy,
            width=120,
            height=32,
            font=("Helvetica", 12)
        )
        close_btn.pack(side="right")
    
    def _show_error_dialog(self, title, message):
        """Show an error dialog."""
        messagebox.showerror(title, message)
    
    def _handle_chat_message(self, message):
        """Handle chat messages in the sustainability tips tab."""
        try:
            # Get response from bot
            response = self.sustainability_bot.get_response(message)
            
            # Add response to chat
            self.sustainability_tips.chat_frame.add_bot_message(response)
            
        except Exception as e:
            logger.error(f"Error handling chat message: {str(e)}")
            self.sustainability_tips.chat_frame.add_bot_message(
                "I'm sorry, but I encountered an error processing your message. Please try again."
            )

if __name__ == "__main__":
    try:
        app = UrbanFarmAI()
        app.mainloop()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        messagebox.showerror(
            "Application Error",
            "An error occurred while running the application."
        ) 