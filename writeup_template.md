## Project: Search and Sample Return
---


**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.

![alt text][image1]  

[//]: # (Image References)

[image1]: ./misc/rover_image.jpg
[image2]: ./calibration_images/example_grid1.jpg
[image3]: ./calibration_images/example_rock1.jpg 
[image4]: ./output/Test_Data/exampleWarp,threshold,rover.png

[image5]: ./autonomousRun1/mapped.8_fid.65.PNG
[image6]: ./autonomousRun1/Mapped.4_fid.7.PNG
[image7]: ./output/realData4pics.png

[image8]: ./autonomousRun1/3colorThreshold.PNG



## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

##### The functions provided were used to process each image and the output of the example data can be seen below.
![alt text][image4]

##### The same functions were also applied to the data recorded from the simulation to ensure all of the parameters could remain the same. The simulation was run at a resolution of 600x800 with fantastic graphics at around 24fps for this image.
![alt text][image7]

##### Additional functions were created in order to detect obstacles and rock samples. The following functions can be seen in the Rover_Project_Final_Notebook.ipynb jupyter notebook under the Color Thresholding section.

##### obstacle_thresh()
###### This function detects areas that the rover would not be able to drive and was used to update the map with known obstacles. By applying the inverse of the navigable terrain threshold, anything that was not ground colored was marked as an obstacle. 

##### sample_thresh()
###### This function was responsible for detecting the yellow rocks and used a similar method to the previous 2 thresholding functions. This function checked the RGB values and if red was greater than 105, green was greater than 105, and blue was < 100 it would be considered a sample. These values align roughly with the color yellow and did a reasonable job of selecting the rocks. This function however was a bit too lenient and some obstacles were mislabled as samples. Adding an upper threshold to these numbers as well would help eliminate this issue.
###### Here is an image from the autonomous run showing the 3 sections of thresholding. Blue is navigable terrain, red is an obstacle, and yellow is a sample.

![alt text][image8] 

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 

##### The process_image() function was populated with all of the previous functions to create a final update map as the rover drove along the ground. The proccessing occurred as follows:
###### ..1. Define the source and destination points for the warp: The source points were determined by looking at the sample image with the grid on and the destination points were defined by a 10x10 square near the bottom of the rover map.
###### ..2. The perspective transform was applied to transform the image into a top down view using the previous points. These points are only valid if the yaw and pitch of the rover are near 0
###### ..3. The 3 color thresholds, obstacles, samples, and navigable terain, were applied to the image and stored in seperate images. 
###### ..4. The 3 new images were converted to rover-centric coordinates
###### ..5. These rover-centric images were then mapped into world coordinates by translating and rotating based off the rover's current position and orientation
###### ..6. Finally the worldmap was updated with these final images to create a visual representation of the map. Again red was obstacles, blue was navigable, and yellow was samples.

##### The output of this function was then used to create a video that can be seen inside of the output folder.

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.
##### The perception_step() function was modified very little from the notebook code. The same steps were taken to process the image however rather than pulling from data already created it pulled location and orientation image from the Rover object and correspondingly update the vision and worldmap of the Rover. I also added in pitch and orientation upper bounds so any images taken while the rover was not in a valid mapping position were thrown out to prevent a loss in map fidelity.

##### The decision_step() function remained similar to the original however some modifications were made to allow for more consistent mapping. The 2 main differences were in how the rover decided to stop and how it chose the correct steering angle. For deciding when to stop I used the rover vision image which was already thresholded and warped and found the furthest navigable set of points that were at least the width of the rover. This happened by scanning down from the top of the image, looking only at the center column that was 10 pixels wide. As soon as 10 pixels were all blue, ie navigable terrain, the distance from an object was set to the height of that row/10. Every 10 pixels corresponded to a single meter so this method returned how far forward the rover could drive and not hit anything.

##### The second major change was in the steering decision. I decided to try and follow the rightmost wall the entire time to map out the entire location. On first try I decided to use only the minimum value of the valid vision angles similar to how the original algorithm used the average of all of the angles to decide a steering angle. The minimum angle then had a constant added to it to create a minimum angle to the right wall to be considered close enough to go straight. This method was not very successful as the rover would often get too close to the wall and stop slowing the process immensely. Instead If finally decided to use a weighted average between the minimum angle and the average angle to create a steering algorithm that would try and navigate to the space with the most navigable terrain but always tend towards the right. This worked very well as in places with multiple paths to take it always chose to take the right most path consistent with what wall following expected. The images in Movie and Movie2 show this process taking place. 


#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

##### All of the testing in autonomous mode was done at a resolution of 600x800 with fantastic graphics running at 24fps. From the testing I was able to successfully map over 80% of the map at a fidelity of 65%. The steering algorithm explained above combined with the perception step were fairly robust in the ability to navigate and did not often get stuck in a location and consistenly mapped the large majority of the available terrain. There were certain small offshoots that it would tend to overlook due to the weighted average not tending hard enough towards the right, but increasing this value caused the rover to drive to close to the wall and stop more frequently. Overall the performance was acceptable however there is much room for improvement.

##### The perception and decision functions were effective at mapping but there was no real way to tell the Rover to stop and pickup a sample using this method. This approach is more feasible for general wandering around the map however additional states would need to be added in order to collect samples and return to the start. Another improvement that could help prevent missing any offshoots is rather than use weighted averages to try and tend towards the wall, I could use the global map the Rover is actively creating to determine the distance to the rightmost wall. This could then be used to always remain a set distance from the right wall and would be much more robust than the method I chose. 


##### Here are 2 pictures of the progression of the map in autonomous mode.

![alt text][image6]

![alt text][image5]


