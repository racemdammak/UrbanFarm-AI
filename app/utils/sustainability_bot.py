from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
import logging
import random
import re
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

class SustainabilityBot:
    """An intelligent chatbot for providing sustainability and urban farming advice."""
    
    def __init__(self):
        # Initialize knowledge base with categorized information
        self.knowledge_base = {
            'urban_farming': {
                'basics': [
                    "Start with easy-to-grow crops like herbs, lettuce, and tomatoes in containers 🌱",
                    "Vertical gardening is perfect for small spaces - use wall-mounted planters 🏗️",
                    "Container gardening offers flexibility and control over growing conditions 🪴",
                    "Create a composting system to recycle kitchen waste into nutrient-rich soil 🔄",
                    "Use companion planting to maximize space and improve crop health 🌿"
                ],
                'advanced': [
                    "Implement hydroponics for water-efficient year-round growing 💧",
                    "Consider aquaponics to combine fish farming with plant growing 🐟",
                    "Use LED grow lights to extend growing seasons indoors 💡",
                    "Create a greenhouse or cold frame for climate control 🏠",
                    "Develop a seed-saving program for sustainable cultivation 🌰"
                ]
            },
            'water_management': {
                'conservation': [
                    "Install a rainwater harvesting system to collect natural water 🌧️",
                    "Use drip irrigation for efficient water delivery 💧",
                    "Apply mulch to reduce water evaporation from soil 🍂",
                    "Water plants early morning or late evening to minimize evaporation ⏰",
                    "Group plants with similar water needs together 🌿"
                ],
                'systems': [
                    "Install moisture sensors to optimize watering schedules 📊",
                    "Use self-watering containers for consistent moisture 🪴",
                    "Create greywater systems for garden irrigation ♻️",
                    "Build swales to capture and direct rainwater 🌊",
                    "Implement automated irrigation with timers ⚡"
                ]
            },
            'soil_health': {
                'basics': [
                    "Test soil pH and nutrient levels regularly 🧪",
                    "Add organic matter to improve soil structure 🍂",
                    "Practice crop rotation to maintain soil health 🔄",
                    "Use cover crops to protect and enrich soil 🌱",
                    "Avoid tilling to preserve soil structure 🚫"
                ],
                'composting': [
                    "Balance green and brown materials in compost 🥬",
                    "Maintain proper moisture in compost pile 💧",
                    "Turn compost regularly for faster decomposition 🔄",
                    "Use vermicomposting for indoor composting 🪱",
                    "Create compost tea for liquid fertilizer 🫖"
                ]
            },
            'pest_management': {
                'prevention': [
                    "Plant pest-resistant varieties when possible 🌿",
                    "Use companion planting for natural pest control 🌱",
                    "Maintain healthy soil to prevent disease 🌍",
                    "Install physical barriers like row covers 🏗️",
                    "Practice proper plant spacing for air circulation 📏"
                ],
                'natural_control': [
                    "Introduce beneficial insects like ladybugs 🐞",
                    "Use neem oil for organic pest control 🌿",
                    "Create herb barriers to repel pests 🌿",
                    "Use diatomaceous earth for crawling insects 🪨",
                    "Make natural pest sprays from herbs and soap 🌿"
                ]
            },
            'seasonal_tips': {
                'spring': [
                    "Start seeds indoors for early planting 🌱",
                    "Prepare garden beds with compost 🌿",
                    "Plan crop rotation for the season 📋",
                    "Install irrigation systems before planting 💧",
                    "Begin hardening off seedlings 🌱"
                ],
                'summer': [
                    "Mulch to retain moisture in hot weather 🌞",
                    "Harvest regularly to encourage production 🌾",
                    "Provide shade for sensitive plants ⛱️",
                    "Monitor for pest issues frequently 🔍",
                    "Water deeply but less frequently 💧"
                ],
                'fall': [
                    "Plant cold-hardy crops for fall harvest 🥬",
                    "Collect seeds from mature plants 🌰",
                    "Add mulch for winter protection 🍂",
                    "Clean and store garden tools 🔧",
                    "Start a compost pile with fallen leaves 🍁"
                ],
                'winter': [
                    "Plan next season's garden 📝",
                    "Maintain indoor herbs and microgreens 🌿",
                    "Check stored seeds for viability 🌱",
                    "Repair and maintain tools 🔧",
                    "Start a windowsill garden 🪴"
                ]
            }
        }
        
        # Define conversation patterns
        self.patterns = {
            'greeting': re.compile(r'hello|hi|hey|greetings', re.I),
            'farewell': re.compile(r'bye|goodbye|thank|thanks', re.I),
            'urban_farming': re.compile(r'urban farm|city garden|grow|plant|space', re.I),
            'water': re.compile(r'water|irrigation|rain|drought|moist', re.I),
            'soil': re.compile(r'soil|dirt|compost|fertilizer|nutrient', re.I),
            'pests': re.compile(r'pest|bug|insect|disease|control', re.I),
            'season': re.compile(r'spring|summer|fall|winter|season', re.I),
            'specific_crop': re.compile(r'how.*(grow|plant|care for) ([a-zA-Z ]+)', re.I)
        }
        
        # Store conversation context
        self.context = {}
        
    def _get_context(self, message: str) -> List[Tuple[str, Optional[str]]]:
        """Determine the context of the user's message."""
        contexts = []
        
        # Check each pattern
        if self.patterns['greeting'].search(message):
            contexts.append(('greeting', None))
        if self.patterns['farewell'].search(message):
            contexts.append(('farewell', None))
        if self.patterns['urban_farming'].search(message):
            contexts.append(('urban_farming', None))
        if self.patterns['water'].search(message):
            contexts.append(('water_management', None))
        if self.patterns['soil'].search(message):
            contexts.append(('soil_health', None))
        if self.patterns['pests'].search(message):
            contexts.append(('pest_management', None))
        
        # Check for seasonal context
        for season in ['spring', 'summer', 'fall', 'winter']:
            if re.search(rf'\b{season}\b', message, re.I):
                contexts.append(('seasonal_tips', season))
        
        # Check for specific crop questions
        crop_match = self.patterns['specific_crop'].search(message)
        if crop_match:
            contexts.append(('specific_crop', crop_match.group(2).strip().lower()))
        
        return contexts if contexts else [('general', None)]
    
    def _get_crop_advice(self, crop: str) -> str:
        """Get specific advice for growing a particular crop."""
        common_crops = {
            'tomato': {
                'sun': 'full sun (6-8 hours)',
                'water': 'consistent moisture',
                'soil': 'rich, well-draining',
                'tips': [
                    "Support with cages or stakes",
                    "Prune suckers for better airflow",
                    "Feed with balanced fertilizer"
                ]
            },
            'lettuce': {
                'sun': 'partial to full sun',
                'water': 'regular watering',
                'soil': 'rich, loose soil',
                'tips': [
                    "Succession plant every 2 weeks",
                    "Harvest outer leaves first",
                    "Provide shade in hot weather"
                ]
            },
            'herbs': {
                'sun': 'full sun',
                'water': 'moderate watering',
                'soil': 'well-draining soil',
                'tips': [
                    "Harvest regularly to promote growth",
                    "Most herbs prefer slightly dry conditions",
                    "Start with basil, mint, or parsley"
                ]
            }
        }
        
        # Find best matching crop
        crop = crop.lower()
        if 'tomato' in crop:
            crop_info = common_crops['tomato']
        elif 'lettuce' in crop:
            crop_info = common_crops['lettuce']
        elif 'herb' in crop or crop in ['basil', 'mint', 'parsley', 'cilantro']:
            crop_info = common_crops['herbs']
        else:
            return f"For growing {crop}:\n" + \
                   "1. Research specific sunlight requirements\n" + \
                   "2. Use well-draining soil with organic matter\n" + \
                   "3. Water consistently based on needs\n" + \
                   "4. Monitor for pests and diseases\n" + \
                   "5. Harvest at the right time"
        
        # Format specific crop advice
        advice = f"🌱 Growing {crop.title()} 🌱\n\n"
        advice += f"☀️ Sunlight: {crop_info['sun']}\n"
        advice += f"💧 Water: {crop_info['water']}\n"
        advice += f"🌍 Soil: {crop_info['soil']}\n\n"
        advice += "📝 Key Tips:\n"
        for tip in crop_info['tips']:
            advice += f"• {tip}\n"
        
        return advice
    
    def _get_relevant_info(self, contexts: List[Tuple[str, Optional[str]]]) -> str:
        """Get relevant information based on the context."""
        responses = []
        
        for context, subtype in contexts:
            if context == 'greeting':
                responses.append("Hello! I'm your Sustainability Assistant. How can I help you today? 🌱")
            
            elif context == 'farewell':
                responses.append("Happy gardening! Feel free to return if you need more advice! 🌿")
            
            elif context == 'specific_crop':
                responses.append(self._get_crop_advice(subtype))
            
            elif context == 'seasonal_tips' and subtype:
                tips = self.knowledge_base['seasonal_tips'][subtype]
                responses.append(f"🗓️ {subtype.title()} Gardening Tips:\n" + "\n".join(f"• {tip}" for tip in tips))
            
            elif context in self.knowledge_base:
                # Get tips from each subcategory
                category = self.knowledge_base[context]
                for subcategory, tips in category.items():
                    responses.append(f"\n{subcategory.title()} Tips:\n" + "\n".join(f"• {tip}" for tip in random.sample(tips, min(2, len(tips)))))
            
            elif context == 'general':
                responses.append(
                    "I can help you with:\n"
                    "🌱 Urban farming techniques\n"
                    "💧 Water management\n"
                    "🌍 Soil health\n"
                    "🐞 Natural pest control\n"
                    "🗓️ Seasonal gardening tips\n"
                    "\nWhat would you like to learn about?"
                )
        
        return "\n\n".join(responses)
    
    def get_response(self, message: str) -> str:
        """Generate a response to the user's message."""
        try:
            # Get message context
            contexts = self._get_context(message)
            
            # Update conversation context
            self.context.update(dict(contexts))
            
            # Get relevant information
            response = self._get_relevant_info(contexts)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error. Please try asking your question differently. 🙏"

    def initialize(self):
        """Initialize the DeepSeek model and tokenizer."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            self.is_initialized = True
            return True
        except Exception as e:
            raise Exception(f"Error initializing DeepSeek model: {str(e)}")
    
    def generate_response(self, user_input, max_length=200):
        """Generate a response using DeepSeek's model."""
        if not self.is_initialized:
            raise Exception("Model needs to be initialized first!")
            
        try:
            # Prepare the prompt for sustainability-focused responses
            prompt = f"""You are an expert in sustainable urban farming. 
            Provide concise, actionable advice on: {user_input}
            
            Answer:"""
            
            # Tokenize and generate
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract the generated text
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response.split("Answer:")[-1].strip()  # Isolate the model's response
            
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
    
    # (Keep the rest of the methods unchanged from your original code)
    def get_sustainability_tips(self, context=None):
        """Get general sustainability tips."""
        if not self.is_initialized:
            raise Exception("Model needs to be initialized first!")
        try:
            prompt = "List 3 practical tips for sustainable urban farming."
            if context:
                prompt = f"Context: {context}\n\n{prompt}"
            return self.generate_response(prompt)
        except Exception as e:
            raise Exception(f"Error getting tips: {str(e)}")
    
    def get_resource_optimization_advice(self, resource_type):
        """Get advice for water/fertilizer optimization."""
        if not self.is_initialized:
            raise Exception("Model needs to be initialized first!")
        try:
            prompt = f"How can urban farmers optimize {resource_type} usage? Give bullet points."
            return self.generate_response(prompt)
        except Exception as e:
            raise Exception(f"Error getting advice: {str(e)}")