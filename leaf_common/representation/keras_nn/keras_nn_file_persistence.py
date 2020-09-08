"""
See class comment for details
"""

from leaf_common.persistence.factory.simple_file_persistence import SimpleFilePersistence
from leaf_common.representation.keras_nn.keras_nn_model_translator import KerasNNModelTranslator
from leaf_common.representation.keras_nn.keras_nn_serialization_format import KerasNNSerializationFormat


class KerasNNFilePersistence(SimpleFilePersistence):
    """
    Implementation of the Persistence interface, enough to save/restore
    Keras neural-nets to/from a file.
    """

    def __init__(self, model_translator: KerasNNModelTranslator):
        """
        Constructor

        :param model_translator: The KerasNNModelTranslator (often an EspEvaluator)
                 to use to help decode the model bytes
        """
        serialization_format = KerasNNSerializationFormat(model_translator)
        super(KerasNNFilePersistence, self).__init__(serialization_format)

    def persist(self, obj: object, file_reference: str = None) -> str:
        """
        Persists the object passed in.

        :param obj: an object to persist
        :param file_reference: The file reference to use when persisting.
        """
        file_name = self.affix_file_extension(file_reference)

        # Convert the received bytes to a Keras model
        # Use everything opaquely, so as not to explicitly drag in unwanted dependencies
        obj.save(file_name, include_optimizer=False)

        return file_name

    def restore(self, file_reference: str = None):
        """
        :param file_reference: The file reference to use when restoring.
        :return: an object from some persisted store
        """
        # Not yet
        raise NotImplementedError
