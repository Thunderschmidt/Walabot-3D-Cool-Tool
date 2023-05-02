import numpy


class CircularArray:
    """
    This is a class designed to store a stack of arrays.
    Used to store the history of clusters, which allows identification.
    """

    def __init__(self, stack_size):
        self.stack_size = stack_size
        self.the_stack = numpy.full(self.stack_size, None, dtype=object)
        self.head = self.stack_size - 1

    def push(self, objects):
        self.head = self.head - 1
        if self.head < 0: self.head = self.stack_size - 1
        self.the_stack[self.head] = objects

    def get(self, index=0):
        local_index = (index + self.head) % self.stack_size
        return self.the_stack[local_index]

    def get_complete_stack(self):
        returner = []
        for i in range(self.stack_size):
            returner.append(self.get(i))
        return returner
