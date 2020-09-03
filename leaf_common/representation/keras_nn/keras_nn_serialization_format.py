"""
See class comment for details
"""

from leaf_common.serialization.interface.serialization_format import SerializationFormat


class KerasNNSerializationFormat(SerializationFormat):
    """
    Implementation of the Persistence interface, enough to save/restore
    Keras neural-nets to/from a file.
    """

    def __init__(self, evaluator):
        """
        Constructor

        :param evaluator: The EspEvaluator to use to help decode the model bytes
        """
        self._evaluator = evaluator

    def get_file_extension(self):
        """
        :return: A string representing a file extension for the
                serialization method, including the ".".
        """
        return ".h5"

    def from_object(self, obj):
        """
        :param obj: The object to serialize
        :return: an open file-like object for streaming the serialized
                bytes.  Any file cursors should be set to the beginning
                of the data (ala seek to the beginning).
        """
        raise NotImplementedError

    def to_object(self, fileobj):
        """
        :param fileobj: The file-like object to deserialize.
                It is expected that the file-like object be open
                and be pointing at the beginning of the data
                (ala seek to the beginning).
    
                After calling this method, the seek pointer
                will be at the end of the data. Closing of the
                fileobj is left to the caller.
        :return: the deserialized object
        """
        keras_model = self._evaluator.keras_model_from_bytes(obj)
        return keras_model
