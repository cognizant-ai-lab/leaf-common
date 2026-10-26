from leaf_common.resolution.deprecation_redirect import DeprecationRedirect


_DEPRECATION_REDIRECT = DeprecationRedirect(
    __name__,
    # A map from old class name to new class name for compatibility
    {
        "leaf_common.logging.conditional_logger.ConditionalLogger":
            "leaf_common.logging.env_var_conditional_logger.EnvVarConditionalLogger"
    },
    next_version="1.5.0"
)

def __getattr__(old_class: str) -> Type[Any]:
    """
    Redirect deprecated classes
    :param old_class: The old class name
    :return: The redirected class
    """
    return _DEPRECATION_REDIRECT.redirect_class(old_class)
