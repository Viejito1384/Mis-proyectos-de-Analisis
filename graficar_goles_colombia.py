from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from statsbombpy import sb

plt.switch_backend("Agg")


COMPETITION_ID = 223
SEASON_ID = 282
OUTPUT_PATH = Path(__file__).with_name("goles_colombia_copa_america_2024.png")


def main() -> None:
    matches = sb.matches(competition_id=COMPETITION_ID, season_id=SEASON_ID)
    colombia_matches = matches[
        (matches["home_team"] == "Colombia") | (matches["away_team"] == "Colombia")
    ].copy()

    match_details = []
    for match in colombia_matches.itertuples(index=False):
        events = sb.events(match_id=match.match_id, split=False)
        shots = events[
            (events["type"] == "Shot") & (events["shot_outcome"] == "Goal")
        ].copy()
        own_goals = events[
            (events["type"] == "Own Goal For") & (events["team"] == "Colombia")
        ].copy()

        scorers = [
            (int(goal.minute), str(goal.player))
            for goal in shots[shots["team"] == "Colombia"].itertuples(index=False)
        ]
        scorers.extend(
            (int(goal.minute), f"Gol en propia puerta ({goal.player})")
            for goal in own_goals.itertuples(index=False)
        )
        scorers.sort(key=lambda item: item[0])

        match_details.append(
            {
                "date": match.match_date,
                "home": match.home_team,
                "away": match.away_team,
                "home_score": int(match.home_score),
                "away_score": int(match.away_score),
                "stage": match.competition_stage,
                "scorers": scorers,
            }
        )

    match_details.sort(key=lambda item: item["date"])
    colombia_goals = sum(len(match["scorers"]) for match in match_details)

    fig, ax = plt.subplots(figsize=(13, 8))
    fig.patch.set_facecolor("#f6f7f9")
    ax.set_facecolor("#f6f7f9")
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, len(match_details) - 0.5)
    ax.axis("off")

    fig.text(
        0.08,
        0.95,
        "COLOMBIA | GOLES EN LA COPA AMÉRICA 2024",
        fontsize=19,
        fontweight="bold",
        color="#17324d",
    )
    fig.text(
        0.08,
        0.905,
        f"{colombia_goals} goles en {len(match_details)} partidos · marcador y anotadores",
        fontsize=12,
        color="#526579",
    )

    for index, match in enumerate(match_details):
        y = len(match_details) - index - 1
        ax.axhline(y - 0.46, color="#dce2e8", linewidth=0.8, xmin=0.02, xmax=0.98)
        ax.text(
            0.03,
            y + 0.16,
            match["stage"].upper(),
            fontsize=8,
            fontweight="bold",
            color="#718096",
            va="center",
        )
        ax.text(
            0.03,
            y - 0.12,
            f'{match["home"]}  {match["home_score"]} – {match["away_score"]}  {match["away"]}',
            fontsize=12,
            fontweight="bold",
            color="#17324d",
            va="center",
        )

        scorer_text = (
            "  ·  ".join(f"{name} ({minute}')"
                         for minute, name in match["scorers"])
            if match["scorers"]
            else "Colombia no anotó"
        )
        ax.text(
            0.56,
            y - 0.02,
            scorer_text,
            fontsize=10,
            color="#263746",
            va="center",
            wrap=True,
        )

    plt.tight_layout(rect=(0.04, 0.04, 0.98, 0.87))
    fig.savefig(OUTPUT_PATH, dpi=180, bbox_inches="tight")
    print(f"Gráfica guardada en: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
