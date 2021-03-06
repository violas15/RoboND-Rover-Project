import numpy as np
import cv2

# Identify pixels below the threshold
def obstacle_thresh(img,rgb_thresh=(160,160,160)):
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    below_thresh = (img[:,:,0] < rgb_thresh[0]) \
                & (img[:,:,1] < rgb_thresh[1]) \
                & (img[:,:,2] < rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[below_thresh] = 1
    # Return the binary image
    return color_select

#identify samples with r>110 g>110 and b<100
def sample_thresh(img):
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    below_thresh = (img[:,:,0] > 105) \
                & (img[:,:,1] > 105) \
                & (img[:,:,2] < 100)
    # Index the array of zeros with the boolean array and set to 1
    color_select[below_thresh] = 1
    # Return the binary image
    return color_select

# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(180, 180, 180)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                | (img[:,:,1] > rgb_thresh[1]) \
                | (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select


# Define a function to convert to rover-centric coordinates
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = np.absolute(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[0]).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to apply a rotation to pixel positions
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_radians = yaw*np.pi/180.0
    # Apply a rotation
    xpix_rotated = xpix*np.cos(yaw_radians) - ypix*np.sin(yaw_radians)
    ypix_rotated = xpix*np.sin(yaw_radians) + ypix *np.cos(yaw_radians)
    # Return the result  
    return xpix_rotated, ypix_rotated

# Define a function to perform a translation
def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated

# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    PITCHTHRESH = .5 #from 0
    ROLLTHRESH = .5 #from 0

    pitch = min(abs(Rover.pitch), abs(Rover.pitch -360))
    roll = min(abs(Rover.roll), abs(Rover.roll -360))
    print("Pitch: ", pitch, "Roll: ", roll)
#don't update if pitch isnt correct
    image = Rover.img
    # 1) Define source and destination points for perspective transform
    dst_size = 5 
    # Set a bottom offset to account for the fact that the bottom of the image 
    # is not the position of the rover but a bit in front of it
    # this is just a rough guess, feel free to change it!
    bottom_offset = 6
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],
                      [image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],
                      [image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset], 
                      [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],
                      ])
    # 2) Apply perspective transform
    warped = perspect_transform(image, source, destination)
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    navigable = color_thresh(warped, rgb_thresh=(160,160, 160))
    obstacles = obstacle_thresh(warped)
    samples = sample_thresh(warped)
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
     # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image
    Rover.vision_image[:,:,0] = obstacles*255
    Rover.vision_image[:,:,1] = samples*255
    Rover.vision_image[:,:,2] = navigable*255

    # 5) Convert map image pixel values to rover-centric coords
    xNavPix, yNavPix  = rover_coords(navigable)
    xObsPix, yObsPix  = rover_coords(obstacles)
    xSamplePix, ySamplePix  = rover_coords(samples)

    # 6) Convert rover-centric pixel values to world coordinates
    worldNavx, worldNavy = pix_to_world(xNavPix, yNavPix, Rover.pos[0], Rover.pos[1],
                                    Rover.yaw, Rover.worldmap.shape[0], 10)
    worldObsx, worldObsy = pix_to_world(xObsPix, yObsPix, Rover.pos[0], Rover.pos[1],
                                    Rover.yaw, Rover.worldmap.shape[0], 10)
    worldSamplex, worldSampley = pix_to_world(xSamplePix, ySamplePix, Rover.pos[0], Rover.pos[1],
                                    Rover.yaw, Rover.worldmap.shape[0], 10)

    # 7) Update Rover worldmap (to be displayed on right side of screen)
    if(abs(pitch) < PITCHTHRESH and abs(roll) < ROLLTHRESH):
        Rover.worldmap[worldObsy, worldObsx, 0] += 1
        Rover.worldmap[worldSampley, worldSamplex, 1] += 1
        Rover.worldmap[worldNavy, worldNavx, 2] += 1

    # 8) Convert rover-centric pixel positions to polar coordinates
    distance,angles = to_polar_coords(xNavPix, yNavPix)
    # Update Rover pixel distances and angles
    Rover.nav_dists = distance
    Rover.nav_angles = angles
        
     
        
        
    return Rover