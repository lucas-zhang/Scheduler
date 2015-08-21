I. Brief Intro:
        This script is meant to do some basic scheduling for tour guides and tour times for a week. This is very useful since generally, that week's schedule can be repeated for the whole month and months generally are the same. Currently as the script is, each tour guide must do at most one tour a week and tour times must have unique start times, which prevents issues of multiple assignment and overlapping times. I did the best I could to make the script general for this specific problem. Hopefully this script is compatible to automate your scheduling process and save you hours of manual scheduling. 
    


II. Higher Level Overview and Algorithm Explained:
        Some clarifications: 
            - if a tour guide prefers a tour time, it means that the tour time is listed as a preference of the tour guide.

            - a tour time is associated to a preference group if it is preferred by a tour guide within the preference group

            - a preference group number refers to the amount of preferences that each tour guide within the preference group shares


        1) Read in tour guide names, statuses, and preferences from the input .csv file with a csv reader.



        2) Sort tour guides by preference groups. A preference group consists of tour guides with the same amount of preferred tour times. 



        3) For each preference group in ascending order (want to schedule people with less preferences first):
            a) If the preference group number is 0: 
                    add the preference group to an array called unassigned and continue to then next iteration


            b) Gather up all the preferred tour times from all tour guides within the preference group


            c) Sort tour times based off popularity (how many tour guides in the preference group prefer it)


            d) For each of these tour times if the tourtime has not reach its maxAllowed:
                i) Assign the tour guide (who is not in the assigned set) within the preference group who prefers the tour time the most compared to the other tour guides of the preference group

                ii) If there are ties, randomly choose the tourguide out of the tour guides who most prefer the tour time

                iii) Add the the tour guide to an assigned set, so he/she is not assigned again


            e) At this point, there can still be tour guides within the preference group unassigned since we may have filled each tour time associated with the preference group. Therefore, the script handles tour guides that are unassigned by either adding them to the array called unassigned or assigning them to a tour time within their preferences that is the least filled (max(max # allowed - current # assigned)). This is decided by the boolean leaveUnassigned that you specify in the .json file.



        4) Categorize the tour guides based off which tour time they are assigned to. Alphabetize the tour guides for each tour time by first or last name (also .json configurable). Alphabetize the unassigned tour guides by first or last name (same .json param referred to previous line). Sort the tour times from earliest to latest (Monday being the earliest day).



        5) Output the data to a csv file using a csv writer.



III. How to Use:
        You need 3 files to run this program: 1) scheduler.py(the main script), 2) a config.json which encodes in some input options, output options, and data, and 3) a .csv file with name (not extension) of choice with the relevant problem at hand and correct relevant columns and rows that you placed in config.json. Please look at config.json as an example and make sure not to change any of the keys names in the json file, but only values. I'll also be writing a template.py file which will create a json file for you where you just have to fill in the values of the json file.

        To run this file, make sure that scheduler.py, config.json, the .csv file as input are in the same directory. For this example let's just say the input .csv file is called input.csv. Then from terminal do the following (*** Note that the .csv you supply as the output will be overwritten if it already exists, so make sure it doesn't have anything important or that it's not in your directory in the first place. ***):

                    $ python scheduler.py input.csv output.csv config.json




IV. More about your .json file:
    *** All indices are 0 based
    input_csv_options is an object with the following keys:
        - startRowInd is the index 1st relevant data row (not including header rows)
        - fNameColInd is the index of the column with first names
        - lNameColInd is the index of the column with last names
        - firstPrefColInd is the index of the first tour time preference column
        - numPrefCols is the amount of tour time preference columns
        - statusColInd is the index of the status column, which indicates a tour guide's overall ability to contribute to leading tours during the semester/year
    
    - tours is an array of data objects which represent time slots. Each tour or time slot has and event name, time, and maxAllowed (raw number not percentage)

    - margin is a parameter which indicates how many people can be assigned over the amount of maxAllowed

    - leaveUnassigned is a boolean parameter indicating in the worst case, if someone can't get assigned since all of their preferred tours are filled, whether to leave them unassigned(leaveUnassigned: true) or to place them in their least filled preference (leaveUnassigned: false)

    -sortByFirst is a boolean parameter indicating whether to sort output by first name (sortByFirst: true) or last name (sortByFirst: false) 


    Also, I included an example with fake data called spring2015.csv file that is compatible with the config.json file, so if you're really having trouble with the json file, you can look in there also tosee how the json matches it. 



