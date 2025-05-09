import matplotlib.pyplot as plt
import states.statesAllRequests as statesAllRequests

def PlotPointParameters():
    if(len(statesAllRequests.PlotTable)>0):
        Values=[x["Value"] for x in statesAllRequests.PlotTable]
        Abs_max = max([abs(x) for x in Values])
        Range = Abs_max if (Abs_max != 0) else 0.00001
        ###access existing fig
        ax=statesAllRequests.ax
        TextScale=float(1)*float (statesAllRequests.RequestTextScale)
        MaxCircleRadius=10
        for PointData in statesAllRequests.PlotTable:
            value = PointData["Value"]
            value = round(value,int (statesAllRequests.RequestDecimalPlaces))
            pt2d = PointData["Pt2d"]
            Text = PointData["Text"]
            CircleRadius = (abs(value)/Range)*MaxCircleRadius*float (statesAllRequests.RequestCircleScale)
            #Plot Circles
            if(value>=0):
                ax.plot(pt2d[0], pt2d[1],
                               marker='o',
                               markersize=CircleRadius,  # Adjust marker size as needed
                               markerfacecolor=(0, 1, 1, 0.5),  # Fill color based on value
                               markeredgecolor=(0, 1, 1, 0.5),  # Border color
                               markeredgewidth=1)  # Border thickness
            if(value<0):
                ax.plot(pt2d[0], pt2d[1],
                               marker='o',
                               markersize=CircleRadius,  # Adjust marker size as needed
                               markerfacecolor=(1, 0, 0, 0.5),  # Fill color based on value
                               markeredgecolor=(1, 0, 0, 0.5),  # Border color
                               markeredgewidth=1)  # Border thickness
            #Plot text
            ax.text(pt2d[0], pt2d[1], Text,
                    fontsize=TextScale,  # Adjust font size as needed
                    color='black',
                    horizontalalignment='center',
                    verticalalignment='center')
        fig = ax.get_figure()
        plt.close(fig)
        statesAllRequests.figs.append(fig)