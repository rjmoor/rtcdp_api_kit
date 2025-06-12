from BOUNTEOUS.KIT.rtcdp_api_kit.cli.segments_cli import SegmentHandler
from rtcdp.utils.auth_helper import AuthHelper

if __name__ == "__main__":
    auth = AuthHelper()
    handler = SegmentHandler(auth)
    handler.run_cli()
