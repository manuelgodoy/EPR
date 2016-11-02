import plotly
import plotly.plotly as py
import plotly.tools as tls
import plotly.graph_objs as go

plotly.tools.set_credentials_file(username='microsilicon', api_key='ekrc27ruwb')
plotly.tools.set_config_file(world_readable=False,
                             sharing='private')
stream_ids = tls.get_credentials_file()['stream_ids']
token_1 = stream_ids[-1]   # I'm getting my stream tokens from the end to ensure I'm not reusing tokens
token_2 = stream_ids[-2]
token_3 = stream_ids[-3]
stream_id1 = dict(token=token_1, maxpoints=100)
stream_id2 = dict(token=token_2, maxpoints=100)
stream_id3 = dict(token=token_3, maxpoints=100)

# stream_1 = dict(token=stream_id, maxpoints=60)
############################ END OF SETTINGS

trace1 = go.Scatter(
    x=[],
    y=[],
    mode='lines+markers',
    stream=stream_id1
)
trace2 = go.Scatter(
    x=[],
    y=[],
    mode='lines+markers',
    stream=stream_id2,

)
trace3 = go.Scatter(
    x=[],
    y=[],
    mode='lines+markers',
    stream=stream_id3,

)
data = [trace1, trace2, trace3]
# layout = go.Layout(
#     xaxis2=dict(
#         domain=[0.5, 0.95],
#         anchor='y2'
#     ),
#     yaxis2=dict(
#         domain=[0, 1],
#         anchor='x2'
#     )
# )
# fig = go.Figure(data=data, layout=layout)
fig = tls.make_subplots(rows=3, cols=1,subplot_titles=('X', 'Y', 'R'))

fig.append_trace(trace1, 1, 1)
fig.append_trace(trace2, 2, 1)
fig.append_trace(trace3, 3, 1)
fig['layout'].update(showlegend=False, title='EPR')
py.iplot(fig, filename='EPR Plots')

s_1 = py.Stream(stream_id=token_1)
s_2 = py.Stream(stream_id=token_2)
s_3 = py.Stream(stream_id=token_3)

# def stream(s1, s2)
#     s_1.open()
#     s_2.open()
# We then open a connection

# s_1.open()
# s_2.open()
#
# import time
# import datetime
# import numpy as np
# k=5
# i=0
# while True:
#     # nums = np.random.random_integers(0,10, size=(3))
#     x = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
#     y = (np.cos(k*i/50.)*np.cos(i/50.)+np.random.randn(1))[0]
#     y2 = (np.cos(k*i/50.)*np.cos(i/50.)+np.random.randn(1))[0]
#
#     # Send data to your plot
#     s_1.write(dict(x=x, y=y))
#     s_2.write(dict(x=x, y=y2))
#     # s_1.write(dict(labels=['one', 'two', 'three'], values=nums, type='pie'))
#     # s_2.write(dict(x=['one', 'two', 'three'], y=nums, type='bar', marker=dict(color=["blue", "orange", "green"])))
#     time.sleep(0.8)
# s_1.close()
# s_2.close()
