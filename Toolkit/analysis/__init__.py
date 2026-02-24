"""
Analysis Package for Space Funky B.O.B. Toolkit

Source-verified analysis modules for ROM data.
"""

from .boss_analyzer import analyze_bosses, get_boss_strategies
from .password_generator import generate_password, validate_password
from .task_analyzer import analyze_task_system, get_task_functions
from .music_analyzer import analyze_music, get_theme_for_level
from .spawn_analyzer import analyze_spawn_patterns, get_enemies_by_category
from .death_analyzer import analyze_death_types, get_death_sound

__all__ = [
    'analyze_bosses',
    'get_boss_strategies',
    'generate_password',
    'validate_password',
    'analyze_task_system',
    'get_task_functions',
    'analyze_music',
    'get_theme_for_level',
    'analyze_spawn_patterns',
    'get_enemies_by_category',
    'analyze_death_types',
    'get_death_sound'
]
