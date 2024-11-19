# Package

This is a place to put things that work on data.

As of 7/13/2023, this really only means stuff that works on Pandas DataFrames,
but that could change at some point in the future.

## Organization

* interfaces - high level interface definitions. Includable by anything, as there are no dependencies.
* persistence - a place to put (ideally leaf-common Persistence) implementations that know
                how to persist/restore data from a file, somewhere
* transformations - data transformations that are generally applicable
* profiling - profiling a dataframe with all the information and statistics about the data, and 
                integrating multiple DataProfiler descriptions of a single field