# DnD dice bot for Discord

## Summary
This bot provides polyhedral dice rolling capabilities for a Discord channel. 

Currently supported commands: (command character is '!' or '.')

|Command|Description|
|---|---|
|!help|Prints a list of all the commands.|
|!d20|Rolls a d20.|
| |- Can also a specify number of d20s with an additional argument (i.e. *!d20 2*)|
|!roll|Rolls the dice. Some examples:|
| |!roll d6 &nbsp;&nbsp;&nbsp;&nbsp;(one d6)|
| |!roll 2d8 &nbsp;&nbsp;&nbsp;&nbsp;(two d8s)|
| |!roll 3d10-1 &nbsp;&nbsp;&nbsp;&nbsp;(three d10s with a -1 on each roll)|
| |!roll (3d8)+3 &nbsp;&nbsp;&nbsp;&nbsp;(three d8s with a +3 to the total)|
| |!roll 2d8, 2d6 &nbsp;&nbsp;&nbsp;&nbsp;(comma-separated: two d8s and 2 d6s)|
| |!roll d20<br/>
| |1d8 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(multi-line: one d20 and one d8)|

## Instructions
1. Update `TOKEN` in **bot.py** with your bot's token ID
2. Run **bot.py**

