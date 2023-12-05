from abc import ABCMeta

class NoAutoInitMeta(type):
    def __call__(cls, *args, **kwargs):
        return cls.__new__(cls, *args, **kwargs)


class NoAutoInitAndABCMeta(NoAutoInitMeta, ABCMeta):
    pass
