def ctypes_function_for_shared_library(libname: str):
    def ctypes_function(
        name: str, argtypes: List[Any], restype: Any
    ):
        enabled = libname in _libraries and hasattr(_libraries[libname], name)
        def decorator(f: F) -> F:
            if enabled:
                func = getattr(_libraries[libname], name)
                func.argtypes = argtypes
                func.restype = restype
                functools.wraps(f)(func)
                return func
            else:
                def f_(*args: Any, **kwargs: Any):
                    raise RuntimeError(
                        f"Function '{name}' is not available in the shared library '{libname}'."
                    )
                return cast(F, f_)

        return decorator

    return ctypes_function