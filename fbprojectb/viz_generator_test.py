#!/usr/bin/env python
"""Tests for viz_generator file."""

import viz_generator

def test_generate_viz_json_with_Charlie_Shae():
    """Test generate_viz_json using Charlie Shae data."""
    viz = viz_generator.VisualizationGenerator('106656393279395')
    viz.generate_viz_json('Charlie Shae')
    print viz.get_pairs()

test_generate_viz_json_with_Charlie_Shae()
