from typing import Any
from typing import Type

from leaf_common.resolution.deprecation_redirect import DeprecationRedirect

_DEPRECATION_REDIRECTS = DeprecationRedirect(
    __name__,
    {
        "leaf_common.config.resolver.Resolver": "leaf_common.resolution.resolver.Resolver",
        "leaf_common.config.resolver_util.ResolverUtil": "leaf_common.resolution.resolver_util.ResolverUtil",
    }
)


def __getattr__(old_class: str) -> Type[Any]:
    """
    Redirect deprecated classes
    :param old_class: The old class name
    :return: The redirected class
    """
    return _DEPRECATION_REDIRECT.redirect_class(old_class)
