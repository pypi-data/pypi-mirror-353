import os
import sys


if not __package__:
    package_source_path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, package_source_path)


from rongcloud_server_mcp.server import main


if __name__ == '__main__':
    main()
