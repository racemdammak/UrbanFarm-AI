import customtkinter as ctk
from typing import Callable, List, Dict
import datetime

class ChatMessage:
    def __init__(self, text: str, is_user: bool, timestamp: datetime.datetime = None):
        self.text = text
        self.is_user = is_user
        self.timestamp = timestamp or datetime.datetime.now()

class ModernChatFrame(ctk.CTkFrame):
    def __init__(self, master, on_send: Callable[[str], None], **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create chat display area
        self.chat_display = ctk.CTkTextbox(
            self,
            wrap="word",
            font=("Helvetica", 12),
            height=400
        )
        self.chat_display.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="nsew")
        self.chat_display.configure(state="disabled")
        
        # Create input area
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        # Create message input
        self.message_input = ctk.CTkTextbox(
            self.input_frame,
            height=40,
            wrap="word",
            font=("Helvetica", 12)
        )
        self.message_input.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Create send button
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="Send",
            width=100,
            command=self._on_send,
            fg_color="#2CC985",
            hover_color="#0CAB6B"
        )
        self.send_button.grid(row=0, column=1, padx=(5, 0))
        
        # Bind Enter key to send message
        self.message_input.bind("<Return>", lambda e: self._on_send())
        self.message_input.bind("<Shift-Return>", lambda e: "break")  # Allow Shift+Enter for new line
        
        # Store callback
        self.on_send = on_send
        
        # Store messages
        self.messages: List[ChatMessage] = []
        
        # Add welcome message
        self.add_bot_message(
            "Hello! I'm your Sustainability Assistant. I can help you with:\n"
            "• Urban farming best practices\n"
            "• Resource conservation tips\n"
            "• Sustainable gardening methods\n"
            "• Eco-friendly pest control\n"
            "What would you like to know about?"
        )
    
    def _on_send(self):
        """Handle send button click."""
        message = self.message_input.get("1.0", "end-1c").strip()
        if message:
            # Clear input
            self.message_input.delete("1.0", "end")
            
            # Add user message to chat
            self.add_user_message(message)
            
            # Call callback
            if self.on_send:
                self.on_send(message)
        
        return "break"  # Prevent default Enter behavior
    
    def add_user_message(self, text: str):
        """Add a user message to the chat."""
        message = ChatMessage(text, is_user=True)
        self.messages.append(message)
        self._display_message(message)
    
    def add_bot_message(self, text: str):
        """Add a bot message to the chat."""
        message = ChatMessage(text, is_user=False)
        self.messages.append(message)
        self._display_message(message)
    
    def _display_message(self, message: ChatMessage):
        """Display a message in the chat."""
        self.chat_display.configure(state="normal")
        
        # Add timestamp
        time_str = message.timestamp.strftime("%H:%M")
        self.chat_display.insert("end", f"{time_str} ", "timestamp")
        
        # Add sender
        sender = "You" if message.is_user else "Assistant"
        self.chat_display.insert("end", f"{sender}: ", "sender")
        
        # Add message
        self.chat_display.insert("end", f"{message.text}\n\n", "message")
        
        # Configure tags
        self.chat_display.tag_config(
            "timestamp",
            foreground="gray",
            font=("Helvetica", 10)
        )
        self.chat_display.tag_config(
            "sender",
            foreground="#2CC985" if message.is_user else "#0CAB6B",
            font=("Helvetica", 12, "bold")
        )
        self.chat_display.tag_config(
            "message",
            font=("Helvetica", 12)
        )
        
        # Scroll to bottom
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled") 