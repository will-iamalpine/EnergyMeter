import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

import plotly.graph_objs as go

data_path = '/Users/louis/Google Drive/ricky-will-louis/data/data_train/'
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
var_names = {'power_factor': 'Power factor', 'phase_angle': 'Phase angle', 'power_real': 'Real power',
 'power_reactive': 'Reactive power', 'power_apparent': 'Apparent power', 'vrms': 'RMS voltage', 'irms': 'RMS current'}
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

vars = ['time', 'power_factor', 'phase_angle', 'power_real', 'power_reactive', 'power_apparent', 'vrms', 'irms']

cell_df = pd.read_csv(data_path+'cell_1.csv', names = vars)
cell_df.columns = cell_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')

lamp_df = pd.read_csv(data_path+'desklamp_1.csv', names = vars)
lamp_df.columns = lamp_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')

fan_df = pd.read_csv(data_path+'fan_1.csv', names = vars)
fan_df.columns = fan_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')

kettle_df = pd.read_csv(data_path+'kettle_1.csv', names = vars)
kettle_df.columns = kettle_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')

laptop_df = pd.read_csv(data_path+'laptop_1.csv', names = vars)
laptop_df.columns = laptop_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')

monitor_df = pd.read_csv(data_path+'monitor_1.csv', names = vars)
monitor_df.columns = monitor_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')

sadlamp_df = pd.read_csv(data_path+'sadlamp_1.csv', names = vars)
sadlamp_df.columns = sadlamp_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')



app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df_list = [cell_df, lamp_df, fan_df, kettle_df, laptop_df, monitor_df, sadlamp_df]
df_names = ['Cell', 'Lamp', 'Fan', 'Kettle', 'Laptop', 'Monitor', 'Sad lamp']
pf_list = []
phase_list = []
real_list = []
reac_list = []
appar_list = []
vrms_list = []
irms_list = []
for i,df in enumerate(df_list):
    pf_list.append(go.Scatter(
                x=df['time'],
                y=df['power_factor'],
                text=[str(str(df_names[i]) + ' Power factor: ' + str(data)) for data in df['power_factor']],
                hoverinfo='text',
                mode='lines',
                opacity=0.7,
                line=dict(
                        width = 2,),name=str(str(df_names[i]) + ' Power factor')))

    phase_list.append(go.Scatter(
                x=df['time'],
                y=df['phase_angle'],
                text=[str(str(df_names[i]) + ' Phase angle: ' + str(data)) for data in df['phase_angle']],
                hoverinfo='text',
                mode='lines',
                opacity=0.7,
                line=dict(
                        width = 2,),name=str(str(df_names[i]) + ' Phase angle')))

    real_list.append(go.Scatter(
                x=df['time'],
                y=df['power_real'],
                text=[str(str(df_names[i]) + ' Real power: ' + str(data)) for data in df['power_real']],
                hoverinfo='text',
                mode='lines',
                opacity=0.7,
                line=dict(
                        width = 2,),name=str(str(df_names[i]) + ' Real power')))

    reac_list.append(go.Scatter(
                x=df['time'],
                y=df['power_reactive'],
                text=[str(str(df_names[i]) + ' Reactive power: ' + str(data)) for data in df['power_reactive']],
                hoverinfo='text',
                mode='lines',
                opacity=0.7,
                line=dict(
                        width = 2,),name=str(str(df_names[i]) + ' Reactive power')))

    appar_list.append(go.Scatter(
                x=df['time'],
                y=df['power_apparent'],
                text=[str(str(df_names[i]) + ' Apparent power: ' + str(data)) for data in df['power_apparent']],
                hoverinfo='text',
                mode='lines',
                opacity=0.7,
                line=dict(
                        width = 2,),name=str(str(df_names[i]) + ' Apparent power')))

    vrms_list.append(go.Scatter(
                x=df['time'],
                y=df['vrms'],
                text=[str(str(df_names[i]) + ' Voltage: ' + str(data)) for data in df['vrms']],
                hoverinfo='text',
                mode='lines',
                opacity=0.7,
                line=dict(
                        width = 2,),name=str(str(df_names[i]) + ' Voltage')))

    irms_list.append(go.Scatter(
        x=df['time'],
        y=df['irms'],
        text=[str(str(df_names[i]) + ' Current: ' + str(data)) for data in df['irms']],
        hoverinfo='text',
        mode='lines',
        opacity=0.7,
        line=dict(
            width=2, ), name=str(str(df_names[i]) + ' Current')))


app.layout = html.Div([
    html.H1(children='EnergyMeter'),
    html.Div('You are now viewing the energy signatures of a sample of devices.'),

    dcc.Graph(
          id='voltage',
          figure={
            'data':vrms_list,
            'layout': go.Layout(
                title='Voltage (V)',
                xaxis=dict(title='Time (s)',
                           range=[0,7.2]),
                yaxis=dict(
                        title='RMS Voltage (V)'
                        ),

                hovermode='closest'
            )
          }),

    dcc.Graph(
          id='current',
          figure={
            'data':irms_list,
            'layout': go.Layout(
                title='Current (A)',
                xaxis=dict(title='Time (s)',
                           range=[0,7.2]),
                yaxis=dict(
                    title='RMS Current (Amp)'
                ),
                hovermode='closest'
            )
          }),


    dcc.Graph(
          id='phase',
          figure={
            'data':phase_list,
            'layout': go.Layout(
                title='Phase angle (ø)',
                xaxis=dict(title='Time (s)',
                           range=[0,7.2]),
                yaxis=dict(
                    title='Phase angle (ø)'
                ),
                hovermode='closest'
            )
          }),

    dcc.Graph(
          id='power factor',
          figure={
            'data':pf_list,
            'layout': go.Layout(
                title='Power factor',
                xaxis=dict(title='Time (s)',
                           range=[0,7.2]),
                yaxis=dict(
                    title='Power facotr'
                ),
                hovermode='closest'
            )
          }),

    dcc.Graph(
        id='real power',
        figure={
            'data': real_list,
            'layout': go.Layout(
                title="Real Power (W)",
                xaxis=dict(range=[0,7.2]),
                yaxis=dict(
                       title='Real Power (W)'))
        }),

    dcc.Graph(
        id='reactive power',
        figure={
            'data': reac_list,
            'layout': go.Layout(
                title="Reactive Power (W)",
                xaxis=dict(range=[0,7.2]),
                yaxis=dict(
                       title='Reactive Power (W)'))
        }),

    dcc.Graph(
        id='apparent power',
        figure={
            'data': appar_list,
            'layout': go.Layout(
                title="Apparent Power (W)",
                xaxis=dict(range=[0,7.2]),
                yaxis=dict(
                       title='Apparent Power (W)'))
        }),
])

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    server = app.server
    app.run_server(debug=True)
