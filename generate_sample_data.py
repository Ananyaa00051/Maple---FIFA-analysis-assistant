"""
generate_sample_data.py
Generates a realistic sample FIFA dataset for testing purposes.
Run: python generate_sample_data.py
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)

PLAYERS = [
    # Name, Age, Nationality, Club, Position, Overall, Potential
    ("Lionel Messi", 36, "Argentina", "Inter Miami", "CAM", 91, 91),
    ("Cristiano Ronaldo", 38, "Portugal", "Al Nassr", "ST", 88, 88),
    ("Kylian Mbappe", 24, "France", "Paris SG", "ST", 91, 95),
    ("Erling Haaland", 23, "Norway", "Manchester City", "ST", 91, 95),
    ("Neymar Jr", 31, "Brazil", "Al Hilal", "LW", 87, 87),
    ("Kevin De Bruyne", 32, "Belgium", "Manchester City", "CM", 91, 91),
    ("Vinicius Jr", 23, "Brazil", "Real Madrid", "LW", 89, 94),
    ("Robert Lewandowski", 34, "Poland", "Barcelona", "ST", 90, 90),
    ("Mohamed Salah", 31, "Egypt", "Liverpool", "RW", 89, 89),
    ("Karim Benzema", 35, "France", "Al Ittihad", "ST", 89, 89),
    ("Luka Modric", 37, "Croatia", "Real Madrid", "CM", 87, 87),
    ("Toni Kroos", 33, "Germany", "Real Madrid", "CM", 88, 88),
    ("Virgil van Dijk", 31, "Netherlands", "Liverpool", "CB", 89, 89),
    ("Alisson Becker", 30, "Brazil", "Liverpool", "GK", 89, 89),
    ("Thibaut Courtois", 31, "Belgium", "Real Madrid", "GK", 90, 90),
    ("Casemiro", 31, "Brazil", "Manchester Utd", "CDM", 89, 89),
    ("Joshua Kimmich", 28, "Germany", "Bayern Munich", "CDM", 89, 91),
    ("Pedri", 21, "Spain", "Barcelona", "CM", 87, 94),
    ("Gavi", 19, "Spain", "Barcelona", "CM", 82, 93),
    ("Jude Bellingham", 20, "England", "Real Madrid", "CM", 88, 95),
    ("Phil Foden", 23, "England", "Manchester City", "CAM", 88, 93),
    ("Bukayo Saka", 21, "England", "Arsenal", "RW", 86, 93),
    ("Jamal Musiala", 20, "Germany", "Bayern Munich", "CAM", 86, 94),
    ("Rodri", 27, "Spain", "Manchester City", "CDM", 89, 90),
    ("Marc-Andre ter Stegen", 31, "Germany", "Barcelona", "GK", 89, 89),
    ("Ruben Dias", 26, "Portugal", "Manchester City", "CB", 88, 90),
    ("Joao Cancelo", 29, "Portugal", "Barcelona", "RB", 87, 88),
    ("Achraf Hakimi", 24, "Morocco", "Paris SG", "RB", 86, 90),
    ("Antonio Rudiger", 30, "Germany", "Real Madrid", "CB", 85, 85),
    ("Marquinhos", 29, "Brazil", "Paris SG", "CB", 87, 87),
    ("Declan Rice", 24, "England", "Arsenal", "CDM", 85, 90),
    ("Martin Odegaard", 24, "Norway", "Arsenal", "CAM", 87, 90),
    ("Granit Xhaka", 30, "Switzerland", "Bayer Leverkusen", "CM", 84, 84),
    ("Bruno Fernandes", 29, "Portugal", "Manchester Utd", "CAM", 87, 87),
    ("Marcus Rashford", 25, "England", "Manchester Utd", "LW", 84, 88),
    ("Harry Kane", 29, "England", "Bayern Munich", "ST", 90, 90),
    ("Heung-min Son", 31, "South Korea", "Tottenham", "LW", 87, 87),
    ("Diogo Jota", 26, "Portugal", "Liverpool", "ST", 84, 87),
    ("Darwin Nunez", 24, "Uruguay", "Liverpool", "ST", 82, 88),
    ("Cody Gakpo", 24, "Netherlands", "Liverpool", "LW", 82, 88),
    ("Gabriel Martinelli", 22, "Brazil", "Arsenal", "LW", 83, 90),
    ("Eduardo Camavinga", 21, "France", "Real Madrid", "CM", 82, 92),
    ("Aurelien Tchouameni", 23, "France", "Real Madrid", "CDM", 84, 91),
    ("Eder Militao", 25, "Brazil", "Real Madrid", "CB", 85, 89),
    ("Federico Valverde", 24, "Uruguay", "Real Madrid", "CM", 86, 91),
    ("Bernardo Silva", 29, "Portugal", "Manchester City", "CM", 87, 87),
    ("Jack Grealish", 28, "England", "Manchester City", "LW", 83, 85),
    ("Riyad Mahrez", 32, "Algeria", "Al Ahli", "RW", 85, 85),
    ("Ilkay Gundogan", 32, "Germany", "Barcelona", "CM", 85, 85),
    ("Manuel Neuer", 37, "Germany", "Bayern Munich", "GK", 87, 87),
    ("Leroy Sane", 27, "Germany", "Bayern Munich", "LW", 86, 87),
    ("Serge Gnabry", 28, "Germany", "Bayern Munich", "RW", 84, 85),
    ("Thomas Muller", 33, "Germany", "Bayern Munich", "CAM", 85, 85),
    ("Leon Goretzka", 28, "Germany", "Bayern Munich", "CM", 85, 87),
    ("Sadio Mane", 31, "Senegal", "Al Nassr", "LW", 85, 85),
    ("Richarlison", 26, "Brazil", "Tottenham", "ST", 81, 85),
    ("Son Heung-min", 31, "South Korea", "Tottenham", "LW", 87, 87),
    ("Dejan Kulusevski", 23, "Sweden", "Tottenham", "RW", 82, 88),
    ("Ivan Perisic", 34, "Croatia", "Hajduk Split", "LM", 82, 82),
    ("Raphael Varane", 30, "France", "Manchester Utd", "CB", 85, 85),
    ("Luke Shaw", 28, "England", "Manchester Utd", "LB", 83, 85),
    ("Aaron Wan-Bissaka", 26, "England", "Manchester Utd", "RB", 80, 83),
    ("Rasmus Hojlund", 21, "Denmark", "Manchester Utd", "ST", 80, 89),
    ("Mason Mount", 24, "England", "Manchester Utd", "CAM", 82, 87),
    ("Kobbie Mainoo", 19, "England", "Manchester Utd", "CM", 77, 89),
    ("William Saliba", 22, "France", "Arsenal", "CB", 85, 91),
    ("Gabriel Magalhaes", 25, "Brazil", "Arsenal", "CB", 84, 88),
    ("Ben White", 26, "England", "Arsenal", "RB", 83, 87),
    ("Oleksandr Zinchenko", 27, "Ukraine", "Arsenal", "LB", 82, 84),
    ("Thomas Partey", 30, "Ghana", "Arsenal", "CDM", 84, 84),
    ("Leandro Trossard", 29, "Belgium", "Arsenal", "LW", 82, 83),
    ("Eddie Nketiah", 24, "England", "Arsenal", "ST", 78, 84),
    ("Kai Havertz", 24, "Germany", "Arsenal", "CAM", 82, 86),
    ("Dominik Szoboszlai", 23, "Hungary", "Liverpool", "CM", 83, 89),
    ("Alexis Mac Allister", 25, "Argentina", "Liverpool", "CM", 84, 87),
    ("Wataru Endo", 30, "Japan", "Liverpool", "CDM", 80, 81),
    ("Trent Alexander-Arnold", 25, "England", "Liverpool", "RB", 87, 89),
    ("Andrew Robertson", 29, "Scotland", "Liverpool", "LB", 87, 87),
    ("Joel Matip", 32, "Cameroon", "free agent", "CB", 83, 83),
    ("Ibrahima Konate", 24, "France", "Liverpool", "CB", 84, 89),
    ("Fermin Lopez", 21, "Spain", "Barcelona", "CM", 78, 88),
    ("Lamine Yamal", 16, "Spain", "Barcelona", "RW", 78, 96),
    ("Joao Felix", 24, "Portugal", "Barcelona", "CAM", 83, 87),
    ("Ansu Fati", 21, "Spain", "Barcelona", "LW", 80, 88),
    ("Alejandro Balde", 20, "Spain", "Barcelona", "LB", 81, 91),
    ("Ronald Araujo", 24, "Uruguay", "Barcelona", "CB", 85, 89),
    ("Jules Kounde", 25, "France", "Barcelona", "CB", 84, 88),
    ("Xavi Simons", 21, "Netherlands", "RB Leipzig", "CM", 82, 92),
    ("Warren Zaire-Emery", 18, "France", "Paris SG", "CM", 78, 92),
    ("Bradley Barcola", 21, "France", "Paris SG", "LW", 78, 88),
    ("Ousmane Dembele", 26, "France", "Paris SG", "RW", 85, 87),
    ("Randal Kolo Muani", 25, "France", "Paris SG", "ST", 83, 87),
    ("Manuel Ugarte", 22, "Uruguay", "Paris SG", "CDM", 80, 88),
    ("Theo Hernandez", 26, "France", "AC Milan", "LB", 86, 87),
    ("Mike Maignan", 28, "France", "AC Milan", "GK", 86, 87),
    ("Rafael Leao", 24, "Portugal", "AC Milan", "LW", 86, 90),
    ("Tijjani Reijnders", 25, "Netherlands", "AC Milan", "CM", 82, 88),
    ("Christian Pulisic", 25, "USA", "AC Milan", "RW", 82, 84),
    ("Lautaro Martinez", 26, "Argentina", "Inter Milan", "ST", 87, 89),
    ("Nicolo Barella", 26, "Italy", "Inter Milan", "CM", 86, 88),
    ("Hakan Calhanoglu", 29, "Turkey", "Inter Milan", "CDM", 85, 85),
    ("Federico Dimarco", 26, "Italy", "Inter Milan", "LB", 83, 86),
    ("Alessandro Bastoni", 24, "Italy", "Inter Milan", "CB", 85, 89),
]

def rand_stat(base, spread=8):
    return int(np.clip(np.random.normal(base, spread), 30, 99))

rows = []
for p in PLAYERS:
    name, age, nat, club, pos, ovr, pot = p

    # Generate position-appropriate stats
    is_gk = pos == "GK"
    is_def = pos in ("CB", "LB", "RB")
    is_mid = pos in ("CM", "CDM", "CAM", "LM", "RM")
    is_att = pos in ("ST", "CF", "LW", "RW", "SS")

    pace      = rand_stat(45 if is_gk else (65 if is_def else (78 if is_mid else 83)))
    shooting  = rand_stat(20 if is_gk else (40 if is_def else (68 if is_mid else 84)))
    passing   = rand_stat(55 if is_gk else (65 if is_def else (82 if is_mid else 75)))
    dribbling = rand_stat(30 if is_gk else (55 if is_def else (78 if is_mid else 85)))
    defending = rand_stat(20 if is_gk else (82 if is_def else (72 if is_mid else 35)))
    physicality = rand_stat(60)

    value = max(100_000, int(np.random.exponential(20_000_000) * (ovr / 85)))
    wage  = max(1_000, int(value * np.random.uniform(0.001, 0.003)))

    rows.append({
        "player_name": name,
        "age": age,
        "nationality": nat,
        "club": club,
        "position": pos,
        "overall": ovr,
        "potential": pot,
        "value_eur": value,
        "wage_eur": wage,
        "pace": pace,
        "shooting": shooting,
        "passing": passing,
        "dribbling": dribbling,
        "defending": defending,
        "physicality": physicality,
    })

# Pad with 400 random players
EXTRA_NAMES = [
    "Carlos Silva", "Ahmed Hassan", "James Wilson", "Pedro Santos", "Yuki Tanaka",
    "Omar Al-Farsi", "Lucas Moura", "Antoine Griezmann clone", "Takumi Minamino",
    "Hwang Hee-chan", "Caglar Soyuncu", "Josko Gvardiol", "Florian Wirtz",
    "Nico Schlotterbeck", "Konstantinos Tsimikas", "Naby Keita", "Alex Oxlade-Chamberlain",
    "Roberto Firmino", "Fabinho", "Jordan Henderson",
]
clubs = [c for _, _, _, c, _, _, _ in PLAYERS]
nationalities = list(set(n for _, _, n, _, _, _, _ in PLAYERS)) + ["Italy", "Spain", "Germany", "Brazil", "Argentina", "England", "France"]
positions = ["ST", "LW", "RW", "CAM", "CM", "CDM", "LB", "RB", "CB", "GK", "CF", "LM", "RM"]

rng_names = [f"Player {i:04d}" for i in range(500)]
for i, pname in enumerate(rng_names):
    ovr = int(np.clip(np.random.normal(74, 8), 50, 92))
    pot = int(np.clip(ovr + np.random.randint(0, 10), ovr, 97))
    age = int(np.clip(np.random.normal(26, 4), 16, 40))
    pos = np.random.choice(positions)
    is_gk = pos == "GK"
    is_def = pos in ("CB", "LB", "RB")
    is_mid = pos in ("CM", "CDM", "CAM", "LM", "RM")
    rows.append({
        "player_name": pname,
        "age": age,
        "nationality": np.random.choice(nationalities),
        "club": np.random.choice(clubs),
        "position": pos,
        "overall": ovr,
        "potential": pot,
        "value_eur": max(50_000, int(np.random.exponential(5_000_000) * (ovr / 85))),
        "wage_eur": max(500, int(np.random.exponential(30_000))),
        "pace": rand_stat(45 if is_gk else 72),
        "shooting": rand_stat(20 if is_gk else (45 if is_def else 72)),
        "passing": rand_stat(60),
        "dribbling": rand_stat(35 if is_gk else 68),
        "defending": rand_stat(25 if not is_def else 75),
        "physicality": rand_stat(65),
    })

df = pd.DataFrame(rows)
os.makedirs("data", exist_ok=True)
df.to_csv("data/fifa_players.csv", index=False)
print(f"✓ Generated {len(df)} players → data/fifa_players.csv")
