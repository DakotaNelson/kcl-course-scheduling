The [KCL timetables site](http://timetables.kcl.ac.uk) is a giant pain to use.

This code uses selenium to drive Chrome (you can change the browser if you want) to scrape the times of all the modules (modules = courses/classes) you specify and put the results in a sqlite database using the excellent [dataset](http://dataset.readthedocs.io/en/latest/). That sqlite database is then used by a "module conflict detector" that takes your existing schedule and finds which modules fit in it. (You should still manually confirm - it only does partial validataion. For example, it only checks the lecture in any course with a lecture, not seminars, so you still might not be able to make those. Also there are some bugs I haven't hunted down, use at your own risk.)

It turns scheduling from a multi-hour chore to probably more like a single-hour chore, which is good enough.
