Question For all: How would you go about solving Issues around data privacy and security for our daily check-in feature and menstrual calendars
- This is a tough question because assuming we could add noise to our data, it would be easy to use something called Local/Central Differential Privacy which guarantees privacy at an individual level from any company that holds the data. It would allow the company to still go about collecting data for metrics because it adds on noise (there is a rigorous mathematical proof for why privacy is guaranteed) and this would be a great way to ensure privacy if noise is okay. However, in general, if we didn't want to use any of the data for metrics in any way, simple data encryption should be safe enough and anonymization by removing personal information identifiers (all though there isn't really a good way to do this that is guaranteed to be safe), but it's a good fast measure that is quite durable. Since this is health data, it's extremely important that this information stays safe. For security, password protection on the calendar can be implemented to ensure privacy and we can ensure that data remains encrypted until it's unlocked by the user to view it so that it minimizes the risk to data security when a user isn't actively trying to view their calendar.

Design Decisions: 
Not much went into the design itself, I just wanted a simple and sleek aesthetic.
For the game, I was thinking of a simple game that would be the easiest to play with any
number of people and would be easy to implement with the tools I had already layed out and
tried to put in as much feadback as possible for the players. 


How to interact with the system:
For best performance, use Safari. Open this code folder in like vscode and do "python server.py"
in order to start the server. Once this is running, go to Safari and type in http://127.0.0.1:5000
to enter your localhost server. From here, any number of tabs can be made (all of which
represent a new player for this game and each tab will have a unique player_id that persists
until the tab is closed). If you encounter an error, check below.

The first two rooms are just there to see what the interface looks on. To actually be able
to play the game, click on create room and then join the room. The other tabs you have open
should be updated to reflect the new room created. Other players can now join. After 5 players
have joined, the game should start. Throughout, there will be alerts telling people in other
rooms of people joining or leaving rooms and games starting. It also allows you to start a game early
if everyone agrees.


LINK TO A DEMO VIDEO: "https://youtu.be/twJ-lY9IxR8"


Implemented:
- Can’t join more than one room at a time
- Can’t create multiple new lobbies
- Ability to play a game real time with people
- Ability to replay game (must get all players to agree real time to do this)
- Ability to leave the game after a round is over instead of automatically replaying
- If within a game room and someone leaves, can continue the game and it’ll update to work with the number of people in the room automatically
- When a game starts, can’t view it in the lobby anymore, but it’s still there so can reference it in code, but will fully delete once all the players leave

Issues:
- In Chrome, sometimes there's an issue with alerts where they won't show up or the redirects won't
happen automatically. Try on Safari if this is the case. If the issue is still there, 
change the URL from "http://127.0.0.1:5000/room/<lobby_id>" to "http://127.0.0.1:5000/game/<lobby_id>"
and you'll be able to play (as long as you're a player that's supposed to be in the game).
