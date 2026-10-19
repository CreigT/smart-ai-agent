import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from agent import run_agent

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H2("Smart AI Agent Dashboard"),
    dcc.Store(id="chat-history", data=[]),
    dbc.Textarea(id="user-input", placeholder="Ask something...", style={"width": "100%", "height": "100px"}),
    dbc.Button("Send", id="send-btn", color="primary", className="mt-2"),
    html.Div(id="chat-display", className="mt-3")
], fluid=True)

@callback(
    Output("chat-display", "children"),
    Output("chat-history", "data"),
    Input("send-btn", "n_clicks"),
    State("user-input", "value"),
    State("chat-history", "data"),
    prevent_initial_call=True
)
def update_chat(n, user_input, history):
    if not user_input:
        return dash.no_update, history
    response = run_agent(user_input, thread_id="dash-session")
    history = history or []
    history.append({"user": user_input, "agent": response})
    display = [html.Div([
        html.P(f"You: {h['user']}", style={"fontWeight": "bold"}),
        html.P(f"Agent: {h['agent']}")
    ]) for h in history]
    return display, history

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
