"""🥏Projectiles! A simple Taipy game by Alexandre Sajus"""
import math
from taipy.gui import Gui, State, notify
import numpy as np
import pandas as pd

initial_speed = 10
initial_angle = 45
dt = 0.01
drag = 0
target_x = 5.0
target_y = 2.0
target_size = 1.0

highscore_path = "highscores.csv"
highscore_data = pd.read_csv(highscore_path)

name = "Anonymous"

positions = pd.DataFrame(
    {
        "x": [
            0.0,
            initial_speed * math.cos(initial_angle / 180 * math.pi) / 10,
        ],
        "Projectile": [
            0.0,
            initial_speed * math.sin(initial_angle / 180 * math.pi) / 10,
        ],
    }
)
target = pd.DataFrame(
    {
        "x": [target_x, target_x],
        "Target": [target_y, target_y + target_size],
    }
)

chart_data = [positions, target]

in_sim = False
score_text = "Score: 0"
score = 0

bullet_text = "Ammo: 🥏🥏"
bullets = 2

highscore_text = "Highscore: 0"
highscore = 0


def run_simulation(state: State) -> None:
    if not state.in_sim:
        state.bullets = state.bullets - 1
        refresh_texts(state)
        state.in_sim = True
        reset_positions(state)
        x = 0.0
        y = 0.0
        x_speed = state.initial_speed * math.cos(state.initial_angle / 180 * math.pi)
        y_speed = state.initial_speed * math.sin(state.initial_angle / 180 * math.pi)
        x_historical = [x]
        y_historical = [y]
        while y >= 0:
            x += x_speed * dt
            y += y_speed * dt
            if (
                x - state.target_x > 0
                and x - state.target_x < 0.3
                and abs(y - state.target_y - state.target_size / 2)
                < (state.target_size / 2) + 0.1
            ):
                notify(state, "success", "Target hit!")
                reset_target(state)
                state.in_sim = False
                state.score = state.score + 1
                state.bullets = 2
                state.target_size = state.target_size * 0.9
                refresh_texts(state)
                break
            y_speed -= 9.8 * dt
            y_speed -= drag * y_speed * dt
            x_speed -= drag * x_speed * dt
            x_historical.append(x)
            y_historical.append(y)
            state.positions = pd.DataFrame(
                {"x": x_historical, "Projectile": y_historical}
            )
            state.chart_data = [state.positions, state.target]
        if state.bullets == 0:
            state.in_sim = False
            state.bullets = 2
            if state.score > state.highscore:
                state.highscore = state.score
            state.score = 0
            state.target_size = 1.0
            refresh_texts(state)
            reset_target(state)
            notify(state, "error", "Game Over!")
        state.in_sim = False


def set_angle(state: State) -> None:
    if not state.in_sim:
        state.positions = pd.DataFrame(
            {
                "x": [
                    0.0,
                    state.initial_speed
                    * math.cos(state.initial_angle / 180 * math.pi)
                    / 10,
                ],
                "Projectile": [
                    0.0,
                    state.initial_speed
                    * math.sin(state.initial_angle / 180 * math.pi)
                    / 10,
                ],
            }
        )
        state.chart_data = [state.positions, state.target]


def reset_target(state: State) -> None:
    state.target_x = np.random.uniform(3, 7)
    state.target_y = np.random.uniform(0, 2.5)
    state.target = pd.DataFrame(
        {
            "x": [state.target_x, state.target_x],
            "Target": [state.target_y, state.target_y + state.target_size],
        }
    )
    state.chart_data = [state.positions, state.target]


def refresh_texts(state: State) -> None:
    state.bullet_text = f"Ammo: {'🥏' * state.bullets}"
    state.score_text = f"Score: {state.score}"
    state.highscore_text = f"Highscore: {state.highscore}"


def reset_positions(state: State) -> None:
    state.positions = pd.DataFrame({"x": [0.0], "Projectile": [0.0]})
    state.chart_data = [state.positions, state.target]


def read_highscore(state: State) -> None:
    state.highscore_data = pd.read_csv(highscore_path)
    state.highscore_data = state.highscore_data.sort_values(
        by="Highscores", ascending=False
    )


def on_init(state: State) -> None:
    read_highscore(state)


def submit_highscore(state: State) -> None:
    state.highscore = max(state.highscore, state.score)
    with open(highscore_path, "a") as f:
        f.write(f"\n{state.name},{state.highscore}")
    read_highscore(state)
    notify(state, "success", "Highscore submitted!")


layout = {
    "xaxis": {"range": [0, 12], "title": "Distance (m)"},
    "yaxis": {"range": [0, 3]},
}

target_prop = {
    "width": 10,
}

page = """
<|layout|columns=1 1 1 1 1|
## Angle (°)<br/><|{initial_angle}|slider|min=0|max=90|on_change=set_angle|>

<br/><br/><|Fire!|button|on_action=run_simulation|>

## <|{bullet_text}|text|raw|>

## <|{score_text}|text|raw|>

## <|{highscore_text}|text|raw|>
|>
<|{chart_data}|chart|mode=lines|layout={layout}|x[1]=0/x|x[2]=1/x|y[1]=0/Projectile|y[2]=1/Target|line[2]={target_prop}|><br/>

# 🥏Projectiles!

A simple Taipy game by Alexandre Sajus

<center><|{name}|input|label=Enter your name:|><br/><|Submit Highscore|button|on_action=submit_highscore|><|Refresh Highscores|button|on_action=read_highscore|><|{highscore_data}|table|width=40%|></center>
"""

Gui(page).run(title="🥏Projectiles!")
