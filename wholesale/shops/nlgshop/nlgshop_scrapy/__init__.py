import sys
import os

# This is the BASE_DIR where the wholesale module is located.
# The following code adds this dir to the python path so that the scrapy project
# can use the wholesale module.
# This works by moving upwards in the directory tree using os.path.dirname until the
# right location is found.
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)
sys.path.append(BASE_DIR)
