# Fuzzy Sets & Systems – Group Project Report: BettAir

## Introduction

According to the ‘world health organization’ (WHO) air pollution is one of the leading environmental risk factors for disease. BettAir is an advanced fuzzy recommender system designed to enhance urban air quality management by integrating data from air quality sensors with additional information such as population density. The system generates a comprehensive heatmap that identifies priority areas where urban planners should focus their efforts to improve air quality. 

*“Reliable estimates of exposure to air pollutants and related impacts on health are key to  better inform policy-makers, as well as other health and development partners.”* p.19 

By analyzing various factors, BettAir provides tailored recommendations based on the specific conditions of each area. For instance, in densely populated regions with limited green spaces, the system may prioritize the creation of parks and vegetation to enhance air quality. Conversely, in areas located near major roads, BettAir might suggest implementing measures to reduce traffic-related emissions, such as optimizing traffic flow or promoting the use of public transportation.

This adaptive approach ensures that interventions are both targeted and effective, addressing the unique air quality challenges of different urban environments. By leveraging real-time sensor data and contextual information, BettAir supports informed decision-making, ultimately contributing to healthier and more sustainable cities.

## The System:

### Heat map
The main output of BettAir is a heatmap that can be used as a layer in GIS-applications (Geographic Information Systems). The heatmap includes the “Stations”, where it takes its input data from, and the output values as a continuous colormap.

In our implementation, each Station holds data for all three input variables; 
- Air pollution (pm2.5 - µg/m³)
- Population density (inhabitants/m2)
- Vegetation cover (%)

Based on the stations placed on the map, we use barycentric interpolation of the data (based on the three closest stations) to make a continuous representation of the data. To efficiently identify nearby stations, we store them in a k-d tree structure.

The output variable of our fuzzy system is called need_for_action (%), which is mapped to a color-scale to create the heat map. When the need_for_action is calculated throughout the entire map, we get a figure looking something like this:

*(Insert image)*

The idea is that this can provide a layer that can be plotted on top of a real world map, indicating what parts of a city that are in need of attention when it comes to green areas.

### Membership functions

#### Before interview:
For our initial membership functions, we made an “educated guess” on what was considered high and low values for the different inputs, with triangles and trapezoids as shapes (using scikit-fuzzy’s functions .trimf() and .trapmf()).

Click [here](./images/membership_functions/before_evaluation) for plots of our early membership functions.

#### After interview:

During the interview, we got some good tips on how we could improve our membership functions. For example, the membership function for population density is now adapted to the scale used in the Swiss Confederation’s official GIS [2].

We also changed the shape of our membership functions to gaussian curves, to reduce the effect of threshold values (e.g. population going from 6 to 7 inhabitants per ha, drastically changing the output). With smoother membership functions, the system also outputs a heatmap with smoother edges.

You can find our updated membership functions [here](./images/membership_functions/after_evaluation)

### Rules

BettAir’s fuzzy rules constitute the core of the software’s logical reasoning with the input data. As the city planner approved them as a reasonable way to determine the need for green areas, they remained almost unchanged after the evaluation interview: 

1. IF air pollution is ‘unhealthy’ AND population density is (‘high’ OR ‘very high’ OR ‘highest’) 
THEN need for action is ‘high’
2. IF air pollution is ‘unhealthy’ AND population density is (‘low’ OR ‘medium’) 
THEN need for action is ‘medium’
3. IF air pollution is ‘unhealthy’ AND population density is ‘very low’ 
THEN need for action is ‘low’
4. IF air pollution is ‘moderate’ 
THEN need for action is ‘medium’
5. IF air pollution is ‘clean’ 
THEN need for action is ‘low’
6. IF vegetation cover is ‘high’ 
THEN need for action is ‘low’

As the only post-evaluation change, Rule 1 had to be updated to handle the new term ‘highest’, as our new scale for air_pollution required six terms instead of our early implementation with only five.

### OpenAQ
We get our air quality pollution data in almost real time using the open air quality API, thus providing a more dynamic experience based on real data. The OpenAQ api is freely accessible online at openaq.org 

### Interface:
For an interface we are using a simple Python Flask web application. 

### Evaluation:
To assess the effectiveness and real-world applicability of our system, we conducted an interview with a professional from the city planning office in Bern. This discussion provided valuable insights into potential improvements and affirmed the system’s practical relevance. 
The interviewee responded positively to the concept of visualizing air quality data through maps rather than relying solely on point measurements. This map-based visualization aims to make air quality information more intuitive and accessible to the general public, who may lack specialized knowledge in this area. Although city planners are already adept at interpreting such data, the participant emphasized that intuitive visualizations could significantly aid in communicating project plans to residents. By clearly illustrating why and how projects are designed, the system can enhance public understanding and facilitate greater community involvement in urban planning processes.
Furthermore, the interview revealed additional factors that could enhance our system’s accuracy and utility. For instance, incorporating measurements related to the proximity of major motorways and nearby industrial sources of pollution could provide a more comprehensive picture of air quality issues. 

The city planner also pointed us toward valuable data sources for these additional measurements, which had not been initially apparent to our team. Integrating these factors and data sources would allow our system to offer more detailed and actionable insights, thereby improving its overall effectiveness in monitoring and managing urban air quality.

For a summary of our interview, please refer to the [Interview Report](.\interview_report.md).

### Discussion
We have developed a system that enhances the accessibility of a city’s air quality data for its residents by integrating real-time dynamic sensor data with a fuzzy rules-based framework to assess the severity of air quality issues. This approach is highly scalable, performing more effectively as additional sensors are deployed, which allows for a more detailed and accurate mapping of air quality distribution throughout the area.

Advancements in sensor technology further support the feasibility of our system, enabling implementation at a relatively low cost. With individual sensors available for approximately 50 CHF, cities can adopt this solution to gain valuable insights into air quality with minimal operational expenses.

Moreover, this system allows for the possibility of directly involving citizens by enabling them to link their personally owned sensors to the network. This crowdsourcing approach not only increases the density and reach of the sensor network but also fosters community engagement, empowering individuals to actively contribute to environmental monitoring and awareness.
This affordability and participatory model ensure municipalities can improve public awareness and response to air quality concerns without significant financial burdens, thereby providing substantial value through enhanced environmental monitoring.

### Project limitations
The current system relies on data from open sources, which provides us with moderately real-time air quality information. However, obtaining accurate data on the extent of green spaces has proven challenging and significantly limits the system's effectiveness. To approximate this data, we manually input information based on GIS maps that indicate the amount of green area surrounding the sensors. Nonetheless, the system would greatly benefit from a more precise and automated method for determining green space coverage.
From our interview, we learned that urban air quality is a multifaceted issue that cannot be fully addressed by simply increasing green spaces or reducing traffic. Numerous variables influence air quality, and accounting for all of them would be a substantial undertaking, extending beyond the scope of this project.

Additionally, the usability of the system could be enhanced by investing more effort into the user interface design. Since user interface development was not the primary focus of the course, the current design is relatively basic. Improving the interface to make the system more user-friendly and accessible would be a valuable enhancement, facilitating broader adoption and more effective use by both urban planners and the general public.


### References:
- http://apps.who.int/iris/bitstream/10665/250141/1/9789241511353-eng.pdf
- Maps of Switzerland - Swiss Confederation - map.geo.admin.ch, last checked at 02.12.2024
