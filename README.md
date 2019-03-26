### Demo


![Working Project](demo/demo.gif)

![Color tracking](demo/trackTarget.gif)

![Move target](demo/setTarget.gif)


### File list:

| Filename | Description |
|---|---|
| color_track.py | Color tracking helper, to be kept in same location as color_uvs_server.py |
| color_uvs_server.py | Server for tracking color target and sending instruction to segway |  
| pendulum_client.py | Client for tracking color. Where Segway receive instructions |
| pendulum_thread.py | Segway internal program, handle movement and balancing |
| diff_uvs_server.py | Server for Differential, handle tracking and instructing Differential to move to target |
| diff_uvs_client.py | Client for Differential. Where it receive instruction to move to target |


### Execution instruction

##### Differential drive robot
Use this to move the ball to desired location.

On robot : 
> python3 diff_uvs_client.py

On PC:
> python3 diff_uvs_server.py

Select ROI (in this case the robot) and press Enter. Doubleclick to move to a target.

#### Segway
On robot:
> python3 pendulum_client.py

On PC:
> python3 color_uvs_server.py

Keep the robot upright. It should start following the ball.
