import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

import plotly.graph_objs as go

data_path = '/Users/louis/Google Drive/ricky-will-louis/data/training/laptop_will_5.csv'
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
var_names = {'power_factor': 'Power factor', 'phase_angle': 'Phase angle', 'power_real': 'Real power',
 'power_reactive': 'Reactive power', 'power_apparent': 'Apparent power', 'vrms': 'RMS voltage', 'irms': 'RMS current'}
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app_df = pd.read_csv(data_path)
app_df.columns = app_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')



app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

trace1 = go.Scatter(
    x=app_df['time'],
    y=app_df['power_factor'],
    text=[str('Power factor: ' + str(data)) for data in app_df['power_factor']],
    hoverinfo='text',
    mode='lines',
    opacity=0.7,
    line=dict(
            color = 'rgb(255,127,0)',
            width = 2,
    ),
    name='Power factor'
)
trace2 = go.Scatter(
    x=app_df['time'],
    y=app_df['phase_angle'],
    text=[str('Phase angle: ' + str(data) + ' ø') for data in app_df['phase_angle']],
    hoverinfo='text',
    mode='lines',
    opacity=0.7,
    line=dict(
            color = 'rgb(227,26,28)',
            width = 2,
    ),
    name='Phase angle',
    yaxis='y2'
)

real_p = go.Scatter(
    x=app_df['time'],
    y=app_df['power_real'],
    text=[str('Real power: ' + str(data) + ' W') for data in app_df['power_real']],
    hoverinfo='text',
    mode='lines',
    opacity=0.7,
    line=dict(
            color = 'rgb(136,65,157)',
            width = 2,
    ),
    name='Real power'
)

app_p = go.Scatter(
    x=app_df['time'],
    y=app_df['power_apparent'],
    text=[str('Apparent power: ' + str(data) + ' W') for data in app_df['power_apparent']],
    hoverinfo='text',
    mode='lines',
    opacity=0.7,
    line=dict(
            color = 'rgb(43,140,190)',
            width = 2,
    ),
    name='Apparent power'
)

reac_p = go.Scatter(
    x=app_df['time'],
    y=app_df['power_reactive'],
    text=[str('Reactive power: ' + str(data) + ' W') for data in app_df['power_reactive']],
    hoverinfo='text',
    mode='lines',
    opacity=0.7,
    line=dict(
            color = 'rgb(215,48,31)',
            width = 2,
    ),
    name='Reactive power'
)

app.layout = html.Div([
    html.H1(children='EnergyMeter'),
    html.Div('You are now viewing data for:'),
    html.Div('Appliance: ' + app_df['app_name'][1]),
    html.Div('Description: ' + app_df['app_desc'][1]),
    html.Div('Sample id: ' + str(app_df['sample_id'][1])),

    dcc.Graph(
          id='voltage',
          figure={
            'data':[
                go.Scatter(
                    x=app_df['time'],
                    y=app_df['vrms'],
                    text=[str('Voltage: ' + str(data) + ' V') for data in app_df['vrms']],
                    hoverinfo='text',
                    mode='lines',
                    line=dict(
                        color = 'rgb(31,120,180)',
                        width = 2
                ))
            ],
            'layout': go.Layout(
                title='Voltage (V)',
                xaxis={'title': 'Time (s)'},
                yaxis=dict(
                        title='RMS Voltage (V)'
                        ),

                hovermode='closest'
            )
          }),

    dcc.Graph(
          id='current',
          figure={
            'data':[
                go.Scatter(
                    x=app_df['time'],
                    y=app_df['irms'],
                    text=[str('Current: ' + str(data) + ' A') for data in app_df['irms']],
                    hoverinfo='text',
                    mode='lines',
                    line=dict(
                        color = 'rgb(178,223,138)',
                        width = 2
                        ))
                ],
            'layout': go.Layout(
                title='Current (A)',
                xaxis={'title': 'Time (s)'},
                yaxis=dict(
                    title='RMS Current (Amp)'
                ),
                hovermode='closest'
            )
          }),

    dcc.Graph(
        id='phase_pf',
        figure={
        'data':[trace1, trace2],
        'layout': go.Layout(
            title='Power factor and Phase angle (ø)',
            yaxis2=dict(
                title='Phase angle (ø)',
                titlefont=dict(
                    color='rgb(227,26,28)'
                ),
                tickfont=dict(
                    color='rgb(227,26,28)'
                ),
                overlaying='y',
                side='right'
            ),
            yaxis=dict(
                title='Power factor',
                titlefont=dict(
                    color='rgb(255,127,0)'
                ),
                tickfont=dict(
                    color='rgb(255,127,03)'
                ),
            )
            )
        }),


    dcc.Graph(
        id='powers',
        figure={
            'data': [reac_p, real_p, app_p],
            'layout': go.Layout(
                title="Real, Apparent, and Reactive Power (W)",
                yaxis=dict(
                       title='Power (W)'))
        }
    )

])

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    server = app.server
    app.run_server(debug=True)
