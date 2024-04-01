import matplotlib.pyplot as plt
import networkx as nx
from MDPparser.mdp_syntax import gramSyntax
import matplotlib
matplotlib.use("TkAgg")


rad = .2


def offset(d, pos, dist=rad/2, loop_shift=.2, asp=1):
    for (u, v), obj in d.items():
        if u != v:
            par = dist*(pos[v] - pos[u])
            dx, dy = par[1]*asp, -par[0]/asp
            x, y = obj.get_position()
            obj.set_position((x+dx, y+dy))
        else:
            x, y = obj.get_position()
            obj.set_position((x, y+loop_shift))


def sub(a, b):
    return a-b


def get_aspect(ax):
    # Total figure size
    figW, figH = ax.get_figure().get_size_inches()
    # Axis size on figure
    _, _, w, h = ax.get_position().bounds
    # Ratio of display units
    disp_ratio = (figH * h) / (figW * w)
    # Ratio of data units
    # Negative over negative because of the order of subtraction
    data_ratio = sub(*ax.get_ylim()) / sub(*ax.get_xlim())

    return disp_ratio / data_ratio


def graphDrawer(state: gramSyntax):

    G = nx.MultiDiGraph(directed=True)

    state_summit = list(state.states.keys())
    labels = {x: x for x in state.states}
    actions_summit = []
    for key, list_action in state.states_action.items():
        for action in list_action:
            summit = key + action
            actions_summit.append(summit)
            labels[summit] = ''

    G.add_nodes_from(state_summit + actions_summit)

    label_edges = {}

    for key, item in state.trans_noact.items():
        for dst, w in item:
            dep = key
            G.add_edge(dep, dst)
            label_edges[(dep, dst)] = str(round(w, 2))

    for key, item in state.trans_act.items():
        dep, act = key
        act_summit = dep + act
        G.add_edge(dep, act_summit)
        label_edges[(dep, act_summit)] = act
        for dst, w in item:
            G.add_edge(act_summit, dst)
            label_edges[(act_summit, dst)] = str(round(w, 2))

    pos = nx.kamada_kawai_layout(G)
    nx.draw_networkx_nodes(G, pos,
                           nodelist=state_summit,
                           node_shape='o',
                           node_color='skyblue',
                           node_size=300)
    nx.draw_networkx_nodes(G, pos,
                           nodelist=actions_summit,
                           node_color='black',
                           node_shape='o',
                           node_size=50)

    nx.draw_networkx_labels(G, pos,
                            labels=labels,
                            font_size=10,
                            font_color='black',
                            font_weight='bold')

    nx.draw_networkx_edges(G, pos,
                           arrows=True,
                           arrowstyle='->',
                           connectionstyle='arc3,rad=0.2')

    d = nx.draw_networkx_edge_labels(G, pos,
                                     edge_labels=label_edges,
                                     bbox={'boxstyle': 'round', 'ec': (1.0, 1.0, 1.0), 'fc': (1.0, 1.0, 1.0), 'alpha': .5})

    current_summit = state.c_state
    nx.draw_networkx_nodes(G, pos,
                           nodelist=[current_summit],
                           node_shape='o',
                           node_color='red',
                           node_size=300)

    offset(d, pos, asp=get_aspect(plt.gca()))

    plt.savefig('test.png')
