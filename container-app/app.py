from viktor.core import ViktorController
from viktor.geometry import SquareBeam, Group, Material
from viktor.parametrization import ViktorParametrization, Text, IntegerField, OptionField, DynamicArray, ActionButton
from viktor.views import SVGView, SVGResult, GeometryResult, GeometryView
from viktor import Color
from io import StringIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from matplotlib.patches import Rectangle
import json
from solver import solver
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime



class Parametrization(ViktorParametrization):
    title = Text('# Container Loading Optimization')

    bin_type = OptionField('What type of container to fill?', options=["20'", "40'"], default="20'", flex=90)

    # dynamic array with box inputs
    array = DynamicArray('Enter box dimensions',
                         default=[{'length': 120, 'width': 80, 'height': 100, 'quantity': 1}])
    array.length = IntegerField('Length (cm)', default=120, flex=25, min=1, max=235)
    array.width = IntegerField('Width (cm)', default=80, flex=25, min=1, max=235)
    array.height = IntegerField('Height (cm)', default=100, flex=25, min=1, max=260)
    array.quantity = IntegerField('Quantity', default=1, flex=25, min=1, step=1)

    # Finalize_Button = ActionButton('Finalize Container 🚀', method='save_image')






class Controller(ViktorController):
    label = 'My Container'
    parametrization = Parametrization(width=35)

    @GeometryView("3D container", duration_guess=5)
    def visualize_container(self, params, **kwargs):
        # Generate container
        length_x = 2.35
        length_z = 2.6
        if params.bin_type == "20'":
            length_y = 5.90
            bin_type = [(235, 590, 260)]
        else:
            length_y = 12.03
            bin_type = [(235, 1203, 260)]
        container = SquareBeam(length_x, length_y, length_z)
        container.material = Material('iron', threejs_opacity=0.5)
        container.translate([(length_x / 2), (length_y / 2), (length_z / 2)])

        # Prepare box data
        boxes = [{'length': box.length, 'width': box.width, 'height': box.height, 'quantity': box.quantity} for box in params.array]

        result, _ = solver(boxes, bin_type)

        if isinstance(result, str):
            # If solver returned an error message, create an error visualization
            error_text = SquareBeam(0.1, 0.1, 0.1)
            error_text.material = Material('plastic', color=Color(255, 0, 0))
            error_text.translate([length_x/2, length_y/2, length_z/2])
            return GeometryResult(Group([container, error_text]), message=result)

        box_geometries = []
        max_boxes = 1000  # Limit the number of boxes to render
        for i, box in enumerate(result):
            if i >= max_boxes:
                break
            length_x = box['length'] / 100
            length_y = box['width'] / 100
            length_z = box['height'] / 100

            # Create box
            box_geometry = SquareBeam(length_x=length_x - 0.01, length_y=length_y - 0.01, length_z=length_z - 0.01)  # add 0.01 loose space between boxes

            # Move box to right location (defining the center of the box)
            box_geometry.translate([(box['x'] / 100 + 0.5 * length_x), (box['y'] / 100 + 0.5 * length_y), (box['z'] / 100 + 0.5 * length_z)])

            # Set Material
            color = Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            box_geometry.material = Material('plastic', color=color)

            # Add to box list
            box_geometries.append(box_geometry)

        boxes_group = Group(box_geometries)

        container_system = Group([container, boxes_group])

        return GeometryResult(container_system)
