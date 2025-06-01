"""
Icon and Emoji Helper Module for Manim

This module provides helper functions to create icons and use emojis in Manim animations
without relying on external SVG files or assets.
"""

import emoji
from manim import *
from typing import Dict, List, Tuple, Optional

def emojized_text(text: str, font_size: int = 24, color: str = WHITE) -> Text:
    """
    Create a Text object with emojis.
    
    Args:
        text: Text string with emoji shortcodes (e.g., ":thumbs_up:")
        font_size: Font size
        color: Text color
        
    Returns:
        Text: Manim Text object with emojis
    """
    emojized = emoji.emojize(text, language='alias')
    return Text(emojized, font_size=font_size, color=color)

def create_ledger_icon(width: float = 2.0, color: str = BLUE_E) -> VGroup:
    """
    Create a ledger/book icon using Manim primitives.
    
    Args:
        width: Width of the icon
        color: Color of the icon
        
    Returns:
        VGroup: Manim VGroup containing the ledger icon
    """
    height = width * 1.3
    
    # Create book/ledger shape
    book = Rectangle(width=width, height=height, fill_opacity=0.8, 
                    fill_color=color, stroke_color=WHITE)
    
    # Create page lines
    page_count = 5
    page_lines = VGroup()
    
    for i in range(1, page_count):
        y_pos = height/2 - (i * height/page_count)
        line = Line(
            start=np.array([-width/2 + 0.1, y_pos, 0]),
            end=np.array([width/2 - 0.1, y_pos, 0]),
            stroke_color=WHITE,
            stroke_width=2
        )
        page_lines.add(line)
    
    # Create binding
    binding = Rectangle(
        width=width/8,
        height=height,
        fill_opacity=1,
        fill_color=darker_color(color),
        stroke_color=WHITE
    ).move_to(book.get_left() + np.array([width/16, 0, 0]))
    
    return VGroup(book, binding, page_lines)

def create_blockchain_icon(width: float = 3.0, num_blocks: int = 4, 
                          block_color: str = BLUE) -> VGroup:
    """
    Create a blockchain icon using Manim primitives.
    
    Args:
        width: Width of the entire chain
        num_blocks: Number of blocks in the chain
        block_color: Color of the blocks
        
    Returns:
        VGroup: Manim VGroup containing the blockchain icon
    """
    block_width = width / (num_blocks * 1.5)
    
    blocks = VGroup()
    links = VGroup()
    
    for i in range(num_blocks):
        # Create block with hash pattern
        block = Square(side_length=block_width, fill_opacity=0.8, 
                      fill_color=block_color, stroke_color=WHITE)
        
        # Add hash pattern inside block
        hash_lines = VGroup()
        for j in range(3):
            line = Line(
                start=np.array([-block_width/3, block_width/4 - j * block_width/3, 0]),
                end=np.array([block_width/3, block_width/4 - j * block_width/3, 0]),
                stroke_width=2,
                stroke_color=WHITE
            )
            hash_lines.add(line)
        
        block_group = VGroup(block, hash_lines)
        block_group.move_to(np.array([i * width / num_blocks, 0, 0]))
        blocks.add(block_group)
        
        # Add chain links between blocks
        if i > 0:
            prev_block_pos = blocks[i-1].get_center()
            curr_block_pos = block_group.get_center()
            
            link = VGroup()
            link1 = Line(
                start=np.array([prev_block_pos[0] + block_width/2, prev_block_pos[1], 0]),
                end=np.array([curr_block_pos[0] - block_width/2, curr_block_pos[1], 0]),
                stroke_width=3,
                stroke_color=YELLOW
            )
            
            link.add(link1)
            links.add(link)
    
    blockchain = VGroup(blocks, links)
    # Center the blockchain
    blockchain.move_to(ORIGIN)
    
    return blockchain

def create_computer_icon(width: float = 2.0, color: str = BLUE_D) -> VGroup:
    """
    Create a computer/laptop icon using Manim primitives.
    
    Args:
        width: Width of the icon
        color: Color of the computer
        
    Returns:
        VGroup: Manim VGroup containing the computer icon
    """
    # Create monitor
    height = width * 0.75
    
    monitor = Rectangle(width=width, height=height, fill_opacity=0.8,
                      fill_color=color, stroke_color=WHITE)
    
    # Create screen
    screen_width = width * 0.85
    screen_height = height * 0.75
    screen = Rectangle(width=screen_width, height=screen_height, fill_opacity=1,
                     fill_color=BLUE_A, stroke_color=WHITE)
    screen.move_to(monitor.get_center() + np.array([0, height*0.05, 0]))
    
    # Create keyboard/base
    base_width = width * 1.2
    base_height = height * 0.2
    base = Rectangle(width=base_width, height=base_height, fill_opacity=0.8,
                   fill_color=darker_color(color), stroke_color=WHITE)
    base.move_to(monitor.get_bottom() + np.array([0, -base_height/2, 0]))
    
    # Create stand
    stand = Triangle(fill_opacity=0.8, fill_color=darker_color(color),
                   stroke_color=WHITE).scale(width/4)
    stand.rotate(PI)  # Rotate to point downward
    stand.move_to(monitor.get_bottom() + np.array([0, -height*0.1, 0]))
    
    return VGroup(base, stand, monitor, screen)

def create_quantum_icon(width: float = 2.0, color: str = BLUE) -> VGroup:
    """
    Create a quantum computing icon (atom-like) using Manim primitives.
    
    Args:
        width: Width of the icon
        color: Color of the icon
        
    Returns:
        VGroup: Manim VGroup containing the quantum icon
    """
    # Create nucleus
    nucleus = Circle(radius=width/6, fill_opacity=0.8, 
                    fill_color=RED, stroke_color=WHITE)
    
    # Create electron orbits
    orbits = VGroup()
    
    # Create three elliptical orbits in different orientations
    for i in range(3):
        angle = i * PI / 3
        orbit = Ellipse(width=width, height=width*0.6, fill_opacity=0,
                       stroke_color=BLUE, stroke_width=2)
        orbit.rotate(angle)
        orbits.add(orbit)
    
    # Create electrons
    electrons = VGroup()
    
    for i, orbit in enumerate(orbits):
        electron = Circle(radius=width/15, fill_opacity=1, 
                         fill_color=BLUE, stroke_color=WHITE)
        # Position electron somewhere on the orbit
        angle = i * 2 * PI / 3
        electron.move_to(orbit.point_from_proportion(angle / (2 * PI)))
        electrons.add(electron)
    
    return VGroup(orbits, nucleus, electrons)

def create_globe_icon(radius: float = 1.0, color: str = BLUE) -> VGroup:
    """
    Create a globe/earth icon using Manim primitives.
    
    Args:
        radius: Radius of the globe
        color: Color of the globe
        
    Returns:
        VGroup: Manim VGroup containing the globe icon
    """
    # Create main sphere
    sphere = Circle(radius=radius, fill_opacity=0.5, 
                   fill_color=color, stroke_color=WHITE)
    
    # Create latitude lines
    latitudes = VGroup()
    
    for i in range(1, 3):
        height = radius * 0.6 * i / 3
        latitude = Ellipse(width=radius*2, height=height*2, fill_opacity=0,
                         stroke_color=WHITE, stroke_width=1)
        latitudes.add(latitude)
    
    # Create longitude lines
    longitudes = VGroup()
    
    for i in range(4):
        angle = i * PI / 4
        longitude = Arc(radius=radius, angle=PI, start_angle=PI/2,
                      stroke_color=WHITE, stroke_width=1)
        longitude.rotate(angle)
        longitudes.add(longitude)
    
    return VGroup(sphere, latitudes, longitudes)

def create_gear_icon(radius: float = 1.0, teeth: int = 8, color: str = GRAY) -> VGroup:
    """
    Create a gear icon using Manim primitives.
    
    Args:
        radius: Radius of the gear
        teeth: Number of teeth on the gear
        color: Color of the gear
        
    Returns:
        VGroup: Manim VGroup containing the gear icon
    """
    # Create center circle
    center = Circle(radius=radius*0.7, fill_opacity=0.8, 
                   fill_color=color, stroke_color=WHITE)
    
    # Create teeth
    teeth_group = VGroup()
    
    for i in range(teeth):
        angle = i * 2 * PI / teeth
        
        tooth = Triangle(fill_opacity=0.8, fill_color=color,
                        stroke_color=WHITE).scale(radius*0.3)
        
        # Position and rotate each tooth
        tooth.move_to(np.array([
            radius * np.cos(angle),
            radius * np.sin(angle),
            0
        ]))
        tooth.rotate(angle - PI/2)  # Point outward
        
        teeth_group.add(tooth)
    
    # Create center hole
    hole = Circle(radius=radius*0.2, fill_opacity=1, 
                 fill_color=BLACK, stroke_color=WHITE)
    
    return VGroup(center, teeth_group, hole) 