import inspect
from operator import itemgetter 


class Base(object):

    @property
    def properties(self):

        # TODO: Make this more explicit so user-added properties or decorators
        # don't show up here.
        def predicate(obj):
            return isinstance(obj, property)
        members = inspect.getmembers(self.__class__, predicate)
        names = map(itemgetter(0), members)
        names.remove('properties')
        return names

    def select(self, name, data):

        # TODO: Don't change object state here.
        self.data = data
        return getattr(self, name)