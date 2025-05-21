import copy

import matplotlib.pyplot as plt
import numpy as np
import states.statesAllRequests as statesAllRequests

def translate_point(point, vector, magnitude):
    # Normalize the vector: divide by its norm.
    norm_vector = vector / np.linalg.norm(vector)
    # Multiply the unit vector by the magnitude and add to the point.
    point+=norm_vector * magnitude
    return point

def PlotVectorsAndPoints():
    if (len(statesAllRequests.PlotTable) > 0):
        Values = [x["Resultant"] for x in statesAllRequests.PlotTable]
        Abs_max = max([abs(x) for x in Values])
        Range = Abs_max if (Abs_max != 0) else 0.00001
        ###access existing fig
        ax = statesAllRequests.ax
        MaxCircleRadius = 10
        TextScale = float(1) * float(statesAllRequests.RequestTextScale) 
        VectorScale = 10*statesAllRequests.RequestCircleScale
        for Pointdata in statesAllRequests.PlotTable:
            Pt=Pointdata["Pt"]
            F1=copy.deepcopy(Pointdata["F1"])
            F2=copy.deepcopy(Pointdata["F2"])
            Resultant=copy.deepcopy(Pointdata["Resultant"])
            Text=copy.deepcopy(Pointdata["Text"])
            Color=Pointdata["Color"]
            F1=float(F1)
            F2=float(F2)
            TextPt=copy.deepcopy(Pt)
            vector = np.array([F1, F2], dtype=float)
            TextPt = translate_point(TextPt, vector, VectorScale*1.2)
            CircleRadius = (abs(Resultant) / Range) * MaxCircleRadius * float(statesAllRequests.RequestCircleScale)
            ax.plot(Pt[0], Pt[1],
                    marker='o',
                    markersize=CircleRadius,  # Adjust marker size as needed
                    markerfacecolor=(0.0, 1.0, 1.0, 0.2),  # Fill color based on value
                    markeredgecolor='none',  # Border color
                    markeredgewidth=1)  # Border thickness
            ax.arrow(Pt[0], Pt[1], F1*VectorScale, F2*VectorScale,
                     head_width=35,  # adjust arrowhead width
                     head_length=50,  # adjust arrowhead length
                     length_includes_head=True,
                     fc=Color,  # face Color of the arrow
                     ec=Color)
            ax.text(TextPt[0], TextPt[1], Text,
                    fontsize=TextScale,  # Adjust font size as needed
                    color='black',
                    horizontalalignment='center',
                    verticalalignment='center')
        fig = ax.get_figure()
        plt.close(fig)
        statesAllRequests.figs.append(fig)
        statesAllRequests.figsNames.append(statesAllRequests.RequestNameFormat1)