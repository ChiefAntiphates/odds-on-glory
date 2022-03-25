# odds-on-glory
Step into the shoes of the ancient Roman elite and become a spectator and active participant in the most dangerous game of all. How do you fancy your odds on glory?

Hunger Games inspired multiplayer betting game where users can join arenas with other "spectators", submit their own gladiators, bet (fake currency) on who is going to win, and send gifts to the gladiators to increase their odds.

The game is hosted on Heroku and can be played live here:
https://odds-on-glory.herokuapp.com/


The version of the game hosted on Heroku is a proof of concept for what I think is a highly enjoyable passive multiplayer game experience. It was completed as a solo passion project in the final months of my tenure at university and helped me learn a lot during the development.

# Features

- Public multiplayer "arenas" where users can witness the same battles happening in real time and impact the outcome by placing bets and sending traps or aid.
- Gladiators act independently of each other and can behave in a number of ways influenced by various factors. For example if a gladiator has a low aggression stat they are less likely to attack, however if they spot a nearby gladiator on low health they may become more inclined to. Gladiator actions include hunting, attacking, fleeing, laying traps, healing, and exploring.
- Players can buy gladiators from the marketplace that is refreshed daily and each gladiator has unique attributes.
- Players can compete with each other to earn the most money by making smart bets and getting good returns. The leaderboard reflects the players with the most money.

# Implementation Details
The application logic was written in Python and uses Flask to communicate with the Frontend client.

The frontend was written in Vanilla JavaScript and two-way communication is facilitated using WebSockets with Socket.IO.
