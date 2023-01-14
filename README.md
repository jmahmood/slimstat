# slimstat
A local-first Linux-based python application that uses statistics and a Nintendo Wii Fit Balanceboard to let you know if you are losing weight

## Requirements
- Nintendo Wii Fit Balanceboard
- Linux (Tested w/ Ubuntu 20.04)
- Python 3.8+

## How to use
1. Clone and install the application into a directory
2. Install the packages either into a virtualenv or your python environment 
3. Ensure your Wii Fit Balanceboard is connected to your computer
4. Run `main.py`
5. Step onto the Balanceboard and stand for 3 seconds.  Get off.  Repeat this process at least 5 times to get 5 readings.
6. Press the front button to get your analysis printed out.  Alternatively you can hit control-c

## Packages Used
- Scipy
- bbev
- evdev

## Warning
I'm not a dietitian nor am I in the health space.  I do have a B.Sc., but my experience with statistics was a long, long time ago.  This application is solely for myself, and I do not intend on modifying it for anyone else's purposes.   You are welcome to alter it and reuse it for your own purposes as long as you abide by the license (GPL v3)

## Long-Term Goals
- Integrate a camera with this to create records for self-comparison

## Why?
### Numbers Exaggerate
Anyone who has lost significant amounts of weight appreciates the stress of getting onto the scale and seeing weeks — or even months of progress — seemingly wiped out in a day or two of poor eating choices.  

If a kilogram of fat is 7700 calories, you are simply not likely to gain that much weight off of a day or two of minor excess. However, this temporary and obvious condition (a weight gain, most likely water weight) can cause anxiety and torpedo an otherwise effective weight loss journey.

### Numbers Inspire Extreme Solutions
Losing fat requires significant mental effort, and seeing how far one needs to go often results in extreme behavior, such as crash diets and/or highly restrictive diets.  

I intuitively agree people like Mike Isratel who claim long-term diets require diet breaks to avoid returning to bad habits; but a daily reminder of how far you need to go during a break is demoralizing.

### Numbers Are Imprecise
Many digital weight scales seem imprecise.  If you stand on them, with no changes, within a minute, you may get multiple readings with different weights.  Any calculations that happen in the backend are opaque and not-at-all valuable for the user; transparency into this should make it better.

(The lack of accuracy in scales is, in of itself, something [I](https://quran.com/17/35) see as immoral/)

### Measurements Are Essential
Dr. Layne Norton, [on the Jeff Nippard Podcast](https://youtu.be/d8V9ZaSq9Oc?t=764), has said that 'Regular Self-Monitoring' is of importance to improving your outcome.  This agrees with my own experiences (n=1).

### I Am Awful at Long-term Trends
Like most people, keeping my mind on long-term trends is hard to do.  There are already excellent applications such as Happy Scale that try to help, but I feel the outwards embracing of numbers is a mistake and create too much of an attachment.

### If Measurements are Demoralizing, but Essential, What Should We Do?
My personal experience is that the *measurement* itself is not demoralizing; it is the momentary association of a number with your weight.

Thus, to avoid demoralization, we concentrate on what matters.

a. Did you weigh yourself today?
b. Did you lose weight today compared to yesterday?
c. Did you lose weight today, compared to seven days ago?
d. Did you lose weight today, compared to one month ago?

A night of poor behavior might impact short term results, but the ease of turning the display from "false" to "true" could create the momentum needed to quick get rid of the unwanted weight. 

(If you really didn't eat 14,000 calories (which [is possible](https://www.youtube.com/watch?v=9dxRjlGio5k), but unlikely), it would be entirely possible to move the needle in a positive direction in a very short time frame)

### Statistics Can Help
My experience with scales, as I have mentioned before, is that they are not precise.  While I don't personally feel they are especially accurate either, they seem to be accurate enough to apply statistics too.

By taking multiple readings in a row, we can then establish a mean and a standard deviation for the values taken.  Then, using a [paired T-Test](https://www.jmp.com/en_gb/statistics-knowledge-portal/t-test/paired-t-test.html), you can theoretically compare your values today to your values on other dates.

The null hypothesis is that the average weight is equal to or greater than zero.  The alternate hypothesis is that the user's weight has reduced.

### Why the Nintendo Balanceboard?
The Balanceboard does not give precise kilogram amounts, or at least the one I have doesn't.  However, it is relatively accurate and the raw data from its sensors are readily available.

### Why Local?
I don't like this sort of data being in "the cloud".

## Inconvenient Things of Note
- The data from the Balanceboard is being stored in the database.  If someone was desperate to see what readings were found, they could examine and try to figure out their weight (although I don't think the Balanceboard is very precise at all)
- I only compare the user to similar data taken at a similar time.  Wearing different clothes / being inconsistent will make the data less useful. 
- This is using a one-tail t-test to determine if a user is losing weight.  It does not distinguish between a user's weight staying steady and a user's weight increasing.  A user could easily increase in weight the whole time.
- I am using a 90% confidence interval, not 95%.  Generally speaking you would use the latter if you wanted scientific evidence of weight loss, but frankly there are too many unknown unknowns at this time for me to get very serious about that.
- I generally believe the weight results from the Balanceboard to be normally distributed, but I haven't done anything beyond a basic visual examination of the data returned.  If it is not normal, the t-test is not appropriate
- I am taking random samples from the "before" and "current" data.  This means you could conceivably have minor differences, but unless there is a large stdev, I don't think this is a big deal.  (My current data shows very small stdevs after correcting for anomalous data from getting on and off of the balance board) 
- I am not correcting for the sample count from the Balanceboard yet.
