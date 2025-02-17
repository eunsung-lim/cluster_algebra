import matplotlib.pyplot as plt
import numpy as np
from .quiver import Quiver

lamination_palette = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
    '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
    '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#9edae5',
    '#393b79', '#637939', '#8c6d31', '#843c39', '#7b4173',
    '#5254a3', '#8ca252', '#bd9e39', '#ad494a', '#a55194',
    '#6b6ecf', '#b5cf6b', '#e7ba52', '#d6616b', '#ce6dbd',
    '#9c9ede', '#cedb9c', '#e7cb94', '#e7969c', '#de9ed6',
    '#3182bd', '#31a354', '#756bb1', '#636363', '#e6550d',
    '#80b1d3', '#8dd3c7', '#ffffb3', '#bebada', '#fb8072',
    '#6baed6', '#74c476', '#9e9ac8', '#969696', '#fd8d3c',
    '#b3cde3', '#ccebc5', '#decbe4', '#fed9a6', '#ffffcc',
    '#e5d8bd', '#fddaec', '#f2f2f2', '#b3e2cd', '#fdcdac',
    '#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99',
    '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a',
    '#b15928', '#8dd3c7', '#ffffb3', '#bebada', '#fb8072',
    '#80b1d3', '#fdb462', '#b3de69', '#fccde5', '#d9d9d9',
    '#bc80bd', '#ccebc5', '#ffed6f', '#66c2a5', '#fc8d62',
    '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f', '#e5c494',
    '#b3b3b3', '#e41a1c', '#377eb8', '#4daf4a', '#984ea3'
]

class Plotter:
    def __init__(self):
        pass
    
    def plot_quiver(self, 
                   quiver: Quiver,
                   ax: plt.Axes = None,
                   vertex_labels: bool = True,
                   frozen_labels: bool = True,
                   cluster_labels: bool = True,
                   plot_laminations: bool = True,
                   laminations_labels: bool = True,
                   rotation: float = 0, 
                   fontsize: int = 7,
                   lamination_label_pos: float = 0.5,
                   ):
        n = quiver.n
        # Calculate polygon vertices positions
        angles = np.linspace(0, 2*np.pi, n, endpoint=False)
        radius = 10
        x = radius * np.cos(angles + rotation)
        y = radius * np.sin(angles + rotation)
        
        # Create figure if not provided
        if ax is None:
            _, ax = plt.subplots()
            ax.set_xticks([])
            ax.set_yticks([])
            ax.axis('off')
        
        
        ############################ POLYGON ############################
        # Plot polygon
        polygon = plt.Polygon(np.column_stack([x, y]), fill=False, linewidth=0.2)
        ax.add_patch(polygon)
        
        #  VERTEX LABELS
        if vertex_labels:
            for i in range(n):
                # Add white circle background for label
                center_x = x[i]
                center_y = y[i]
                circle = plt.Circle((center_x, center_y), 0.1, color='white')
                ax.add_patch(circle)
                
                # Add text label
                ax.text(center_x, center_y, f'v_{i}', 
                        horizontalalignment='center',
                        verticalalignment='center', fontsize=fontsize)
        
        ############################ FROZEN EDGES ############################
        for i in range(len(quiver.frozens)):
            p, q = quiver.frozens[i]
            
            center_x = (x[p] + x[(p+1)%n])/2
            center_y = (y[p] + y[(p+1)%n])/2
            
            ax.plot([x[p], x[q]], [y[p], y[q]], color='black')
            
            if frozen_labels:
                # Add white circle background for label
                circle = plt.Circle((center_x, center_y), 0.1, color='white')
                ax.add_patch(circle)
                
                # Add text label
                ax.text(center_x, center_y, f'e_{i}',
                        horizontalalignment='center',
                        verticalalignment='center', fontsize=fontsize)
        
        ############################ CLUSTERS ############################
        for i in range(len(quiver.clusters)):
            p, q = quiver.clusters[i]
            
            ax.plot([x[p], x[q]], [y[p], y[q]], color='black')
            
            if cluster_labels:
                center_x = (x[p]+x[q])/2
                center_y = (y[p]+y[q])/2
                circle = plt.Circle((center_x, center_y), 0.1, color='white')
                ax.add_patch(circle)
                
                # Add text label
                ax.text(center_x, center_y, 'x_' + quiver.cluster_names[i], 
                        horizontalalignment='center',
                        verticalalignment='center', fontsize=fontsize)
        
        ############################ LAMINATIONS ############################
        if plot_laminations:
            for i, lamination in enumerate(quiver.laminations):
                for edge in lamination:
                    p, q = edge
                    
                    x1 = (x[p]+x[(p+1)%n])/2
                    y1 = (y[p]+y[(p+1)%n])/2
                    x2 = (x[q]+x[(q+1)%n])/2
                    y2 = (y[q]+y[(q+1)%n])/2
                    
                    ax.plot([x1, x2], [y1, y2], color=lamination_palette[i])
            
                if laminations_labels:
                    center_x = x1 + lamination_label_pos * (x2-x1)
                    center_y = y1 + lamination_label_pos * (y2-y1)
                    circle = plt.Circle((center_x, center_y), 0.1, color='white')
                    ax.add_patch(circle)
                    
                    # Add text label
                    ax.text(center_x, center_y, 'u_' + quiver.lamination_names[i], 
                            horizontalalignment='center',
                            verticalalignment='center', fontsize=fontsize)
        
        return ax