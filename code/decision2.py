import numpy as np


# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def setVelocity(Rover, vel):
    print ("Velocity = ", vel)
    if Rover.vel < vel:
                    # Set throttle value to throttle setting
        Rover.brake = 0
        Rover.throttle = Rover.throttle_set
    elif Rover.vel >= vel: # Else coast
        Rover.throttle = 0



def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        distanceThresh = 1.5
        # Check for Rover.mode status
        offset = 7
        xCenter = (int) (Rover.vision_image.shape[1]/2)

        canNav = Rover.vision_image[:,xCenter-offset:xCenter+offset,2] #strip of the image that if we drive straight we will be good
        distance = 0
        for row in range(0,canNav.shape[0]):
            goodRow = True
            for col in range(offset*2):
                if(canNav[row,col] == 0):
                    #print("row failed: ", row)
                    goodRow = False
                    break
            if(goodRow):
                distance = (Rover.vision_image.shape[0] - row)/15
                break
        #print (canNav.shape)
        print ("distance: ", distance)
        print("rover mode: ", Rover.mode)

        if(Rover.mode == 'init'):     
            if distance >=1.5:
                Rover.steer = 0
                print ("forward:", distance)
                setVelocity(Rover, 1)
                Rover.steer = -1
                #Rover.steer = np.clip(np.min(Rover.nav_angles * 180/np.pi)-1, -15, 15)
            else:
                Rover.throttle = 0
                Rover.setYaw = Rover.yaw +90#turn 90 degrees to the left
                if(Rover.setYaw > 360):
                    Rover.setYaw -= 360
                Rover.brake = Rover.brake_set
                Rover.mode = 'turnLeft'

        elif(Rover.mode == 'navigate'):
            #if len(Rover.nav_angles) < Rover.stop_forward:
             #       # Set mode to "stop" and hit the brakes!
              #      Rover.throttle = 0
               #     # Set brake to stored brake value
                #    Rover.brake = Rover.brake_set
                 #   Rover.steer = 0
                  #  Rover.mode = 'turnLeft'
            if distance >=distanceThresh:
                print ("forward:", distance)
                setVelocity(Rover, distance*distance/10)
                angle = np.mean (Rover.nav_angles * 180/np.pi)# +45  #+43
                Rover.steer = np.clip(angle,-15,15)
                print ("Steering: ", angle)
                print("Min angle: ", np.min(Rover.nav_angles* 180/np.pi))
            else:
                Rover.throttle = 0
                if(Rover.setYaw > 360):
                    Rover.setYaw -= 360
                Rover.brake = 1
                Rover.mode = 'turnLeft'


        elif (Rover.mode == 'turnLeft'):
            print(Rover.mode)
            if Rover.vel > .2:
                print("stopping")
                Rover.throttle = 0
                Rover.brake = 1
                Rover.steer = 0
            else:
                Rover.throttle = 0
                    # Release the brake to allow turning
                Rover.brake = 0
                print("turning")
                Rover.steer  = 7
                if(distance >distanceThresh*2): #turn until distance is great enough
                    print("Forward Again")
                    Rover.mode = 'navigate'
        elif (Rover.mode == 'driveToWall'):

            print ('go to wall')

        elif Rover.mode == 'forward': 
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:  
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                #Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.mean(Rover.nav_angles * 180/np.pi)
                    Rover.mode = 'forward'
    # Just to make the rover do something 
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0

    return Rover

