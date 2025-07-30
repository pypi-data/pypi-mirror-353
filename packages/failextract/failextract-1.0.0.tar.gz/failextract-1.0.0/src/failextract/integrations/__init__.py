"""Failextract Integrations Module.

This module contains all external integrations including CI/CD platforms,
chat systems, and editor integrations. These are designed as pluggable
components that can be extended without modifying core functionality.
"""

# Import editor integration components
try:
    from .editors import (
        EditorAdapter,
        EditorIntegration,
        LSPMessage,
        TestDiscoveryResult,
        FailureHighlight,
        EditorCommand
    )
    from .editors.adapters import VSCodeAdapter, GenericEditorAdapter, adapter_registry
    from .editors.lsp import LSPServer
    from .editors.vscode import VSCodeExtension
    
    __all__ = [
        "EditorAdapter",
        "EditorIntegration", 
        "LSPMessage",
        "TestDiscoveryResult",
        "FailureHighlight",
        "EditorCommand",
        "VSCodeAdapter",
        "GenericEditorAdapter",
        "adapter_registry",
        "LSPServer",
        "VSCodeExtension"
    ]
except ImportError:
    # Editor integration not available
    __all__ = []