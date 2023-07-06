import meo
import sys
sys.path.insert(0, meo.utils.ScriptPath(__file__).join("./SocketUI").path)

import SocketUI

SocketUI.run()