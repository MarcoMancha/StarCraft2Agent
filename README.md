# StarCraft2Agent (Zerg)
![starcraft](https://bnetcmsus-a.akamaihd.net/cms/carousel_header/YYFJAEYVDXJQ1538090707313.png)

Agent implemented in python using pysc2 framework.

## Purpose of Implementation

This implementation it's a simple StarCraft 2 building order implementation. A building implementation builds depending on the supply number, in this case we didn't focus in that number because the focus of pysc2 is different. 

The purpose was to build 2 hatchery, obtain as much materials as we could and in the mean time build queens in order to defend the hatchery and zergling's and hydras to attack the enemy.

## Build Order

* Overlord	  
* Hatchery
* Extractor
* Spawning Pool 
* Queen  
* Zergling
* Drones (mostly for the second hatchery)
* Lair
* Hydralisk Den
* Hydras

Considerations: We build an overlord every time we have less than 2 of free supply.

## Pros, Cons 

### Pros:

* Relatively easy to follow but can be very difficult to master

* Leads in to a very strong macro mid-game

* Focuses on the core aspects of Zerg

### Cons:

* Potentially weak against aggressive openers

* May lead to early frustration

## Acknowledgments

Thanks to APandaSniper for providing [this](https://lotv.spawningtool.com/build/82658/) building order on which this implemenation is based on.

## Demo video

[Link](https://drive.google.com/open?id=1VJBdAKkD1QA7f0LTKitQr9px0WZyLsKi) to demo.