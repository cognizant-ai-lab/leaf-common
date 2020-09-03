"""
See class comment for details.
"""


class KerasNNModelTranslator():
    """
    Interface that translates a keras model into bytes abstractly
    """

    def keras_model_from_bytes(self, model_bytes: bytes) -> object:
        """
        Converts bytes into a Keras model
        :param model_bytes: bytes corresponding to a model (hdf5) or pickled weights dictionary
        :return: a Keras model
        """
        raise NotImplementedError
