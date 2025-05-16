import states.statesAllRequests as statesAllRequests
def PlotColumnsAndBraces():
    if statesAllRequests.RequestViewType == "Story":
        for ColumnEnd in statesAllRequests.PlanColumns:
            Pt2d = ColumnEnd["Pt2d"]
            statesAllRequests.ax.plot(Pt2d[0], Pt2d[1],
                    marker='o',
                    markersize=6,
                    markerfacecolor='gray',
                    markeredgecolor="black",
                    markeredgewidth=0.5)
        for BraceEnd in statesAllRequests.PlanBraces:
            Pt2d = BraceEnd["Pt2d"]
            statesAllRequests.ax.plot(Pt2d[0], Pt2d[1],
                    marker='x',
                    markersize=6,  # Adjust size as needed
                    markerfacecolor='red',
                    markeredgecolor="black",  # Fill color of the circle
                    markeredgewidth=0.5)