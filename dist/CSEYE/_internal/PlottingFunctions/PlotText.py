import matplotlib.pyplot as plt
import states.statesAllRequests as statesAllRequests

def PlotText():
    if (len(statesAllRequests.PlotTable) > 0):
        ax=statesAllRequests.ax
        TextScale = float(1)*float (statesAllRequests.RequestTextScale)
        for pointdata in statesAllRequests.PlotTable:
            Pt=pointdata['Pt2d']
            Text=pointdata['Text']
            ax.text(Pt[0], Pt[1], Text,
                    fontsize=TextScale,  # Adjust font size as needed
                    color='black',
                    horizontalalignment='center',
                    verticalalignment='center')
        fig = ax.get_figure()
        plt.close(fig)
        statesAllRequests.figs.append(fig)
        statesAllRequests.figsNames.append(statesAllRequests.RequestNameFormat1)