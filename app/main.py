import os
import sys
import logging
import customtkinter as ctk
from utils.interface import ModernFrame, ModernButton, ModernLabel, CropAdvisorFrame, ModernChatFrame, SustainabilityTipsFrame
from utils.data_processor import DataProcessor
from utils.sustainability_bot import SustainabilityBot
import tkinter as tk
from tkinter import messagebox
import datetime
from typing import List, Dict

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
            
            # Format predictions for display
            predictions = []
            if isinstance(result, dict) and 'top_3' in result:
                predictions = result['top_3']
            else:
                # If we only have a single prediction
                predictions = [(result['prediction'], result['confidence'])]
                # Add some dummy values for other positions if top_3 isn't available
                if len(predictions) < 3:
                    remaining = 3 - len(predictions)
                    for _ in range(remaining):
                        predictions.append(("N/A", 0.0))
            
            # Show prediction dialog
            self._show_prediction_dialog(predictions, params)
            
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
    
    def _show_prediction_dialog(self, predictions, params):
        """Show the prediction results in a dialog."""
        try:
            # Create dialog window
            dialog = ctk.CTkToplevel(self)
            dialog.title("Crop Recommendation Results")
            dialog.geometry("600x700")
            dialog.resizable(False, False)
            
            # Make dialog modal
            dialog.transient(self)
            dialog.grab_set()
            
            # Configure grid
            dialog.grid_columnconfigure(0, weight=1)
            
            # Create header
            header_frame = ModernFrame(dialog, fg_color="#2CC985")
            header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
            header_frame.grid_columnconfigure(0, weight=1)
            
            # Add title
            title = ModernLabel(
                header_frame,
                text="🌱 Crop Recommendation Results",
                font=("Helvetica", 18, "bold"),
                text_color="white"
            )
            title.grid(row=0, column=0, padx=20, pady=20)
            
            # Create content frame
            content_frame = ModernFrame(dialog)
            content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
            content_frame.grid_columnconfigure(0, weight=1)
            
            # Add timestamp
            timestamp = ModernLabel(
                content_frame,
                text=f"Analysis Date: {datetime.datetime.now().strftime('%B %d, %Y %H:%M')}",
                font=("Helvetica", 10),
                text_color="#666666"
            )
            timestamp.grid(row=0, column=0, sticky="w", pady=(0, 20))
            
            # Add top predictions section
            predictions_label = ModernLabel(
                content_frame,
                text="Top Recommended Crops",
                font=("Helvetica", 14, "bold")
            )
            predictions_label.grid(row=1, column=0, sticky="w", pady=(0, 10))
            
            # Create predictions display
            for i, (crop, probability) in enumerate(predictions):
                pred_frame = ModernFrame(content_frame)
                pred_frame.grid(row=i+2, column=0, sticky="ew", pady=(0, 10))
                pred_frame.grid_columnconfigure(1, weight=1)
                
                # Add rank emoji
                rank_emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                rank_label = ModernLabel(
                    pred_frame,
                    text=rank_emoji,
                    font=("Segoe UI Emoji", 16)
                )
                rank_label.grid(row=0, column=0, padx=(0, 10))
                
                # Add crop name
                crop_label = ModernLabel(
                    pred_frame,
                    text=crop,
                    font=("Helvetica", 14, "bold")
                )
                crop_label.grid(row=0, column=1, sticky="w")
                
                # Add probability bar
                prob_frame = ModernFrame(pred_frame, height=6, fg_color="#E0E0E0", corner_radius=3)
                prob_frame.grid(row=1, column=1, sticky="ew", pady=(5, 0))
                prob_frame.grid_propagate(False)
                
                bar_width = int(probability * 100)
                bar = ModernFrame(prob_frame, fg_color="#2CC985", corner_radius=3)
                bar.place(relx=0, rely=0, relwidth=bar_width/100, relheight=1)
                
                # Add percentage
                prob_label = ModernLabel(
                    pred_frame,
                    text=f"{probability:.1%}",
                    font=("Helvetica", 12)
                )
                prob_label.grid(row=0, column=2, padx=(10, 0))
            
            # Add parameters section
            params_label = ModernLabel(
                content_frame,
                text="Input Parameters",
                font=("Helvetica", 14, "bold")
            )
            params_label.grid(row=5, column=0, sticky="w", pady=(20, 10))
            
            # Create parameters frame
            params_frame = ModernFrame(content_frame)
            params_frame.grid(row=6, column=0, sticky="ew")
            params_frame.grid_columnconfigure(0, weight=1)
            params_frame.grid_columnconfigure(1, weight=1)
            
            # Split parameters into two groups
            soil_params = {
                "Nitrogen": (params["Nitrogen"], "mg/kg"),
                "Phosphorus": (params["Phosphorus"], "mg/kg"),
                "Potassium": (params["Potassium"], "mg/kg"),
                "pH Value": (params["pH_Value"], "")
            }
            
            climate_params = {
                "Temperature": (params["Temperature"], "°C"),
                "Humidity": (params["Humidity"], "%"),
                "Rainfall": (params["Rainfall"], "mm")
            }
            
            # Add soil parameters
            soil_title = ModernLabel(
                params_frame,
                text="Soil Parameters",
                font=("Helvetica", 12, "bold")
            )
            soil_title.grid(row=0, column=0, sticky="w", pady=(0, 5))
            
            for i, (name, (value, unit)) in enumerate(soil_params.items()):
                param_label = ModernLabel(
                    params_frame,
                    text=f"{name}:",
                    font=("Helvetica", 11)
                )
                param_label.grid(row=i+1, column=0, sticky="w", padx=(20, 0))
                
                value_label = ModernLabel(
                    params_frame,
                    text=f"{value:.1f} {unit}",
                    font=("Helvetica", 11)
                )
                value_label.grid(row=i+1, column=0, sticky="e", padx=(0, 20))
            
            # Add climate parameters
            climate_title = ModernLabel(
                params_frame,
                text="Climate Parameters",
                font=("Helvetica", 12, "bold")
            )
            climate_title.grid(row=0, column=1, sticky="w", pady=(0, 5))
            
            for i, (name, (value, unit)) in enumerate(climate_params.items()):
                param_label = ModernLabel(
                    params_frame,
                    text=f"{name}:",
                    font=("Helvetica", 11)
                )
                param_label.grid(row=i+1, column=1, sticky="w", padx=(20, 0))
                
                value_label = ModernLabel(
                    params_frame,
                    text=f"{value:.1f} {unit}",
                    font=("Helvetica", 11)
                )
                value_label.grid(row=i+1, column=1, sticky="e", padx=(0, 20))
            
            # Add download report button
            download_button = ModernButton(
                dialog,
                text="Download Report",
                width=200,
                height=35,
                font=("Helvetica", 12, "bold"),
                command=lambda: self._generate_report(predictions, params)
            )
            download_button.grid(row=2, column=0, pady=20)
            
            # Add close button
            close_button = ModernButton(
                dialog,
                text="Close",
                width=200,
                height=35,
                font=("Helvetica", 12, "bold"),
                command=dialog.destroy
            )
            close_button.grid(row=3, column=0, pady=(0, 20))
            
            # Center the dialog on the screen
            dialog.update_idletasks()
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            x = (dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (dialog.winfo_screenheight() // 2) - (height // 2)
            dialog.geometry(f"{width}x{height}+{x}+{y}")
            
        except Exception as e:
            logger.error(f"Error showing prediction dialog: {str(e)}")
            self._show_error_dialog("Error", "Failed to display prediction results.")
    
    def _generate_report(self, predictions, params):
        """Generate and save a detailed PDF report."""
        try:
            # Get timestamp for filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"crop_recommendation_report_{timestamp}.txt"
            
            # Create report content
            report = []
            report.append("=" * 80)
            report.append("URBAN FARM AI - CROP RECOMMENDATION REPORT")
            report.append("=" * 80)
            report.append("")
            
            # Add timestamp
            report.append(f"Generated on: {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}")
            report.append("")
            
            # Add top recommendations
            report.append("-" * 80)
            report.append("TOP RECOMMENDED CROPS")
            report.append("-" * 80)
            report.append("")
            
            for i, (crop, probability) in enumerate(predictions, 1):
                report.append(f"{i}. {crop}")
                report.append(f"   Confidence Score: {probability:.1%}")
                
                # Add crop-specific tips
                if i == 1:  # Add detailed information for the top recommendation
                    report.append("   Key Growing Tips:")
                    tips = self._get_crop_tips(crop)
                    for tip in tips:
                        report.append(f"   • {tip}")
                report.append("")
            
            # Add input parameters
            report.append("-" * 80)
            report.append("SOIL PARAMETERS")
            report.append("-" * 80)
            report.append(f"Nitrogen (N):     {params['Nitrogen']:.1f} mg/kg")
            report.append(f"Phosphorus (P):   {params['Phosphorus']:.1f} mg/kg")
            report.append(f"Potassium (K):    {params['Potassium']:.1f} mg/kg")
            report.append(f"pH Value:         {params['pH_Value']:.1f}")
            report.append("")
            
            report.append("-" * 80)
            report.append("CLIMATE PARAMETERS")
            report.append("-" * 80)
            report.append(f"Temperature:      {params['Temperature']:.1f}°C")
            report.append(f"Humidity:         {params['Humidity']:.1f}%")
            report.append(f"Rainfall:         {params['Rainfall']:.1f} mm")
            report.append("")
            
            # Add analysis and recommendations
            report.append("-" * 80)
            report.append("ANALYSIS & RECOMMENDATIONS")
            report.append("-" * 80)
            report.append("")
            
            # Soil analysis
            report.append("Soil Analysis:")
            soil_analysis = self._analyze_soil_parameters(params)
            for point in soil_analysis:
                report.append(f"• {point}")
            report.append("")
            
            # Climate analysis
            report.append("Climate Analysis:")
            climate_analysis = self._analyze_climate_parameters(params)
            for point in climate_analysis:
                report.append(f"• {point}")
            report.append("")
            
            # Add sustainability tips
            report.append("-" * 80)
            report.append("SUSTAINABILITY TIPS")
            report.append("-" * 80)
            report.append("")
            
            sustainability_tips = [
                "Practice crop rotation to maintain soil health and prevent pest buildup",
                "Consider companion planting to maximize space and improve crop yields",
                "Implement water-efficient irrigation systems like drip irrigation",
                "Use organic mulch to retain soil moisture and suppress weeds",
                "Monitor and maintain proper pH levels for optimal nutrient absorption"
            ]
            
            for tip in sustainability_tips:
                report.append(f"• {tip}")
            report.append("")
            
            # Add footer
            report.append("=" * 80)
            report.append("Thank you for using Urban Farm AI!")
            report.append("For more information and support, visit our website or contact our support team.")
            report.append("=" * 80)
            
            # Save report to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report))
            
            # Show success message
            self._show_success_dialog("Report Generated", f"Report has been saved as:\n{filename}")
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            self._show_error_dialog("Error", "Failed to generate report.")
    
    def _get_crop_tips(self, crop: str) -> List[str]:
        """Get specific growing tips for a crop."""
        # Define tips for common crops
        crop_tips = {
            "rice": [
                "Maintain standing water of 2-5 cm during growth",
                "Ensure good drainage during harvesting",
                "Control weeds early in the growing season",
                "Monitor for pests like stem borers"
            ],
            "wheat": [
                "Plant in well-draining soil",
                "Maintain consistent moisture levels",
                "Apply nitrogen fertilizer in split doses",
                "Watch for rust and fungal diseases"
            ],
            "maize": [
                "Plant in full sun exposure",
                "Space plants 20-30 cm apart",
                "Keep soil consistently moist",
                "Add support for tall varieties"
            ],
            "potato": [
                "Plant in loose, well-draining soil",
                "Hill soil around plants as they grow",
                "Maintain even moisture levels",
                "Watch for signs of blight"
            ],
            "tomato": [
                "Provide support with stakes or cages",
                "Prune suckers for indeterminate varieties",
                "Water deeply and consistently",
                "Monitor for blight and pests"
            ]
        }
        
        # Return generic tips if crop not in database
        default_tips = [
            "Ensure proper soil preparation before planting",
            "Monitor water needs regularly",
            "Watch for signs of pest infestation",
            "Maintain appropriate spacing between plants"
        ]
        
        return crop_tips.get(crop.lower(), default_tips)
    
    def _analyze_soil_parameters(self, params: Dict[str, float]) -> List[str]:
        """Analyze soil parameters and provide recommendations."""
        analysis = []
        
        # Analyze N-P-K levels
        if params["Nitrogen"] < 50:
            analysis.append("Nitrogen levels are low. Consider adding nitrogen-rich fertilizers or composted manure.")
        elif params["Nitrogen"] > 100:
            analysis.append("Nitrogen levels are high. Monitor plant growth for excessive vegetative growth.")
            
        if params["Phosphorus"] < 50:
            analysis.append("Phosphorus levels are low. Add rock phosphate or bone meal to improve levels.")
        elif params["Phosphorus"] > 100:
            analysis.append("Phosphorus levels are high. Avoid adding phosphorus-rich fertilizers.")
            
        if params["Potassium"] < 50:
            analysis.append("Potassium levels are low. Consider adding potash or wood ash.")
        elif params["Potassium"] > 150:
            analysis.append("Potassium levels are high. Monitor for nutrient imbalances.")
        
        # Analyze pH
        if params["pH_Value"] < 6.0:
            analysis.append("Soil is acidic. Consider adding lime to raise pH.")
        elif params["pH_Value"] > 7.5:
            analysis.append("Soil is alkaline. Consider adding sulfur to lower pH.")
        else:
            analysis.append("Soil pH is in optimal range for most crops.")
        
        return analysis
    
    def _analyze_climate_parameters(self, params: Dict[str, float]) -> List[str]:
        """Analyze climate parameters and provide recommendations."""
        analysis = []
        
        # Analyze temperature
        if params["Temperature"] < 15:
            analysis.append("Temperature is low. Consider cold-hardy crops or greenhouse cultivation.")
        elif params["Temperature"] > 30:
            analysis.append("Temperature is high. Provide shade and adequate irrigation.")
        else:
            analysis.append("Temperature is in optimal range for most crops.")
        
        # Analyze humidity
        if params["Humidity"] < 40:
            analysis.append("Humidity is low. Consider using mulch and regular misting.")
        elif params["Humidity"] > 80:
            analysis.append("Humidity is high. Ensure good air circulation to prevent fungal diseases.")
        else:
            analysis.append("Humidity levels are suitable for most crops.")
        
        # Analyze rainfall
        if params["Rainfall"] < 100:
            analysis.append("Rainfall is low. Implement irrigation system and moisture conservation practices.")
        elif params["Rainfall"] > 200:
            analysis.append("Rainfall is high. Ensure good drainage and consider raised beds.")
        else:
            analysis.append("Rainfall levels are adequate for most crops.")
        
        return analysis
    
    def _show_success_dialog(self, title: str, message: str):
        """Show a success dialog."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # Make dialog modal
        dialog.transient(self)
        dialog.grab_set()
        
        # Configure grid
        dialog.grid_columnconfigure(0, weight=1)
        
        # Add success icon
        icon_label = ModernLabel(
            dialog,
            text="✅",
            font=("Segoe UI Emoji", 48)
        )
        icon_label.grid(row=0, column=0, pady=(20, 10))
        
        # Add message
        msg_label = ModernLabel(
            dialog,
            text=message,
            font=("Helvetica", 12)
        )
        msg_label.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # Add close button
        close_button = ModernButton(
            dialog,
            text="OK",
            width=100,
            command=dialog.destroy
        )
        close_button.grid(row=2, column=0, pady=(0, 20))
    
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