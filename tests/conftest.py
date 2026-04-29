"""
Test configuration for quinn-awesome-skills.
Adds presearch modules to sys.path so bare imports work.
"""

import sys
import os

# Add presearch modules directory to sys.path so bare imports like
# `from translator import TechTranslator` work correctly
modules_dir = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "skills", "core", "presearch", "modules"
)
if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)