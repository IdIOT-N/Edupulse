"""
Field Selection Module - Updated with Custom Input
Allows users to type their own interest or choose from suggestions
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle, Line
from cache_manager import CacheManager  # Add this import
import json
import os
from datetime import datetime


class FieldSelectionScreen(Screen):
    """Screen for selecting or typing educational field"""
    
    def __init__(self, **kwargs):  # Changed from _init_ to __init__
        super().__init__(**kwargs)
        
        # Main layout with gradient background
        main_layout = BoxLayout(orientation='vertical', padding=40, spacing=25)
        
        # Background gradient effect
        with main_layout.canvas.before:
            Color(0.05, 0.05, 0.1, 1)
            self.bg_rect = RoundedRectangle(pos=main_layout.pos, size=main_layout.size)
        
        main_layout.bind(
            pos=lambda instance, value: setattr(self.bg_rect, 'pos', instance.pos),
            size=lambda instance, value: setattr(self.bg_rect, 'size', instance.size)
        )
        
        # Title with emoji
        title = Label(
            text='[b]🎓 What Do You Want to Learn?[/b]',
            markup=True,
            font_size='36sp',
            color=(0.2, 0.8, 1, 1),
            size_hint_y=0.15
        )
        
        # Subtitle
        subtitle = Label(
            text='Type your interest or choose from popular topics',
            font_size='16sp',
            color=(1, 1, 1, 0.6),
            size_hint_y=0.08
        )
        
        # Custom input section
        input_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.2)
        
        input_label = Label(
            text='Enter Your Field of Interest:',
            font_size='18sp',
            color=(1, 1, 1, 0.8),
            size_hint_y=0.3,
            halign='left'
        )
        input_label.bind(size=input_label.setter('text_size'))
        
        # Text input field
        self.field_input = TextInput(
            hint_text='e.g., Artificial Intelligence, Finance, Quantum Physics...',
            multiline=False,
            font_size='16sp',
            size_hint_y=0.7,
            background_color=(0.15, 0.15, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.2, 0.8, 1, 1),
            padding=[15, 15]
        )
        
        # Style the text input
        with self.field_input.canvas.before:
            Color(0.2, 0.8, 1, 0.3)
            self.input_border = Line(rectangle=(0, 0, 0, 0), width=2)
        
        self.field_input.bind(
            pos=self.update_input_border,
            size=self.update_input_border
        )
        
        input_container.add_widget(input_label)
        input_container.add_widget(self.field_input)
        
        # Quick suggestions
        suggestions_label = Label(
            text='[b]Popular Topics:[/b]',
            markup=True,
            font_size='16sp',
            color=(1, 1, 1, 0.7),
            size_hint_y=0.06
        )
        
        # Popular fields with icons
        self.popular_fields = [
            {'name': 'Artificial Intelligence', 'emoji': '🤖', 'keywords': 'AI machine learning deep learning'},
            {'name': 'Finance & Economics', 'emoji': '💰', 'keywords': 'finance stock market economics investing'},
            {'name': 'Science & Research', 'emoji': '🔬', 'keywords': 'science research biology physics chemistry'},
            {'name': 'Technology & Engineering', 'emoji': '⚙', 'keywords': 'technology engineering software hardware'},
            {'name': 'Health & Medicine', 'emoji': '🏥', 'keywords': 'health medicine medical healthcare'},
            {'name': 'Space & Astronomy', 'emoji': '🚀', 'keywords': 'space astronomy NASA planets'},
        ]
        
        # Create suggestion chips
        suggestions_grid = BoxLayout(orientation='vertical', spacing=12, size_hint_y=0.4)
        
        row1 = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.5)
        row2 = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.5)
        
        for i, field in enumerate(self.popular_fields):
            chip = self.create_suggestion_chip(field)
            if i < 3:
                row1.add_widget(chip)
            else:
                row2.add_widget(chip)
        
        suggestions_grid.add_widget(row1)
        suggestions_grid.add_widget(row2)
        
        # Continue button
        continue_btn = Button(
            text='Continue ➜',
            font_size='20sp',
            size_hint_y=0.11,
            background_color=(0.2, 0.8, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        continue_btn.bind(on_press=self.save_and_continue)
        
        # Add all widgets
        main_layout.add_widget(title)
        main_layout.add_widget(subtitle)
        main_layout.add_widget(input_container)
        main_layout.add_widget(suggestions_label)
        main_layout.add_widget(suggestions_grid)
        main_layout.add_widget(continue_btn)
        
        self.add_widget(main_layout)
    
    def update_input_border(self, instance, value):
        """Update text input border position"""
        self.input_border.rectangle = (
            self.field_input.x,
            self.field_input.y,
            self.field_input.width,
            self.field_input.height
        )
    
    def create_suggestion_chip(self, field):
        """Create a clickable suggestion chip"""
        chip = BoxLayout(orientation='horizontal', padding=10, spacing=8)
        
        # Chip background
        with chip.canvas.before:
            Color(0.15, 0.15, 0.25, 1)
            chip_rect = RoundedRectangle(pos=chip.pos, size=chip.size, radius=[20])
        
        chip.bind(
            pos=lambda instance, value, r=chip_rect: setattr(r, 'pos', instance.pos),
            size=lambda instance, value, r=chip_rect: setattr(r, 'size', instance.size)
        )
        
        # Emoji
        emoji = Label(
            text=field['emoji'],
            font_size='24sp',
            size_hint_x=0.2
        )
        
        # Name
        name = Label(
            text=field['name'],
            font_size='13sp',
            color=(1, 1, 1, 0.9),
            size_hint_x=0.8,
            halign='left'
        )
        name.bind(size=name.setter('text_size'))
        
        chip.add_widget(emoji)
        chip.add_widget(name)
        
        # Make clickable
        from kivy.uix.behaviors import ButtonBehavior
        
        class ClickableChip(ButtonBehavior, BoxLayout):
            pass
        
        clickable = ClickableChip()
        clickable.add_widget(chip)
        clickable.bind(on_press=lambda x: self.select_suggestion(field))
        
        return clickable
    
    def select_suggestion(self, field):
        """Fill input with selected suggestion"""
        self.field_input.text = field['name']
    
    def save_and_continue(self, instance):
        """Save custom field and navigate to news"""
        user_input = self.field_input.text.strip()
        
        if not user_input:
            self.field_input.hint_text = '⚠ Please enter a field or choose a suggestion'
            self.field_input.background_color = (0.3, 0.1, 0.1, 1)
            return
        
        # Save preference
        preferences = {
            'field': user_input,
            'field_name': user_input,
            'keywords': user_input.lower(),
            'selected_at': datetime.now().isoformat()
        }
        
        with open('user_preferences.json', 'w') as f:
            json.dump(preferences, f, indent=4)
        
        print(f"✅ Selected field: {user_input}")
        
        # Clear cache to force new content
        cache_manager = CacheManager()
        cache_manager.clear_cache()
        
        # Navigate to news screen and force refresh
        news_screen = self.manager.get_screen('news')
        self.manager.current = 'news'
        news_screen.load_news(force_refresh=True)  # Force refresh when field changesresh when field changes
