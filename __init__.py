def initialize(context):
    # Import lazily, and defer initialization to the module
    import XWFIdFactory
    XWFIdFactory.initialize(context)
