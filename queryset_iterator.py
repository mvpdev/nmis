import gc


def queryset_iterator(queryset, chunksize=100):
    '''''
    Iterate over a Django Queryset.

    This method loads a maximum of chunksize (default: 100) rows in
    its memory at the same time while django normally would load all
    rows in its memory. Using the iterator() method only causes it to
    not preload all the classes.
    '''
    start = 0
    end = chunksize
    while start < queryset.count():
        for row in queryset[start:end]:
            yield row
        start += chunksize
        end += chunksize
        gc.collect()
