"""
For various random utils that don't fit anywhere else.
"""


def split_list(main_list, chunk_size):
    """
    Splits the supplied list into sublists of size each `chunk_size`.
    There may be "stragglers" in the last returned list if `chunk_size` doesn't divide the original list evenly
    See: https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
    :param main_list: List to be split
    :param chunk_size: Number of elements to put in each chunk
    :return: A "list of lists", where each sublist is of size `chunk_size` except potentially for the last one
    which has the remaining items (mod chunk_size)
    """
    sub_lists = [
        main_list[i * chunk_size:(i + 1) * chunk_size]
        for i in range((len(main_list) + chunk_size - 1) // chunk_size)
    ]
    return sub_lists
