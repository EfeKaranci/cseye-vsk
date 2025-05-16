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

def PlotVectors():
    if (len(statesAllRequests.PlotTable) > 0):
        ax=statesAllRequests.ax
        TextScale = float(1)*float (statesAllRequests.RequestTextScale)
        VectorScale = 60*statesAllRequests.RequestCircleScale
        for Pointdata in statesAllRequests.PlotTable:
            Pt=Pointdata["Pt"]
            F1=copy.deepcopy(Pointdata["F1"])
            F2=copy.deepcopy(Pointdata["F2"])
            Text=copy.deepcopy(Pointdata["Text"])
            Color=Pointdata["Color"]
            F1=float(F1)
            F2=float(F2)
            TextPt=copy.deepcopy(Pt)
            vector = np.array([F1, F2], dtype=float)
            TextPt = translate_point(TextPt, vector, VectorScale)
            ax.arrow(Pt[0], Pt[1], F1*VectorScale, F2*VectorScale,
                     head_width=3*statesAllRequests.RequestCircleScale,  # adjust arrowhead width
                     head_length=3*statesAllRequests.RequestCircleScale,  # adjust arrowhead length
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