from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
from absl import app
import random
import numpy

class ZergAgent(base_agent.BaseAgent):

    def __init__(self):
        super(ZergAgent, self).__init__()  
        self.attack_coordinates = None
        self.safe_coordinates = None
        self.safe_coordinates2 = None
        self.second_hatchery = 0
        self.position = ""
        self.extractor = 0
        self.pool = 0
    
    def unit_type_is_selected(self, obs, unit_type):
        if (len(obs.observation.single_select) > 0 and
                obs.observation.single_select[0].unit_type == unit_type):
            return True
            
        if (len(obs.observation.multi_select) > 0 and 
                obs.observation.multi_select[0].unit_type == unit_type):
            return True
        
        return False

    def get_units_by_type(self, obs, unit_type):
        return [unit for unit in obs.observation.feature_units
                if unit.unit_type == unit_type]
    
    def can_do(self, obs, action):
        if action in obs.observation.available_actions:
            result = True
        else:
            result = False
        return result
    
    # Function to send to attack zerlings and hydras
    def my_attack(self, obs):
        zerglings = self.get_units_by_type(obs, units.Zerg.Zergling)
        hydras = self.get_units_by_type(obs, units.Zerg.Hydralisk)
        # If army is enough
        if len(zerglings) >= 5 and len(hydras) >= 5:
            print("Going to select")
            if self.unit_type_is_selected(obs, units.Zerg.Zergling):
                if self.can_do(obs, actions.FUNCTIONS.Attack_minimap.id):
                    print("Attacking")
                    return actions.FUNCTIONS.Attack_minimap("now", self.attack_coordinates)
            
            # Select zerlings and hydras
            if self.can_do(obs, actions.FUNCTIONS.select_army.id):
                print("selecting army attack")
                return actions.FUNCTIONS.select_army("select")

    # Function to defend the hatchery with queens
    def my_defense(self, obs):
        # Check features on position of each element
        player_relative = obs.observation.feature_screen.player_relative
        # If coordinates belong to an enemy
        enemy_y, enemy_x = (player_relative == 4).nonzero()
        # If there is an enemy
        if enemy_y.any():
            if self.unit_type_is_selected(obs, units.Zerg.Queen):
                if self.can_do(obs, actions.FUNCTIONS.Attack_screen.id):
                    # Calculate enemy coordinates
                    index = numpy.argmax(enemy_y)
                    target = [enemy_x[index], enemy_y[index]]
                    # if enemy is on the screen
                    if enemy_x[index] > 0 and enemy_x[index] < 84 and enemy_y[index] > 0 and enemy_y[index] < 84:
                        print("defending")
                        return actions.FUNCTIONS.Attack_screen("now", target)

            # Select queens to defend the hatchery
            queens = self.get_units_by_type(obs, units.Zerg.Queen)                
            if len(queens) > 0 :
                queen = random.choice(queens)
                if self.can_do(obs,actions.FUNCTIONS.select_point.id):
                    print("selecting army defense")
                    # If queen is on the screen
                    if queen.x > 0 and queen.y > 0 and queen.x < 84 and queen.y < 84:
                        return actions.FUNCTIONS.select_point("select_all_type",(queen.x, queen.y))

    # Function to build spawning pools
    def my_spawning_pool(self, obs):
        spawning_pools = self.get_units_by_type(obs, units.Zerg.SpawningPool)
        if len (spawning_pools) == 0 and self.second_hatchery == 3 and self.pool < 2:
            if self.unit_type_is_selected(obs, units.Zerg.Drone):        
                if self.can_do(obs,actions.FUNCTIONS.Build_SpawningPool_screen.id):
                    x = random.randint(0,63)
                    y = random.randint(0,63)
                    print("building pool")
                    self.pool = self.pool + 1
                    return actions.FUNCTIONS.Build_SpawningPool_screen("now", (x,y))
                
            drones = self.get_units_by_type(obs, units.Zerg.Drone)                
            if len(drones) > 0 :
                drone = random.choice(drones)
                if self.can_do(obs,actions.FUNCTIONS.select_point.id):
                    print("selecting drones pool")
                    return actions.FUNCTIONS.select_point("select_all_type",(drone.x, 
                                                                    drone.y))
    # Function to move the camera to the second hatchery
    def move_camera_second(self,obs):
        hatchery = self.get_units_by_type(obs, units.Zerg.Hatchery)
        # If no second hatchery
        if self.can_do(obs, actions.FUNCTIONS.move_camera.id) and len(hatchery) == 1 and self.unit_type_is_selected(obs, units.Zerg.Drone):
            if self.second_hatchery == 0:
                self.second_hatchery = 1
                print("second camera")
                return actions.FUNCTIONS.move_camera((self.safe_coordinates2[0],self.safe_coordinates2[1]))

    # Function to move the camera to the first hatchery
    def move_camera_first(self,obs):
        if self.second_hatchery == 2:
            self.second_hatchery = 3
            print("first camera")
            return actions.FUNCTIONS.move_camera((self.safe_coordinates[0],self.safe_coordinates[1]))

    # Function to build the second hatchery
    def my_hatchery(self, obs):
        hatchery = self.get_units_by_type(obs, units.Zerg.Hatchery)
        # If camera is already in position for the second hatchery
        if len(hatchery) == 0 and self.second_hatchery == 1:
            if self.unit_type_is_selected(obs, units.Zerg.Drone): 
                if self.can_do(obs,actions.FUNCTIONS.Build_Hatchery_screen.id):
                    print("building hatchery")
                    self.second_hatchery = 2
                    return actions.FUNCTIONS.Build_Hatchery_screen("now", (32,32))

        # If no second hatchery, select drones
        if self.second_hatchery == 0:
            drones = self.get_units_by_type(obs, units.Zerg.Drone)                
            if len(drones) > 0 :
                drone = random.choice(drones)
                if self.can_do(obs,actions.FUNCTIONS.select_point.id):
                    if self.can_do(obs,actions.FUNCTIONS.select_point.id):
                        print("selecting drones hatchery")
                        return actions.FUNCTIONS.select_point("select_all_type",(drone.x, drone.y))

    # Function to evolve a hatchery into a lair
    def my_lair(self, obs):
        lair = self.get_units_by_type(obs, units.Zerg.Lair)
        if len(lair) == 0 and self.second_hatchery == 3:
            if self.unit_type_is_selected(obs, units.Zerg.Hatchery):        
                if self.can_do(obs,actions.FUNCTIONS.Morph_Lair_quick.id):
                    print("lair")
                    return actions.FUNCTIONS.Morph_Lair_quick("now")
                
            hatchery = self.get_units_by_type(obs, units.Zerg.Hatchery)                
            if len(hatchery) > 0 :
                hatchery = random.choice(hatchery)  
                if self.can_do(obs,actions.FUNCTIONS.select_point.id):      
                    print("selecting hatchery lair")
                    return actions.FUNCTIONS.select_point("select_all_type",(hatchery.x, 
                                                                    hatchery.y))
    # Function to build hydralisk den in order to build hydras
    def my_den(self, obs):
        den = self.get_units_by_type(obs, units.Zerg.HydraliskDen)
        if len(den) == 0 and self.second_hatchery == 3:
            if self.unit_type_is_selected(obs, units.Zerg.Drone):        
                if self.can_do(obs,actions.FUNCTIONS.Build_HydraliskDen_screen.id):
                    x = random.randint(0,63)
                    y = random.randint(0,63)
                    print("building hydralisk")
                    return actions.FUNCTIONS.Build_HydraliskDen_screen("now", (x,y))
                
            drones = self.get_units_by_type(obs, units.Zerg.Drone)                
            if len(drones) > 0 :
                drone = random.choice(drones)   
                if self.can_do(obs,actions.FUNCTIONS.select_point.id):   
                    print("selecting drones den")
                    return actions.FUNCTIONS.select_point("select_all_type",(drone.x, 
                                                                    drone.y))
    # Function to build an extractor
    def my_extractor(self, obs):
        extractor = self.get_units_by_type(obs, units.Zerg.Extractor)
        geysers = self.get_units_by_type(obs, units.Neutral.VespeneGeyser)
        # If no extractors, geysers available and second hatchery built
        if len(extractor) < 1 and self.second_hatchery == 3 and self.extractor < 2:
            if self.unit_type_is_selected(obs, units.Zerg.Drone):
                print("Extractor - drones selected")     
                if self.can_do(obs,actions.FUNCTIONS.Build_Extractor_screen.id):
                    print("Extractor - can do")
                    geysers = self.get_units_by_type(obs, units.Neutral.VespeneGeyser)
                    if len(geysers) > 0 :
                        print("Extractor - geysers available")
                        # Build extractor
                        self.extractor = self.extractor + 1
                        geyser = random.choice(geysers)
                        return actions.FUNCTIONS.Build_Extractor_screen("now", (geyser.x,geyser.y))
                
            drones = self.get_units_by_type(obs, units.Zerg.Drone)                
            if len(drones) > 0 :
                drone = random.choice(drones)
                if self.can_do(obs,actions.FUNCTIONS.select_point.id):
                    print("selecting drones extractor")
                    return actions.FUNCTIONS.select_point("select_all_type",(drone.x,drone.y))

    # Function to obtain gas from the extractors
    def my_harvest_gas(self,obs):
        extractor = self.get_units_by_type(obs, units.Zerg.Extractor)
        if len(extractor) > 0:
            extractor = random.choice(extractor)
            # If assigned drones are less than 3
            if extractor['assigned_harvesters'] < 3:
                print("EXTRACTOR -  " + str(extractor))
                if self.unit_type_is_selected(obs, units.Zerg.Drone):
                    # If less than 2 drones were selected
                    if len(obs.observation.single_select) < 2 and len(obs.observation.multi_select) < 2 :
                        if self.can_do(obs,actions.FUNCTIONS.Harvest_Gather_screen.id):      
                            print("harvesting gas")                 
                            return actions.FUNCTIONS.Harvest_Gather_screen("now",(extractor.x, extractor.y))

                drones = self.get_units_by_type(obs, units.Zerg.Drone)                
                if len(drones) > 0 :
                    drone = random.choice(drones) 
                    if self.can_do(obs,actions.FUNCTIONS.select_point.id):     
                        print("selecting drones harvest gas")                      
                        return actions.FUNCTIONS.select_point("select",(drone.x,drone.y))
    # Function to obtain minerals 
    def my_harvest_minerals(self,obs):
        mineral = self.get_units_by_type(obs, units.Neutral.MineralField)
        if len(mineral) > 0:
            mineral = random.choice(mineral)
            print("MINERAL -  " + str(mineral))
            # If assigned drones are less than 3
            if mineral['assigned_harvesters'] < 3:
                if self.unit_type_is_selected(obs, units.Zerg.Drone):
                    # if selection is less than 3
                    if len(obs.observation.single_select) < 3 and len(obs.observation.multi_select) < 3:
                        if self.can_do(obs,actions.FUNCTIONS.Harvest_Gather_screen.id):        
                            print("harvesting minerals")               
                            return actions.FUNCTIONS.Harvest_Gather_screen("now",(mineral.x, mineral.y))
                            
                drones = self.get_units_by_type(obs, units.Zerg.Drone)                
                if len(drones) > 0 :
                    drone = random.choice(drones) 
                    if self.can_do(obs,actions.FUNCTIONS.select_point.id):  
                        print("selecting drones minerals")                           
                        return actions.FUNCTIONS.select_point("select",(drone.x,drone.y))

    # Function to move overlords in order to free space for building
    def move_overlords(self,obs):
        overlords = self.get_units_by_type(obs, units.Zerg.Overlord)
        if len(overlords) > 2:
            if self.unit_type_is_selected(obs, units.Zerg.Overlord):
                if self.can_do(obs, actions.FUNCTIONS.Attack_minimap.id):
                    # Move overlords to a safe position depending on the position
                    if self.position == "up":
                        x = 0
                        y = 0
                    else:
                        x = 63
                        y = 63
                    print("moving overlords")
                    return actions.FUNCTIONS.Attack_minimap("now", (x,y))
            overlord = random.choice(overlords)    
            # Move only overlords tha are near the hatchery
            if overlord.x != 0 or overlord.x != 63:    
                print("selecting overlords")                    
                return actions.FUNCTIONS.select_point("select_all_type",(overlord.x,overlord.y))

    # Function to build queens
    def my_queen(self, obs):
        queens = self.get_units_by_type(obs, units.Zerg.Queen)
        spawning = self.get_units_by_type(obs, units.Zerg.SpawningPool)
        # If spawning pool exist 
        if len(queens) < 2 and len(spawning) > 0:
            if self.unit_type_is_selected(obs, units.Zerg.Hatchery) or self.unit_type_is_selected(obs, units.Zerg.Lair) or self.unit_type_is_selected(obs, units.Zerg.Hive):
                if self.can_do(obs,actions.FUNCTIONS.Train_Queen_quick.id):
                    print("building queen")
                    return actions.FUNCTIONS.Train_Queen_quick("now")
            # Select the present building in order to build the queen
            hatch = self.get_units_by_type(obs, units.Zerg.Hatchery)
            if len(hatch) > 0:
                hatch = random.choice(hatch)
                print("selecting hatch queen")
                return actions.FUNCTIONS.select_point("select",(hatch.x,hatch.y))

            hatch = self.get_units_by_type(obs, units.Zerg.Lair)
            if len(hatch) > 0:
                hatch = random.choice(hatch)
                print("selecting lair queen")
                return actions.FUNCTIONS.select_point("select",(hatch.x,hatch.y))

            hatch = self.get_units_by_type(obs, units.Zerg.Hive)
            if len(hatch) > 0:
                hatch = random.choice(hatch)
                print("selecting hive queen")
                return actions.FUNCTIONS.select_point("select",(hatch.x,hatch.y))

    # Function to build more supply and attack units
    def my_more_units(self, obs, type):
        if self.unit_type_is_selected(obs, units.Zerg.Larva):
            free_supply = (obs.observation.player.food_cap - obs.observation.player.food_used)

            if free_supply < 2 :
                if self.can_do(obs, actions.FUNCTIONS.Train_Overlord_quick.id):
                    print("making overlord")
                    return actions.FUNCTIONS.Train_Overlord_quick("now")

            if type == "zergling":
                if self.can_do(obs, actions.FUNCTIONS.Train_Zergling_quick.id):
                    print("Building zerling")
                    return actions.FUNCTIONS.Train_Zergling_quick("now")
            
            if type == "drone":
                if self.can_do(obs, actions.FUNCTIONS.Train_Drone_quick.id):
                    print("making drones")
                    return actions.FUNCTIONS.Train_Drone_quick("now")
                        
            if type == "hydralisk":
                if self.can_do(obs, actions.FUNCTIONS.Train_Hydralisk_quick.id):
                    print("making hydralisk")
                    return actions.FUNCTIONS.Train_Hydralisk_quick("now")
    
        larvae = self.get_units_by_type(obs, units.Zerg.Larva)
        if len(larvae) > 0 :
            larva = random.choice(larvae)
            if self.can_do(obs,actions.FUNCTIONS.select_point.id):
                print("selecting larva more units")
                return actions.FUNCTIONS.select_point("select_all_type", (larva.x, 
                                                                    larva.y))
   
    def step(self, obs):
        super(ZergAgent, self).step(obs)
            
        if obs.first():
            player_y, player_x = (obs.observation.feature_minimap.player_relative ==
                                features.PlayerRelative.SELF).nonzero()
            xmean = player_x.mean()
            ymean = player_y.mean()
            
            # Define coordinates for first and second hatchery
            if xmean <= 31 and ymean <= 31:
                self.attack_coordinates = [40,47]
                self.safe_coordinates = [17,24]
                self.safe_coordinates2 = [43,23]
                self.position = "up"
            else:
                self.attack_coordinates = [17,24]
                self.safe_coordinates = [40,47]
                self.safe_coordinates2 = [20,49]
                self.position = "down"

        # Attack with zerlings and hydras
        attack = self.my_attack(obs)  
        if attack:
            return attack

        # Defend hatchery with queens
        defense = self.my_defense(obs)  
        if defense:
            return defense

        # Move camera to second position
        camera = self.move_camera_second(obs)
        if camera:
            return camera

        # Build hatchery on second position
        hatchery = self.my_hatchery(obs)
        if hatchery:
            return hatchery

        # Move camera to first position
        camera = self.move_camera_first(obs)
        if camera:
            return camera
        
        # Build extractor to obtain gas
        extractor = self.my_extractor(obs)
        if extractor:
            return extractor

        # Build spawning pool
        spawning_pool = self.my_spawning_pool(obs)
        if spawning_pool:
            return spawning_pool

        # Move overlords to have more space
        overlords = self.move_overlords(obs)
        if overlords:
            return overlords

        # Build queens to defend hatchery
        queen = self.my_queen(obs)
        if queen:
            return queen

        # Build zerlings to attack enemy
        zerglings =  self.get_units_by_type(obs, units.Zerg.Zergling)
        if len(zerglings) <= 9:
            make_units = self.my_more_units(obs,"zergling")
            if make_units:
                return make_units

        # Build more drones to harvest gas and minerals
        drones =  self.get_units_by_type(obs, units.Zerg.Drone)
        if len(drones) <= 3:
            make_units = self.my_more_units(obs,"drone")
            if make_units:
                return make_units

        # Put drones to harvest gas
        gas = self.my_harvest_gas(obs)
        if gas:
            return gas

        # Evolve hatchery into lair      
        lair = self.my_lair(obs)
        if lair:
            return lair

        # Build den to build hydras   
        den = self.my_den(obs)
        if den:
            return den
        
        # Build hydras in order to attack
        hydras =  self.get_units_by_type(obs, units.Zerg.Hydralisk)
        if len(hydras) <= 12:
            make_units = self.my_more_units(obs,"hydralisk")
            if make_units:
                return make_units  
                
        # Obtain mineral
        mineral = self.my_harvest_minerals(obs)
        if mineral:
            return mineral 
        
        return actions.FUNCTIONS.no_op()

def main(unused_argv):
    agent = ZergAgent()
    try:
        while True:
            with sc2_env.SC2Env(
                map_name="Simple64",
                players=[sc2_env.Agent(sc2_env.Race.zerg),
                        sc2_env.Bot(sc2_env.Race.protoss,
                                    sc2_env.Difficulty.easy)],
                agent_interface_format=features.AgentInterfaceFormat(
                    feature_dimensions=features.Dimensions(screen=84, minimap=64),
                    use_feature_units=True),
                step_mul=16,
                game_steps_per_episode=0,
                visualize=False) as env:
                
                agent.setup(env.observation_spec(), env.action_spec())
                
                timesteps = env.reset()
                agent.reset()
                
                while True:
                    step_actions = [agent.step(timesteps[0])]
                    if timesteps[0].last():
                        break
                    timesteps = env.step(step_actions)
        
    except KeyboardInterrupt:
        pass
  
if __name__ == "__main__":
    app.run(main)