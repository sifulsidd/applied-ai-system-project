# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
The UML diagram will have there components, Task, Owner and Pet. A pet is assigned to one owner. An owner can select a task. A task will consist of a string of what needs to be done and contain an integer stating how long that task takes. The pet will contain the name for the pet and the owner's name. The owner will contain a name and an array of pets that he/she owns.

- What classes did you include, and what responsibilities did you assign to each?
I included the Owner, Pet and Task classes. A task will consist of a string of what needs to be done and contain an integer stating how long that task takes. The pet will contain the name for the pet and the owner's name. The owner will contain a name and an array of pets that he/she owns. 

**b. Design changes**

- Did your design change during implementation?
Yes, based on what I described there was a redundant, conflicting arrow between Owner and Pet.
- If yes, describe at least one change and why you made it.
I changed the redundancy by changing --> to *-- on the Owner-Pet relationship to show that pets are a part of an owner (All pets need an owner). Instead of just the owner name being in the Pet, I included a reference to the Owner class and the name being found that way. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
My scheduler currently checks the time of the task and duration.

- How did you decide which constraints mattered most?
I believe starting off with the time is the most efficient way, because from there we can figure out what else needs to be done. It's a basis for things that are to happen in the future. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
One tradeoff that is currently happening is if there are tasks in different days, my scheduler isn't identifying that right now. 

- Why is that tradeoff reasonable for this scenario?
Currently, it is only identifying the times and I believe this is okay for now because we have to figure out if the timing is correct first before we move onto add separate days. 

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I prompted Claude in order to brainstorm how to do the UML-diagram and based on the diagram I asked it for assistance in order to create the classes that were necessary.

- What kinds of prompts or questions were most helpful?
I believe the prompts that were the most benefical were the ones that contained the most directions. When Claude knew exactly what to do it was easier for it to solve the issues I was having. Also it didn't make any judgements and mess with the workflow I currently have. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
There was a point where my UML-diagram wasn't working as intended. It was showing a redundant relationship between my Owner and Pet. As a result, I had to ask Claude in order to help me figure it out further and debug the issue.

- How did you evaluate or verify what the AI suggested?
I verified it was working and evaluated it by running the mermaid.js code, I had to ensure everything was working as intended. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested whether a task status gets updated, whether a task gets added, sorting tasks by their time, testing if a daily task that has been completed gets added again, and test conflict detection with multiple tasks at the same time. 
- Why were these tests important?
These tasks verify the core funcitonalty of the app. If all these tasks work as intended then we can grow from here. Essentially these basics are the building blocks to implement more complex methods. 

**b. Confidence**

- How confident are you that your scheduler works correctly?
I am very confident it is working as anticipated based off of times. 

- What edge cases would you test next if you had more time?
I think an edge case I haven't checked is if we have an upcoming task on a different day, whether it conflicts with the current task or not if it is a repeating one. 

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am very satisfied with the app.py logic. I felt as if my AI needed the least input on that for correcting errors.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would redesign my pawpal_system. I think there are some edge cases I would reimplement or implement better. 

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
When designing large systems, AI tends to get out of whack. For me that occurred in the beginning when I was working on my UML diagram. As I created more and more of the project, AI knew how to implement changes in one file to other files. It worked effectively. 